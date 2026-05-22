# Authentication Specification

## Overview

This specification defines the authentication flow, permission management, and session handling for the Human Evaluation Workshop system. It establishes requirements for reliable login, graceful error recovery, and proper loading state management.

## Architecture Context

V2 uses provider-resolved app identity. In production, Databricks Apps authenticates users before requests reach the application and forwards trusted identity headers to the backend. The SPA does not present an app-owned login screen and does not restore users from browser-stored app session state.

The system has two distinct authentication concerns:

1. **Workshop application auth** (this spec) — login, roles, permissions, sessions
2. **Databricks API auth** — how the backend authenticates to Databricks services (MLflow, serving endpoints, volumes)

```
┌─────────────────────────────────────────────────────────────┐
│                    Databricks Workspace                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         Databricks API Auth (SDK-based)              │    │
│  │    Service principal (Apps) / CLI profile (local)    │    │
│  └─────────────────────────────────────────────────────┘    │
│                           │                                  │
│                           ▼                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │        Workshop Application Auth (this spec)         │    │
│  │    (handles app-specific roles & permissions)        │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

**Why two layers?**
- Databricks API auth handles backend-to-Databricks communication (MLflow traces, serving endpoints, volume access)
- Workshop auth handles application-level permissions (what users can do within the app)
- Workshop roles (participant, SME, facilitator) are app-specific concepts not in Databricks IAM

## V2 Application Identity

### Current Session

`GET /api/auth/session` is the frontend source of truth for authentication and authorization state.

- `200` means the backend resolved a trusted provider identity, materialized or updated the app user, resolved provider role, and returned role/capability permissions.
- `401` means no valid provider identity was present. The frontend does not render a login form; Databricks Apps is expected to redirect unauthenticated production users to Databricks login before the SPA loads.
- The frontend uses TanStack Query for the current-session query.
- Browser localStorage must not store or restore app user session state.

### IdentityProvider Boundary

The backend owns an identity-provider boundary. Providers return provider facts; the auth session service maps those facts into app users and app permissions.

Provider facts:

```python
ProviderIdentity {
  provider: str
  email: str
  display_name: str | None
}

ProviderRole = "CAN_MANAGE" | "CAN_USE"
```

Provider requirements:

- Missing provider identity is unauthenticated.
- Databricks Apps identity comes from forwarded identity headers such as `X-Forwarded-Email`, `X-Forwarded-User`, and `X-Forwarded-Preferred-Username`.
- Databricks Apps role comes from Databricks Apps permissions data, using the forwarded `X-Forwarded-Access-Token` with SDK Apps `get_permissions(app_name)` or an equivalent documented endpoint.
- `DATABRICKS_APP_NAME` or `APP_NAME` must be set in Apps deployment so the backend knows which app's permissions to query.
- If app name, delegated token, or permission lookup is unavailable, an authenticated Databricks Apps user falls back to `CAN_USE`.
- Provider role lookup may use a short TTL cache so Databricks App permission changes appear after a normal session refresh without calling the provider permissions endpoint on every protected route.
- `LocalDevIdentityProvider` implements the same session contract, defaults to `CAN_MANAGE`, and can be configured to return `CAN_USE` in tests.

### Authorization Mapping

- `CAN_MANAGE` grants `can_manage_project` and materializes the app user as a facilitator.
- `CAN_USE` grants non-power-user app access and does not grant `can_manage_project`.
- Existing non-facilitator app subroles such as `sme` and `participant` may remain in the user model; new `CAN_USE` users default to SME.
- App user display data and status are persisted locally.

### Removed Legacy Auth

V2 removes app-owned password login:

- No frontend login form.
- No `/users/auth/login` endpoint.
- No facilitator YAML password config.
- No password hash persistence on users.
- No browser-restored `workshop_user` session.

## Databricks API Authentication

All Databricks API calls (MLflow, model serving, volume access) use the **Databricks SDK unified auth**. Users never provide Personal Access Tokens (PATs) through the UI.

### Token Resolution

The backend resolves auth tokens via `resolve_databricks_token()` in `server/services/databricks_service.py`:

```
Token Resolution Order:
1. Databricks SDK (WorkspaceClient().config.authenticate())
   - On Databricks Apps: uses platform-injected service principal
     (DATABRICKS_CLIENT_ID / DATABRICKS_CLIENT_SECRET)
   - Locally: uses CLI profile from `databricks auth login`
