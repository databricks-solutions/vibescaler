---
id: TRACE_DISPLAY_SPEC
title: Trace JSONPath Display Customization Spec
---

import SpecCoverage from '@site/src/components/SpecCoverage';

# Trace JSONPath Display Customization Spec

## Overview

This feature allows facilitators to optionally configure how trace inputs and outputs are displayed in the TraceViewer. Two opt-in stages are applied in order:

1. **Span attribute filter** — select a specific span from the trace (by name, type, and/or attribute) and display its inputs/outputs instead of the root trace data.
2. **JSONPath extraction** — extract specific values from the (possibly span-filtered) input/output JSON.

This helps when raw trace data contains complex JSON objects that are not readable for non-technical workshop participants.

**Key Principle**: Both stages are **opt-in** features. When not configured, trace inputs/outputs display exactly as the raw trace data.

---

## Core Concepts

### JSONPath Query
A JSONPath expression (e.g., `$.messages[0].content`, `$.response.text`) that extracts a specific value from a JSON object. Applied to the trace's `input` and/or `output` fields (after span filtering, if configured).

### Span Attribute Filter
An optional per-workshop filter with up to four fields: `span_name`, `span_type`, `attribute_key`, `attribute_value`. Criteria are AND-combined and the first matching span in the trace context wins; its inputs/outputs replace the root trace input/output before JSONPath extraction. An empty filter means no filtering (root trace data is used).

### Scope
- Configured **per workshop** by the facilitator
- Applied to **all traces** displayed in the TraceViewer for that workshop
- Stored in workshop settings (`input_jsonpath`, `output_jsonpath`, `span_attribute_filter`)

---

## User Stories

### Facilitator
1. As a facilitator, I want to configure optional JSONPath queries for input and output so that participants see clean, readable text instead of raw JSON.
2. As a facilitator, I want to preview my JSONPath queries against actual trace data before saving, so I can verify they extract the right content.
3. As a facilitator, I want to leave JSONPath fields empty to show the original trace data.

### Participant/SME
1. As a participant, I want to see clearly formatted input/output text without needing to understand JSON structure.

---

## Data Model

### Workshop Model Extension

Three optional fields on the `Workshop` model:

```python
# server/models.py - Workshop model
class Workshop(BaseModel):
    # ... existing fields ...
    input_jsonpath: str | None = None        # JSONPath query for extracting trace input display
    output_jsonpath: str | None = None       # JSONPath query for extracting trace output display
    span_attribute_filter: dict | None = None  # Filter config for selecting a span's inputs/outputs
```

### Database Migrations

- `migrations/versions/0005_add_jsonpath_columns.py` — adds `input_jsonpath` and `output_jsonpath` TEXT columns to `workshops`
- `migrations/versions/0016_add_span_attribute_filter.py` — adds the `span_attribute_filter` column to `workshops`

---

## Behavior

### Display Pipeline

When displaying a trace in the TraceViewer (and when backend services consume trace text), the same two-stage pipeline applies:

1. **Span attribute filter (if configured)**:
   - Match spans in the trace context against the filter criteria (AND-combined, first matching span wins)
   - On a match, the span's inputs/outputs become the working input/output
   - String span inputs/outputs are used as-is (no double serialization); non-string values are JSON-serialized
   - If no span matches or no filter is configured, the root trace input/output is used

2. **JSONPath extraction (if configured, non-empty)**:
   - Parse the working input/output as JSON
   - Apply the JSONPath query
   - **If multiple values match**: Concatenate with newlines (`\n`)
   - **If query succeeds and returns non-empty/non-null**: Display extracted value(s)
   - **If query fails, returns empty string, or returns null**: Fall back to the working (span-filtered or raw) text

If neither stage is configured, the raw input/output displays unchanged.

