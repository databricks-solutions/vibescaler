# Spec Test Coverage Map

**Generated**: 2026-06-09 21:11:53

This report shows test coverage for each specification's success criteria.

## Test Pyramid Summary

| Type | Count | Description |
|------|-------|-------------|
| Unit | 720 | pytest unit tests, Vitest tests |
| Integration | 60 | pytest with real DB/API |
| E2E (Mocked) | 11 | Playwright with mocked API |
| E2E (Real) | 77 | Playwright with real API |

## Coverage Summary

| Spec | Reqs | Covered | Cover% | Unit | Int | E2E-M | E2E-R | BE-only |
|------|------|---------|--------|------|-----|-------|-------|---------|
| [ANNOTATION_SPEC](#annotation-spec) | 21 | 8 | 38% | 50 | 0 | 0 | 7 | **6** |
| [ASSISTED_FACILITATION_SPEC](#assisted-facilitation-spec) | 7 | 7 | 100% | 31 | 0 | 0 | 42 | 0 |
| [AUTHENTICATION_SPEC](#authentication-spec) | 28 | 5 | 17% | 11 | 0 | 2 | 0 | **4** |
| [BUILD_AND_DEPLOY_SPEC](#build-and-deploy-spec) | 16 | 13 | 81% | 64 | 0 | 0 | 0 | **13** |
| [CUSTOM_LLM_PROVIDER_SPEC](#custom-llm-provider-spec) | 15 | 0 | 0% | 13 | 0 | 0 | 0 | 0 |
| [DATASETS_SPEC](#datasets-spec) | 9 | 7 | 77% | 25 | 0 | 0 | 1 | **7** |
| [DESIGN_SYSTEM_SPEC](#design-system-spec) | 7 | 0 | 0% | 4 | 0 | 1 | 0 | 0 |
| [DISCOVERY_SPEC](#discovery-spec) | 72 | 61 | 84% | 207 | 5 | 4 | 1 | **40** |
| [DISCOVERY_TRACE_ASSIGNMENT_SPEC](#discovery-trace-assignment-spec) | 13 | 12 | 92% | 20 | 0 | 1 | 1 | **11** |
| [JUDGE_EVALUATION_SPEC](#judge-evaluation-spec) | 25 | 24 | 96% | 70 | 7 | 0 | 8 | **19** |
| [PROJECT_SETUP_SPEC](#project-setup-spec) | 26 | 6 | 23% | 9 | 0 | 1 | 0 | **2** |
| [ROLE_PERMISSIONS_SPEC](#role-permissions-spec) | 16 | 16 | 100% | 24 | 0 | 0 | 0 | **16** |
| [RUBRIC_SPEC](#rubric-spec) | 25 | 25 | 100% | 63 | 0 | 1 | 6 | **17** |
| [TESTING_SPEC](#testing-spec) | 30 | 0 | 0% | 35 | 48 | 0 | 0 | 0 |
| [TRACE_DISPLAY_SPEC](#trace-display-spec) | 18 | 18 | 100% | 68 | 0 | 0 | 7 | **11** |
| [UI_COMPONENTS_SPEC](#ui-components-spec) | 16 | 0 | 0% | 4 | 0 | 0 | 4 | 0 |
| [EVAL_MODE_SPEC](#eval-mode-spec) | 35 | 14 | 40% | 22 | 0 | 1 | 0 | **14** |

**Total**: 216/379 requirements covered (56%)

---

## ANNOTATION_SPEC

**Coverage**: 8/21 requirements (38%)

### Uncovered Requirements

- [ ] Toast shows "Annotation saved!" for new submissions
- [ ] Toast shows "Annotation updated!" only when changes detected
- [ ] No toast when navigating without changes
- [ ] Multi-line comments preserved throughout the stack
- [ ] Comments display with proper line breaks
- [ ] Next button enabled for annotated traces (allows re-navigation)
- [ ] Duplicate feedback entries are detected and skipped
- [ ] Bulk resync re-exports all annotations when rubric titles change
- [ ] Failed saves are queued and retried automatically with exponential backoff
- [ ] Navigation is optimistic (UI advances immediately, save completes in background)
- [ ] Navigation debounced at 300ms to prevent duplicate saves
- [ ] Freeform question responses are optional (not required for navigation)
- [ ] Freeform responses are encoded in the comment field as JSON

### Backend-Only Requirements (no frontend tests)

These requirements are covered by backend tests only. UI regressions won't be caught:

- :warning: Users can edit previously submitted annotations (unit)
- :warning: Annotations sync to MLflow as feedback on save (one entry per rubric question) (unit)
- :warning: MLflow trace tagged with `label: "align"` and `workshop_id` on annotation (unit)
- :warning: Feedback source is HUMAN with annotator's user_id (unit)
- :warning: Annotation comment maps to MLflow feedback rationale (unit)
- :warning: Legacy single-rating format loads correctly alongside multi-rating format (unit)

### Covered Requirements

- [x] Users can edit previously submitted annotations (unit) **[BE-only]**
- [x] Changes automatically save on navigation (Next/Previous) (e2e-real, unit)
- [x] Annotation count reflects unique submissions (not re-submissions) (e2e-real, unit)
- [x] Annotations sync to MLflow as feedback on save (one entry per rubric question) (unit) **[BE-only]**
- [x] MLflow trace tagged with `label: "align"` and `workshop_id` on annotation (unit) **[BE-only]**
- [x] Feedback source is HUMAN with annotator's user_id (unit) **[BE-only]**
- [x] Annotation comment maps to MLflow feedback rationale (unit) **[BE-only]**
- [x] Legacy single-rating format loads correctly alongside multi-rating format (unit) **[BE-only]**

### Tests Without Requirement Links

These tests are tagged with the spec but don't link to specific requirements:

- `tests/unit/routers/test_annotation_crud.py` (test_upsert_creates_new_annotation) [unit]
- `tests/unit/routers/test_participant_notes.py` (test_create_discovery_note) [unit]
- `tests/unit/routers/test_participant_notes.py` (test_create_annotation_note) [unit]
- `tests/unit/routers/test_participant_notes.py` (test_create_note_defaults_to_discovery_phase) [unit]
- `tests/unit/routers/test_participant_notes.py` (test_create_note_without_trace_id) [unit]
- `tests/unit/routers/test_participant_notes.py` (test_create_note_missing_workshop_returns_404) [unit]
- `tests/unit/routers/test_participant_notes.py` (test_create_note_service_error_returns_500) [unit]
- `tests/unit/routers/test_participant_notes.py` (test_get_all_notes) [unit]
- `tests/unit/routers/test_participant_notes.py` (test_get_notes_filtered_by_user) [unit]
- `tests/unit/routers/test_participant_notes.py` (test_get_notes_filtered_by_discovery_phase) [unit]
- `tests/unit/routers/test_participant_notes.py` (test_get_notes_filtered_by_annotation_phase) [unit]
- `tests/unit/routers/test_participant_notes.py` (test_get_notes_filtered_by_user_and_phase) [unit]
- `tests/unit/routers/test_participant_notes.py` (test_get_notes_missing_workshop_returns_404) [unit]
- `tests/unit/routers/test_participant_notes.py` (test_delete_note_success) [unit]
- `tests/unit/routers/test_participant_notes.py` (test_delete_nonexistent_note_returns_404) [unit]
- `tests/unit/routers/test_participant_notes.py` (test_delete_note_missing_workshop_returns_404) [unit]
- `tests/unit/routers/test_participant_notes.py` (test_multiple_notes_same_user_same_trace_append) [unit]
- `tests/unit/routers/test_participant_notes.py` (test_notes_from_both_phases_coexist) [unit]
- `tests/unit/routers/test_participant_notes.py` (test_toggle_participant_notes_enables) [unit]
- `tests/unit/routers/test_participant_notes.py` (test_toggle_participant_notes_disables) [unit]
- `tests/unit/routers/test_participant_notes.py` (test_toggle_missing_workshop_returns_404) [unit]
- `tests/unit/routers/test_participant_notes.py` (test_multiple_annotators_notes_during_annotation) [unit]
- `tests/unit/routers/test_participant_notes.py` (test_participant_note_create_model_defaults) [unit]
- `tests/unit/routers/test_participant_notes.py` (test_participant_note_create_model_with_annotation_phase) [unit]
- `tests/unit/routers/test_participant_notes.py` (test_participant_note_model_serialization) [unit]
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
- `client/tests/e2e/annotation-mlflow-feedback.spec.ts` (file-level) [e2e-real]
- `client/tests/e2e/annotation-flow.spec.ts` (file-level) [e2e-real]
- `client/tests/e2e/annotation-last-trace.spec.ts` (file-level) [e2e-real]

## ASSISTED_FACILITATION_SPEC

**Coverage**: 7/7 requirements (100%)

### Covered Requirements

- [x] Findings are classified in real-time as participants submit them (e2e-real, unit)
- [x] Facilitators see per-trace structured view with category breakdown (e2e-real, unit)
- [x] Facilitators can generate targeted questions that broadcast to all participants (e2e-real, unit)
- [x] Disagreements are auto-detected and surfaced (e2e-real, unit)
- [x] Participants see only fuzzy progress (no category bias) (e2e-real, unit)
- [x] Findings can be promoted to draft rubric staging area (e2e-real, unit)
- [x] Thresholds are configurable per category per trace (e2e-real, unit)

### Tests Without Requirement Links

These tests are tagged with the spec but don't link to specific requirements:

- `tests/unit/services/test_discovery_dspy_mlflow_autolog.py` (test_dspy_mlflow_autolog_is_noop_when_env_var_unset) [unit]
- `tests/unit/services/test_discovery_dspy_mlflow_autolog.py` (test_dspy_mlflow_autolog_uses_experiment_id_from_env) [unit]
- `client/tests/e2e/assisted-facilitation.spec.ts` (file-level) [e2e-real]
- `client/tests/e2e/assisted-facilitation-rubric-promotion.spec.ts` (file-level) [e2e-real]
- `client/tests/e2e/assisted-facilitation-classification.spec.ts` (file-level) [e2e-real]
- `client/tests/e2e/assisted-facilitation-discovery.spec.ts` (file-level) [e2e-real]
- `client/tests/e2e/assisted-facilitation-dashboard.spec.ts` (file-level) [e2e-real]
- `client/tests/e2e/example-new-infrastructure.spec.ts` (file-level) [e2e-real]
- `client/tests/e2e/example-new-infrastructure.spec.ts` (file-level) [e2e-real]
- `client/tests/e2e/example-new-infrastructure.spec.ts` (file-level) [e2e-real]

## AUTHENTICATION_SPEC

**Coverage**: 5/28 requirements (17%)

### Uncovered Requirements

- [ ] Slow network: Loading indicator shown until ready
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

- :warning: No "permission denied" errors on normal login (unit)
- :warning: No page refresh required after login (unit)
- :warning: Permission API failure: User can log in with defaults (unit)
- :warning: Error recovery: Errors cleared on new login attempt (unit)

### Covered Requirements

- [x] No "permission denied" errors on normal login (unit) **[BE-only]**
- [x] No page refresh required after login (unit) **[BE-only]**
- [x] Permission API failure: User can log in with defaults (unit) **[BE-only]**
- [x] Rapid navigation: Components wait for `isLoading = false` (unit)
- [x] Error recovery: Errors cleared on new login attempt (unit) **[BE-only]**

### Tests Without Requirement Links

These tests are tagged with the spec but don't link to specific requirements:

- `tests/unit/routers/test_auth_edge_cases.py` (test_permission_api_failure_returns_defaults_when_user_not_found) [unit]
- `tests/unit/routers/test_auth_edge_cases.py` (test_permission_api_returns_role_based_defaults_for_valid_user) [unit]
- `tests/unit/test_db_config.py` (test_get_password_rejects_unset_or_empty_endpoint[None]) [unit]
- `tests/unit/test_db_config.py` (test_get_password_rejects_unset_or_empty_endpoint[]) [unit]
- `tests/unit/test_db_config.py` (test_postgresql_engine_raises_without_endpoint_name) [unit]
- `client/tests/e2e/facilitator-create-workshop.spec.ts` (file-level) [e2e-mocked]
- `client/tests/e2e/authentication.spec.ts` (file-level) [e2e-mocked]
- `client/src/context/UserContext.test.tsx` (file-level) [unit]

## BUILD_AND_DEPLOY_SPEC

**Coverage**: 13/16 requirements (81%)

### Uncovered Requirements

- [ ] Production build completes without errors
- [ ] Console statements removed in production
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
- :warning: Server starts and serves frontend (unit)
- :warning: API endpoints respond correctly (unit)
- :warning: Database connection established (unit)
- :warning: Release workflow creates zip artifact (unit)
- :warning: Pre-built client included in release (unit)
- :warning: No sensitive files in artifact (unit)

### Covered Requirements

- [x] Assets minified and hashed (unit) **[BE-only]**
- [x] Build directory contains all required files (unit) **[BE-only]**
- [x] `just db-bootstrap` creates database if missing (unit) **[BE-only]**
- [x] Migrations apply without errors (unit) **[BE-only]**
- [x] Batch mode works for SQLite ALTER TABLE (unit) **[BE-only]**
- [x] File lock prevents race conditions with multiple workers (unit) **[BE-only]**
- [x] Pending Alembic migrations are applied automatically before workers accept traffic (unit) **[BE-only]**
- [x] Server starts and serves frontend (unit) **[BE-only]**
- [x] API endpoints respond correctly (unit) **[BE-only]**
- [x] Database connection established (unit) **[BE-only]**
- [x] Release workflow creates zip artifact (unit) **[BE-only]**
- [x] Pre-built client included in release (unit) **[BE-only]**
- [x] No sensitive files in artifact (unit) **[BE-only]**

### Tests Without Requirement Links

These tests are tagged with the spec but don't link to specific requirements:

- `tests/unit/test_build_deploy.py` (test_migration_schema_grant_is_best_effort) [unit]
- `tests/unit/test_build_deploy.py` (test_migration_version_table_is_created_wide_enough) [unit]
- `tests/unit/test_build_deploy.py` (test_boolean_migration_defaults_are_postgres_safe) [unit]
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

**Coverage**: 0/15 requirements (0%)

### Uncovered Requirements

- [ ] Users can configure custom LLM provider via UI
- [ ] Base URL, API key, and model name are captured
- [ ] API key is stored securely in memory (not database)
- [ ] Configuration persists across page refreshes (except API key which requires re-entry after 24h)
- [ ] "Test Connection" button verifies endpoint is reachable
- [ ] Clear error messages for common failures (auth, timeout, invalid URL)
- [ ] Response time is displayed on success
- [ ] When custom provider is enabled, judge evaluation uses the custom endpoint
- [ ] `proxy_url` parameter is correctly passed to MLflow
- [ ] Evaluation results are identical in format to Databricks FMAPI results
- [ ] Errors from custom provider are properly surfaced to UI
- [ ] Custom provider option appears in model selector when configured
- [ ] Clear indication of which provider is being used
- [ ] Easy to switch between Databricks and custom provider
- [ ] Configuration can be updated without losing other workshop data

### Tests Without Requirement Links

These tests are tagged with the spec but don't link to specific requirements:

- `tests/unit/routers/test_custom_llm_provider_router.py` (test_get_custom_llm_provider_not_configured) [unit]
- `tests/unit/routers/test_custom_llm_provider_router.py` (test_get_custom_llm_provider_configured) [unit]
- `tests/unit/routers/test_custom_llm_provider_router.py` (test_create_custom_llm_provider) [unit]
- `tests/unit/routers/test_custom_llm_provider_router.py` (test_delete_custom_llm_provider) [unit]
- `tests/unit/routers/test_custom_llm_provider_router.py` (test_test_custom_llm_provider_success) [unit]
- `tests/unit/routers/test_custom_llm_provider_router.py` (test_test_custom_llm_provider_auth_failure) [unit]
- `tests/unit/routers/test_custom_llm_provider_router.py` (test_test_custom_llm_provider_no_config) [unit]
- `tests/unit/routers/test_custom_llm_provider_router.py` (test_test_custom_llm_provider_no_api_key) [unit]
- `tests/unit/services/test_judge_custom_provider.py` (test_custom_provider_sets_proxy_url_in_mlflow_configuration) [unit]
- `tests/unit/services/test_judge_custom_provider.py` (test_build_chat_completions_url_with_v1_suffix) [unit]
- `tests/unit/services/test_judge_custom_provider.py` (test_build_chat_completions_url_already_has_suffix) [unit]
- `tests/unit/services/test_judge_custom_provider.py` (test_build_chat_completions_url_strips_trailing_slash) [unit]
- `tests/unit/services/test_judge_custom_provider.py` (test_custom_provider_api_key_stored_with_correct_key_format) [unit]

## DATASETS_SPEC

**Coverage**: 7/9 requirements (77%)

### Uncovered Requirements

- [ ] Datasets can be created with arbitrary trace lists
- [ ] Dataset lineage tracked (source datasets, operations)

### Backend-Only Requirements (no frontend tests)

These requirements are covered by backend tests only. UI regressions won't be caught:

- :warning: Union operation combines traces from multiple datasets (unit)
- :warning: Subtract operation removes specified traces (unit)
- :warning: Same user sees same order for same dataset (deterministic) (unit)
- :warning: Different users see different orders (per-user randomization) (unit)
- :warning: Adding traces preserves existing order (incremental) (unit)
- :warning: New round triggers fresh randomization (unit)
- :warning: Facilitators see chronological order (no randomization) (unit)

### Covered Requirements

- [x] Union operation combines traces from multiple datasets (unit) **[BE-only]**
- [x] Subtract operation removes specified traces (unit) **[BE-only]**
- [x] Same user sees same order for same dataset (deterministic) (unit) **[BE-only]**
- [x] Different users see different orders (per-user randomization) (unit) **[BE-only]**
- [x] Adding traces preserves existing order (incremental) (unit) **[BE-only]**
- [x] New round triggers fresh randomization (unit) **[BE-only]**
- [x] Facilitators see chronological order (no randomization) (unit) **[BE-only]**

### Tests Without Requirement Links

These tests are tagged with the spec but don't link to specific requirements:

- `tests/unit/services/test_dataset_operations.py` (test_union_preserves_first_occurrence_order) [unit]
- `tests/unit/services/test_dataset_operations.py` (test_union_three_datasets) [unit]
- `tests/unit/services/test_dataset_operations.py` (test_union_with_empty_dataset) [unit]
- `tests/unit/services/test_dataset_operations.py` (test_union_identical_datasets) [unit]
- `tests/unit/services/test_dataset_operations.py` (test_union_result_has_no_duplicates) [unit]
- `tests/unit/services/test_dataset_operations.py` (test_subtract_empty_removal_set) [unit]
- `tests/unit/services/test_dataset_operations.py` (test_subtract_all_traces) [unit]
- `tests/unit/services/test_dataset_operations.py` (test_subtract_nonexistent_traces_ignored) [unit]
- `tests/unit/services/test_dataset_operations.py` (test_subtract_single_trace) [unit]
- `tests/unit/services/test_dataset_operations.py` (test_subtract_result_has_correct_length) [unit]
- `client/tests/e2e/dataset-operations.spec.ts` (file-level) [e2e-real]
- `client/src/utils/traceUtils.test.ts` (file-level) [unit]
- `client/src/utils/traceUtils.test.ts` (file-level) [unit]

## DESIGN_SYSTEM_SPEC

**Coverage**: 0/7 requirements (0%)

### Uncovered Requirements

- [ ] Primary purple consistent across all components
- [ ] Dark mode fully functional
- [ ] All text meets WCAG AA contrast
- [ ] Focus indicators visible
- [ ] No hardcoded colors in components
- [ ] Badges use secondary color scheme
- [ ] Buttons use appropriate variants

### Tests Without Requirement Links

These tests are tagged with the spec but don't link to specific requirements:

- `client/tests/e2e/design-system.spec.ts` (file-level) [e2e-mocked]
- `client/src/test/design-system.test.ts` (file-level) [unit]
- `client/src/test/design-system.test.ts` (file-level) [unit]
- `client/src/lib/utils.test.ts` (file-level) [unit]
- `client/src/lib/utils.test.ts` (file-level) [unit]

## DISCOVERY_SPEC

**Coverage**: 61/72 requirements (84%)

### Uncovered Requirements

- [ ] Facilitator can switch Discovery workspace between `analysis` mode and `social` mode
- [ ] In social mode, users can create trace-level comments
- [ ] In social mode, users can create milestone-level comments
- [ ] Users can reply to comments in-thread
- [ ] Thread updates appear live in the workspace while participants collaborate
- [ ] Facilitator `@assistant` tool-availability questions for a milestone return grounded context as a thread reply
- [ ] `@agent` run lifecycle is visible (`running`, `completed`, `failed`, `timeout`) with final persisted reply
- [ ] Non-facilitator mentions do not trigger assistant/agent execution (treated as plain text mentions)
- [ ] Clear progress indication (X of Y traces completed)
- [ ] Draft rubric sidebar is always visible while browsing traces
- [ ] Social mode provides a modern live collaboration experience with streamed in-thread updates for assistant/agent responses

### Backend-Only Requirements (no frontend tests)

These requirements are covered by backend tests only. UI regressions won't be caught:

- :warning: Facilitator can start Discovery phase with configurable trace limit (unit)
- :warning: Participants view traces and provide GOOD/BAD + comment (unit)
- :warning: AI generates 3 follow-up questions per trace based on feedback (unit)
- :warning: Questions build progressively on prior answers (unit)
- :warning: All 3 questions required before moving to next trace (unit)
- :warning: Error handling with retry for LLM failures (unit)
- :warning: Completion status shows % of participants finished (integration, unit)
- :warning: Facilitator can trigger analysis at any time (even partial feedback) (unit)
- :warning: System aggregates feedback by trace (unit)
- :warning: Disagreements detected at 3 priority levels (deterministic, no LLM) (unit)
- :warning: LLM distills evaluation criteria with evidence from trace IDs (unit)
- :warning: LLM analyzes disagreements with follow-up questions and suggestions (unit)
- :warning: Analysis record stores which template was used (unit)
- :warning: Each analysis run creates a new record (history preserved) (unit)
- :warning: Re-runnable — new analysis as more feedback comes in, prior analyses retained (unit)
- :warning: Facilitator can promote distilled criteria to draft rubric (unit)
- :warning: Facilitator can promote disagreement insights to draft rubric (unit)
- :warning: Facilitator can promote raw participant feedback to draft rubric (unit)
- :warning: Facilitator can manually add draft rubric items (unit)
- :warning: Draft rubric items editable and removable (unit)
- :warning: "Suggest Groups" returns LLM proposal without persisting (unit)
- :warning: Facilitator can review, adjust, and apply group proposal (unit)
- :warning: Manual grouping: create groups, name them, move items between groups (unit)
- :warning: Each group maps to one rubric question (group name = question title) (unit)
- :warning: Draft rubric items available during Rubric Creation phase (unit)
- :warning: Source traceability maintained (which traces support each item) (unit)
- :warning: Users can upvote/downvote comments (single vote per user per comment with toggle behavior) (unit)
- :warning: Facilitator `@assistant summarize this thread` returns a grounded summary as a thread reply (unit)
- :warning: Facilitator `@agent` starts a bounded tool-calling run and posts streamed partial output in the thread (unit)
- :warning: One feedback record per (workshop, trace, user) — upsert behavior (integration, unit)
- :warning: Q&A pairs appended in order to JSON array (integration, unit)
- :warning: Multiple analysis records per workshop allowed (history preserved) (unit)
- :warning: Draft rubric items track promotion source and promoter (unit)
- :warning: Fallback question if LLM unavailable after retries (unit)
- :warning: Form validation prevents empty submissions (unit)
- :warning: When follow-up questions are disabled, participant flow is GOOD/BAD + comment only (unit)
- :warning: Trace-specific analysis findings appear on the trace card, pinned above feedback (collapsible) (unit)
- :warning: Promote action visibly moves items from trace feed/summary into the sidebar (unit)
- :warning: Draft rubric items show trace reference badges (interactive: hover for preview, click to scroll) (unit)
- :warning: "Create Rubric →" in sidebar transitions to rubric creation with groups pre-populated as criteria (unit)

### Covered Requirements

- [x] Facilitator can start Discovery phase with configurable trace limit (unit) **[BE-only]**
- [x] Participants view traces and provide GOOD/BAD + comment (unit) **[BE-only]**
- [x] Facilitator can select LLM model for follow-up question generation in Discovery dashboard (integration, unit)
- [x] AI generates 3 follow-up questions per trace based on feedback (unit) **[BE-only]**
- [x] Questions build progressively on prior answers (unit) **[BE-only]**
- [x] All 3 questions required before moving to next trace (unit) **[BE-only]**
- [x] Previous Q&A visible while answering new questions (unit)
- [x] Loading spinner during LLM generation (1-3s) (unit)
- [x] Error handling with retry for LLM failures (unit) **[BE-only]**
- [x] Feedback saved incrementally (no data loss on failure) (e2e-real, unit)
- [x] Completion status shows % of participants finished (integration, unit) **[BE-only]**
- [x] Facilitator can view participant feedback details (label, comment, follow-up Q&A) (integration, unit)
- [x] Facilitator can trigger analysis at any time (even partial feedback) (unit) **[BE-only]**
- [x] Facilitator selects analysis template (Evaluation Criteria or Themes & Patterns) before running (unit)
- [x] System aggregates feedback by trace (unit) **[BE-only]**
- [x] Disagreements detected at 3 priority levels (deterministic, no LLM) (unit) **[BE-only]**
- [x] LLM distills evaluation criteria with evidence from trace IDs (unit) **[BE-only]**
- [x] LLM analyzes disagreements with follow-up questions and suggestions (unit) **[BE-only]**
- [x] Analysis record stores which template was used (unit) **[BE-only]**
- [x] Each analysis run creates a new record (history preserved) (unit) **[BE-only]**
- [x] Re-runnable — new analysis as more feedback comes in, prior analyses retained (unit) **[BE-only]**
- [x] Warning if < 2 participants (not an error) (unit)
- [x] Data freshness banner (participant count, last run timestamp) (unit)
- [x] Results organized by priority (HIGH → MEDIUM → LOWER) (unit)
- [x] Facilitator can promote distilled criteria to draft rubric (unit) **[BE-only]**
- [x] Facilitator can promote disagreement insights to draft rubric (unit) **[BE-only]**
- [x] Facilitator can promote raw participant feedback to draft rubric (unit) **[BE-only]**
- [x] Facilitator can manually add draft rubric items (unit) **[BE-only]**
- [x] Draft rubric items editable and removable (unit) **[BE-only]**
- [x] "Suggest Groups" returns LLM proposal without persisting (unit) **[BE-only]**
- [x] Facilitator can review, adjust, and apply group proposal (unit) **[BE-only]**
- [x] Manual grouping: create groups, name them, move items between groups (unit) **[BE-only]**
- [x] Each group maps to one rubric question (group name = question title) (unit) **[BE-only]**
- [x] Draft rubric items available during Rubric Creation phase (unit) **[BE-only]**
- [x] Source traceability maintained (which traces support each item) (unit) **[BE-only]**
- [x] Users can upvote/downvote comments (single vote per user per comment with toggle behavior) (unit) **[BE-only]**
- [x] Facilitator `@assistant summarize this thread` returns a grounded summary as a thread reply (unit) **[BE-only]**
- [x] Facilitator `@agent` starts a bounded tool-calling run and posts streamed partial output in the thread (unit) **[BE-only]**
- [x] One feedback record per (workshop, trace, user) — upsert behavior (integration, unit) **[BE-only]**
- [x] Q&A pairs appended in order to JSON array (integration, unit) **[BE-only]**
- [x] Multiple analysis records per workshop allowed (history preserved) (unit) **[BE-only]**
- [x] Draft rubric items track promotion source and promoter (unit) **[BE-only]**
- [x] LLM failures show error toast with retry (unit)
- [x] Fallback question if LLM unavailable after retries (unit) **[BE-only]**
- [x] Fallback warning banner shown only to facilitators, never to participants/SMEs (unit)
- [x] Analysis shows warning (not error) if < 2 participants (unit)
- [x] Form validation prevents empty submissions (unit) **[BE-only]**
- [x] Progressive disclosure (one question at a time) (unit)
- [x] Submit buttons disabled until required fields filled (unit)
- [x] Smooth transitions between feedback states (unit)
- [x] When follow-up questions are disabled, participant flow is GOOD/BAD + comment only (unit) **[BE-only]**
- [x] Single two-panel workspace replaces multi-page flow (no FacilitatorDashboard discovery tabs, no FindingsReviewPage) (unit)
- [x] Trace feed shows actual trace content (input/output), not trace ID badges (unit)
- [x] Trace-specific analysis findings appear on the trace card, pinned above feedback (collapsible) (unit) **[BE-only]**
- [x] Cross-trace analysis findings appear in collapsible summary section above the feed (unit)
- [x] Overview bar shows stats inline + compact controls (Run Analysis, Add Traces, Pause, Model selector) (unit)
- [x] Promote action visibly moves items from trace feed/summary into the sidebar (unit) **[BE-only]**
- [x] Draft rubric items show trace reference badges (interactive: hover for preview, click to scroll) (unit) **[BE-only]**
- [x] Draft rubric items do NOT show source-type badges (Finding, Disagreement, etc.) (unit)
- [x] Disagreements color-coded by priority (red/yellow/blue) on trace cards (unit)
- [x] "Create Rubric →" in sidebar transitions to rubric creation with groups pre-populated as criteria (unit) **[BE-only]**

### Tests Without Requirement Links

These tests are tagged with the spec but don't link to specific requirements:

- `tests/unit/routers/test_discovery_feedback.py` (test_assistant_mention_creates_agent_run) [unit]
- `tests/unit/routers/test_discovery_feedback.py` (test_assistant_tool_context_mention_uses_trace_context) [unit]
- `tests/unit/routers/test_discovery_feedback.py` (test_facilitator_can_delete_comment_tree) [unit]
- `tests/unit/routers/test_discovery_feedback.py` (test_non_facilitator_cannot_delete_comment) [unit]
- `tests/unit/routers/test_discovery_feedback.py` (test_agent_run_uses_trace_context_tools) [unit]
- `tests/unit/services/test_discovery_analysis_service.py` (test_draft_items_expose_source_trace_ids_for_display) [unit]
- `tests/unit/services/test_draft_rubric_items.py` (test_ungrouped_items_each_become_question) [unit]
- `tests/unit/services/test_draft_rubric_items.py` (test_no_items_raises_400) [unit]
- `tests/unit/services/test_draft_rubric_items.py` (test_mixed_grouped_and_ungrouped) [unit]
- `client/tests/e2e/discovery-social-scroll-sync.spec.ts` (file-level) [e2e-mocked]
- `client/tests/e2e/discovery-model-selection.spec.ts` (file-level) [e2e-mocked]
- `client/tests/e2e/discovery-analysis.spec.ts` (file-level) [e2e-mocked]
- `client/tests/e2e/discovery-sidebar-visibility.spec.ts` (file-level) [e2e-mocked]
- `client/src/components/DiscoveryFeedbackView.submitDisabled.test.tsx` (file-level) [unit]
- `client/src/components/DiscoveryFeedbackView.stateTransitions.test.tsx` (file-level) [unit]
- `client/src/components/DiscoveryStartPage.modelSelector.test.tsx` (file-level) [unit]
- `client/src/components/DiscoveryFeedbackView.previousQA.test.tsx` (file-level) [unit]
- `client/src/components/DiscoveryFeedbackView.errorRetry.test.tsx` (file-level) [unit]
- `client/src/components/DiscoveryAnalysisTab.evidence.test.tsx` (file-level) [unit]
- `client/src/components/FacilitatorDashboard.feedbackDetail.test.tsx` (file-level) [unit]
- `client/src/components/DiscoveryFeedbackView.progressiveDisclosure.test.tsx` (file-level) [unit]
- `client/src/components/DraftRubricPanel.test.tsx` (file-level) [unit]
- `client/src/components/DiscoveryFeedbackView.loadingSpinner.test.tsx` (file-level) [unit]
- `client/src/components/__tests__/DiscoveryFeedbackView.fallback.test.tsx` (file-level) [unit]

## DISCOVERY_TRACE_ASSIGNMENT_SPEC

**Coverage**: 12/13 requirements (92%)

### Uncovered Requirements

- [ ] When new discovery round starts, old traces hidden (not deleted)

### Backend-Only Requirements (no frontend tests)

These requirements are covered by backend tests only. UI regressions won't be caught:

- :warning: Participants only see traces in current active discovery dataset (unit)
- :warning: Switching between discovery rounds hides/shows appropriate traces (unit)
- :warning: Phase/round context properly scoped in database (unit)
- :warning: Annotation traces randomized per (user_id, trace_set) pair (unit)
- :warning: Randomization persistent across page reloads for same trace set (unit)
- :warning: When annotation dataset changes mid-round, new traces appended (unit)
- :warning: When annotation round changes, full re-randomization applied (unit)
- :warning: Randomization context includes phase and round info (unit)
- :warning: Dataset operations (union, subtract) work correctly and maintain audit trail (unit)
- :warning: Multiple participants can see same trace with different orders (unit)
- :warning: Inter-rater reliability (IRR) can be measured (same traces, different orders) (unit)

### Covered Requirements

- [x] Participants only see traces in current active discovery dataset (unit) **[BE-only]**
- [x] Switching between discovery rounds hides/shows appropriate traces (unit) **[BE-only]**
- [x] Phase/round context properly scoped in database (unit) **[BE-only]**
- [x] Annotation traces randomized per (user_id, trace_set) pair (unit) **[BE-only]**
- [x] Randomization persistent across page reloads for same trace set (unit) **[BE-only]**
- [x] When annotation dataset changes mid-round, new traces appended (unit) **[BE-only]**
- [x] When annotation round changes, full re-randomization applied (unit) **[BE-only]**
- [x] Randomization context includes phase and round info (unit) **[BE-only]**
- [x] Dataset operations (union, subtract) work correctly and maintain audit trail (unit) **[BE-only]**
- [x] Multiple participants can see same trace with different orders (unit) **[BE-only]**
- [x] Assignment metadata properly tracks all context (unit)
- [x] Inter-rater reliability (IRR) can be measured (same traces, different orders) (unit) **[BE-only]**

### Tests Without Requirement Links

These tests are tagged with the spec but don't link to specific requirements:

- `client/tests/e2e/trace-visibility.spec.ts` (file-level) [e2e-real]
- `client/tests/e2e/discovery-invite-traces.spec.ts` (file-level) [e2e-mocked]

## JUDGE_EVALUATION_SPEC

**Coverage**: 24/25 requirements (96%)

### Uncovered Requirements

- [ ] Spinner stops when re-evaluation completes

### Backend-Only Requirements (no frontend tests)

These requirements are covered by backend tests only. UI regressions won't be caught:

- :warning: Fallback conversion handles Likert-style returns for binary (unit)
- :warning: Evaluation results persisted to database (integration, unit)
- :warning: Results reload correctly in UI (unit)
- :warning: Judge prompt auto-derived from rubric questions (unit)
- :warning: Per-question judge_type parsed from rubric (`[JUDGE_TYPE:xxx]`) (unit)
- :warning: Binary rubrics evaluated with 0/1 scale (not 1-5) (unit)
- :warning: Re-evaluate loads registered judge with aligned instructions (integration, unit)
- :warning: Uses same model as initial auto-evaluation (unit)
- :warning: Results stored against correct prompt version (integration, unit)
- :warning: Pre-align and post-align scores directly comparable (integration, unit)
- :warning: Alignment jobs run asynchronously (unit)
- :warning: MemAlign distills semantic memory (guidelines) (unit)
- :warning: Aligned judge registered to MLflow (unit)
- :warning: Metrics reported (guideline count, example count) (unit)
- :warning: Works for both Likert and Binary scales (unit)
- :warning: Krippendorff's Alpha calculated correctly (unit)
- :warning: Cohen's Kappa calculated for rater pairs (unit)
- :warning: Handles edge cases (no variation, single rater) (unit)
- :warning: Updates when new annotations added (unit)

### Covered Requirements

- [x] Likert judges return values 1-5 (unit)
- [x] Binary judges return values 0 or 1 (unit)
- [x] Fallback conversion handles Likert-style returns for binary (unit) **[BE-only]**
- [x] Evaluation results persisted to database (integration, unit) **[BE-only]**
- [x] Results reload correctly in UI (unit) **[BE-only]**
- [x] Auto-evaluation runs in background when annotation phase starts (e2e-real, unit)
- [x] Judge prompt auto-derived from rubric questions (unit) **[BE-only]**
- [x] Per-question judge_type parsed from rubric (`[JUDGE_TYPE:xxx]`) (unit) **[BE-only]**
- [x] Binary rubrics evaluated with 0/1 scale (not 1-5) (unit) **[BE-only]**
- [x] Auto-evaluation model stored for re-evaluation consistency (e2e-real)
- [x] Results appear in Judge Tuning page (e2e-real)
- [x] Re-evaluate loads registered judge with aligned instructions (integration, unit) **[BE-only]**
- [x] Uses same model as initial auto-evaluation (unit) **[BE-only]**
- [x] Results stored against correct prompt version (integration, unit) **[BE-only]**
- [x] Pre-align and post-align scores directly comparable (integration, unit) **[BE-only]**
- [x] Alignment jobs run asynchronously (unit) **[BE-only]**
- [x] MemAlign distills semantic memory (guidelines) (unit) **[BE-only]**
- [x] Aligned judge registered to MLflow (unit) **[BE-only]**
- [x] Metrics reported (guideline count, example count) (unit) **[BE-only]**
- [x] Works for both Likert and Binary scales (unit) **[BE-only]**
- [x] Krippendorff's Alpha calculated correctly (unit) **[BE-only]**
- [x] Cohen's Kappa calculated for rater pairs (unit) **[BE-only]**
- [x] Handles edge cases (no variation, single rater) (unit) **[BE-only]**
- [x] Updates when new annotations added (unit) **[BE-only]**

### Tests Without Requirement Links

These tests are tagged with the spec but don't link to specific requirements:

- `tests/integration/test_judge_evaluation_storage.py` (test_promote_finding_returns_500_on_db_error) [integration]
- `tests/integration/test_judge_evaluation_storage.py` (test_promote_real_finding_succeeds) [integration]
- `tests/unit/routers/test_workshops_begin_annotation.py` (test_begin_annotation_requires_rubric) [unit]
- `tests/unit/routers/test_workshops_re_evaluate.py` (test_re_evaluate_tags_traces_before_evaluation) [unit]
- `tests/unit/routers/test_workshops_re_evaluate.py` (test_re_evaluate_tags_traces_fallback_when_no_active_annotation_ids) [unit]
- `tests/unit/services/test_alignment_service.py` (test_likert_agreement_metric_from_store_is_one_when_equal) [unit]
- `tests/unit/services/test_cohens_kappa.py` (test_interpret_cohens_kappa_bucket_edges) [unit]
- `tests/unit/services/test_cohens_kappa.py` (test_is_cohens_kappa_acceptable_default_threshold) [unit]
- `tests/unit/services/test_discovery_dspy_litellm_interop.py` (test_get_sdk_token_normalizes_env_host_for_m2m_token_url) [unit]
- `tests/unit/services/test_evaluation_tag_overwrite.py` (test_search_tagged_traces_uses_dedicated_align_key) [unit]
- `tests/unit/services/test_evaluation_tag_overwrite.py` (test_run_evaluation_yields_error_when_no_eval_tagged_traces) [unit]
- `tests/unit/services/test_irr_utils.py` (test_format_irr_result_rounding_and_ready_flag) [unit]
- `client/tests/e2e/judge-evaluation.spec.ts` (file-level) [e2e-real]
- `client/tests/e2e/evaluation-tagging.spec.ts` (file-level) [e2e-real]
- `client/tests/e2e/evaluation-tagging.spec.ts` (file-level) [e2e-real]
- `client/tests/e2e/evaluation-tagging.spec.ts` (file-level) [e2e-real]
- `client/src/components/JudgeTypeSelector.test.tsx` (file-level) [unit]
- `client/src/components/JudgeTypeSelector.test.tsx` (file-level) [unit]
- `client/src/components/JudgeTypeSelector.test.tsx` (file-level) [unit]

## PROJECT_SETUP_SPEC

**Coverage**: 6/26 requirements (23%)

### Uncovered Requirements

- [ ] Setup persists the project name, agent/app description, facilitator id, and Databricks UC trace table path
- [ ] `/project/setup` renders a setup form backed by shared form, input, button, card, alert, and badge atoms
- [ ] Project name, agent/app description, facilitator identity, and Databricks UC trace table path are required before submission
- [ ] Required setup fields show client-side validation before submission
- [ ] SMEs, participants, and users without `can_manage_workshop` cannot access the setup form
- [ ] Successful setup submission navigates to the facilitator root workspace with setup job progress available
- [ ] UI implementation follows the wiring architecture diagram and keeps setup entry, submission, and progress concerns separate
- [ ] After setup completes, facilitators and users with `can_manage_workshop` can reach `/project/setup` from the facilitator root workspace
- [ ] After setup completes, `/project/setup` loads server project state instead of creating a new project by default
- [ ] The setup form is synced with server project state before and after setup completes
- [ ] The app shell project setup link navigates to the same server-synced setup form
- [ ] Facilitators and users with `can_manage_workshop` can update project name and agent/app description after setup completes
- [ ] Facilitators and users with `can_manage_workshop` can update Databricks UC trace table path after setup completes
- [ ] Changing the Databricks UC trace table path persists the new trace provider config and exposes setup refresh or validation status
- [ ] The setup form exposes participant/SME invitation controls from the same visual surface
- [ ] SMEs, participants, and users without `can_manage_workshop` cannot update project settings or invite SMEs
- [ ] Setup enqueue failures are visible as recoverable failed state rather than a ready project
- [ ] Failed or enqueue_failed setup states keep the user out of the ready workspace path and present recoverable copy
- [ ] Setup orchestration uses the app task queue, not Databricks Jobs, for ordered setup pipeline execution
- [ ] Expensive parallelizable setup steps may record delegated Databricks/Lakeflow run ids without becoming the top-level setup queue

### Backend-Only Requirements (no frontend tests)

These requirements are covered by backend tests only. UI regressions won't be caught:

- :warning: Submitting `/api/project/setup` enqueues a setup pipeline worker job (unit)
- :warning: The facilitator root workspace can query setup progress and display pending or running setup state (unit)

### Covered Requirements

- [x] Submitting `/api/project/setup` enqueues a setup pipeline worker job (unit) **[BE-only]**
- [x] `POST /api/project/setup` returns `project_id` and `setup_job_id` (unit)
- [x] Authenticated facilitators and users with `can_manage_workshop` can access `/project/setup` when no project has completed setup (unit)
- [x] The app shell navigation bar exposes a project setup link for facilitators and users with `can_manage_workshop` (unit)
- [x] The facilitator root workspace can query setup progress and display pending or running setup state (unit) **[BE-only]**
- [x] Pending/running setup states render a facilitator root workspace progress card with current step and message (unit)

### Tests Without Requirement Links

These tests are tagged with the spec but don't link to specific requirements:

- `tests/unit/features/project_setup/test_project_setup_service.py` (test_project_setup_service_completes_dev_queue_fallback) [unit]
- `client/tests/e2e/project-setup-settings.spec.ts` (file-level) [e2e-mocked]

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
- :warning: Only facilitators can advance workshop phases (unit)
- :warning: Phase advancement validates prerequisites before transitioning (unit)
- :warning: Phase advancement returns 400 if prerequisites not met (unit)
- :warning: Facilitators authenticate via YAML config (preconfigured credentials) (unit)
- :warning: SMEs and participants authenticate via database credentials (unit)
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
- [x] Only facilitators can advance workshop phases (unit) **[BE-only]**
- [x] Phase advancement validates prerequisites before transitioning (unit) **[BE-only]**
- [x] Phase advancement returns 400 if prerequisites not met (unit) **[BE-only]**
- [x] Facilitators authenticate via YAML config (preconfigured credentials) (unit) **[BE-only]**
- [x] SMEs and participants authenticate via database credentials (unit) **[BE-only]**
- [x] Login response includes is_preconfigured_facilitator flag for facilitator logins (unit) **[BE-only]**

## RUBRIC_SPEC

**Coverage**: 25/25 requirements (100%)

### Backend-Only Requirements (no frontend tests)

These requirements are covered by backend tests only. UI regressions won't be caught:

- :warning: Questions with multi-line descriptions parse correctly (unit)
- :warning: Delimiter never appears in user input (by design) (unit)
- :warning: Parsed questions have stable UUIDs within session (unit)
- :warning: Empty/whitespace-only parts filtered out (unit)
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
- :warning: Invalid judge type in suggestions defaults to likert (unit)
- :warning: Facilitator can accept, reject, or edit suggestions before adding to rubric (unit)

### Covered Requirements

- [x] Questions with multi-line descriptions parse correctly (unit) **[BE-only]**
- [x] Delimiter never appears in user input (by design) (unit) **[BE-only]**
- [x] Frontend and backend use same delimiter constant (unit)
- [x] Per-question judge_type parsed from `[JUDGE_TYPE:xxx]` format (e2e-real, unit)
- [x] Parsed questions have stable UUIDs within session (unit) **[BE-only]**
- [x] Empty/whitespace-only parts filtered out (unit) **[BE-only]**
- [x] Likert scale shows 1-5 rating options (e2e-real)
- [x] Binary scale shows Pass/Fail buttons (not star ratings) (e2e-real)
- [x] Binary feedback logged as 0/1 to MLflow (not 3) (e2e-real)
- [x] Mixed rubrics support different scales per question (e2e-real, unit)
- [x] Facilitator can create a rubric question with title and description (e2e-mocked, unit)
- [x] Facilitator can edit an existing rubric question (unit) **[BE-only]**
- [x] Facilitator can delete a rubric question (unit) **[BE-only]**
- [x] Only one rubric exists per workshop (upsert semantics) (unit) **[BE-only]**
- [x] Rubric persists and is retrievable via GET after creation (e2e-real)
- [x] Rubric required before advancing to annotation phase (unit) **[BE-only]**
- [x] No phase restriction on rubric CRUD (unit) **[BE-only]**
- [x] Question IDs re-indexed sequentially after deletion (unit) **[BE-only]**
- [x] Annotation data preserved when rubric questions are deleted (unit) **[BE-only]**
- [x] Judge name auto-derived from first rubric question title (unit) **[BE-only]**
- [x] MLflow re-sync triggered on rubric create/update (best-effort) (unit) **[BE-only]**
- [x] AI suggestions generated from discovery findings and participant notes (unit) **[BE-only]**
- [x] Suggestions validated: title >= 3 chars, description >= 10 chars (unit) **[BE-only]**
- [x] Invalid judge type in suggestions defaults to likert (unit) **[BE-only]**
- [x] Facilitator can accept, reject, or edit suggestions before adding to rubric (unit) **[BE-only]**

### Tests Without Requirement Links

These tests are tagged with the spec but don't link to specific requirements:

- `client/src/utils/rubricUtils.test.ts` (file-level) [unit]

## TESTING_SPEC

**Coverage**: 0/30 requirements (0%)

### Uncovered Requirements

- [ ] `tests/integration/conftest.py` provides real-DB fixtures with transaction rollback isolation
- [ ] Integration tests run against SQLite (default) and Postgres (via testcontainers)
- [ ] `just test-integration` recipe exists and passes
- [ ] Workshop CRUD tested end-to-end through HTTP → DB → response
- [ ] Trace ingestion tested: bulk upload, retrieval, metadata persistence
- [ ] Phase transition prerequisites enforced: no discovery without traces, no annotation without rubric
- [ ] Annotation upsert semantics verified: same user+trace updates (not duplicates), different users create separate records
- [ ] Discovery finding upsert semantics verified at DB level
- [ ] All integration tests tagged with `@pytest.mark.integration` and `@pytest.mark.spec()`
- [ ] External services (MLflow, Databricks) mocked — only database is real
- [ ] Connection resilience tested (Postgres-only): pool reset disposes + refreshes OAuth, `get_db()` retries with backoff, stale connections detected via `pool_pre_ping`
- [ ] Tests are hermetic: no shared state, runnable in any order
- [ ] Contract shapes documented for all 5 MLflow domains (trace ops, feedback, evaluation, alignment, experiment management)
- [ ] Mock shape tests verify test mocks match real MLflow response structures
- [ ] Call-site tests verify services pass correct parameter types to MLflow methods
- [ ] Error classification tested: retryable vs non-retryable errors handled correctly
- [ ] Feedback value types validated: binary (0.0/1.0 float), likert (1.0-5.0 float)
- [ ] Assessment limit (50 per trace) handling tested
- [ ] Contract tests tagged with `@pytest.mark.spec("TESTING_SPEC")`
- [ ] Server unit tests pass with >20% coverage
- [ ] Client unit tests pass with >20% coverage
- [ ] Integration tests pass against real database (SQLite + Postgres)
- [ ] Contract tests verify MLflow integration boundaries
- [ ] E2E tests pass for critical flows
- [ ] Tests run in CI on every PR
- [ ] Coverage reports generated and accessible
- [ ] No flaky tests (consistent pass/fail)
- [ ] Test isolation (no shared state between tests)
- [ ] `just test-integration` recipe works
- [ ] `just test-contract` recipe works

### Tests Without Requirement Links

These tests are tagged with the spec but don't link to specific requirements:

- `tests/contract/test_mlflow_contracts.py` (test_trace_info_has_required_fields) [unit]
- `tests/contract/test_mlflow_contracts.py` (test_trace_data_has_required_fields) [unit]
- `tests/contract/test_mlflow_contracts.py` (test_span_has_required_fields) [unit]
- `tests/contract/test_mlflow_contracts.py` (test_assessment_has_required_fields) [unit]
- `tests/contract/test_mlflow_contracts.py` (test_assessment_source_has_required_fields) [unit]
- `tests/contract/test_mlflow_contracts.py` (test_experiment_has_required_fields) [unit]
- `tests/contract/test_mlflow_contracts.py` (test_assessment_limit_not_retried) [unit]
- `tests/contract/test_mlflow_contracts.py` (test_not_found_not_retried) [unit]
- `tests/contract/test_mlflow_contracts.py` (test_404_error_not_retried) [unit]
- `tests/contract/test_mlflow_contracts.py` (test_unauthorized_not_retried) [unit]
- `tests/contract/test_mlflow_contracts.py` (test_transient_error_retried) [unit]
- `tests/contract/test_mlflow_contracts.py` (test_retry_succeeds_on_second_attempt) [unit]
- `tests/contract/test_mlflow_contracts.py` (test_exponential_backoff_delays) [unit]
- `tests/contract/test_mlflow_contracts.py` (test_binary_values_are_float) [unit]
- `tests/contract/test_mlflow_contracts.py` (test_likert_values_in_range) [unit]
- `tests/contract/test_mlflow_contracts.py` (test_rating_normalization) [unit]
- `tests/contract/test_mlflow_contracts.py` (test_log_feedback_parameter_types) [unit]
- `tests/contract/test_mlflow_contracts.py` (test_log_feedback_ai_source_format) [unit]
- `tests/contract/test_mlflow_contracts.py` (test_retry_wrapper_passes_through_return_value) [unit]
- `tests/contract/test_mlflow_contracts.py` (test_set_trace_tag_receives_strings) [unit]
- `tests/contract/test_mlflow_contracts.py` (test_search_traces_parameter_types) [unit]
- `tests/contract/test_mlflow_contracts.py` (test_assessment_limit_error_returns_none) [unit]
- `tests/contract/test_mlflow_contracts.py` (test_dedup_check_counts_existing_assessments) [unit]
- `tests/integration/test_annotation_submission.py` (test_submit_annotation) [integration]
- `tests/integration/test_annotation_submission.py` (test_annotation_upsert_same_user_same_trace) [integration]
- `tests/integration/test_annotation_submission.py` (test_annotation_different_users_create_separate_records) [integration]
- `tests/integration/test_annotation_submission.py` (test_annotation_with_multi_ratings) [integration]
- `tests/integration/test_annotation_submission.py` (test_get_annotations_filtered_by_user) [integration]
- `tests/integration/test_connection_resilience.py` (test_disconnection_error_is_connection_error) [integration]
- `tests/integration/test_connection_resilience.py` (test_operational_error_is_connection_error) [integration]
- `tests/integration/test_connection_resilience.py` (test_generic_exception_with_connection_message) [integration]
- `tests/integration/test_connection_resilience.py` (test_generic_exception_without_connection_message) [integration]
- `tests/integration/test_connection_resilience.py` (test_known_pg_error_messages[server closed the connection unexpectedly]) [integration]
- `tests/integration/test_connection_resilience.py` (test_known_pg_error_messages[terminating connection]) [integration]
- `tests/integration/test_connection_resilience.py` (test_known_pg_error_messages[connection reset]) [integration]
- `tests/integration/test_connection_resilience.py` (test_known_pg_error_messages[ssl connection has been closed unexpectedly]) [integration]
- `tests/integration/test_connection_resilience.py` (test_known_pg_error_messages[could not connect to server]) [integration]
- `tests/integration/test_connection_resilience.py` (test_known_pg_error_messages[connection refused]) [integration]
- `tests/integration/test_connection_resilience.py` (test_known_pg_error_messages[invalid authorization]) [integration]
- `tests/integration/test_connection_resilience.py` (test_known_pg_error_messages[database is locked]) [integration]
- `tests/integration/test_connection_resilience.py` (test_pool_exhaustion_timeout_is_not_connection_error) [integration]
- `tests/integration/test_connection_resilience.py` (test_reset_disposes_engine) [integration]
- `tests/integration/test_connection_resilience.py` (test_reset_disposes_engine_for_postgres) [integration]
- `tests/integration/test_connection_resilience.py` (test_retries_on_connection_error_then_succeeds) [integration]
- `tests/integration/test_connection_resilience.py` (test_gives_up_after_max_attempts) [integration]
- `tests/integration/test_connection_resilience.py` (test_non_connection_error_raises_immediately) [integration]
- `tests/integration/test_connection_resilience.py` (test_stream_discovery_comments_has_no_db_dependency) [integration]
- `tests/integration/test_connection_resilience.py` (test_stream_discovery_agent_run_has_no_db_dependency) [integration]
- `tests/integration/test_discovery_findings.py` (test_submit_finding) [integration]
- `tests/integration/test_discovery_findings.py` (test_finding_upsert_same_user_same_trace) [integration]
- `tests/integration/test_discovery_findings.py` (test_finding_different_users_create_separate_records) [integration]
- `tests/integration/test_discovery_findings.py` (test_get_findings_filtered_by_user) [integration]
- `tests/integration/test_discovery_findings.py` (test_findings_scoped_to_workshop) [integration]
- `tests/integration/test_phase_transitions.py` (test_advance_to_discovery_requires_traces) [integration]
- `tests/integration/test_phase_transitions.py` (test_advance_to_discovery_succeeds_with_traces) [integration]
- `tests/integration/test_phase_transitions.py` (test_advance_to_discovery_wrong_phase) [integration]
- `tests/integration/test_phase_transitions.py` (test_advance_to_rubric_requires_findings) [integration]
- `tests/integration/test_phase_transitions.py` (test_advance_to_rubric_succeeds_with_findings) [integration]
- `tests/integration/test_phase_transitions.py` (test_advance_to_annotation_requires_rubric) [integration]
- `tests/integration/test_phase_transitions.py` (test_advance_to_annotation_succeeds_with_rubric) [integration]
- `tests/integration/test_phase_transitions.py` (test_advance_to_discovery_workshop_not_found) [integration]
- `tests/integration/test_trace_ingestion.py` (test_upload_traces) [integration]
- `tests/integration/test_trace_ingestion.py` (test_upload_traces_with_metadata) [integration]
- `tests/integration/test_trace_ingestion.py` (test_upload_traces_with_mlflow_fields) [integration]
- `tests/integration/test_trace_ingestion.py` (test_get_all_traces) [integration]
- `tests/integration/test_trace_ingestion.py` (test_traces_scoped_to_workshop) [integration]
- `tests/integration/test_workshop_crud.py` (test_create_workshop) [integration]
- `tests/integration/test_workshop_crud.py` (test_get_workshop) [integration]
- `tests/integration/test_workshop_crud.py` (test_get_workshop_not_found) [integration]
- `tests/integration/test_workshop_crud.py` (test_list_workshops) [integration]
- `tests/integration/test_workshop_crud.py` (test_list_workshops_filtered_by_facilitator) [integration]
- `tests/unit/test_testing_infrastructure.py` (test_mock_db_session_fixture_exists) [unit]
- `tests/unit/test_testing_infrastructure.py` (test_mock_db_session_has_rollback) [unit]
- `tests/unit/test_testing_infrastructure.py` (test_async_client_fixture_works) [unit]
- `tests/unit/test_testing_infrastructure.py` (test_override_get_db_provides_session) [unit]
- `tests/unit/test_testing_infrastructure.py` (test_conftest_has_spec_option) [unit]
- `tests/unit/test_testing_infrastructure.py` (test_conftest_has_collection_modifier) [unit]
- `tests/unit/test_testing_infrastructure.py` (test_spec_marker_filters_this_test) [unit]
- `tests/unit/test_testing_infrastructure.py` (test_e2e_workflow_exists) [unit]
- `tests/unit/test_testing_infrastructure.py` (test_workflow_runs_pytest) [unit]
- `tests/unit/test_testing_infrastructure.py` (test_workflow_runs_playwright) [unit]
- `tests/unit/test_testing_infrastructure.py` (test_workflow_installs_playwright_browsers) [unit]
- `tests/unit/test_testing_infrastructure.py` (test_workflow_triggers_on_pull_request) [unit]

## TRACE_DISPLAY_SPEC

**Coverage**: 18/18 requirements (100%)

### Backend-Only Requirements (no frontend tests)

These requirements are covered by backend tests only. UI regressions won't be caught:

- :warning: JSONPath fields are optional and clearly labeled as such (unit)
- :warning: Multiple JSONPath matches are concatenated with newlines (unit)
- :warning: System falls back to raw display when JSONPath is not configured, JSON parsing fails, JSONPath query fails, or JSONPath returns null/empty (unit)
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
- [x] JSONPath fields are optional and clearly labeled as such (unit) **[BE-only]**
- [x] Preview shows extraction results against first workshop trace (e2e-real)
- [x] TraceViewer applies JSONPath when configured (unit)
- [x] Multiple JSONPath matches are concatenated with newlines (unit) **[BE-only]**
- [x] System falls back to raw display when JSONPath is not configured, JSON parsing fails, JSONPath query fails, or JSONPath returns null/empty (unit) **[BE-only]**
- [x] Settings are persisted per workshop (e2e-real)
- [x] Facilitator can configure span attribute filter with span name, span type, attribute key, and attribute value (unit) **[BE-only]**
- [x] Filter criteria are AND-combined and first matching span wins (unit) **[BE-only]**
- [x] Attribute value input is disabled until attribute key has a value (unit)
- [x] Span filter preview shows match status and filtered inputs/outputs against first trace (e2e-real)
- [x] Span filter is applied before JSONPath extraction in TraceViewer (unit) **[BE-only]**
- [x] Empty filter config results in no filtering and root trace data is used (unit) **[BE-only]**
- [x] String span inputs and outputs are returned as-is without double-serialization (unit) **[BE-only]**
- [x] All backend services that consume trace input/output apply the same span filter and JSONPath pipeline as the TraceViewer (unit) **[BE-only]**
- [x] JSONPath evaluation does not noticeably slow down trace display (unit) **[BE-only]**
- [x] Preview responds within 500ms (unit) **[BE-only]**
- [x] Invalid JSONPath syntax shows helpful error message in preview (e2e-real, unit)

### Tests Without Requirement Links

These tests are tagged with the spec but don't link to specific requirements:

- `client/tests/e2e/jsonpath-trace-display.spec.ts` (file-level) [e2e-real]
- `client/tests/e2e/jsonpath-trace-display.spec.ts` (file-level) [e2e-real]
- `client/src/hooks/useJsonPathExtraction.test.ts` (file-level) [unit]
- `client/src/components/JsonPathSettings.attrValueDisabled.test.tsx` (file-level) [unit]

## UI_COMPONENTS_SPEC

**Coverage**: 0/16 requirements (0%)

### Uncovered Requirements

- [ ] Page navigation works correctly (first, prev, next, last)
- [ ] Items per page selector updates page size
- [ ] Quick jump navigates to valid pages
- [ ] Keyboard shortcuts work when enabled
- [ ] Disabled states shown for unavailable actions
- [ ] Page info accurately reflects data
- [ ] JSON arrays render as tables
- [ ] SQL queries formatted with line breaks
- [ ] CSV export includes all table data
- [ ] Copy to clipboard works for all content
- [ ] Invalid JSON shows error + fallback
- [ ] Responsive layout on different screens
- [ ] Keyboard navigation works throughout
- [ ] Screen reader announces state changes
- [ ] Focus visible and managed correctly
- [ ] Color contrast meets WCAG AA

### Tests Without Requirement Links

These tests are tagged with the spec but don't link to specific requirements:

- `client/tests/e2e/ui-components.spec.ts` (file-level) [e2e-real]
- `client/tests/e2e/ui-components.spec.ts` (file-level) [e2e-real]
- `client/tests/e2e/ui-components.spec.ts` (file-level) [e2e-real]
- `client/tests/e2e/ui-components.spec.ts` (file-level) [e2e-real]
- `client/src/components/TraceDataViewer.test.tsx` (file-level) [unit]
- `client/src/components/TraceDataViewer.test.tsx` (file-level) [unit]
- `client/src/components/Pagination.test.tsx` (file-level) [unit]
- `client/src/components/Pagination.test.tsx` (file-level) [unit]

## EVAL_MODE_SPEC

**Coverage**: 14/35 requirements (40%)

### Uncovered Requirements

- [ ] Criteria can be authored directly (without discovery)
- [ ] Discovery analysis can run agent loops over trace spans as alternative to summaries
- [ ] Richer findings surface example-specific observations
- [ ] Negative-weight criteria penalize when met
- [ ] Normalized score = raw / max_possible, clipped to [0, 1]
- [ ] One independent judge call per criterion
- [ ] Judge sees trace content + single criterion, not other criteria
- [ ] Judge returns met (boolean) + rationale
- [ ] Evaluation runs as background job with progress tracking
- [ ] Judge scores optionally hidden from human reviewer
- [ ] One task-level judge aligned using all criteria across all traces as examples
- [ ] Each criterion's human met/not-met decision stored as a separate MLflow assessment on the trace
- [ ] All assessments share the judge name; extraction yields all (not just most recent)
- [ ] Semantic memory distills guidelines from overlapping criteria patterns
- [ ] Episodic memory indexes specific criterion examples for retrieval
- [ ] Aligned judge registered to MLflow
- [ ] Re-hydration rebuilds episodic memory from trace assessments without external state
- [ ] Re-evaluation compares pre/post alignment accuracy on same trace set
- [ ] Export produces trace → criteria mapping
- [ ] Export includes scoring configuration (types, weights, aggregation rules)
- [ ] Exported eval can be re-run via `mlflow.genai.evaluate()`

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
- :warning: Scoring handles edge cases: no criteria, all hurdles, all negative weights (unit)
- :warning: Results stored per-criterion with rationale (unit)

### Covered Requirements

- [x] Workshop can be created with `mode: "eval"` (unit) **[BE-only]**
- [x] Mode is immutable after creation (unit) **[BE-only]**
- [x] Eval-mode workshops do not use the global rubric system (unit) **[BE-only]**
- [x] Existing workshop-mode behavior is unchanged (unit) **[BE-only]**
- [x] Facilitator can create criteria on a specific trace (unit) **[BE-only]**
- [x] Each criterion has a type (standard or hurdle) and weight (-10 to +10) (unit) **[BE-only]**
- [x] Criteria can be promoted from discovery findings (unit) **[BE-only]**
- [x] Criteria are editable and deletable (unit) **[BE-only]**
- [x] Per-trace rubric is rendered as markdown (unit) **[BE-only]**
- [x] Discovery analysis uses trace summaries when available (unit) **[BE-only]**
- [x] Hurdle criteria gate the entire trace — any hurdle failure → score 0 (unit) **[BE-only]**
- [x] Standard criteria scored as met (1) or not met (0) × weight (unit) **[BE-only]**
- [x] Scoring handles edge cases: no criteria, all hurdles, all negative weights (unit) **[BE-only]**
- [x] Results stored per-criterion with rationale (unit) **[BE-only]**

### Tests Without Requirement Links

These tests are tagged with the spec but don't link to specific requirements:

- `client/tests/e2e/eval-mode-workflow.spec.ts` (file-level) [e2e-mocked]
- `client/src/components/eval/CriterionEditor.eval.test.tsx` (file-level) [unit]

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