2. DATABRICKS_TOKEN environment variable (fallback for CI/containers)
3. Raise RuntimeError if nothing available
```

### Environment-Specific Behavior

| Environment | Auth Method | Setup |
|-------------|-------------|-------|
| Databricks Apps | Service principal (automatic) | Platform injects `DATABRICKS_CLIENT_ID`/`SECRET` |
| Local development | CLI profile | Run `databricks auth login --host <workspace-url>` |
| CI / containers | Environment variable | Set `DATABRICKS_TOKEN` |

### MLflow Auth

MLflow operations (`search_traces`, `log_feedback`, `set_experiment`) use whatever auth the Databricks SDK provides. `DATABRICKS_HOST` is set by the platform (Databricks Apps) or the developer (`.env.local`). `MLFLOW_EXPERIMENT_ID` is provided via the app.yaml resource declaration. The backend calls `mlflow.set_tracking_uri('databricks')` — the SDK handles auth automatically. No user-configurable host or token is stored.

### Required Service Principal Permissions

The app's service principal needs access to these Databricks resources. On Databricks Apps, grant these through the Apps UI "Add resource" flow.

#### Core Resources (required)

| Resource | Operations | Required Permission |
|----------|-----------|-------------------|
| **Lakebase (PostgreSQL)** | Primary production database. OAuth tokens injected per-connection via `do_connect` event. Configured via `DATABASE_ENV=postgres` + `PGHOST`/`PGDATABASE`/`PGUSER`/`ENDPOINT_NAME` env vars. | Postgres role with `databricks_auth` extension ([docs](https://docs.databricks.com/aws/en/lakebase/admin/authentication.html)) |
| **MLflow Experiment** | `search_traces`, `get_experiment`, `set_experiment`, `log_feedback`, `set_trace_tag`. Declared as app.yaml resource (`MLFLOW_EXPERIMENT_ID`). | Can edit |
| **Model Serving Endpoints** | `chat.completions.create` (judge evaluation, rubric generation, discovery). Includes embedding endpoints (e.g. `databricks-gte-large-en`) used by MemAlign. | Can query |

#### Optional Resources

| Resource | Operations | When Needed | Required Permission |
|----------|-----------|-------------|-------------------|
| **SQL Warehouse** | DBSQL export via `databricks.sql.connect()` | DBSQL export feature | Can use |
| **Unity Catalog Volume** | SQLite backup/restore via SDK Files API (`files.upload`, `files.download`, `files.get_status`) | Only if using SQLite with SQLite Rescue (not needed with Lakebase) | Can read and write |

### Lakebase Connection Pool

The app connects to Lakebase Autoscaling (serverless PostgreSQL) using SQLAlchemy + psycopg with OAuth token rotation. This section defines the required connection pool behavior.

**Reference:** [Connect a custom Databricks app to Lakebase](https://docs.databricks.com/aws/en/lakebase/connect/custom-app.html), [Token rotation in Lakebase](https://docs.databricks.com/aws/en/lakebase/connect/token-rotation.html)

#### Token Lifecycle

- OAuth tokens expire after **1 hour**, but expiration is enforced **only at connection establishment** (login), not on existing connections
- Existing pooled connections remain valid after their token expires — no need to recycle them
- Fresh tokens are needed only when creating **new** physical connections (pool growth or replacing dropped connections)

#### Token Injection Pattern

Use the SQLAlchemy `do_connect` event listener to inject fresh tokens into new physical connections. Do **not** bake the token into the connection URL or use a `creator` callable.

```python
@event.listens_for(engine, "do_connect")
def provide_token(dialect, conn_rec, cargs, cparams):
    # Refresh token if near expiry (2 min buffer before 1-hour lifetime)
    if token is None or near_expiry:
        cred = w.postgres.generate_database_credential(endpoint=endpoint_name)
        token = cred.token
    cparams["password"] = token
