# Release v1.10.0

Release notes draft — factual skeleton for the v1.10.0 release candidate.
Polished highlights are curated at release time; see `doc/CHANGELOG.md` for
the detailed change history.

## 📦 Quick Start

### Use the release artifact (pre-built client)

When a release is published, CI (`.github/workflows/release-build.yml`)
attaches `project-with-build.zip` to the GitHub release. It contains the full
project with the frontend already built into `client/build/`.

1. **Download `project-with-build.zip`** from the
   [Releases page](https://github.com/databricks-solutions/project-0xfffff/releases)
   and unzip it.

2. **Run the server:**
   ```bash
   uv run uvicorn server.app:app --port 8000
   ```
   The database is bootstrapped automatically on startup (Alembic migrations).

3. **Open your browser:**
   ```
   http://localhost:8000
   ```

### Build from source

```bash
git clone https://github.com/databricks-solutions/project-0xfffff.git
cd project-0xfffff
just setup        # uv + npm install, configure
just dev          # API (8000) + UI dev server
```

### Deploy to Databricks Apps

```bash
just configure    # set app name / profile
just deploy       # databricks sync + apps deploy (source-based)
```

Databricks Apps builds on the platform (`npm install` → `pip install -r
requirements.txt` → `npm run build`) and runs the `app.yaml` gunicorn command.
On Apps the default backend is Lakebase Postgres (`DATABASE_ENV=postgres`);
see the in-app setup guide at `/docs/lakebase-setup/`.

## ✨ What's in v1.10.0 (high level)

- **Lakebase (Postgres) persistence** — app data lives in Lakebase on
  Databricks Apps and survives container restarts; SQLite remains the local
  development backend
- **Setup gate + bundled docs site** — the app serves a Docusaurus docs site
  (including the Lakebase setup guide) and gates the UI until Lakebase is
  configured on Postgres targets
- **Optimistic startup** — migration/bootstrap failures no longer prevent the
  server from starting; setup docs stay reachable while the database comes up
- **Discovery, annotation, judge alignment, and eval-mode improvements** —
  see `doc/CHANGELOG.md` for the full list

## 📚 Documentation

- [Specs Index](/specs/) — searchable specifications index
- [Facilitator Guide](/FACILITATOR_GUIDE) — deployment and workshop facilitation
- [Lakebase Setup](/lakebase-setup) — Lakebase configuration for Databricks Apps
- [BUILD_AND_DEPLOY_SPEC](/specs/BUILD_AND_DEPLOY_SPEC) — build, deploy, and migrations

## 📝 License

See [LICENSE.md](https://github.com/databricks-solutions/project-0xfffff/blob/main/LICENSE.md) for details.
