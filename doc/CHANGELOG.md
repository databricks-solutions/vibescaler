# Changelog

## v1.10.0 (Upcoming)

### New Features
- **Trace Summarization**: AI-generated trace summaries with a milestone timeline view in the trace viewer
  - Facilitator settings to enable and configure summarization, including model selection
  - Batch summarization on trace ingestion, with re-summarize and cancel controls
  - Facilitator visibility into summarization status and results
  - Per-trace event timelines persisted for summarization jobs
- **Discovery Social Threads**: threaded discussion during the discovery phase, integrated with the trace milestone timeline
  - Streaming agent responses to @-mentions
  - Milestone comments persisted, with scroll synced to the active milestone
  - Facilitator comment moderation controls
- **Eval Mode Workflow**: per-trace evaluation criteria, rubric rendering, scoring aggregation, and mode-gated routing so evaluation and workshop flows can evolve independently
- **Redesigned Project Setup Flow**: server-synced setup form with progress tracking and header-based use case editing
- **Documentation Site**: built-in docs served at `/docs` (Docusaurus) with local search
- **Dynamic Model List**: available models are now fetched from Databricks serving endpoints instead of a hardcoded list, with endpoint caching
- **Cross-Provider LLM Support**: Gemini models routed through AI Gateway for chat and summarization; correct temperature handling for GPT-5 / o-series endpoints

### Improvements
- **Simplified Databricks Authentication**: credentials now resolve automatically via the Databricks SDK and app resources — manual host and token inputs removed from the UI and API
- Database migrations run automatically before workers start during deployment
- Discovery milestone context is propagated to judge evaluations
- Embedding model selection for judge alignment

### Bug Fixes
- Judge evaluation pipeline fixes: re-evaluation now uses the aligned judge, baseline scores are preserved across prompt versions instead of being overwritten, and unparseable judge output is skipped (and counted) rather than silently defaulting
- Judge alignment and annotation-to-MLflow feedback sync reliability fixes
- PostgreSQL (Lakebase) fixes: token expiry caching, stale connection detection, connection pool settings, and dialect-safe migrations
- Trace viewer now renders multi-turn message arrays instead of extracting a single message
- Summarization retries with backoff on rate-limit (429) errors
- Discovery stability fixes: database sessions released between live-update polls, findings navigation improvements

### Breaking Changes
- Removed manual Databricks token storage and host/token fields from the API — authentication is now handled by the Databricks SDK and app resources
- Removed the DBSQL and Unity Catalog export paths

---

## v1.9.0 (March 23, 2026)

### New Features
- **PostgreSQL (Lakebase) Backend**: optional PostgreSQL backend as an alternative to SQLite, with robust bootstrap, credential rotation, connection retry logic, and serverless resilience
- **Facilitator Discovery Workspace**: redesigned two-panel discovery workspace
  - Trace cards with co-located participant findings
  - Cross-trace analysis summary and compact overview bar
  - Draft rubric sidebar with promotion animations and undo
- **Assisted Discovery Facilitation**: AI-assisted structuring of the discovery phase
  - Real-time classification of participant findings into category buckets
  - Facilitator-controlled, AI-generated follow-up questions per trace
  - Automatic detection of disagreements between participants
  - Promotion of findings to a draft rubric staging area
- **Draft-to-Rubric Creation**: create a rubric directly from promoted draft items with one click
- **Memory-Based Judge Alignment**: re-evaluation loads the registered judge with memory learned during alignment; pre- and post-alignment scores are stored against separate prompt versions
- **Participant Notepad**: personal notes available during discovery and annotation phases
- **AI Rubric Generation**: generate rubric drafts with AI assistance, alongside a UI modernization pass across the app
- **Span Attribute Filter**: facilitators can configure which span's inputs/outputs are displayed (by span name, type, or attribute) instead of the root trace input/output
- **Expanded CSV Import**: supports the raw `mlflow.search_traces()` export format

### Improvements
- Dedicated MLflow tag keys for evaluation and alignment traces
- Reduced backend polling intervals; no polling on the login page
- React Error Boundaries prevent full-app crashes
- Workshop descriptions truncate to a single line in the header