```

**Reference:** [About authentication in Lakebase](https://docs.databricks.com/aws/en/lakebase/admin/authentication.html)

#### Required Pool Settings

| Setting | Value | Rationale |
|---------|-------|-----------|
| `pool_size` | 5 | Matches recommended range (5–10). With 2 gunicorn workers = 10 base connections. |
| `max_overflow` | 5 | Caps burst at 10 per worker, 20 total. Docs recommend 0–5. |
| `pool_recycle` | 3600 | Match 1-hour token lifetime. 300s (5 min) causes excessive connection churn. |
| `pool_pre_ping` | False | Conflicts with `do_connect` token injection. Use retry logic instead. |

#### Credential API

For Lakebase Autoscaling, use `WorkspaceClient().postgres.generate_database_credential(endpoint=endpoint_name)` to generate connection-scoped credentials. This requires the `ENDPOINT_NAME` environment variable (format: `projects/<id>/branches/<id>/endpoints/<id>`).

**Reference:** [Connect external app to Lakebase using SDK](https://docs.databricks.com/aws/en/lakebase/connect/external-app.html)

#### Lakebase Setup Prerequisites

**Databricks Apps (production):** Add the Lakebase database as an App resource in the Apps UI. Databricks automatically creates a Postgres role for the app's service principal (named after its `DATABRICKS_CLIENT_ID`) with `CONNECT` and `CREATE` grants. No manual role creation needed.

**External / additional identities:** If connecting from outside Databricks Apps or adding extra identities beyond the app SP, a workspace admin must manually create roles:

1. Enable the `databricks_auth` extension: `CREATE EXTENSION IF NOT EXISTS databricks_auth`
2. Create a Postgres role: `SELECT databricks_create_role('<DATABRICKS_CLIENT_ID>', 'service_principal')`
3. Grant `CONNECT` on the database and `CREATE, USAGE` on schemas
4. Grant table-level permissions on app tables

**Reference:** [Lakebase authentication](https://docs.databricks.com/aws/en/lakebase/admin/authentication.html), [Databricks Apps resources](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/resources)

### What Was Removed

Prior to this migration, the system had:
- Token input fields in the UI (IntakePage, DBSQLExportPage)
- In-memory token storage (`TokenStorageService`) with 24-hour expiration
- Database-persisted tokens (`databricks_tokens` table)
- A 4-level token fallback chain (SDK → explicit → stored → env var)
- `os.environ["DATABRICKS_TOKEN"]` mutations at runtime

All of this was replaced by the single `resolve_databricks_token()` function.

### Future: Per-User Data Plane Auth

Databricks Apps forwards the logged-in user's OAuth token via the `x-forwarded-access-token` HTTP header. The current implementation uses that delegated token to resolve the user's Databricks Apps permission level. It does not yet use the delegated token for all MLflow, Unity Catalog, or model-serving data plane calls; those still use SDK-resolved service principal or local developer auth.

## Core Concepts

### User
- A workshop participant, SME, or facilitator with a unique identity
- Has associated permissions that control access to features
- Resolved from the configured identity provider and materialized as an app user

### Permission
- Authorization flag controlling access to specific features
- Loaded from the current-session endpoint
- V2 project actions use project capabilities such as `can_manage_project`

### Session
- Backend-resolved state representing the authenticated app user for the current request
- Includes user data, provider role, and permissions
- Loaded through TanStack Query from `GET /api/auth/session`

## Permission Model

### Permission Types

| Permission | Description | Default |
|------------|-------------|---------|
| `can_annotate` | User can submit annotations | `true` |
| `can_view_rubric` | User can view rubric questions | `true` |
| `can_create_rubric` | User can create/edit rubrics | `false` |
| `can_manage_workshop` | User can manage workshop settings | `false` |
| `can_manage_project` | User can manage V2 project setup and global project actions | `false` |
| `can_assign_annotations` | User can assign traces to annotators | `false` |

### Permission Loading

```
Permission Loading Flow:
1. Attempt to load `GET /api/auth/session`
2. On 200: Apply returned user and permissions
3. On 401: Do not render app-owned login; show authentication-required state
4. On other error: Surface session loading error
```

## Authentication Flow

### Initialization (App Load)

```
App Initialization:
1. Set isLoading = true
2. Fetch `GET /api/auth/session`
3. If the response is 200, render based on returned user and permissions
4. If the response is 401, show an authentication-required state instead of a login form
5. Set isLoading = false only after the session query resolves
```

**Critical Requirement**: `isLoading` must remain `true` until ALL initialization steps complete, including permission loading.

### Login Flow

Login is owned by Databricks Apps or the configured trusted provider. The SPA has no app-owned JSON login mutation.

### Logout Flow

Logout is owned by Databricks Apps or the configured trusted provider. The app may clear local workflow context, but it must not maintain a separate browser-restored auth session.

## Error Handling

### Race Condition Prevention

**Problem**: Setting `isLoading = false` before permissions load causes "permission denied" errors.

**Solution**:
- `isLoading` set to `false` ONLY at the end of initialization
- All async operations complete before loading state changes
- Components render only when `isLoading === false`

### Session Errors

When current-session loading fails:

- `401`: no trusted identity was present. The frontend shows an authentication-required state and relies on Databricks Apps/provider login.
- Other errors: the frontend surfaces the session load failure; it must not fabricate a browser session or fall back to app-owned login.

## Data Model

### UserContext State

```typescript
interface UserContextState {
  user: User | null;
  permissions: Permissions | null;
  isLoading: boolean;
  error: string | null;
}
```

### User

```typescript
interface User {
  id: string;
  name: string;
  email?: string;
  role: 'participant' | 'sme' | 'facilitator';
  created_at: string;
}
```

### Permissions

```typescript
interface Permissions {
  can_annotate: boolean;
  can_view_rubric: boolean;
  can_create_rubric: boolean;
  can_manage_workshop: boolean;
  can_manage_project: boolean;
  can_assign_annotations: boolean;
}
```

## Implementation

### File: `client/src/context/UserContext.tsx`

Key implementation points:

1. **Loading State Management**
   - Initialize `isLoading = true`
   - Derive loading state from the `GET /api/auth/session` query
   - Never render role-gated app content before the session query resolves

2. **Permission Loading**
   - Permissions come from the backend session response
   - The frontend does not call a separate login mutation or restore `workshop_user`

3. **Error Handling**
   - Show authentication-required state for missing provider identity
   - Surface unexpected session errors

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/auth/session` | GET | Resolve current provider-authenticated session |
| `/users/me` | GET | Return current materialized app user |
| `/users/{id}/permissions` | GET | Load user permissions |