On the backend, the pipeline is implemented once in `server/utils/trace_display_utils.py` (`get_display_text(trace, workshop)`), which also supports optional milestone-context enrichment (appending the trace's milestone summary to the output text for LLM consumers such as judges).

### Fallback Cases

JSONPath extraction falls back to the working (span-filtered or raw) text when:
- JSONPath field is empty or null
- Input/output is not valid JSON
- JSONPath query syntax is invalid
- JSONPath query returns no matches
- JSONPath query returns `null`
- JSONPath query returns empty string `""`

### Multiple Matches Behavior

When a JSONPath query returns multiple values (e.g., `$.messages[*].content`):

```
Result 1
Result 2
Result 3
```

Values are joined with newline characters for readable display.

---

## UI Components

### Facilitator Settings Panel

Location: `client/src/components/JsonPathSettings.tsx` — the "Trace Display Settings" card in the facilitator settings. It contains a Span Attribute Filter section (span name, span type, attribute key, attribute value — with its own Preview/Save/Clear buttons) followed by the Input/Output JSONPath fields. The span filter section and both JSONPath fields carry an "optional" badge; the attribute value input is disabled until an attribute key is entered.

```
+--------------------------------------------------+
| Trace Display Settings                            |
+--------------------------------------------------+
|                                                   |
| Input JSONPath (optional)                         |
| +----------------------------------------------+ |
| | $.messages[0].content                        | |
| +----------------------------------------------+ |
| Extract specific content from trace input JSON    |
|                                                   |
| Output JSONPath (optional)                        |
| +----------------------------------------------+ |
| | $.response.text                              | |
| +----------------------------------------------+ |
| Extract specific content from trace output JSON   |
|                                                   |
| +------------------+                              |
| |  Preview         |                              |
| +------------------+                              |
|                                                   |
+--------------------------------------------------+
```

### Preview Panel

When "Preview" is clicked, show extracted values using the **first trace** from the workshop's dataset:

```
+--------------------------------------------------+
| Preview (Trace: abc123...)                        |
+--------------------------------------------------+
|                                                   |
| Input Result:                                     |
| +----------------------------------------------+ |
| | "What is the capital of France?"             | |
| +----------------------------------------------+ |
|                                                   |
| Output Result:                                    |
| +----------------------------------------------+ |
| | "The capital of France is Paris."            | |
| +----------------------------------------------+ |
|                                                   |
+--------------------------------------------------+
```

If extraction fails:
```
| Input Result:                                     |
| +----------------------------------------------+ |
| | (Showing original - JSONPath returned empty) | |
| | {"messages": [...], "metadata": {...}}       | |
| +----------------------------------------------+ |
```

---

## API Endpoints

### Update Workshop JSONPath Settings

```
PUT /workshops/{workshop_id}/jsonpath-settings
```

Request body:
```json
{
  "input_jsonpath": "$.messages[0].content",
  "output_jsonpath": "$.response.text"
}
```

Response: Updated `Workshop` object. Invalid JSONPath syntax is rejected with a 400 error containing the validation message.

### Update Span Attribute Filter

```
PUT /workshops/{workshop_id}/span-attribute-filter
```

Request body:
```json
{
  "span_attribute_filter": {
    "span_name": "AzureChatOpenAI",
    "span_type": "CHAT_MODEL",
    "attribute_key": "model",
    "attribute_value": "gpt-4"
  }
}
```

All filter fields are optional; send `"span_attribute_filter": null` to clear the filter. Response: Updated `Workshop` object.

### Preview Span Filter

```
POST /workshops/{workshop_id}/preview-span-filter
```

Applies the candidate filter against the first workshop trace and returns `trace_id`, `matched`, `input_result`, and `output_result`.

### Preview JSONPath

```
POST /workshops/{workshop_id}/preview-jsonpath
```

The preview applies the workshop's **saved** span attribute filter first, then the candidate JSONPath expressions — mirroring the display pipeline.

Request body:
```json
{
  "input_jsonpath": "$.messages[0].content",
  "output_jsonpath": "$.response.text"
}
```

Response:
```json
{
  "trace_id": "abc123...",
  "input_result": "What is the capital of France?",
  "input_success": true,
  "output_result": "The capital of France is Paris.",
  "output_success": true
}
```

If no traces exist:
```json
{
  "error": "No traces available for preview"
}
```

---

## Implementation

### Backend (Python)

Shipped modules (JSONPath evaluation uses the `jsonpath-ng` library):

- `server/utils/jsonpath_utils.py` — `apply_jsonpath(data_str, jsonpath_expr) -> (extracted_value | None, success)` plus `validate_jsonpath(expr)` used by the settings endpoint. Multiple matches are joined with newlines; empty/null results report failure so callers fall back.
- `server/utils/span_filter_utils.py` — `apply_span_filter(trace_context, span_attribute_filter) -> (input | None, output | None)`. Criteria are AND-combined, the first matching span wins, and string span inputs/outputs are returned as-is (no double serialization).
- `server/utils/trace_display_utils.py` — `get_display_text(trace, workshop)`, the single source of truth for the span-filter → JSONPath pipeline, plus `format_milestone_context(...)` for optional milestone-context enrichment of the output text.

Backend consumers of `get_display_text`: `server/services/judge_service.py`, `server/services/discovery_service.py`, `server/services/discovery_analysis_service.py`.

### Frontend (React)

- `client/src/hooks/useJsonPathExtraction.ts` — applies JSONPath via the `jsonpath-plus` library; returns the original data on any failure (invalid JSON, no matches, null/empty results).
- `client/src/components/TraceViewer.tsx` — applies the workshop's span attribute filter against the trace context (memoized), then `useJsonPathExtraction` on the resulting input/output.
- `client/src/components/JsonPathSettings.tsx` — facilitator settings UI for both stages (see UI Components above).

### Dependencies

**Backend**: `jsonpath-ng>=1.5.3` (in `pyproject.toml`)

**Frontend**: `jsonpath-plus` (in `client/package.json`)

---

## Success Criteria

<SpecCoverage spec="TRACE_DISPLAY_SPEC" />

### Functional — JSONPath

- [ ] Facilitator can configure input/output JSONPath in settings panel
- [ ] JSONPath fields are optional and clearly labeled as such
- [ ] Preview shows extraction results against first workshop trace
- [ ] TraceViewer applies JSONPath when configured
- [ ] Multiple JSONPath matches are concatenated with newlines
- [ ] System falls back to raw display when JSONPath is not configured, JSON parsing fails, JSONPath query fails, or JSONPath returns null/empty
- [ ] Settings are persisted per workshop

### Functional — Span Attribute Filter

- [ ] Facilitator can configure span attribute filter with span name, span type, attribute key, and attribute value
- [ ] Filter criteria are AND-combined and first matching span wins
- [ ] Attribute value input is disabled until attribute key has a value
- [ ] Span filter preview shows match status and filtered inputs/outputs against first trace
- [ ] Span filter is applied before JSONPath extraction in TraceViewer
- [ ] Empty filter config results in no filtering and root trace data is used
- [ ] String span inputs and outputs are returned as-is without double-serialization

### Functional — Consistency

- [ ] All backend services that consume trace input/output apply the same span filter and JSONPath pipeline as the TraceViewer
<!-- AUDIT: alignment_service bypasses this pipeline; owner decision pending -->
- [ ] Copy Output copies the representation currently displayed (formatted vs raw)

### Non-Functional

- [ ] JSONPath evaluation does not noticeably slow down trace display
- [ ] Preview responds within 500ms
- [ ] Invalid JSONPath syntax shows helpful error message in preview

---

## Testing

Shipped test locations:

### Unit Tests

- `tests/unit/utils/test_jsonpath_utils.py` — JSONPath extraction, multiple matches, and fallback cases
- `tests/unit/utils/test_span_filter_utils.py` — span matching, AND-combination, string passthrough
- `tests/unit/services/test_trace_display_pipeline_consistency.py` — backend services use the shared `get_display_text` pipeline
- `tests/unit/routers/test_preview_jsonpath_performance.py` — preview endpoint behavior and responsiveness
- `client/src/hooks/useJsonPathExtraction.test.ts` — frontend extraction hook
- `client/src/components/JsonPathSettings.attrValueDisabled.test.tsx` — attribute value input disabled until attribute key set
- `client/src/components/JsonPathSettings.optionalLabels.test.tsx` — JSONPath fields labeled optional and not required
- `client/src/components/TraceViewer.copyOutput.test.tsx` — Copy Output copies the displayed representation

### E2E Tests

- `client/tests/e2e/jsonpath-trace-display.spec.ts` — facilitator configures, previews, and saves settings; TraceViewer reflects them

---

## Future Work (Out of Scope)

The following are explicitly **not** included in this implementation:

1. **Per-trace JSONPath** - Different JSONPath for specific traces
2. **Multiple JSONPath queries** - Only one per field (input/output)
3. **JSONPath editing in trace viewer** - Configuration only in settings
4. **Custom separators** - Multiple matches always use newline
5. **JSONPath validation UI** - Only shown in preview errors
6. **Export with JSONPath applied** - Exports use raw data

---

## Related Specs

- [UI_COMPONENTS_SPEC](./UI_COMPONENTS_SPEC.md) - TraceViewer component
- [DATASETS_SPEC](./DATASETS_SPEC.md) - Trace data structure
- [DISCOVERY_SPEC](./DISCOVERY_SPEC.md) - Trace assignment & display phases

---

## Implementation Log

| Date | Plan | Status | Summary |
|------|------|--------|---------|
| 2026-04-15 | [Pipeline Consistency Fix](../.claude/plans/2026-04-15-trace-display-pipeline-consistency.md) | partial | Shared helper `get_display_text` extracted and wired into judge_service, discovery_service, and discovery_analysis_service; alignment_service not yet wired (owner decision pending) |