### Bug Fixes
- Fixed SME view showing the wrong workshop for users who belong to multiple workshops
- Fixed trace ingestion identity issues
- Binary scale fixes: annotation UI shows Pass/Fail instead of star ratings for binary rubrics, and 0/1 values are logged to MLflow correctly
- Fixed re-evaluation prompt version selection and completion spinner
- Fixed trace output display for malformed JSON

---

## v1.8.0 (February 2, 2026)

### New Features
- **Auto-Evaluation**: LLM judge evaluation runs automatically in the background when the annotation phase begins
  - Judge prompts auto-derived from rubric questions
  - Supports multiple judges, with results displayed in Judge Tuning
  - Re-evaluation after alignment uses the same model
  - Endpoint to restart auto-evaluation
- **Run Evaluation Button**: trigger evaluation for the current judge from the Judge Tuning page
- Expanded model options for judge evaluation

### Improvements
- Better MLflow sync diagnostics and standard judge prompt templates

### Bug Fixes
- Binary scale fixes, including per-question judge type detection
- Added retry logic for SQLite locking when beginning annotation

---

## v1.7.3 (February 2, 2026)

- SQLite backups are now time-based (every 10 minutes) instead of write-count-based
- Removed hardcoded localhost URLs in favor of the dev server proxy

## v1.7.2 (January 29, 2026)

- Support multiple judges for MLflow feedback logging
- Fixed rubric description collapse for bullet-point formats

## v1.7.1 (January 27, 2026)

- **SQLite Rescue**: database persistence across ephemeral Databricks Apps container restarts — restores from a Unity Catalog Volume on startup, backs up on shutdown and periodically, with status surfaced in the detailed health endpoint

## v1.7.0 (January 27, 2026)

### New Features
- **Smart Trace Formatting**: the trace viewer now handles arbitrary JSON schemas with user-friendly formatting for structured inputs and outputs
- **Facilitator Guide**: comprehensive facilitator documentation with screenshots under `doc/`

### Improvements
- Improved rubric description formatting in the annotation phase
- CI now runs E2E tests and builds release assets automatically

### Bug Fixes
- Rubric delete now updates the UI immediately

---

## v1.6.3 (January 26, 2026)

- Fixed annotation and discovery save reliability on SQLite (removed row locking that caused save failures)
- Fixed rubric delete

## v1.6.2 (January 21, 2026)

- **Custom LLM Provider Support**: configure a custom LLM provider for judge evaluation

## v1.6.1 (January 21, 2026)

- Fixed E2E test failures when running with parallel workers

## v1.6.0 (January 21, 2026)

### New Features
- **JSONPath Trace Display Customization**: configure which parts of a trace are displayed in the trace viewer using JSONPath expressions
- **Workshop Access Control**: participants and SMEs can only access workshops they belong to

### Improvements
- Automated spec coverage tracking with framework-specific test markers
- "Join Existing" is disabled on the login page when no workshops exist

### Bug Fixes
- Workshop selection now distinguishes same-named workshops
- Invalid workshop IDs no longer cause an empty workshop list
- Fixed workshop loading and URL parameter handling on the login page

---

## v1.5.0 (January 17, 2026)

This release completes four focus areas: binary judge labeling, discovery-to-rubric streamlining, judge alignment integration, and quality/tech debt.

### New Features
- **Multi-Workshop Support**: run multiple workshops side by side with fully isolated data
- **CSV Upload Improvements**: separate import paths for Discovery and MLflow traces; MLflow configuration is remembered between imports
- **Judge Tuning Enhancements**: per-question persistence, compact toggles, and the ability to reset annotations

### Improvements
- Enhanced automatic retry for discovery findings and annotation saves
- SQLite WAL mode enabled on every connection for better concurrency under load
- Easier test framework and expanded developer documentation

### Bug Fixes
- Fixed the last trace not saving when clicking the Complete button
- Fixed trace randomization and discovery reset issues

---

## v1.3.0 (January 13, 2026)

### New Features
- **Database Migrations with Alembic**: Added Alembic for proper database schema migrations (contributed by Forrest Murray)
  - `0001_baseline.py` - Initial schema baseline
  - `0002_legacy_schema_fixes.py` - Legacy schema compatibility
  - `0003_judge_schema_updates.py` - Judge table schema updates