## Success Criteria

### Workshop Application Auth
- [ ] No app-owned login form exists in the frontend
- [ ] No `/users/auth/login` endpoint exists
- [ ] No facilitator YAML password config exists
- [ ] No user password hash is persisted
- [ ] Browser localStorage does not restore `workshop_user`
- [ ] Current session loads through `GET /api/auth/session`
- [ ] Databricks Apps identity headers authenticate the current session
- [ ] Databricks Apps `CAN_MANAGE` grants `can_manage_project`
- [ ] Databricks Apps `CAN_USE` denies `can_manage_project`
- [ ] Local development defaults to `CAN_MANAGE` and can be configured to `CAN_USE`
- [ ] Slow network: Loading indicator shown until session resolves
- [ ] Rapid navigation: Components wait for `isLoading = false`

### Databricks API Auth
- [ ] All Databricks API calls use SDK-resolved tokens (no user-provided PATs)
- [ ] MLflow operations use SDK auth without `os.environ["DATABRICKS_TOKEN"]` mutation
- [ ] No token input fields exist in the frontend UI
- [ ] No token persistence in memory (`TokenStorageService` for Databricks) or database (`databricks_tokens` table)
- [ ] Local development works via `databricks auth login` CLI profile
- [ ] Databricks Apps deployment works via platform-injected service principal
- [ ] `DATABRICKS_TOKEN` env var works as fallback for CI/containers
- [ ] `resolve_databricks_token()` raises `RuntimeError` with actionable message when no auth available
- [ ] No user-configurable `databricks_host` — app always uses its own workspace
- [ ] `DATABRICKS_HOST` comes from environment (Databricks Apps platform or developer), not stored config
- [ ] `MLFLOW_EXPERIMENT_ID` comes from app.yaml resource declaration
- [ ] `DatabricksService` does not accept `workspace_url` parameter — uses env-based host only
- [ ] MemAlign embedding model is selectable with default to `databricks-gte-large-en`
- [ ] No dead `OPENAI_API_KEY` code paths in alignment service

