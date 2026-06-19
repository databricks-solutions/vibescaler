# Spec Test Coverage Map

**Generated**: 2026-06-19 16:23:47

This report shows test coverage for each specification's success criteria.

## :rotating_light: Unknown Spec Tags

**3 test tag(s) reference specs not registered in `KNOWN_SPECS`.**
These tests earn ZERO coverage credit until the spec is registered or the tag is fixed:

| Unknown Spec | Tagged Tests |
|--------------|--------------|
| SQLITE_CONCURRENCY | 3 |

## Test Pyramid Summary

| Type | Count | Description |
|------|-------|-------------|
| Unit | 1118 | pytest unit tests, Vitest tests |
| Integration | 61 | pytest with real DB/API |
| E2E (Mocked) | 23 | Playwright with mocked API |
| E2E (Real) | 67 | Playwright with real API |

## Coverage Summary

| Spec | Reqs | Covered | Cover% | Unit | Int | E2E-M | E2E-R | BE-only |
|------|------|---------|--------|------|-----|-------|-------|---------|
| [ANNOTATION_SPEC](#annotation-spec) | 26 | 19 | 73% | 57 | 0 | 0 | 17 | **6** |
| [AUTHENTICATION_SPEC](#authentication-spec) | 29 | 4 | 13% | 9 | 0 | 3 | 0 | **1** |
| [BUILD_AND_DEPLOY_SPEC](#build-and-deploy-spec) | 19 | 17 | 89% | 87 | 2 | 0 | 0 | **17** |
| [CUSTOM_LLM_PROVIDER_SPEC](#custom-llm-provider-spec) | 11 | 11 | 100% | 17 | 0 | 8 | 0 | **3** |
| [DATASETS_SPEC](#datasets-spec) | 5 | 5 | 100% | 31 | 0 | 0 | 2 | **4** |
| [DESIGN_SYSTEM_SPEC](#design-system-spec) | 7 | 2 | 28% | 40 | 0 | 2 | 0 | 0 |
| [DISCOVERY_SPEC](#discovery-spec) | 79 | 77 | 97% | 318 | 4 | 7 | 22 | **39** |
| [JUDGE_EVALUATION_SPEC](#judge-evaluation-spec) | 31 | 29 | 93% | 112 | 7 | 0 | 11 | **20** |
| [ROLE_PERMISSIONS_SPEC](#role-permissions-spec) | 16 | 16 | 100% | 30 | 0 | 0 | 0 | **15** |
| [RUBRIC_SPEC](#rubric-spec) | 26 | 26 | 100% | 98 | 0 | 2 | 6 | **18** |
| [TESTING_SPEC](#testing-spec) | 25 | 16 | 64% | 65 | 48 | 0 | 0 | **16** |
| [TRACE_DISPLAY_SPEC](#trace-display-spec) | 19 | 19 | 100% | 96 | 0 | 0 | 7 | **9** |
| [TRACE_INGESTION_SPEC](#trace-ingestion-spec) | 17 | 9 | 52% | 16 | 0 | 0 | 0 | **9** |
| [TRACE_SUMMARIZATION_SPEC](#trace-summarization-spec) | 64 | 23 | 35% | 58 | 0 | 0 | 0 | **23** |
| [UI_COMPONENTS_SPEC](#ui-components-spec) | 16 | 2 | 12% | 57 | 0 | 0 | 2 | 0 |
| [EVAL_MODE_SPEC](#eval-mode-spec) | 19 | 18 | 94% | 27 | 0 | 1 | 0 | **17** |

**Total**: 293/409 requirements covered (71%)

---

## ANNOTATION_SPEC

**Coverage**: 19/26 requirements (73%)

### Uncovered Requirements

- [ ] Save success is silent; toasts appear only for save failures, retries, and bulk-recovery outcomes
- [ ] Comments display with proper line breaks
- [ ] Duplicate feedback entries are detected and skipped
- [ ] Bulk resync re-exports all annotations when rubric titles change
- [ ] Navigation is optimistic (UI advances immediately, save completes in background)
- [ ] Freeform question responses are optional (not required for navigation)
- [ ] Freeform responses are encoded in the comment field as JSON

### Backend-Only Requirements (no frontend tests)

These requirements are covered by backend tests only. UI regressions won't be caught:

- :warning: MLflow trace tagged with `label: "align"` and `workshop_id` on annotation (unit)
- :warning: Annotation comment maps to MLflow feedback rationale (unit)
- :warning: Participants can create, retrieve, and delete notes during discovery and annotation phases (unit)
- :warning: Participant notes always append as new entries; existing notes are never overwritten (unit)
- :warning: Facilitators can toggle participant notes visibility per workshop (unit)
- :warning: Legacy single-rating format loads correctly alongside multi-rating format (unit)

### Covered Requirements

- [x] Users can edit previously submitted annotations (e2e-real, unit)
- [x] Changes automatically save on navigation (Next/Previous) (e2e-real)
- [x] Annotated traces show a persistent Saved indicator instead of a success toast (e2e-real)
- [x] Multi-line comments preserved throughout the stack (e2e-real)
- [x] Next button enabled for annotated traces (allows re-navigation) (e2e-real)
- [x] Annotation count reflects unique submissions (not re-submissions) (e2e-real, unit)
- [x] Annotation upsert persists every trace submission, including the final trace in a session (e2e-real, unit)
- [x] Completing the final trace shows a terminal completion state (e2e-real, unit)
- [x] Annotations sync to MLflow as feedback on save (one entry per rubric question) (e2e-real, unit)
- [x] MLflow trace tagged with `label: "align"` and `workshop_id` on annotation (unit) **[BE-only]**
- [x] Feedback source is HUMAN with annotator's user_id (e2e-real, unit)
- [x] Annotation comment maps to MLflow feedback rationale (unit) **[BE-only]**
- [x] Failed saves are queued and retried automatically with exponential backoff (unit)
- [x] Navigation debounced at 300ms to prevent duplicate saves (unit)
- [x] Facilitator annotation stats poll every 15 seconds while the tab is in the foreground (unit)
- [x] Participants can create, retrieve, and delete notes during discovery and annotation phases (unit) **[BE-only]**
- [x] Participant notes always append as new entries; existing notes are never overwritten (unit) **[BE-only]**
- [x] Facilitators can toggle participant notes visibility per workshop (unit) **[BE-only]**
- [x] Legacy single-rating format loads correctly alongside multi-rating format (unit) **[BE-only]**

### Tests Without Requirement Links

These tests are tagged with the spec but don't link to specific requirements:

- `tests/unit/routers/test_annotation_crud.py` (test_upsert_creates_new_annotation) [unit]
- `tests/unit/services/test_annotation_mlflow_sync.py` (test_same_value_resync_skipped) [unit]
- `tests/unit/services/test_annotation_mlflow_sync.py` (test_different_value_edit_overwrites) [unit]
- `tests/unit/services/test_annotation_mlflow_sync.py` (test_update_failure_does_not_log_duplicate) [unit]
- `tests/unit/services/test_annotation_mlflow_sync.py` (test_missing_assessment_id_does_not_log_duplicate) [unit]
- `tests/unit/services/test_database_service_participant_notes.py` (test_add_participant_note_discovery) [unit]
- `tests/unit/services/test_database_service_participant_notes.py` (test_add_participant_note_annotation) [unit]
- `tests/unit/services/test_database_service_participant_notes.py` (test_add_participant_note_without_trace) [unit]
- `tests/unit/services/test_database_service_participant_notes.py` (test_add_participant_note_always_creates_new) [unit]
- `tests/unit/services/test_database_service_participant_notes.py` (test_get_participant_notes_no_filters) [unit]
- `tests/unit/services/test_database_service_participant_notes.py` (test_get_participant_notes_filtered_by_user) [unit]
- `tests/unit/services/test_database_service_participant_notes.py` (test_get_participant_notes_filtered_by_phase) [unit]
- `tests/unit/services/test_database_service_participant_notes.py` (test_get_participant_notes_filtered_by_user_and_phase) [unit]
- `tests/unit/services/test_database_service_participant_notes.py` (test_get_participant_notes_empty_result) [unit]
- `tests/unit/services/test_database_service_participant_notes.py` (test_delete_participant_note_success) [unit]
- `tests/unit/services/test_database_service_participant_notes.py` (test_delete_participant_note_not_found) [unit]

## AUTHENTICATION_SPEC

**Coverage**: 4/29 requirements (13%)

### Uncovered Requirements

- [ ] No "permission denied" errors on normal login
- [ ] No page refresh required after login
- [ ] Permission API failure: User can log in with defaults
- [ ] 404 on validation: Session cleared, fresh login allowed
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
- [ ] Token injection uses `do_connect` event listener, not `creator` callable or baked-in URL
- [ ] Tokens generated via `generate_database_credential(endpoint=...)` for Lakebase Autoscaling
- [ ] Token refresh only when creating new physical connections (not on every checkout)
- [ ] `pool_recycle=3600` (not shorter — avoids unnecessary connection churn)
- [ ] `pool_pre_ping=False` (conflicts with `do_connect` token injection)
- [ ] `max_overflow` ≤ 5 (caps total connections at 20 across 2 gunicorn workers)
- [ ] `ENDPOINT_NAME` environment variable required for Lakebase Autoscaling deployments

### Backend-Only Requirements (no frontend tests)

These requirements are covered by backend tests only. UI regressions won't be caught:

- :warning: Invalid login credentials are rejected with HTTP 401 and an explanatory error message (unit)

### Covered Requirements

- [x] Slow network: Loading indicator shown until ready (e2e-mocked)
- [x] Rapid navigation: Components wait for `isLoading = false` (unit)
- [x] Error recovery: Errors cleared on new login attempt (e2e-mocked)
- [x] Invalid login credentials are rejected with HTTP 401 and an explanatory error message (unit) **[BE-only]**

### Tests Without Requirement Links

These tests are tagged with the spec but don't link to specific requirements:

- `tests/unit/routers/test_auth_edge_cases.py` (test_permission_api_failure_returns_defaults_when_user_not_found) [unit]
- `tests/unit/routers/test_auth_edge_cases.py` (test_permission_api_returns_role_based_defaults_for_valid_user) [unit]
- `tests/unit/routers/test_auth_edge_cases.py` (test_permission_api_failure_when_db_service_raises) [unit]
- `tests/unit/test_db_config.py` (test_get_password_rejects_unset_or_empty_endpoint[None]) [unit]
- `tests/unit/test_db_config.py` (test_get_password_rejects_unset_or_empty_endpoint[]) [unit]
- `tests/unit/test_db_config.py` (test_postgresql_engine_raises_without_endpoint_name) [unit]
- `client/tests/e2e/facilitator-create-workshop.spec.ts` (facilitator can log in and create a workshop) [e2e-mocked]

## BUILD_AND_DEPLOY_SPEC

**Coverage**: 17/19 requirements (89%)

### Uncovered Requirements

- [ ] Production build completes without errors
- [ ] Full deployment completes successfully

### Backend-Only Requirements (no frontend tests)

These requirements are covered by backend tests only. UI regressions won't be caught:

- :warning: Assets minified and hashed (unit)
- :warning: Build directory contains all required files (unit)
- :warning: `just db-bootstrap` creates database if missing (unit)
- :warning: Migrations apply without errors (unit)
- :warning: Batch mode works for SQLite ALTER TABLE (unit)
- :warning: File lock prevents race conditions with multiple workers (unit)
- :warning: Pending Alembic migrations are applied automatically before workers accept traffic (unit)
- :warning: Lakebase schema privilege grants are best-effort (unit)
- :warning: App serves setup docs and gates the UI until Lakebase is configured (postgres targets only; sqlite deployments are fully operable without setup) (unit)
- :warning: Server starts and serves frontend (unit)
- :warning: API endpoints respond correctly (integration, unit)
- :warning: Database connection established (integration)
- :warning: Lakebase (Postgres) persistence: with `DATABASE_ENV=postgres`, bootstrap provisions the app schema and reuses existing data across restarts (unit)
- :warning: Release workflow creates zip artifact (unit)
- :warning: Pre-built client included in release (unit)
- :warning: No sensitive files in artifact (unit)
- :warning: Lockfiles resolve against public registries (no internal proxy URLs) (unit)

### Covered Requirements

- [x] Assets minified and hashed (unit) **[BE-only]**
- [x] Build directory contains all required files (unit) **[BE-only]**
- [x] `just db-bootstrap` creates database if missing (unit) **[BE-only]**
- [x] Migrations apply without errors (unit) **[BE-only]**
- [x] Batch mode works for SQLite ALTER TABLE (unit) **[BE-only]**
- [x] File lock prevents race conditions with multiple workers (unit) **[BE-only]**
- [x] Pending Alembic migrations are applied automatically before workers accept traffic (unit) **[BE-only]**
- [x] Lakebase schema privilege grants are best-effort (unit) **[BE-only]**
- [x] App serves setup docs and gates the UI until Lakebase is configured (postgres targets only; sqlite deployments are fully operable without setup) (unit) **[BE-only]**
- [x] Server starts and serves frontend (unit) **[BE-only]**
- [x] API endpoints respond correctly (integration, unit) **[BE-only]**
- [x] Database connection established (integration) **[BE-only]**
- [x] Lakebase (Postgres) persistence: with `DATABASE_ENV=postgres`, bootstrap provisions the app schema and reuses existing data across restarts (unit) **[BE-only]**
- [x] Release workflow creates zip artifact (unit) **[BE-only]**
- [x] Pre-built client included in release (unit) **[BE-only]**
- [x] No sensitive files in artifact (unit) **[BE-only]**
- [x] Lockfiles resolve against public registries (no internal proxy URLs) (unit) **[BE-only]**

### Roadmap (not shipping)

These criteria are roadmap-only and excluded from the coverage denominator:

- Console statements removed in production (roadmap)

### Tests Without Requirement Links

These tests are tagged with the spec but don't link to specific requirements:

- `tests/unit/test_build_deploy.py` (test_database_url_has_default) [unit]
- `tests/unit/test_build_deploy.py` (test_detect_backend_defaults_to_sqlite) [unit]
- `tests/unit/test_sqlite_rescue.py` (test_default_database_url) [unit]
- `tests/unit/test_sqlite_rescue.py` (test_sqlite_triple_slash_url) [unit]
- `tests/unit/test_sqlite_rescue.py` (test_sqlite_double_slash_url) [unit]
- `tests/unit/test_sqlite_rescue.py` (test_non_sqlite_url_returns_none) [unit]
- `tests/unit/test_sqlite_rescue.py` (test_volume_backup_path_direct) [unit]
- `tests/unit/test_sqlite_rescue.py` (test_volume_path_appends_workshop_db) [unit]
- `tests/unit/test_sqlite_rescue.py` (test_volume_path_with_trailing_slash) [unit]
- `tests/unit/test_sqlite_rescue.py` (test_backup_path_takes_precedence) [unit]
- `tests/unit/test_sqlite_rescue.py` (test_custom_backup_interval) [unit]
- `tests/unit/test_sqlite_rescue.py` (test_backup_interval_zero_disables) [unit]
- `tests/unit/test_sqlite_rescue.py` (test_valid_volume_path) [unit]
- `tests/unit/test_sqlite_rescue.py` (test_valid_nested_path) [unit]
- `tests/unit/test_sqlite_rescue.py` (test_empty_path_is_invalid) [unit]
- `tests/unit/test_sqlite_rescue.py` (test_none_path_is_invalid) [unit]
- `tests/unit/test_sqlite_rescue.py` (test_non_volumes_prefix_is_invalid) [unit]
- `tests/unit/test_sqlite_rescue.py` (test_incomplete_volume_path_is_invalid) [unit]
- `tests/unit/test_sqlite_rescue.py` (test_just_volumes_root_is_invalid) [unit]
- `tests/unit/test_sqlite_rescue.py` (test_case_sensitive_volumes_prefix) [unit]
- `tests/unit/test_sqlite_rescue.py` (test_extracts_volume_root) [unit]
- `tests/unit/test_sqlite_rescue.py` (test_extracts_root_from_nested_path) [unit]
- `tests/unit/test_sqlite_rescue.py` (test_returns_none_for_short_path) [unit]
- `tests/unit/test_sqlite_rescue.py` (test_returns_none_for_empty_path) [unit]
- `tests/unit/test_sqlite_rescue.py` (test_exact_volume_path_returns_self) [unit]

## CUSTOM_LLM_PROVIDER_SPEC

**Coverage**: 11/11 requirements (100%)

### Backend-Only Requirements (no frontend tests)

These requirements are covered by backend tests only. UI regressions won't be caught:

- :warning: Configuration persists across page refreshes (except API key which requires re-entry after 24h) (unit)
- :warning: Clear error messages for common failures (auth, timeout, invalid URL) (unit)
- :warning: When the Discovery follow-up model is set to custom, follow-up questions are generated through the configured endpoint via build_custom_llm (unit)

### Covered Requirements

- [x] Users can configure custom LLM provider via UI (e2e-mocked)
- [x] Base URL, API key, and model name are captured (e2e-mocked)
- [x] API key is stored securely in memory (not database) (e2e-mocked, unit)
- [x] Configuration persists across page refreshes (except API key which requires re-entry after 24h) (unit) **[BE-only]**
- [x] Configuration can be updated without losing other workshop data (e2e-mocked)
- [x] Configuration can be deleted, removing both the stored config and the in-memory API key (e2e-mocked, unit)
- [x] Test Connection button verifies endpoint is reachable (e2e-mocked, unit)
- [x] Clear error messages for common failures (auth, timeout, invalid URL) (unit) **[BE-only]**
- [x] Response time is displayed on success (e2e-mocked)
- [x] Custom provider option appears in the Discovery model selector when configured and enabled (unit)
- [x] When the Discovery follow-up model is set to custom, follow-up questions are generated through the configured endpoint via build_custom_llm (unit) **[BE-only]**

### Roadmap (not shipping)

These criteria are roadmap-only and excluded from the coverage denominator:

- When custom provider is enabled, judge evaluation uses the custom endpoint (roadmap)
- proxy_url parameter is correctly passed to MLflow (roadmap)
- Evaluation results are identical in format to Databricks FMAPI results (roadmap)
- Errors from custom provider are properly surfaced to UI (roadmap)
- Custom provider option appears in the judge model selector when configured (roadmap)
- Easy to switch between Databricks and custom provider for judge evaluation (roadmap)

## DATASETS_SPEC

**Coverage**: 5/5 requirements (100%)

### Backend-Only Requirements (no frontend tests)

These requirements are covered by backend tests only. UI regressions won't be caught:

- :warning: Same user sees same order for same dataset (deterministic) (unit)
- :warning: Adding traces preserves existing order (incremental) (unit)
- :warning: New round triggers fresh randomization (unit)
- :warning: Facilitators see chronological order (no randomization) (unit)

### Covered Requirements

- [x] Same user sees same order for same dataset (deterministic) (unit) **[BE-only]**
- [x] Different users see different orders (per-user randomization) (e2e-real, unit)
- [x] Adding traces preserves existing order (incremental) (unit) **[BE-only]**
- [x] New round triggers fresh randomization (unit) **[BE-only]**
- [x] Facilitators see chronological order (no randomization) (unit) **[BE-only]**

### Roadmap (not shipping)

These criteria are roadmap-only and excluded from the coverage denominator:

- Datasets can be created with arbitrary trace lists (roadmap)
- Union operation combines traces from multiple datasets (roadmap)
- Subtract operation removes specified traces (roadmap)
- Dataset lineage tracked (source datasets, operations) (roadmap)

### Tests Without Requirement Links

These tests are tagged with the spec but don't link to specific requirements:

- `tests/unit/services/test_dataset_operations.py` (test_union_two_disjoint_datasets) [unit]
- `tests/unit/services/test_dataset_operations.py` (test_union_overlapping_datasets_deduplicates) [unit]
- `tests/unit/services/test_dataset_operations.py` (test_union_preserves_first_occurrence_order) [unit]
- `tests/unit/services/test_dataset_operations.py` (test_union_three_datasets) [unit]
- `tests/unit/services/test_dataset_operations.py` (test_union_with_empty_dataset) [unit]
- `tests/unit/services/test_dataset_operations.py` (test_union_identical_datasets) [unit]
- `tests/unit/services/test_dataset_operations.py` (test_union_result_has_no_duplicates) [unit]
- `tests/unit/services/test_dataset_operations.py` (test_subtract_removes_specified_traces) [unit]
- `tests/unit/services/test_dataset_operations.py` (test_subtract_preserves_order_of_remaining) [unit]
- `tests/unit/services/test_dataset_operations.py` (test_subtract_empty_removal_set) [unit]
- `tests/unit/services/test_dataset_operations.py` (test_subtract_all_traces) [unit]
- `tests/unit/services/test_dataset_operations.py` (test_subtract_nonexistent_traces_ignored) [unit]
- `tests/unit/services/test_dataset_operations.py` (test_subtract_single_trace) [unit]
- `tests/unit/services/test_dataset_operations.py` (test_subtract_result_has_correct_length) [unit]
- `client/tests/e2e/dataset-operations.spec.ts` (facilitator creates dataset, traces appear) [e2e-real]
- `client/src/utils/traceUtils.test.ts` (converts basic API trace fields) [unit]
- `client/src/utils/traceUtils.test.ts` (normalizes null optional fields to undefined) [unit]
- `client/src/utils/traceUtils.test.ts` (normalizes empty string optional fields to undefined) [unit]
- `client/src/utils/traceUtils.test.ts` (normalizes zero/falsy optional fields to undefined) [unit]
- `client/src/utils/traceUtils.test.ts` (preserves valid MLflow metadata) [unit]
- `client/src/utils/traceUtils.test.ts` (preserves complex JSON input/output) [unit]
- `client/src/utils/traceUtils.test.ts` (handles trace with only required fields) [unit]
- `client/src/utils/traceUtils.test.ts` (handles trace with complex context object) [unit]

## DESIGN_SYSTEM_SPEC

**Coverage**: 2/7 requirements (28%)

### Uncovered Requirements

- [ ] Primary purple consistent across all components
- [ ] All text meets WCAG AA contrast
- [ ] Focus indicators visible
- [ ] Badges use secondary color scheme
- [ ] Buttons use appropriate variants

### Covered Requirements

- [x] `cn()` utility merges class names and resolves Tailwind conflicts (later value wins) (unit)
- [x] No hardcoded colors in components (unit)

### Roadmap (not shipping)

These criteria are roadmap-only and excluded from the coverage denominator:

- Dark mode fully functional (roadmap)

### Tests Without Requirement Links

These tests are tagged with the spec but don't link to specific requirements:

- `client/tests/e2e/design-system.spec.ts` (adding .dark class to html element switches CSS variables (no product toggle ships)) [e2e-mocked]
- `client/tests/e2e/design-system.spec.ts` (focus indicators visible when tabbing through interactive elements) [e2e-mocked]

## DISCOVERY_SPEC

**Coverage**: 77/79 requirements (97%)

### Uncovered Requirements

- [ ] Promote action visibly moves items from trace feed/summary into the sidebar
- [ ] Draft rubric items link to their origin (inline origin link; click routes to the originating trace/finding)

### Backend-Only Requirements (no frontend tests)

These requirements are covered by backend tests only. UI regressions won't be caught:

- :warning: Facilitator can start Discovery phase with configurable trace limit (unit)
- :warning: Participants view traces and provide GOOD/BAD + comment (unit)
- :warning: AI generates 3 follow-up questions per trace based on feedback (unit)
- :warning: Questions build progressively on prior answers (unit)
- :warning: All 3 questions required before moving to next trace (unit)
- :warning: Error handling with retry for LLM failures (unit)
- :warning: Completion status shows % of participants finished (integration, unit)
- :warning: System aggregates feedback by trace (unit)
- :warning: Disagreements detected at 3 priority levels (deterministic, no LLM) (unit)
- :warning: LLM distills evaluation criteria with evidence from trace IDs (unit)
- :warning: LLM analyzes disagreements with follow-up questions and suggestions (unit)
- :warning: Analysis record stores which template was used (unit)
- :warning: Each analysis run creates a new record (history preserved) (unit)
- :warning: Re-runnable — new analysis as more feedback comes in, prior analyses retained (unit)
- :warning: Results organized by priority (HIGH → MEDIUM → LOWER) (unit)
- :warning: Facilitator can switch Discovery workspace between `analysis` mode and `social` mode (unit)
- :warning: In social mode, users can create trace-level comments (unit)
- :warning: In social mode, users can create milestone-level comments (unit)
- :warning: Users can reply to comments in-thread (unit)
- :warning: Users can upvote/downvote comments (single vote per user per comment with toggle behavior) (unit)
- :warning: Thread updates appear live in the workspace while participants collaborate (unit)
- :warning: Facilitator can moderate social discussion threads by deleting comments (unit)
- :warning: Only facilitator can delete social thread comments (unit)
- :warning: Non-facilitator mentions do not trigger assistant/agent execution (treated as plain text mentions) (unit)
- :warning: Facilitator `@assistant` mentions post an automated assistant reply in-thread (deterministic template stub) (unit)
- :warning: Facilitator can invoke `@agent` to run a bounded tool loop and receive a persisted agent reply in-thread with clear success/failure status (unit)
- :warning: `@agent` run lifecycle is visible (`running`, `completed`, `failed`, `timeout`) with final persisted reply (unit)
- :warning: One feedback record per (workshop, trace, user) — upsert behavior (integration, unit)
- :warning: Q&A pairs appended in order to JSON array (integration, unit)
- :warning: Multiple analysis records per workshop allowed (history preserved) (unit)
- :warning: Draft rubric items track promotion source and promoter (unit)
- :warning: Annotators see the same trace set in different per-user orders, enabling inter-rater reliability measurement (unit)
- :warning: Adding annotation traces mid-round appends them without reshuffling a user's existing order (unit)
- :warning: Changing the annotation trace set produces a fresh randomized order (unit)
- :warning: DSPy MLflow autologging activates only when MLFLOW_DSPY_DEV_EXPERIMENT_ID is set (unit)
- :warning: Fallback question if LLM unavailable after retries (unit)
- :warning: Form validation prevents empty submissions (unit)
- :warning: When follow-up questions are disabled, participant flow is GOOD/BAD + comment only (unit)
- :warning: "Create Rubric →" in sidebar transitions to rubric creation with groups pre-populated as criteria (unit)

### Covered Requirements

- [x] Facilitator can start Discovery phase with configurable trace limit (unit) **[BE-only]**
- [x] Participants view traces and provide GOOD/BAD + comment (unit) **[BE-only]**
- [x] Facilitator can select LLM model for follow-up question generation in Discovery dashboard (e2e-mocked, unit)
- [x] AI generates 3 follow-up questions per trace based on feedback (unit) **[BE-only]**
- [x] Questions build progressively on prior answers (unit) **[BE-only]**
- [x] All 3 questions required before moving to next trace (unit) **[BE-only]**
- [x] Previous Q&A visible while answering new questions (unit)
- [x] Loading spinner during LLM generation (1-3s) (unit)
- [x] Error handling with retry for LLM failures (unit) **[BE-only]**
- [x] Feedback saved incrementally (no data loss on failure) (e2e-real, unit)
- [x] Completion status shows % of participants finished (integration, unit) **[BE-only]**
- [x] Facilitator can view participant feedback details (label, comment, follow-up Q&A) (e2e-real, integration, unit)
- [x] Facilitator can trigger analysis at any time (even partial feedback) (e2e-mocked, unit)
- [x] Facilitator selects analysis template (Evaluation Criteria or Themes & Patterns) before running (e2e-mocked, unit)
- [x] System aggregates feedback by trace (unit) **[BE-only]**
- [x] Disagreements detected at 3 priority levels (deterministic, no LLM) (unit) **[BE-only]**
- [x] LLM distills evaluation criteria with evidence from trace IDs (unit) **[BE-only]**
- [x] LLM analyzes disagreements with follow-up questions and suggestions (unit) **[BE-only]**
- [x] Analysis record stores which template was used (unit) **[BE-only]**
- [x] Each analysis run creates a new record (history preserved) (unit) **[BE-only]**
- [x] Re-runnable — new analysis as more feedback comes in, prior analyses retained (unit) **[BE-only]**
- [x] Warning if < 2 participants (not an error) (e2e-mocked, unit)
- [x] Data freshness banner (participant count, last run timestamp) (unit)
- [x] Results organized by priority (HIGH → MEDIUM → LOWER) (unit) **[BE-only]**
- [x] Facilitator can promote distilled criteria to draft rubric (e2e-real, unit)
- [x] Facilitator can promote disagreement insights to draft rubric (e2e-real, unit)
- [x] Facilitator can promote raw participant feedback to draft rubric (e2e-real, unit)
- [x] Facilitator can manually add draft rubric items (e2e-real, unit)
- [x] Draft rubric items editable and removable (e2e-real, unit)
- [x] "Suggest Groups" returns LLM proposal without persisting (e2e-real, unit)
- [x] Facilitator can review, adjust, and apply group proposal (e2e-real, unit)
- [x] Manual grouping: create groups, name them, move items between groups (e2e-real, unit)
- [x] Each group maps to one rubric question (group name = question title) (e2e-real, unit)
- [x] Draft rubric items available during Rubric Creation phase (e2e-real, unit)
- [x] Source traceability maintained (which traces support each item) (e2e-real, unit)
- [x] Facilitator can switch Discovery workspace between `analysis` mode and `social` mode (unit) **[BE-only]**
- [x] In social mode, users can create trace-level comments (unit) **[BE-only]**
- [x] In social mode, users can create milestone-level comments (unit) **[BE-only]**
- [x] Users can reply to comments in-thread (unit) **[BE-only]**
- [x] Users can upvote/downvote comments (single vote per user per comment with toggle behavior) (unit) **[BE-only]**
- [x] Thread updates appear live in the workspace while participants collaborate (unit) **[BE-only]**
- [x] Facilitator can moderate social discussion threads by deleting comments (unit) **[BE-only]**
- [x] Only facilitator can delete social thread comments (unit) **[BE-only]**
- [x] Non-facilitator mentions do not trigger assistant/agent execution (treated as plain text mentions) (unit) **[BE-only]**
- [x] Facilitator `@assistant` mentions post an automated assistant reply in-thread (deterministic template stub) (unit) **[BE-only]**
- [x] Facilitator can invoke `@agent` to run a bounded tool loop and receive a persisted agent reply in-thread with clear success/failure status (unit) **[BE-only]**
- [x] `@agent` run lifecycle is visible (`running`, `completed`, `failed`, `timeout`) with final persisted reply (unit) **[BE-only]**
- [x] One feedback record per (workshop, trace, user) — upsert behavior (integration, unit) **[BE-only]**
- [x] Q&A pairs appended in order to JSON array (integration, unit) **[BE-only]**
- [x] Multiple analysis records per workshop allowed (history preserved) (unit) **[BE-only]**
- [x] Draft rubric items track promotion source and promoter (unit) **[BE-only]**
- [x] Participants only see traces in the current active discovery trace list (e2e-real)
- [x] Traces outside the active discovery selection are hidden from participants but not deleted (e2e-real)
- [x] Annotation trace order is deterministic per user and persists across page reloads (e2e-real, unit)
- [x] Annotators see the same trace set in different per-user orders, enabling inter-rater reliability measurement (unit) **[BE-only]**
- [x] Adding annotation traces mid-round appends them without reshuffling a user's existing order (unit) **[BE-only]**
- [x] Changing the annotation trace set produces a fresh randomized order (unit) **[BE-only]**
- [x] DSPy MLflow autologging activates only when MLFLOW_DSPY_DEV_EXPERIMENT_ID is set (unit) **[BE-only]**
- [x] LLM failures show error toast with retry (unit)
- [x] Fallback question if LLM unavailable after retries (unit) **[BE-only]**
- [x] Fallback warning banner shown only to facilitators, never to participants/SMEs (unit)
- [x] Analysis shows warning (not error) if < 2 participants (unit)
- [x] Form validation prevents empty submissions (unit) **[BE-only]**
- [x] Progressive disclosure (one question at a time) (e2e-real, unit)
- [x] Submit buttons disabled until required fields filled (unit)
- [x] Clear progress indication (X of Y traces completed) (e2e-real)
- [x] Smooth transitions between feedback states (unit)
- [x] When follow-up questions are disabled, participant flow is GOOD/BAD + comment only (unit) **[BE-only]**
- [x] Single two-panel workspace replaces multi-page flow (no FacilitatorDashboard discovery tabs, no FindingsReviewPage) (unit)
- [x] Trace feed shows actual trace content (input/output), not trace ID badges (unit)
- [x] Trace-specific analysis findings appear on the trace card, pinned above feedback (collapsible) (unit)
- [x] Cross-trace analysis findings appear in collapsible summary section above the feed (unit)
- [x] Overview bar shows stats inline + compact controls (Run Analysis, Add Traces, Pause, Model selector) (unit)
- [x] Draft rubric sidebar is always visible while browsing traces (e2e-mocked)
- [x] Draft rubric items do NOT show source-type badges (Finding, Disagreement, etc.) (unit)
- [x] Disagreements color-coded by priority (red/yellow/blue) on trace cards (unit)
- [x] "Create Rubric →" in sidebar transitions to rubric creation with groups pre-populated as criteria (unit) **[BE-only]**

### Roadmap (not shipping)

These criteria are roadmap-only and excluded from the coverage denominator:

- Facilitator `@assistant summarize this thread` returns a grounded summary as a thread reply (roadmap)
- Facilitator `@assistant` tool-availability questions for a milestone return grounded context as a thread reply (roadmap)
- Facilitator `@agent` starts a bounded tool-calling run and posts streamed partial output in the thread (roadmap)
- Social mode provides a modern live collaboration experience with streamed in-thread updates for assistant/agent responses (roadmap)

### Tests Without Requirement Links

These tests are tagged with the spec but don't link to specific requirements:

- `tests/unit/services/test_discovery_analysis_service.py` (test_draft_items_expose_source_trace_ids_for_display) [unit]
- `tests/unit/services/test_discovery_workspace_ui_contracts.py` (test_findings_have_evidence_trace_ids_for_card_pinning) [unit]
- `tests/unit/services/test_discovery_workspace_ui_contracts.py` (test_finding_model_validates_evidence_trace_ids) [unit]
- `tests/unit/services/test_draft_rubric_items.py` (test_ungrouped_items_each_become_question) [unit]
- `tests/unit/services/test_draft_rubric_items.py` (test_no_items_raises_400) [unit]
- `tests/unit/services/test_draft_rubric_items.py` (test_mixed_grouped_and_ungrouped) [unit]
- `client/src/components/DiscoveryAnalysisTab.test.tsx` (renders template selector with Evaluation Criteria as the default selected value) [unit]
- `client/src/components/DiscoveryAnalysisTab.test.tsx` (renders a model selector alongside the template selector) [unit]
- `client/src/components/DiscoveryAnalysisTab.test.tsx` (renders the Run Analysis button) [unit]
- `client/src/components/DiscoveryAnalysisTab.test.tsx` (shows warning alert when participant_count is 1) [unit]
- `client/src/components/DiscoveryAnalysisTab.test.tsx` (shows warning alert when participant_count is 0) [unit]
- `client/src/components/DiscoveryAnalysisTab.test.tsx` (does NOT show warning when participant_count >= 2) [unit]
- `client/src/components/DiscoveryAnalysisTab.test.tsx` (warning is an Alert (not destructive variant), confirming it is a warning not an error) [unit]
- `client/src/components/DiscoveryAnalysisTab.test.tsx` (displays participant count in the freshness banner) [unit]
- `client/src/components/DiscoveryAnalysisTab.test.tsx` (displays singular participant text when count is 1) [unit]
- `client/src/components/DiscoveryAnalysisTab.test.tsx` (displays the analysis timestamp) [unit]
- `client/src/components/DiscoveryAnalysisTab.test.tsx` (displays the template name in the freshness banner) [unit]
- `client/src/components/DiscoveryAnalysisTab.test.tsx` (displays the model used in the freshness banner) [unit]
- `client/src/components/DiscoveryAnalysisTab.test.tsx` (renders disagreement sections in order: HIGH, MEDIUM, LOWER) [unit]
- `client/src/components/DiscoveryAnalysisTab.test.tsx` (renders findings with priority badges) [unit]
- `client/src/components/DiscoveryAnalysisTab.test.tsx` (HIGH disagreement section uses red color classes) [unit]
- `client/src/components/DiscoveryAnalysisTab.test.tsx` (MEDIUM disagreement section uses yellow color classes) [unit]
- `client/src/components/DiscoveryAnalysisTab.test.tsx` (LOWER disagreement section uses blue color classes) [unit]
- `client/src/components/DiscoveryAnalysisTab.test.tsx` (HIGH items use red background) [unit]
- `client/src/components/DiscoveryAnalysisTab.test.tsx` (MEDIUM items use yellow background) [unit]
- `client/src/components/DiscoveryAnalysisTab.test.tsx` (LOWER items use blue background) [unit]
- `client/src/components/DiscoveryAnalysisTab.test.tsx` (renders evidence trace IDs for findings) [unit]
- `client/src/components/DiscoveryAnalysisTab.test.tsx` (shows trace ID for each disagreement item) [unit]
- `client/src/components/DiscoveryAnalysisTab.test.tsx` (shows the findings count in the header) [unit]
- `client/src/components/DiscoveryAnalysisTab.test.tsx` (shows disagreement counts by priority level) [unit]
- `client/src/components/DiscoveryAnalysisTab.test.tsx` (renders disagreement summary and underlying theme) [unit]
- `client/src/components/DiscoveryAnalysisTab.test.tsx` (renders follow-up questions for disagreements) [unit]
- `client/src/components/DiscoveryAnalysisTab.test.tsx` (renders facilitator suggestions for disagreements) [unit]
- `client/src/components/DiscoveryAnalysisTab.test.tsx` (shows no-results message when no analyses exist) [unit]
- `client/src/components/DiscoveryAnalysisTab.test.tsx` (hides disagreement section when that priority level has no items) [unit]
- `client/src/components/DiscoveryAnalysisTab.warning.test.tsx` (shows warning alert when participant_count is 1) [unit]
- `client/src/components/DiscoveryAnalysisTab.warning.test.tsx` (shows warning alert when participant_count is 0) [unit]
- `client/src/components/DiscoveryAnalysisTab.warning.test.tsx` (does NOT show warning when participant_count >= 2) [unit]
- `client/src/components/DiscoveryAnalysisTab.warning.test.tsx` (warning uses default Alert variant (not destructive/error)) [unit]
- `client/src/components/DiscoveryAnalysisTab.colorCoding.test.tsx` (HIGH disagreement section uses red border) [unit]
- `client/src/components/DiscoveryAnalysisTab.colorCoding.test.tsx` (MEDIUM disagreement section uses yellow border) [unit]
- `client/src/components/DiscoveryAnalysisTab.colorCoding.test.tsx` (LOWER disagreement section uses blue border) [unit]
- `client/src/components/DiscoveryAnalysisTab.colorCoding.test.tsx` (HIGH items use red background) [unit]
- `client/src/components/DiscoveryAnalysisTab.colorCoding.test.tsx` (MEDIUM items use yellow background) [unit]
- `client/src/components/DiscoveryAnalysisTab.colorCoding.test.tsx` (LOWER items use blue background) [unit]
- `client/src/components/DiscoveryAnalysisTab.warningNotError.test.tsx` (shows a warning (not destructive error) when < 2 participants) [unit]
- `client/src/components/DiscoveryAnalysisTab.warningNotError.test.tsx` (does not show any alert when >= 2 participants) [unit]
- `client/src/components/DiscoveryAnalysisTab.evidence.test.tsx` (renders evidence trace IDs for findings (truncated to 8 chars)) [unit]
- `client/src/components/DiscoveryAnalysisTab.evidence.test.tsx` (shows trace ID badge for each disagreement item) [unit]
- `client/src/components/DraftRubricPanel.test.tsx` (renders trace ID badges for items with source_trace_ids) [unit]
- `client/src/components/DraftRubricPanel.test.tsx` (does not render trace badges for manual items with no trace IDs) [unit]
- `client/src/components/DraftRubricPanel.test.tsx` (renders source type badges for each item) [unit]
- `client/src/components/DraftRubricPanel.test.tsx` (shows item count in header) [unit]
- `client/src/components/DraftRubricPanel.test.tsx` (creates a new manual group from item controls) [unit]
- `client/src/components/DraftRubricPanel.test.tsx` (moves an item into an existing group from item controls) [unit]
- `client/src/components/DiscoveryAnalysisTab.freshness.test.tsx` (displays participant count) [unit]
- `client/src/components/DiscoveryAnalysisTab.freshness.test.tsx` (displays singular participant text when count is 1) [unit]
- `client/src/components/DiscoveryAnalysisTab.freshness.test.tsx` (displays the analysis timestamp) [unit]
- `client/src/components/DiscoveryAnalysisTab.freshness.test.tsx` (displays the template name) [unit]
- `client/src/components/DiscoveryAnalysisTab.freshness.test.tsx` (displays the model used) [unit]
- `client/src/components/DiscoveryAnalysisTab.priorityOrder.test.tsx` (renders disagreement sections in order: HIGH, MEDIUM, LOWER) [unit]
- `client/src/components/DiscoveryAnalysisTab.priorityOrder.test.tsx` (renders findings with priority badges) [unit]

## JUDGE_EVALUATION_SPEC

**Coverage**: 29/31 requirements (93%)

### Uncovered Requirements

- [ ] Spinner stops when re-evaluation completes
- [ ] MemAlign distills semantic memory (guidelines)

### Backend-Only Requirements (no frontend tests)

These requirements are covered by backend tests only. UI regressions won't be caught:

- :warning: Fallback conversion handles Likert-style returns for binary (unit)
- :warning: Auto-evaluation runs in background when annotation phase starts (unit)
- :warning: Judge prompt auto-derived from rubric questions (unit)
- :warning: Per-question judge_type parsed from rubric (`[JUDGE_TYPE:xxx]`) (unit)
- :warning: Binary rubrics evaluated with 0/1 scale (not 1-5) (unit)
- :warning: Auto-evaluation model stored for re-evaluation consistency (unit)
- :warning: Re-evaluate loads registered judge with aligned instructions (integration, unit)
- :warning: Uses same model as initial auto-evaluation (unit)
- :warning: Re-evaluation computes agreement against human ratings (Cohen's Kappa over human/judge pairs), not over an empty set (`require_human_ratings=True`) (unit)
- :warning: Alignment jobs run asynchronously (unit)
- :warning: Aligned judge registered to MLflow (unit)
- :warning: Episodic trace IDs persist on the registered judge across alignment runs (unit)
- :warning: Re-alignment skips traces already in the judge's episodic memory (unit)
- :warning: Metrics reported (guideline count, example count) (unit)
- :warning: Works for both Likert and Binary scales (unit)
- :warning: Krippendorff's Alpha calculated correctly (unit)
- :warning: Cohen's Kappa calculated for rater pairs (unit)
- :warning: Handles edge cases (no variation, single rater) (unit)
- :warning: Updates when new annotations added (unit)
- :warning: Traces with extreme disagreement surfaced in IRR diagnostics (unit)

### Covered Requirements

- [x] Likert judges return values 1-5 (unit)
- [x] Binary judges return values 0 or 1 (unit)
- [x] Fallback conversion handles Likert-style returns for binary (unit) **[BE-only]**
- [x] Evaluation results persisted to database (e2e-real, integration, unit)
- [x] Results reload correctly in UI (e2e-real, unit)
- [x] Auto-evaluation runs in background when annotation phase starts (unit) **[BE-only]**
- [x] Judge prompt auto-derived from rubric questions (unit) **[BE-only]**
- [x] Per-question judge_type parsed from rubric (`[JUDGE_TYPE:xxx]`) (unit) **[BE-only]**
- [x] Binary rubrics evaluated with 0/1 scale (not 1-5) (unit) **[BE-only]**
- [x] Auto-evaluation model stored for re-evaluation consistency (unit) **[BE-only]**
- [x] Results appear in Judge Tuning page (e2e-real)
- [x] Facilitator can toggle auto-evaluation and select a model at annotation start (e2e-real)
- [x] Annotation phase can start with auto-evaluation disabled (e2e-real)
- [x] Re-evaluate loads registered judge with aligned instructions (integration, unit) **[BE-only]**
- [x] Uses same model as initial auto-evaluation (unit) **[BE-only]**
- [x] Results stored against correct prompt version (e2e-real, integration, unit)
- [x] Pre-align and post-align scores directly comparable (e2e-real, integration, unit)
- [x] Re-evaluation computes agreement against human ratings (Cohen's Kappa over human/judge pairs), not over an empty set (`require_human_ratings=True`) (unit) **[BE-only]**
- [x] Alignment jobs run asynchronously (unit) **[BE-only]**
- [x] Aligned judge registered to MLflow (unit) **[BE-only]**
- [x] Episodic trace IDs persist on the registered judge across alignment runs (unit) **[BE-only]**
- [x] Re-alignment skips traces already in the judge's episodic memory (unit) **[BE-only]**
- [x] Metrics reported (guideline count, example count) (unit) **[BE-only]**
- [x] Works for both Likert and Binary scales (unit) **[BE-only]**
- [x] Krippendorff's Alpha calculated correctly (unit) **[BE-only]**
- [x] Cohen's Kappa calculated for rater pairs (unit) **[BE-only]**
- [x] Handles edge cases (no variation, single rater) (unit) **[BE-only]**
- [x] Updates when new annotations added (unit) **[BE-only]**
- [x] Traces with extreme disagreement surfaced in IRR diagnostics (unit) **[BE-only]**

### Tests Without Requirement Links

These tests are tagged with the spec but don't link to specific requirements:

- `tests/integration/test_judge_evaluation_storage.py` (test_promote_finding_returns_500_on_db_error) [integration]
- `tests/integration/test_judge_evaluation_storage.py` (test_promote_real_finding_succeeds) [integration]
- `tests/unit/routers/test_databricks_router.py` (test_databricks_test_connection_success) [unit]
- `tests/unit/routers/test_databricks_router.py` (test_databricks_judge_evaluate_without_workshop_id_uses_request_config) [unit]
- `tests/unit/routers/test_workshops_begin_annotation.py` (test_begin_annotation_requires_rubric) [unit]
- `tests/unit/routers/test_workshops_re_evaluate.py` (test_re_evaluate_tags_traces_before_evaluation) [unit]
- `tests/unit/routers/test_workshops_re_evaluate.py` (test_re_evaluate_tags_traces_fallback_when_no_active_annotation_ids) [unit]
- `tests/unit/services/test_alignment_service.py` (test_likert_agreement_metric_from_store_is_one_when_equal) [unit] **[skipped — not counted]**
- `tests/unit/services/test_alignment_service.py` (test_episodic_log_shows_two_full_examples_without_truncation) [unit]
- `tests/unit/services/test_alignment_service.py` (test_evaluation_with_zero_results_fails_instead_of_reporting_success) [unit]
- `tests/unit/services/test_cohens_kappa.py` (test_interpret_cohens_kappa_bucket_edges) [unit]
- `tests/unit/services/test_cohens_kappa.py` (test_is_cohens_kappa_acceptable_default_threshold) [unit]
- `tests/unit/services/test_discovery_dspy_litellm_interop.py` (test_get_sdk_token_normalizes_env_host_for_m2m_token_url) [unit]
- `tests/unit/services/test_evaluation_tag_overwrite.py` (test_search_tagged_traces_uses_dedicated_align_key) [unit]
- `tests/unit/services/test_evaluation_tag_overwrite.py` (test_run_evaluation_yields_error_when_no_eval_tagged_traces) [unit]
- `tests/unit/services/test_irr_service.py` (test_calculate_irr_for_workshop_sends_no_canned_suggestions_for_low_agreement) [unit]
- `tests/unit/services/test_irr_service.py` (test_calculate_irr_for_workshop_sends_no_canned_suggestions_krippendorff_path) [unit]
- `tests/unit/services/test_irr_service.py` (test_problematic_patterns_gated_per_metric_on_actual_agreement) [unit]
- `tests/unit/services/test_irr_utils.py` (test_validate_annotations_for_irr_valid_case) [unit]
- `tests/unit/services/test_irr_utils.py` (test_format_irr_result_rounding_and_ready_flag) [unit]
- `tests/unit/services/test_irr_utils.py` (test_detect_problematic_patterns_question_id_scopes_to_that_metric) [unit]
- `tests/unit/services/test_irr_utils.py` (test_detect_problematic_patterns_question_id_excludes_other_metric_ratings) [unit]
- `client/tests/e2e/evaluation-tagging.spec.ts` (re-evaluate endpoint tags traces before searching MLflow) [e2e-real]
- `client/tests/e2e/evaluation-tagging.spec.ts` (begin-annotation auto-eval creates job and attempts tagging) [e2e-real]
- `client/tests/e2e/evaluation-tagging.spec.ts` (begin-annotation without eval model skips auto-eval) [e2e-real]
- `client/src/pages/IRRResultsDemo.agreement.test.ts` (only counts annotators who rated the requested metric (no legacy fallback)) [unit]
- `client/src/pages/IRRResultsDemo.agreement.test.ts` (excludes traces with fewer than two ratings for the requested metric) [unit]
- `client/src/pages/IRRResultsDemo.agreement.test.ts` (still reports high disagreement when ratings genuinely diverge) [unit]
- `client/src/pages/IRRResultsDemo.agreement.test.ts` (uses the legacy rating field when no metric is requested) [unit]

## ROLE_PERMISSIONS_SPEC

**Coverage**: 16/16 requirements (100%)

### Backend-Only Requirements (no frontend tests)

These requirements are covered by backend tests only. UI regressions won't be caught:

- :warning: Facilitator role grants: can_create_rubric, can_manage_workshop, can_assign_annotations, can_view_all_findings, can_view_all_annotations, can_view_results (unit)
- :warning: Facilitator role denies: can_annotate, can_create_findings (unit)
- :warning: SME role grants: can_annotate, can_create_findings, can_view_discovery (unit)
- :warning: SME role denies: can_create_rubric, can_manage_workshop, can_view_results, can_view_all_annotations (unit)
- :warning: Participant role grants: can_annotate, can_create_findings, can_view_discovery (unit)
- :warning: Participant role denies: can_create_rubric, can_manage_workshop, can_view_results, can_view_all_annotations (unit)
- :warning: Permissions derived from role via UserPermissions.for_role() classmethod (unit)
- :warning: Facilitator role cannot be changed via update endpoint (unit)
- :warning: Facilitator accounts cannot be deleted via delete endpoint (unit)
- :warning: Only facilitators can create invitations (unit)
- :warning: Phase advancement validates prerequisites before transitioning (unit)
- :warning: Phase advancement returns 400 if prerequisites not met (unit)
- :warning: Facilitators authenticate via YAML config (preconfigured credentials) (unit)
- :warning: SMEs and participants authenticate via database email lookup (no password verification) (unit)
- :warning: Login response includes is_preconfigured_facilitator flag for facilitator logins (unit)

### Covered Requirements

- [x] Facilitator role grants: can_create_rubric, can_manage_workshop, can_assign_annotations, can_view_all_findings, can_view_all_annotations, can_view_results (unit) **[BE-only]**
- [x] Facilitator role denies: can_annotate, can_create_findings (unit) **[BE-only]**
- [x] SME role grants: can_annotate, can_create_findings, can_view_discovery (unit) **[BE-only]**
- [x] SME role denies: can_create_rubric, can_manage_workshop, can_view_results, can_view_all_annotations (unit) **[BE-only]**
- [x] Participant role grants: can_annotate, can_create_findings, can_view_discovery (unit) **[BE-only]**
- [x] Participant role denies: can_create_rubric, can_manage_workshop, can_view_results, can_view_all_annotations (unit) **[BE-only]**
- [x] Permissions derived from role via UserPermissions.for_role() classmethod (unit) **[BE-only]**
- [x] Facilitator role cannot be changed via update endpoint (unit) **[BE-only]**
- [x] Facilitator accounts cannot be deleted via delete endpoint (unit) **[BE-only]**
- [x] Only facilitators can create invitations (unit) **[BE-only]**
- [x] Phase advancement is gated client-side: non-facilitators are blocked from the facilitator dashboard that hosts the advance-phase control (unit)
- [x] Phase advancement validates prerequisites before transitioning (unit) **[BE-only]**
- [x] Phase advancement returns 400 if prerequisites not met (unit) **[BE-only]**
- [x] Facilitators authenticate via YAML config (preconfigured credentials) (unit) **[BE-only]**
- [x] SMEs and participants authenticate via database email lookup (no password verification) (unit) **[BE-only]**
- [x] Login response includes is_preconfigured_facilitator flag for facilitator logins (unit) **[BE-only]**

## RUBRIC_SPEC

**Coverage**: 26/26 requirements (100%)

### Backend-Only Requirements (no frontend tests)

These requirements are covered by backend tests only. UI regressions won't be caught:

- :warning: Delimiter never appears in user input (by design) (unit)
- :warning: Per-question judge_type parsed from the `|||JUDGE_TYPE|||` delimiter (unit)
- :warning: Parsed questions get sequential `q_N` ids (unit)
- :warning: Legacy `freeform` judge type coerces to likert at the parse boundary (unit)
- :warning: Empty/whitespace-only parts filtered out (unit)
- :warning: Binary feedback logged as 0/1 to MLflow (not 3) (unit)
- :warning: Facilitator can edit an existing rubric question (unit)
- :warning: Facilitator can delete a rubric question (unit)
- :warning: Only one rubric exists per workshop (upsert semantics) (unit)
- :warning: Rubric required before advancing to annotation phase (unit)
- :warning: No phase restriction on rubric CRUD (unit)
- :warning: Question IDs re-indexed sequentially after deletion (unit)
- :warning: Annotation data preserved when rubric questions are deleted (unit)
- :warning: Judge name auto-derived from first rubric question title (unit)
- :warning: MLflow re-sync triggered on rubric create/update (best-effort) (unit)
- :warning: AI suggestions generated from discovery findings and participant notes (unit)
- :warning: Suggestions validated: title >= 3 chars, description >= 10 chars (unit)
- :warning: Facilitator can accept, reject, or edit suggestions before adding to rubric (unit)

### Covered Requirements

- [x] Questions with multi-line descriptions parse correctly (unit)
- [x] Delimiter never appears in user input (by design) (unit) **[BE-only]**
- [x] Frontend and backend use same delimiter constant (unit)
- [x] Per-question judge_type parsed from the `|||JUDGE_TYPE|||` delimiter (unit) **[BE-only]**
- [x] Parsed questions get sequential `q_N` ids (unit) **[BE-only]**
- [x] Legacy `freeform` judge type coerces to likert at the parse boundary (unit) **[BE-only]**
- [x] Empty/whitespace-only parts filtered out (unit) **[BE-only]**
- [x] Likert scale shows 1-5 rating options (e2e-real)
- [x] Binary scale shows Pass/Fail buttons (not star ratings) (e2e-real)
- [x] Binary feedback logged as 0/1 to MLflow (not 3) (unit) **[BE-only]**
- [x] Mixed rubrics support different scales per question (e2e-real, unit)
- [x] Facilitator can create a rubric question with title and description (e2e-mocked, unit)
- [x] Facilitator can edit an existing rubric question (unit) **[BE-only]**
- [x] Facilitator can delete a rubric question (unit) **[BE-only]**
- [x] Only one rubric exists per workshop (upsert semantics) (unit) **[BE-only]**
- [x] Rubric persists and is retrievable via GET after creation (e2e-mocked, e2e-real)
- [x] Rubric required before advancing to annotation phase (unit) **[BE-only]**
- [x] No phase restriction on rubric CRUD (unit) **[BE-only]**
- [x] Question IDs re-indexed sequentially after deletion (unit) **[BE-only]**
- [x] Annotation data preserved when rubric questions are deleted (unit) **[BE-only]**
- [x] Judge name auto-derived from first rubric question title (unit) **[BE-only]**
- [x] MLflow re-sync triggered on rubric create/update (best-effort) (unit) **[BE-only]**
- [x] AI suggestions generated from discovery findings and participant notes (unit) **[BE-only]**
- [x] Suggestions validated: title >= 3 chars, description >= 10 chars (unit) **[BE-only]**
- [x] Invalid judge type in suggestions defaults to likert (unit)
- [x] Facilitator can accept, reject, or edit suggestions before adding to rubric (unit) **[BE-only]**

### Tests Without Requirement Links

These tests are tagged with the spec but don't link to specific requirements:

- `client/tests/e2e/rubric-judge-type.spec.ts` (binary annotation rating stored as 0/1 via workshop API) [e2e-real]

## TESTING_SPEC

**Coverage**: 16/25 requirements (64%)

### Uncovered Requirements

- [ ] `tests/integration/conftest.py` provides real-DB fixtures with transaction rollback isolation
- [ ] Integration tests run against SQLite (default) and Postgres (via testcontainers)
- [ ] `just test-integration` recipe exists and passes
- [ ] All integration tests tagged with `@pytest.mark.integration` and `@pytest.mark.spec()`
- [ ] External services (MLflow, Databricks) mocked — only database is real
- [ ] Tests are hermetic: no shared state, runnable in any order
- [ ] Call-site tests verify services pass correct parameter types to MLflow methods
- [ ] pytest emits coverage reports (term, HTML, XML) via `addopts` in `pyproject.toml`
- [ ] `just test-contract` recipe works

### Backend-Only Requirements (no frontend tests)

These requirements are covered by backend tests only. UI regressions won't be caught:

- :warning: Workshop CRUD tested end-to-end through HTTP → DB → response (integration)
- :warning: Trace ingestion tested: bulk upload, retrieval, metadata persistence (integration)
- :warning: Phase transition prerequisites enforced: no discovery without traces, no annotation without rubric (integration)
- :warning: Annotation upsert semantics verified: same user+trace updates (not duplicates), different users create separate records (integration)
- :warning: Discovery finding upsert semantics verified at DB level (integration)
- :warning: Connection resilience tested: connection errors classified as transient vs not, `_reset_connection_pool()` disposes the engine, `get_db()` retries with backoff and gives up after 3 attempts (integration)
- :warning: Mock shape tests verify test mocks match real MLflow response structures (unit)
- :warning: Error classification tested: retryable vs non-retryable errors handled correctly (unit)
- :warning: Feedback value types validated: binary (0.0/1.0 float), likert (1.0-5.0 float) (unit)
- :warning: Assessment limit (50 per trace) handling tested (unit)
- :warning: Tests run in CI on every PR (unit)
- :warning: pytest `--spec` option filters collection to tests tagged for the requested spec (unit)
- :warning: Test isolation (no shared state between tests) (unit)
- :warning: Coverage analyzer excludes skipped and xfail tests from requirement coverage and annotates skipped-only criteria (unit)
- :warning: Coverage analyzer excludes roadmap criteria from the coverage denominator and lists them separately (unit)
- :warning: Coverage analyzer reports unknown spec tags with tagged test counts without crashing (unit)

### Covered Requirements

- [x] Workshop CRUD tested end-to-end through HTTP → DB → response (integration) **[BE-only]**
- [x] Trace ingestion tested: bulk upload, retrieval, metadata persistence (integration) **[BE-only]**
- [x] Phase transition prerequisites enforced: no discovery without traces, no annotation without rubric (integration) **[BE-only]**
- [x] Annotation upsert semantics verified: same user+trace updates (not duplicates), different users create separate records (integration) **[BE-only]**
- [x] Discovery finding upsert semantics verified at DB level (integration) **[BE-only]**
- [x] Connection resilience tested: connection errors classified as transient vs not, `_reset_connection_pool()` disposes the engine, `get_db()` retries with backoff and gives up after 3 attempts (integration) **[BE-only]**
- [x] Mock shape tests verify test mocks match real MLflow response structures (unit) **[BE-only]**
- [x] Error classification tested: retryable vs non-retryable errors handled correctly (unit) **[BE-only]**
- [x] Feedback value types validated: binary (0.0/1.0 float), likert (1.0-5.0 float) (unit) **[BE-only]**
- [x] Assessment limit (50 per trace) handling tested (unit) **[BE-only]**
- [x] Tests run in CI on every PR (unit) **[BE-only]**
- [x] pytest `--spec` option filters collection to tests tagged for the requested spec (unit) **[BE-only]**
- [x] Test isolation (no shared state between tests) (unit) **[BE-only]**
- [x] Coverage analyzer excludes skipped and xfail tests from requirement coverage and annotates skipped-only criteria (unit) **[BE-only]**
- [x] Coverage analyzer excludes roadmap criteria from the coverage denominator and lists them separately (unit) **[BE-only]**
- [x] Coverage analyzer reports unknown spec tags with tagged test counts without crashing (unit) **[BE-only]**

### Roadmap (not shipping)

These criteria are roadmap-only and excluded from the coverage denominator:

- Coverage thresholds (server >20%, client >20%) enforced by a CI gate (roadmap)
- Flaky-test detection and quarantine process in place (roadmap)

### Tests Without Requirement Links

These tests are tagged with the spec but don't link to specific requirements:

- `tests/contract/test_mlflow_contracts.py` (test_binary_values_are_float) [unit]
- `tests/contract/test_mlflow_contracts.py` (test_likert_values_in_range) [unit]
- `tests/contract/test_mlflow_contracts.py` (test_log_feedback_parameter_types) [unit]
- `tests/contract/test_mlflow_contracts.py` (test_log_feedback_ai_source_format) [unit]
- `tests/contract/test_mlflow_contracts.py` (test_retry_wrapper_passes_through_return_value) [unit]
- `tests/contract/test_mlflow_contracts.py` (test_set_trace_tag_receives_strings) [unit]
- `tests/contract/test_mlflow_contracts.py` (test_search_traces_parameter_types) [unit]
- `tests/contract/test_mlflow_contracts.py` (test_dedup_check_counts_existing_assessments) [unit]
- `tests/integration/test_annotation_submission.py` (test_submit_annotation) [integration]
- `tests/integration/test_annotation_submission.py` (test_annotation_with_multi_ratings) [integration]
- `tests/integration/test_annotation_submission.py` (test_get_annotations_filtered_by_user) [integration]
- `tests/integration/test_connection_resilience.py` (test_stream_discovery_comments_has_no_db_dependency) [integration]
- `tests/integration/test_connection_resilience.py` (test_stream_discovery_agent_run_has_no_db_dependency) [integration]
- `tests/integration/test_discovery_findings.py` (test_submit_finding) [integration]
- `tests/integration/test_discovery_findings.py` (test_get_findings_filtered_by_user) [integration]
- `tests/integration/test_discovery_findings.py` (test_findings_scoped_to_workshop) [integration]

## TRACE_DISPLAY_SPEC

**Coverage**: 19/19 requirements (100%)

### Backend-Only Requirements (no frontend tests)

These requirements are covered by backend tests only. UI regressions won't be caught:

- :warning: Multiple JSONPath matches are concatenated with newlines (unit)
- :warning: Facilitator can configure span attribute filter with span name, span type, attribute key, and attribute value (unit)
- :warning: Filter criteria are AND-combined and first matching span wins (unit)
- :warning: Span filter is applied before JSONPath extraction in TraceViewer (unit)
- :warning: Empty filter config results in no filtering and root trace data is used (unit)
- :warning: String span inputs and outputs are returned as-is without double-serialization (unit)
- :warning: All backend services that consume trace input/output apply the same span filter and JSONPath pipeline as the TraceViewer (unit)
- :warning: JSONPath evaluation does not noticeably slow down trace display (unit)
- :warning: Preview responds within 500ms (unit)

### Covered Requirements

- [x] Facilitator can configure input/output JSONPath in settings panel (e2e-real)
- [x] JSONPath fields are optional and clearly labeled as such (unit)
- [x] Preview shows extraction results against first workshop trace (e2e-real)
- [x] TraceViewer applies JSONPath when configured (unit)
- [x] Multiple JSONPath matches are concatenated with newlines (unit) **[BE-only]**
- [x] System falls back to raw display when JSONPath is not configured, JSON parsing fails, JSONPath query fails, or JSONPath returns null/empty (e2e-real, unit)
- [x] Settings are persisted per workshop (e2e-real)
- [x] Facilitator can configure span attribute filter with span name, span type, attribute key, and attribute value (unit) **[BE-only]**
- [x] Filter criteria are AND-combined and first matching span wins (unit) **[BE-only]**
- [x] Attribute value input is disabled until attribute key has a value (unit)
- [x] Span filter preview shows match status and filtered inputs/outputs against first trace (e2e-real)
- [x] Span filter is applied before JSONPath extraction in TraceViewer (unit) **[BE-only]**
- [x] Empty filter config results in no filtering and root trace data is used (unit) **[BE-only]**
- [x] String span inputs and outputs are returned as-is without double-serialization (unit) **[BE-only]**
- [x] All backend services that consume trace input/output apply the same span filter and JSONPath pipeline as the TraceViewer (unit) **[BE-only]**
- [x] Copy Output copies the representation currently displayed (formatted vs raw) (unit)
- [x] JSONPath evaluation does not noticeably slow down trace display (unit) **[BE-only]**
- [x] Preview responds within 500ms (unit) **[BE-only]**
- [x] Invalid JSONPath syntax shows helpful error message in preview (e2e-real, unit)

## TRACE_INGESTION_SPEC

**Coverage**: 9/17 requirements (52%)

### Uncovered Requirements

- [ ] MLflow link in TraceViewer opens the correct trace in the correct experiment
- [ ] Extraction handles the list-of-items and `{"object": "response"}` output formats
- [ ] Re-ingesting traces preserves existing `DiscoveryFeedbackDB` FK references
- [ ] Re-ingesting traces preserves existing `AnnotationDB` FK references
- [ ] `active_discovery_trace_ids` remain valid after re-ingestion
- [ ] Preview format (`request_preview`/`response_preview`) uses column values directly
- [ ] Raw format (`request`/`response`) applies content extraction with role-aware logic
- [ ] `mlflow_trace_id` from CSV `trace_id` column is used for deduplication

### Backend-Only Requirements (no frontend tests)

These requirements are covered by backend tests only. UI regressions won't be caught:

- :warning: Traces are deduplicated by `(workshop_id, mlflow_trace_id)` — re-ingest updates, not duplicates (unit)
- :warning: `mlflow_url`, `mlflow_host`, and `mlflow_experiment_id` are persisted on ingest (unit)
- :warning: Traces without `mlflow_trace_id` get a generated UUID and insert normally (unit)
- :warning: Input extraction prefers the last user-role message from the request payload (unit)
- :warning: Output extraction prefers the last assistant-role message from the response payload (unit)
- :warning: Each trace gets its own unique extracted input (no shared-prefix duplication) (unit)
- :warning: Extraction handles the `{"messages": [...]}` and `{"request": {"input": [...]}}` formats (unit)
- :warning: Extraction falls back to cleaned raw text when no structured format matches (unit)
- :warning: Re-ingesting traces preserves existing `DiscoveryFindingDB` FK references (unit)

### Covered Requirements

- [x] Traces are deduplicated by `(workshop_id, mlflow_trace_id)` — re-ingest updates, not duplicates (unit) **[BE-only]**
- [x] `mlflow_url`, `mlflow_host`, and `mlflow_experiment_id` are persisted on ingest (unit) **[BE-only]**
- [x] Traces without `mlflow_trace_id` get a generated UUID and insert normally (unit) **[BE-only]**
- [x] Input extraction prefers the last user-role message from the request payload (unit) **[BE-only]**
- [x] Output extraction prefers the last assistant-role message from the response payload (unit) **[BE-only]**
- [x] Each trace gets its own unique extracted input (no shared-prefix duplication) (unit) **[BE-only]**
- [x] Extraction handles the `{"messages": [...]}` and `{"request": {"input": [...]}}` formats (unit) **[BE-only]**
- [x] Extraction falls back to cleaned raw text when no structured format matches (unit) **[BE-only]**
- [x] Re-ingesting traces preserves existing `DiscoveryFindingDB` FK references (unit) **[BE-only]**

## TRACE_SUMMARIZATION_SPEC

**Coverage**: 23/64 requirements (35%)

### Uncovered Requirements

- [ ] Facilitator can enable/disable trace summarization per workshop
- [ ] Settings are persisted per workshop
- [ ] Summarization runs at ingestion time when enabled and model is configured
- [ ] Milestone summaries contain substantive content from spans (actual queries, results, decisions)
- [ ] Milestone summaries avoid mechanical flow narration (not "query received", "results returned")
- [ ] Summary is stored as JSON on the trace record
- [ ] The agent determines the number of milestones based on trace complexity
- [ ] Milestone view is the default display when a summary exists
- [ ] User can toggle between milestone view and the existing trace viewer
- [ ] Milestone view shows executive summary at the top
- [ ] Milestones are numbered and show title, summary, and resolved span data (inputs → outputs)
- [ ] When no summary exists, the existing trace viewer is shown (no toggle)
- [ ] Re-ingesting with summarization enabled regenerates summaries
- [ ] Re-ingesting with summarization disabled preserves existing summaries
- [ ] Facilitator can trigger re-summarization without full re-ingestion
- [ ] Ingestion API returns immediately; summarization runs in the background
- [ ] The ingestion response includes `summarization_job_id` when summarization is triggered
- [ ] Failed individual traces are retried up to 2 times with exponential backoff
- [ ] Rate limit responses (429) trigger backoff, not failure
- [ ] A batch of 100 traces completes summarization within a reasonable wall-clock time given the concurrency limit and model latency
- [ ] Concurrent LLM calls do not exceed the serving endpoint's rate limit
- [ ] Summarization does not block the ingestion API response
- [ ] Individual trace summarization errors are logged with trace ID, error type, and retry count
- [ ] SummarizationSettings shows a progress indicator while a summarization job is running
- [ ] Progress indicator shows completed/total/failed counts (e.g., "Summarizing... 45/80 complete, 2 failed")
- [ ] Progress updates automatically via polling while the job is active
- [ ] On completion, succeeded/failed counts are displayed in SummarizationSettings
- [ ] Failed traces are listed with their error descriptions
- [ ] Facilitator can retry failed traces from the completion view (creates a new job for just those traces)
- [ ] Re-summarize button exists in SummarizationSettings (disabled while a job is running)
- [ ] Facilitator can choose to re-summarize all traces or only unsummarized traces
- [ ] Confirmation dialog is shown before starting re-summarization
- [ ] `POST /resummarize` accepts a `mode` parameter: "all", "unsummarized", or "failed"
- [ ] Re-summarization creates a tracked `SummarizationJob` with the same progress UI
- [ ] Trace list in FacilitatorDashboard shows a visual indicator for traces that have summaries
- [ ] Aggregate count of summarized vs. unsummarized traces is visible (e.g., "45/80 traces summarized")
- [ ] Last summarization timestamp is visible in SummarizationSettings
- [ ] DiscoveryTraceCard defaults to summary view when a summary exists
- [ ] Facilitator can toggle between summary view and raw user/assistant content
- [ ] Summary view shows the executive summary text
- [ ] Summary view has expandable milestones with titles and descriptions

### Backend-Only Requirements (no frontend tests)

These requirements are covered by backend tests only. UI regressions won't be caught:

- :warning: Facilitator can select a model for summarization from available Databricks endpoints (unit)
- :warning: Facilitator can provide optional free-text guidance for the summarization prompt (unit)
- :warning: Agent accesses trace data through inspection tools (not a full-text dump) (unit)
- :warning: Agent produces an executive summary as the first pass (unit)
- :warning: Agent extracts milestones with relevant span data as the second pass (unit)
- :warning: Each milestone includes span data references resolved to actual trace values (unit)
- :warning: Span data references are resolved in a post-processing step (not LLM-generated values) (unit)
- :warning: Agent uses trace inspection tools to selectively examine spans (not a full-text dump) (unit)
- :warning: Agent tools include: get_trace_overview, list_spans, get_span_detail, get_root_span, search_spans (unit)
- :warning: Summarization failure does not block trace ingestion (unit)
- :warning: Each milestone has a number, title, and summary (unit)
- :warning: Each milestone has zero or more input span data references (span_name, field, optional jsonpath) (unit)
- :warning: Each milestone has zero or more output span data references (span_name, field, optional jsonpath) (unit)
- :warning: Span data references are resolved to actual values from the trace after agent output (unit)
- :warning: When jsonpath is null, the entire span inputs or outputs field is included (unit)
- :warning: Invalid span references (nonexistent span or path) resolve to null without failing the milestone (unit)
- :warning: Multiple traces are summarized concurrently up to a configurable concurrency limit (unit)
- :warning: A `SummarizationJob` database row is created when summarization starts (unit)
- :warning: The job row is updated as each trace completes (trace ID appended to `completed_traces` or `failed_traces`) (unit)
- :warning: Partial failures do not block the batch — failed traces are ingested with `summary = null` (unit)
- :warning: `GET /workshops/{id}/summarization-job/{job_id}` returns job status with completed/total/failed counts (unit)
- :warning: `GET /workshops/{id}/summarization-status` returns summary coverage stats and last job info (unit)
- :warning: `summarization-status` endpoint provides the data for these indicators without requiring a job (unit)

### Covered Requirements

- [x] Facilitator can select a model for summarization from available Databricks endpoints (unit) **[BE-only]**
- [x] Facilitator can provide optional free-text guidance for the summarization prompt (unit) **[BE-only]**
- [x] Agent accesses trace data through inspection tools (not a full-text dump) (unit) **[BE-only]**
- [x] Agent produces an executive summary as the first pass (unit) **[BE-only]**
- [x] Agent extracts milestones with relevant span data as the second pass (unit) **[BE-only]**
- [x] Each milestone includes span data references resolved to actual trace values (unit) **[BE-only]**
- [x] Span data references are resolved in a post-processing step (not LLM-generated values) (unit) **[BE-only]**
- [x] Agent uses trace inspection tools to selectively examine spans (not a full-text dump) (unit) **[BE-only]**
- [x] Agent tools include: get_trace_overview, list_spans, get_span_detail, get_root_span, search_spans (unit) **[BE-only]**
- [x] Summarization failure does not block trace ingestion (unit) **[BE-only]**
- [x] Each milestone has a number, title, and summary (unit) **[BE-only]**
- [x] Each milestone has zero or more input span data references (span_name, field, optional jsonpath) (unit) **[BE-only]**
- [x] Each milestone has zero or more output span data references (span_name, field, optional jsonpath) (unit) **[BE-only]**
- [x] Span data references are resolved to actual values from the trace after agent output (unit) **[BE-only]**
- [x] When jsonpath is null, the entire span inputs or outputs field is included (unit) **[BE-only]**
- [x] Invalid span references (nonexistent span or path) resolve to null without failing the milestone (unit) **[BE-only]**
- [x] Multiple traces are summarized concurrently up to a configurable concurrency limit (unit) **[BE-only]**
- [x] A `SummarizationJob` database row is created when summarization starts (unit) **[BE-only]**
- [x] The job row is updated as each trace completes (trace ID appended to `completed_traces` or `failed_traces`) (unit) **[BE-only]**
- [x] Partial failures do not block the batch — failed traces are ingested with `summary = null` (unit) **[BE-only]**
- [x] `GET /workshops/{id}/summarization-job/{job_id}` returns job status with completed/total/failed counts (unit) **[BE-only]**
- [x] `GET /workshops/{id}/summarization-status` returns summary coverage stats and last job info (unit) **[BE-only]**
- [x] `summarization-status` endpoint provides the data for these indicators without requiring a job (unit) **[BE-only]**

### Tests Without Requirement Links

These tests are tagged with the spec but don't link to specific requirements:

- `tests/unit/services/test_trace_summarization_service.py` (test_from_dict) [unit]
- `tests/unit/services/test_trace_summarization_service.py` (test_from_dict_missing_fields_uses_defaults) [unit]
- `tests/unit/services/test_trace_summarization_service.py` (test_batch_progress_callback) [unit]
- `tests/unit/test_summarization_job.py` (test_get_summarization_job_not_found) [unit]
- `tests/unit/test_summarization_job.py` (test_update_job_status) [unit]
- `tests/unit/test_summarization_job.py` (test_get_latest_job) [unit]
- `tests/unit/test_summarization_job.py` (test_get_latest_job_none) [unit]

## UI_COMPONENTS_SPEC

**Coverage**: 2/16 requirements (12%)

### Uncovered Requirements

- [ ] Items per page selector updates page size
- [ ] Quick jump navigates to valid pages
- [ ] Keyboard shortcuts work when enabled
- [ ] Disabled states shown for unavailable actions
- [ ] Page info accurately reflects data
- [ ] SQL queries formatted with line breaks
- [ ] CSV export includes all table data
- [ ] Copy to clipboard works for all content
- [ ] Invalid JSON shows error + fallback
- [ ] Responsive layout on different screens
- [ ] Keyboard navigation works throughout
- [ ] Screen reader announces state changes
- [ ] Focus visible and managed correctly
- [ ] Color contrast meets WCAG AA

### Covered Requirements

- [x] Page navigation works correctly (first, prev, next, last) (unit)
- [x] JSON arrays render as tables (unit)

### Tests Without Requirement Links

These tests are tagged with the spec but don't link to specific requirements:

- `client/tests/e2e/ui-components.spec.ts` (pagination in annotation view navigates between pages) [e2e-real]
- `client/tests/e2e/ui-components.spec.ts` (trace viewer renders trace content) [e2e-real]

## EVAL_MODE_SPEC

**Coverage**: 18/19 requirements (94%)

### Uncovered Requirements

- [ ] Discovery analysis can run agent loops over trace spans as alternative to summaries

### Backend-Only Requirements (no frontend tests)

These requirements are covered by backend tests only. UI regressions won't be caught:

- :warning: Workshop can be created with `mode: "eval"` (unit)
- :warning: Mode is immutable after creation (unit)
- :warning: Eval-mode workshops do not use the global rubric system (unit)
- :warning: Existing workshop-mode behavior is unchanged (unit)
- :warning: Facilitator can create criteria on a specific trace (unit)
- :warning: Each criterion has a type (standard or hurdle) and weight (-10 to +10) (unit)
- :warning: Criteria can be promoted from discovery findings (unit)
- :warning: Criteria are editable and deletable (unit)
- :warning: Per-trace rubric is rendered as markdown (unit)
- :warning: Discovery analysis uses trace summaries when available (unit)
- :warning: Hurdle criteria gate the entire trace — any hurdle failure → score 0 (unit)
- :warning: Standard criteria scored as met (1) or not met (0) × weight (unit)
- :warning: Negative-weight criteria penalize when met (unit)
- :warning: Normalized score = raw / max_possible, clipped to [0, 1] (unit)
- :warning: Scoring handles edge cases: no criteria, all hurdles, all negative weights (unit)
- :warning: Results stored per-criterion with rationale (unit)
- :warning: Aggregated eval scores are available per trace or for all workshop traces (unit)

### Covered Requirements

- [x] Workshop can be created with `mode: "eval"` (unit) **[BE-only]**
- [x] Mode is immutable after creation (unit) **[BE-only]**
- [x] Eval-mode workshops do not use the global rubric system (unit) **[BE-only]**
- [x] Existing workshop-mode behavior is unchanged (unit) **[BE-only]**
- [x] Facilitator can create criteria on a specific trace (unit) **[BE-only]**
- [x] Each criterion has a type (standard or hurdle) and weight (-10 to +10) (unit) **[BE-only]**
- [x] Criteria can be promoted from discovery findings (unit) **[BE-only]**
- [x] Criteria can be authored directly (without discovery) (unit)
- [x] Criteria are editable and deletable (unit) **[BE-only]**
- [x] Per-trace rubric is rendered as markdown (unit) **[BE-only]**
- [x] Discovery analysis uses trace summaries when available (unit) **[BE-only]**
- [x] Hurdle criteria gate the entire trace — any hurdle failure → score 0 (unit) **[BE-only]**
- [x] Standard criteria scored as met (1) or not met (0) × weight (unit) **[BE-only]**
- [x] Negative-weight criteria penalize when met (unit) **[BE-only]**
- [x] Normalized score = raw / max_possible, clipped to [0, 1] (unit) **[BE-only]**
- [x] Scoring handles edge cases: no criteria, all hurdles, all negative weights (unit) **[BE-only]**
- [x] Results stored per-criterion with rationale (unit) **[BE-only]**
- [x] Aggregated eval scores are available per trace or for all workshop traces (unit) **[BE-only]**

### Tests Without Requirement Links

These tests are tagged with the spec but don't link to specific requirements:

- `tests/unit/services/test_database_service_eval_mode.py` (test_eval_mode_tables_are_present_in_metadata) [unit]
- `client/tests/e2e/eval-mode-workflow.spec.ts` (eval mode supports per-trace criteria and scoring) [e2e-mocked]

---

## How to Tag Tests

### pytest
```python
@pytest.mark.spec("SPEC_NAME")
@pytest.mark.req("Requirement text from success criteria")
def test_something(): ...
```

### Playwright
```typescript
test.use({ tag: ['@spec:SPEC_NAME', '@req:Requirement text'] });
```

### Vitest
```typescript
// @spec SPEC_NAME
// @req Requirement text from success criteria
```