- **Comprehensive Test Coverage** (contributed by Forrest Murray)
  - Server unit tests for routers (`databricks`, `dbsql_export`, `users`, `workshops`)
  - Server unit tests for services (`alignment`, `cohens_kappa`, `irr`, `krippendorff_alpha`, `token_storage`)
  - Client-side unit tests
  - E2E tests with Playwright (`rubric-creation`, `workshop-flow`)
- **Justfile Commands**: New database management commands (contributed by Forrest Murray)
  - `just db-upgrade` - Run Alembic migrations
  - `just db-stamp` - Stamp current migration
  - `just db-revision` - Create new migration
  - `just db-bootstrap` - Bootstrap database
  - `just e2e` - Run end-to-end tests
- **DB Bootstrap on FastAPI Lifecycle**: Database bootstrap now runs automatically on app startup
- **MLflow GenAI Skills**: Added Claude skills documentation for MLflow GenAI evaluation, tracing, and troubleshooting (`.cursor/skills/`)

### Bug Fixes
- **Binary Judge Fix**: Fixed critical issue where MLflow was returning Likert-style values (e.g., 3.0) instead of binary 0/1 for binary judges
  - Prepended strong binary format instructions to judge prompts (models pay more attention to prompt start)
  - Changed `feedback_value_type` from `bool` to `float` for more reliable 0/1 parsing
  - Added fallback threshold conversion: Likert values >=3 convert to PASS (1), &lt;3 to FAIL (0)
- **Database Indentation Fix**: Fixed IndentationError in `server/database.py` that prevented server startup

### Improvements
- Binary judge prompts now include explicit examples showing valid 0/1 output format
- Better error messages with fallback conversion logging for debugging
- Log messages now accurately reflect the `feedback_value_type` being used

### Contributors
- Forrest Murray - Database migrations, Alembic setup, test coverage
- Wenwen Xie - Binary judge fixes, MLflow GenAI skills

---

## v1.2.0 (January 5, 2026)

### New Features
- **Binary Scale Support**: Full support for Pass/Fail evaluation alongside Likert (1-5) scale
- **Free-form Text Responses**: Qualitative feedback in annotations
- **Binary SIMBA Optimizer**: Judge alignment for binary judges
- **Auto-refresh Annotations**: Judge Tuning now picks up new annotations automatically

### Improvements
- IRR recalculation uses `toast.promise()` for better UX (no duplicate toasts)
- MLflow locked to version 3.7 for compatibility
- Default annotation traces increased from 10 to 15
- Mode badge now correctly shows MLflow vs Simple Model Serving

### Bug Fixes
- Fixed IRR recalculation showing duplicate notifications
- Fixed Judge Tuning not recognizing new annotations after adding more traces

---

## v1.1.0 (December 8, 2025)

### New Features
- **Alignment Service**: New polling-based alignment with file job store
- **Judge Evaluation Persistence**: Results saved to database and reload in UI
- **Auto-derived Judge Name**: Judge name derived from rubric question
- **Automated Release Workflow**: GitHub Actions creates `project-with-build.zip`

### Improvements
- Judge name input moved to Annotation Phase dashboard
- Client build included in repository for easier deployment
- Login routing fixes

### Bug Fixes
- Fixed Judge Tuning save functionality
- Removed redundant proceed button
- Fixed user login routing issues
- Removed unnecessary auth sync

---

## v1.0.0 (December 5, 2025)

### Initial Release
- **Workshop Management**: Create and manage annotation workshops
- **Discovery Phase**: Users explore traces and identify patterns
- **Annotation Phase**: Rate traces based on custom rubrics
- **IRR Analysis**: Calculate inter-rater reliability (Krippendorff's Alpha, Cohen's Kappa)
- **MLflow Integration**: Import traces from MLflow experiments
- **Judge Tuning**: Create and evaluate AI judges
- **Pre-built Client**: Ready-to-deploy frontend

### Features
- Annotation editing with smart change detection
- Multi-line comment support
- Per-user randomized trace ordering
- CSV upload for trace import

---

## Unreleased (After v1.2.0)

### Bug Fixes
- Fixed Mode toggle in Judge Tuning to correctly show MLflow vs Simple