### Lakebase Connection Pool
- [ ] Token injection uses `do_connect` event listener, not `creator` callable or baked-in URL
- [ ] Tokens generated via `generate_database_credential(endpoint=...)` for Lakebase Autoscaling
- [ ] Token refresh only when creating new physical connections (not on every checkout)
- [ ] `pool_recycle=3600` (not shorter — avoids unnecessary connection churn)
- [ ] `pool_pre_ping=False` (conflicts with `do_connect` token injection)
- [ ] `max_overflow` ≤ 5 (caps total connections at 20 across 2 gunicorn workers)
- [ ] `ENDPOINT_NAME` environment variable required for Lakebase Autoscaling deployments

## Testing Scenarios

### Scenario 1: Databricks Apps Session
- Request includes trusted Databricks Apps identity headers
- Backend materializes or updates user
- Backend resolves provider role using Apps permissions data
- Frontend renders according to returned permissions

### Scenario 2: Slow Network
- Current-session endpoint is delayed
- Loading indicator shown
- No race condition errors
- Access granted when complete

### Scenario 3: Missing Provider Identity
- Session endpoint returns 401
- Frontend does not show app-owned login
- Authentication-required state is displayed

### Scenario 4: Local Development
- No Databricks Apps headers are present
- LocalDev provider returns configured identity
- Default local provider role is `CAN_MANAGE`
- `LOCAL_DEV_PROVIDER_ROLE=CAN_USE` returns non-power-user permissions

### Scenario 5: Rapid Navigation
- User opens app and navigates immediately
- Components wait for loading
- No permission errors

## Backwards Compatibility

- This is a breaking auth migration: app-owned password login is intentionally removed.
- Existing users can be materialized by email through provider identity.
- Existing workshop roles for SME/participant can be preserved after materialization.
- Database migrations remove legacy password-auth persistence.

## Implementation Log

| Date | Plan | Status | Summary |
|------|------|--------|---------|
| 2026-04-10 | [SDK Auth Migration](../.claude/plans/2026-04-10-sdk-auth-migration.md) | complete | Replace PAT token auth with Databricks SDK unified auth |
| 2026-04-11 | (inline) | complete | Fix Lakebase connection pool: switch to `do_connect` + `generate_database_credential()`, fix pool settings to match Databricks docs |
| 2026-04-15 | [Remove databricks_host](../.claude/plans/2026-04-15-remove-databricks-host-app-yaml-resources.md) | in-progress | Remove user-configurable host, use app.yaml resources for MLflow experiment, fix MemAlign embedding model |
| 2026-05-22 | (inline) | complete | Replace app-owned login with provider-resolved Databricks Apps identity and current-session loading |
