---
id: BUILD_AND_DEPLOY_SPEC
title: Build and Deploy Specification
---

import SpecCoverage from '@site/src/components/SpecCoverage';

# Build and Deploy Specification

## Overview

This specification defines the build process, database migrations, and deployment procedures for the Human Evaluation Workshop. It covers frontend builds, backend database management with Alembic (SQLite locally, Lakebase Postgres on Databricks Apps via `DATABASE_ENV=postgres`), and production deployment to Databricks Apps.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Build & Deploy Pipeline                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Frontend   │    │   Backend    │    │   Database   │  │
│  │  (Vite/React)│    │  (FastAPI)   │    │   (SQLite)   │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘  │
│         │                   │                   │           │
│         ▼                   ▼                   ▼           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  npm build   │    │  gunicorn +  │    │   Alembic    │  │
│  │  (terser)    │    │uvicorn worker│    │  migrations  │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Frontend Build

### Vite Configuration

The frontend uses Vite with terser for production builds.

**File**: `client/vite.config.ts`

```typescript
export default defineConfig({
  build: {
    outDir: 'build',
    minify: 'terser',
    terserOptions: {
      compress: {
        // Temporarily keep console statements for debugging
        // TODO: Re-enable drop_console: true for production
        drop_console: false,
        drop_debugger: true,   // Remove debugger statements
      },
    },
  },
});
```

### Build Commands

| Command | Purpose | Output |
|---------|---------|--------|
| `just ui-build` (`npm run build`) | Production build | `client/build/` |
| `just ui-dev` (`npm run dev`) | Development server | localhost:5173 |
| `npm run preview` | Preview production build | localhost:4173 |

### Console and Debugger Statements

Production builds remove `debugger` statements (`drop_debugger: true`).

`console.*` statements are **currently preserved** in production builds
(`drop_console: false`) to aid debugging of deployed apps. Re-enabling
`drop_console: true` is roadmap (see Success Criteria); when that happens this
section and the linked tests must be updated together.

### Build Output

```
client/build/
├── index.html
├── assets/
│   ├── index-[hash].js      # Main bundle (minified)
│   ├── index-[hash].css     # Styles (minified)
│   └── [chunk]-[hash].js    # Code-split chunks
└── ...
```

---

## Database Migrations (Alembic)

### Overview

The project uses Alembic for database migrations against both backends: SQLite (local development, E2E) and Lakebase Postgres (`DATABASE_ENV=postgres`, the Databricks Apps default in `app.yaml`). SQLite migrations use batch mode (required for SQLite's limited ALTER TABLE capabilities).

### Configuration Files

| File | Purpose |
|------|---------|
| `alembic.ini` | Alembic CLI configuration |
| `migrations/env.py` | Migration environment setup |
| `migrations/versions/*.py` | Individual migration scripts |
| `server/db_bootstrap.py` | Bootstrap module |
| `gunicorn_conf.py` | Gunicorn server hooks (runs migrations in master before workers fork) |

### Migration Commands (via justfile)

| Command | Purpose |
|---------|---------|
| `just db-bootstrap` | Bootstrap database (create if missing, run migrations) |
| `just db-upgrade` | Apply pending migrations |
| `just db-stamp` | Mark existing DB as up-to-date with current migrations |
| `just db-revision message="..."` | Create new migration |

### Migration Files

```
migrations/versions/
├── 0001_baseline.py              # Initial schema
├── 0002_legacy_schema_fixes.py   # Legacy compatibility
├── 0003_judge_schema_updates.py  # Judge table updates
├── ...                           # 0004–0021: feature migrations
│                                 # (randomization, discovery, summarization,
│                                 #  eval mode, social threads, ...)
└── 0f8f0efbbe57_add_assisted_facilitation_v2_tables.py
```

The history contains parallel branches (duplicate `0006`–`0010` prefixes,
different slugs) joined by merge revisions (`0013_merge_heads.py`,
`0015_merge_analysis_and_draft_rubric.py`). `alembic upgrade head` resolves
the full graph; see `migrations/versions/` for the authoritative list.

### Batch Mode for SQLite

SQLite cannot perform many ALTER TABLE operations directly. Alembic uses batch mode:

```python
# In migration file
def upgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('new_column', sa.String()))
```

This creates a new table, copies data, drops old table, and renames.

### Bootstrap Behavior

**Development**: `just api-dev`, `just api`, and `just dev` automatically run `just db-bootstrap` before starting.

**Production (Gunicorn)**: The `gunicorn_conf.py` `on_starting` hook runs `bootstrap_database(full=True)` once in the master process before workers fork. This ensures pending migrations are applied before any worker accepts traffic when the database is reachable. Startup is **optimistic**: if bootstrap fails (e.g., Lakebase is unconfigured or waking up), the failure is logged and gunicorn continues starting so the app can still serve `/docs` and the setup-status gate. Database-backed routes may return errors until the database becomes available.

**Production (Manual)**: Run `just db-bootstrap` as a separate step before starting the server.

### Startup Fallback

When running under **uvicorn directly** (dev mode, no gunicorn master), the FastAPI lifespan calls `maybe_bootstrap_db_on_startup()` as a fallback. This is skipped under gunicorn since the `on_starting` hook handles it.

| Scenario | Behavior |
|----------|----------|
| DB file missing | Create via Alembic (with file lock for multi-worker safety) |
| DB exists, no migration table | Stamp to baseline |
| DB exists, pending migrations | Apply if `DB_BOOTSTRAP_ON_STARTUP=true` |

**Environment Variable**:
- `DB_BOOTSTRAP_ON_STARTUP=true`: Auto-stamp legacy DBs + apply pending migrations
- `DB_BOOTSTRAP_ON_STARTUP=false`: Disable fallback entirely

### Creating New Migrations

After modifying `server/database.py`:

```bash
just db-revision message="add user preferences"
```

This auto-generates a migration based on model changes.

---

## Deployment

### Databricks Apps Deployment Command

```bash
just deploy
```

This deploys source (not artifacts) to a Databricks App:
1. `databricks sync . "$WORKSPACE_PATH"` — sync the repo to the workspace,
   excluding `.git`, `.claude`, `node_modules`, `package-lock.json`,
   `__pycache__`, `*.db`, `.venv`, `docs/.docusaurus`, `docs/build`,
   `docs/package-lock.json`, `.e2e-*`, and `htmlcov`
2. `databricks apps create "$APP"` — create the app if it doesn't exist
3. `databricks apps deploy "$APP" --source-code-path "$WORKSPACE_PATH"`

The Databricks Apps build then runs on the platform:
`npm install` → `pip install -r requirements.txt` → `npm run build` → the
`app.yaml` command. Requires `DATABRICKS_APP_NAME` (set by `just configure`)
and optionally `DATABRICKS_CONFIG_PROFILE`.

There is no `deploy.sh`; database bootstrap happens at app startup via the
gunicorn `on_starting` hook (see Bootstrap Behavior), not as a deploy step.

### Manual Steps (local production-style run)

```bash
# 1. Database
just db-bootstrap

# 2. Frontend
cd client && npm install && npm run build && cd ..

# 3. Server
uv run uvicorn server.app:app --host 0.0.0.0 --port 8000
```

### Production Server

The `app.yaml` command (what Databricks Apps actually runs):

```bash
gunicorn server.app:app \
  -c gunicorn_conf.py \
  -w 2 \
  --worker-class uvicorn.workers.UvicornWorker \
  --timeout 1800
```

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `DATABASE_URL` | Database connection string (SQLite only) | `sqlite:///workshop.db` |
| `DATABASE_ENV` | Database backend: `postgres` (Lakebase) or `sqlite` | `sqlite` |
| `DB_BOOTSTRAP_ON_STARTUP` | Auto-run migrations on startup | `false` |
| `MLFLOW_TRACKING_URI` | MLflow server URL (set to `databricks` on Apps) | (required) |
| `DATABRICKS_HOST` | Databricks workspace URL (set by platform on Apps, developer locally) | (required) |
| `MLFLOW_EXPERIMENT_ID` | MLflow experiment ID (from app.yaml resource declaration) | (required) |
| `DATABRICKS_TOKEN` | Databricks access token (fallback — SDK auth preferred) | (optional) |
| `PGHOST` | Lakebase endpoint hostname | (required for Lakebase) |
| `PGDATABASE` | Lakebase database name | `databricks_postgres` |
| `PGUSER` | Lakebase username (service principal `DATABRICKS_CLIENT_ID`) | (required for Lakebase) |
| `PGPORT` | Lakebase port | `5432` |
| `PGSSLMODE` | Lakebase SSL mode | `require` |
| `PGAPPNAME` | Application name for connection tracking / schema derivation | `human-eval-workshop` |
| `ENDPOINT_NAME` | Lakebase endpoint for credential generation (`projects/<id>/branches/<id>/endpoints/<id>`) | (required for Lakebase) |

---

## Justfile Commands

### Database

```bash
just db-bootstrap     # Bootstrap database
just db-upgrade       # Run Alembic migrations
just db-stamp         # Stamp current migration
just db-revision      # Create new migration
```

### Development

```bash
just dev              # Start full dev environment (API + UI)
just api-dev          # Start API with hot reload
just ui-dev           # Start frontend dev server
```

### Testing

```bash
just test-server      # Run Python unit tests
just test-integration # Run Python integration tests
just ui-test          # Run React tests (typecheck + vitest)
just e2e              # Run E2E tests (headless)
just e2e headed       # Run E2E tests (with browser)
just e2e ui           # Run E2E tests (Playwright UI)
```

### Build & Deploy

```bash
just ui-build         # Build frontend
just deploy           # Sync source to the workspace and deploy the Databricks App
```

---

## GitHub Actions (Releases)

### Automated Release Workflow

**File**: `.github/workflows/release-build.yml`

Triggers on:
- GitHub release **published**

Creates:
- `project-with-build.zip` with pre-built client, uploaded as a release asset
  via `softprops/action-gh-release`

### Release Artifact Contents

```
project-with-build.zip
├── server/
├── client/
│   └── build/          # Pre-built frontend
├── migrations/
├── alembic.ini
├── pyproject.toml
└── README.md
```

**Excludes**: `node_modules/`, `.git/`, `.github/`, `*.db`, `__pycache__/`,
`.env`, `.venv/`/`venv/`, `uv.lock`, `doc/`, test caches, and editor/OS files

---

## Success Criteria

<SpecCoverage spec="BUILD_AND_DEPLOY_SPEC" />

### Frontend Build
- [ ] Production build completes without errors
- [ ] Assets minified and hashed
- [ ] Build directory contains all required files

### Database Migrations
- [ ] `just db-bootstrap` creates database if missing
- [ ] Migrations apply without errors
- [ ] Batch mode works for SQLite ALTER TABLE
- [ ] File lock prevents race conditions with multiple workers
- [ ] Pending Alembic migrations are applied automatically before workers accept traffic
- [ ] Lakebase schema privilege grants are best-effort

### Deployment
- [ ] Full deployment completes successfully
- [ ] App serves setup docs and gates the UI until Lakebase is configured (postgres targets only; sqlite deployments are fully operable without setup)
- [ ] Server starts and serves frontend
- [ ] API endpoints respond correctly
- [ ] Database connection established
- [ ] Lakebase (Postgres) persistence: with `DATABASE_ENV=postgres`, bootstrap provisions the app schema and reuses existing data across restarts

### CI/CD
- [ ] Release workflow creates zip artifact
- [ ] Pre-built client included in release
- [ ] No sensitive files in artifact
- [ ] Lockfiles resolve against public registries (no internal proxy URLs)

### Roadmap
- [ ] Console statements removed in production (roadmap)

---

## Troubleshooting

### Build Fails

```bash
# Clear cache and rebuild
rm -rf client/node_modules client/build
npm -C client install
npm -C client run build
```

### Migration Errors

```bash
# Reset to known state
rm workshop.db
just db-bootstrap
```

### Multi-Worker Database Issues

Ensure `DB_BOOTSTRAP_ON_STARTUP=false` in production and run migrations as a separate step before starting workers.

## Databricks Apps Deployment

### Overview

When deploying to Databricks Apps, the application runs in ephemeral containers that can be restarted during platform updates. SQLite databases stored on the local container filesystem will be lost. The SQLite Rescue module provides
persistence by backing up to Unity Catalog Volumes.

### Databricks Apps Authentication

Databricks Apps automatically provides authentication to workspace resources via a dedicated **service principal**. The application uses Databricks SDK unified auth exclusively — no PAT tokens are accepted from users or stored.

**Automatic Credentials** (injected by the platform):
- `DATABRICKS_CLIENT_ID` - Service principal client ID
- `DATABRICKS_CLIENT_SECRET` - Service principal client secret

**How it works**:
- `resolve_databricks_token()` in `server/services/databricks_service.py` calls `WorkspaceClient().config.authenticate()` which auto-detects the injected credentials
- MLflow uses the same SDK auth via `mlflow.set_tracking_uri('databricks')`
- No token input fields exist in the UI — auth is fully automatic
- See [AUTHENTICATION_SPEC](./AUTHENTICATION_SPEC.md) § Databricks API Authentication for the full contract

**Best Practices**:
- Never hardcode personal access tokens (PATs) in code
- Use the app's service principal for all Databricks API calls
- Don't share service principal credentials between apps
- Apply least privilege: grant only minimum required permissions

**Resource Permissions**:
| Resource Type | Common Permissions |
|--------------|-------------------|
| SQL Warehouse | CAN USE (queries), CAN MANAGE |
| Unity Catalog Volume | Can read, Can read and write |
| Secrets | Can read, Can write, Can manage |
| Model Serving Endpoint | Can view, Can query, Can manage |
| MLflow Experiments | Can read, Can edit, Can manage |

**Configuring Resources**:
1. In Databricks Apps UI, navigate to Configure step
2. Click "+ Add resource" in App resources section
3. Select resource type and set permissions for app service principal
4. Assign a key and reference in `app.yaml` via `valueFrom`

Reference: [Databricks Apps Resources Documentation](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/resources)

### SQLite Rescue Module

**Purpose**: Persist SQLite database across container restarts by backing up to Unity Catalog Volumes.

**IMPORTANT**: Databricks Apps do NOT support FUSE mounts for UC volumes. This module uses the
Databricks SDK Files API (`WorkspaceClient.files`) for all volume operations.

**Architecture**:
┌─────────────────────────────────────────────────────────────────┐
│                     CONTAINER LIFECYCLE                          │
├─────────────────────────────────────────────────────────────────┤
│  STARTUP                                                         │
│  1. Check Unity Catalog Volume for backup (via SDK Files API)    │
│  2. If found → download to local filesystem                      │
│  3. Bootstrap/migrate as usual                                   │
├─────────────────────────────────────────────────────────────────┤
│  RUNNING                                                         │
│  4. SQLite operates on local file (fast)                         │
│  5. After N write operations → background upload to Volume       │
├─────────────────────────────────────────────────────────────────┤
│  SHUTDOWN (SIGTERM)                                              │
│  6. Signal handler triggers backup to Volume                     │
│  7. Upload local DB → Unity Catalog Volume (via SDK Files API)   │
│  8. Exit cleanly                                                 │
└─────────────────────────────────────────────────────────────────┘

**Configuration** (`app.yaml`):

Recommended: Use `valueFrom` to reference an App resource (the volume path is injected automatically):
```yaml
env:
  - name: SQLITE_VOLUME_PATH
    valueFrom: db_backup_volume  # Resource key from Apps UI
  - name: SQLITE_BACKUP_INTERVAL_MINUTES
    value: "10"  # Backup every 10 minutes (default: 10, 0 to disable)
```

Alternative: Hardcode the full path (less portable):
```yaml
env:
  - name: SQLITE_VOLUME_BACKUP_PATH
    value: "/Volumes/<catalog>/<schema>/<volume>/workshop.db"
```

Environment Variables:
┌─────────────────────────────────┬──────────────────────────────────────────────────┬──────────────────────────┐
│            Variable             │               Purpose                            │         Default          │
├─────────────────────────────────┼──────────────────────────────────────────────────┼──────────────────────────┤
│ SQLITE_VOLUME_PATH              │ Base volume path (appends /workshop.db)          │ (none - rescue disabled) │
├─────────────────────────────────┼──────────────────────────────────────────────────┼──────────────────────────┤
│ SQLITE_VOLUME_BACKUP_PATH       │ Full path including filename (overrides above)   │ (none - rescue disabled) │
├─────────────────────────────────┼──────────────────────────────────────────────────┼──────────────────────────┤
│ SQLITE_BACKUP_INTERVAL_MINUTES  │ Minutes between automatic backups                │ 10                       │
└─────────────────────────────────┴──────────────────────────────────────────────────┴──────────────────────────┘

Key Files:
┌─────────────────────────┬─────────────────────────────────────────────────────────┐
│          File           │                         Purpose                         │
├─────────────────────────┼─────────────────────────────────────────────────────────┤
│ server/sqlite_rescue.py │ Core backup/restore logic (uses Databricks SDK)         │
├─────────────────────────┼─────────────────────────────────────────────────────────┤
│ server/app.py           │ Lifespan integration (startup restore, shutdown backup) │
└─────────────────────────┴─────────────────────────────────────────────────────────┘

API:
- restore_from_volume() - Called on startup before DB bootstrap
- backup_to_volume(force=True) - Called on shutdown
- start_backup_timer() - Starts periodic background backup (every N minutes)
- stop_backup_timer() - Stops the background backup timer
- get_rescue_status() - Returns current config and status (exposed in /health/detailed)

Prerequisites:
1. Create Unity Catalog Volume in your workspace
2. Add the volume as an App resource in the Apps UI
3. Grant the app "Can read and write" permission on the volume
4. Assign a resource key (e.g., "db_backup_volume")
5. Configure SQLITE_VOLUME_PATH in app.yaml using `valueFrom`

Health Check:
The /health/detailed endpoint includes sqlite_rescue status:
```json
{
  "sqlite_rescue": {
    "configured": true,
    "volume_backup_path": "/Volumes/catalog/schema/volume/workshop.db",
    "backup_interval_minutes": 10,
    "local_exists": true,
    "volume_backup_exists": true,
    "sdk_available": true,
    "backup_timer_running": true,
    "shutdown_handlers_installed": true
  }
}
```

Limitations:
- Uses Databricks SDK Files API (FUSE mounts NOT supported in Apps)
- The rescue module copies the entire DB file; not suitable for very large databases
- Brief data loss possible if container crashes between backups (up to backup interval worth of writes)

## Implementation Log

| Date | Plan | Status | Summary |
|------|------|--------|---------|
| 2026-04-10 | [SDK Auth Migration](../.claude/plans/2026-04-10-sdk-auth-migration.md) | complete | Replace PAT token auth with SDK auth; update Databricks Apps auth section; add Lakebase env vars |
| 2026-04-11 | (inline) | complete | Fix Lakebase connection pool: `do_connect` token injection, `pool_recycle=3600`, `pool_pre_ping=False`, `generate_database_credential()` API |
| 2026-04-11 | [Gunicorn on_starting hook](../.claude/plans/jaunty-leaping-lighthouse.md) | complete | Run Alembic migrations in gunicorn master before workers fork |
| 2026-06-10 | (inline) | complete | v1.10 honesty pass: optimistic-startup prose (no gunicorn exit on migration failure), real `just deploy` path (databricks sync + apps deploy; no deploy.sh), console removal moved to roadmap (`drop_console: false` today), added Lakebase persistence + registry-portability criteria and genuine runtime tests |

