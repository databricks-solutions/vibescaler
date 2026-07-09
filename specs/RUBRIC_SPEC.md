---
id: RUBRIC_SPEC
title: Rubric Specification
---

import SpecCoverage from '@site/src/components/SpecCoverage';

# Rubric Specification

## Overview

This specification defines the rubric system for the Human Evaluation Workshop, including how evaluation criteria are structured, stored, parsed, and used across the annotation workflow. Rubrics support both Likert (1-5) and binary (Pass/Fail) scales.

## Core Concepts

### Rubric
- A collection of evaluation questions/criteria for rating traces
- Associated with a specific workshop
- Defines the evaluation framework for annotation phase
- Supports multiple scale types (Likert, Binary)

### Rubric Question
- A single evaluation criterion within a rubric
- Has a title (short label) and description (detailed guidance)
- Specifies the rating scale (Likert 1-5 or Binary 0/1)
- For binary scales, includes custom labels (e.g., "Good/Bad", "Pass/Fail")

### Scale Types

| Scale | Values | Use Case |
|-------|--------|----------|
| **Likert** | 1, 2, 3, 4, 5 | Nuanced quality assessment |
| **Binary** | 0 (Fail), 1 (Pass) | Pass/fail or categorical judgment |

## Data Model

### Rubric

```
Rubric:
  - id: UUID
  - workshop_id: UUID
  - name: string
  - questions: string          # Serialized question data (see format below)
  - judge_type: 'likert' | 'binary'
  - binary_labels: Optional[{pass: string, fail: string}]
  - created_at: timestamp
  - updated_at: timestamp
```

### Question Format (Serialized)

Each question is serialized as `Title: Description|||JUDGE_TYPE|||judgeType`, and questions
are joined with `|||QUESTION_SEPARATOR|||` (no surrounding newlines). The title is everything
before the **first** colon; the description is everything after it and may contain newlines
and further colons:

```
Accuracy: Is the response factually correct?|||JUDGE_TYPE|||binary|||QUESTION_SEPARATOR|||Helpfulness: Does the response address the user's need?
It may span multiple lines.|||JUDGE_TYPE|||likert
```

### Question Object (Parsed)

```typescript
interface RubricQuestion {
  id: string;           // Sequential, position-based: "q_1", "q_2", ... (re-derived on every parse)
  title: string;        // Text before the first colon
  description: string;  // Text after the first colon (may span multiple lines)
  judgeType: 'likert' | 'binary';  // Per-question judge type (legacy 'freeform' coerces to likert)
}
```

Question ids are **not** stored UUIDs — they are regenerated from list position on every
parse, which is why annotation `ratings` keys use the `q_N` format and why deletions
re-index the remaining questions.

### Per-Question Judge Type

Each question can specify its own judge type by appending the `|||JUDGE_TYPE|||` delimiter
to its serialized content:

```
Accuracy: Is the response correct?|||JUDGE_TYPE|||binary|||QUESTION_SEPARATOR|||Helpfulness: Rate helpfulness 1-5|||JUDGE_TYPE|||likert
```

**Delimiter**: `|||JUDGE_TYPE|||`

**Parsing Logic**:
1. Split each question part on `|||JUDGE_TYPE|||`
2. Accept `binary` or `likert`; the legacy `freeform` type coerces to `likert`
3. Split the remaining content at the first colon into title and description
4. Default to `likert` if no judge type is specified

This enables mixed rubrics where some questions use Pass/Fail and others use 1-5 scale.

## Delimiter System

### The Problem

Previous implementations used `---` as the question delimiter. This broke when users included horizontal rules or dashes in question descriptions, and plain-newline schemes broke on blank lines.

### The Solution

Use a unique delimiter that won't appear in user input:

```
|||QUESTION_SEPARATOR|||
```

### Why This Delimiter?

- Highly unlikely to appear in natural text
- Human-readable for debugging
- No special regex characters (simple string match)
- Consistent across frontend and backend

## Parsing & Formatting

### Shared Utility: `client/src/utils/rubricUtils.ts`

```typescript
export const QUESTION_DELIMITER = '|||QUESTION_SEPARATOR|||';
const JUDGE_TYPE_DELIMITER = '|||JUDGE_TYPE|||';

export const parseRubricQuestions = (questionText: string): RubricQuestion[] => {
  if (!questionText) return [];

  return questionText
    .split(QUESTION_DELIMITER)
    .map((part, index): RubricQuestion | null => {
      const trimmedText = part.trim();
      if (!trimmedText) return null;

      // Extract judge type (binary | likert; anything else — incl. legacy 'freeform' — coerces to likert)
      let content = trimmedText;
      let judgeType: QuestionJudgeType = JudgeType.LIKERT;
      if (trimmedText.includes(JUDGE_TYPE_DELIMITER)) {
        const [contentPart, typePart] = trimmedText.split(JUDGE_TYPE_DELIMITER);
        content = contentPart.trim();
        const parsedType = typePart?.trim() as JudgeType;
        if (parsedType === JudgeType.LIKERT || parsedType === JudgeType.BINARY) {
          judgeType = parsedType;
        }
      }

      // Split at the FIRST colon only; no colon means title-only with empty description
      const colonIndex = content.indexOf(':');
      const title = colonIndex === -1 ? content.trim() : content.substring(0, colonIndex).trim();
      const description = colonIndex === -1 ? '' : content.substring(colonIndex + 1).trim();

      return { id: `q_${index + 1}`, title, description, judgeType };
    })
    .filter((q): q is RubricQuestion => q !== null);
};

export const formatRubricQuestions = (questions: RubricQuestion[]): string =>
  questions
    .map(q => `${q.title}: ${q.description}${JUDGE_TYPE_DELIMITER}${q.judgeType}`)
    .join(QUESTION_DELIMITER);
```

### Backend Parsing: `server/services/database_service.py`

`DatabaseService._parse_rubric_questions` mirrors the frontend parser (same delimiters,
same first-colon split, same sequential `q_N` ids, same freeform→likert coercion), with
one difference: parts **without a colon are skipped** by the backend, while the frontend
keeps them as title-only questions.

```python
def _parse_rubric_questions(self, question_text: str) -> list:
    QUESTION_DELIMITER = '|||QUESTION_SEPARATOR|||'
    JUDGE_TYPE_DELIMITER = '|||JUDGE_TYPE|||'
    questions = []
    for i, part in enumerate((question_text or '').split(QUESTION_DELIMITER)):
        part = part.strip()
        if not part:
            continue
        content, judge_type = part, 'likert'
        if JUDGE_TYPE_DELIMITER in part:
            content_part, type_part = part.split(JUDGE_TYPE_DELIMITER, 1)
            content = content_part.strip()
            parsed_type = type_part.strip()
            if parsed_type in ('likert', 'binary'):
                judge_type = parsed_type
            # legacy 'freeform' (and anything else) coerces to the 'likert' default
        if ':' in content:
            title, description = content.split(':', 1)
            questions.append({
                'id': f'q_{i + 1}',
                'title': title.strip(),
                'description': description.strip(),
                'judge_type': judge_type,
            })
    return questions
```

`_reconstruct_rubric_questions` is the inverse: it re-indexes ids to `q_1..q_N` and
re-joins `f'{title}: {description}|||JUDGE_TYPE|||{judge_type}'` parts with the
question delimiter.

## Judge Type Integration

### Likert Scale

```typescript
// Rubric definition
{
  judge_type: 'likert',
  binary_labels: null
}

// Rating UI shows: 1 2 3 4 5
// Rating values: integers 1-5
```

### Binary Scale

```typescript
// Rubric definition
{
  judge_type: 'binary',
  binary_labels: { pass: 'Good', fail: 'Bad' }
}

// Rating UI shows: [Fail] [Pass]
// Rating values: 0 (Fail) or 1 (Pass)
```

### Binary Labels

`binary_labels` are stored on the rubric and accepted by the API, but the annotation
UI currently renders the fixed labels "Pass" and "Fail" for binary questions.

## Files Using Rubric Parsing

All these files import from `rubricUtils.ts`:

| File | Usage |
|------|-------|
| `RubricCreationDemo.tsx` | Create/edit rubric questions |
| `AnnotationDemo.tsx` | Display questions for rating |
| `AnnotationReviewPage.tsx` | Show questions in review |
| `AnnotationStartPage.tsx` | Preview questions before annotation |
| `IRRResultsDemo.tsx` | Display questions in IRR analysis |
| `RubricViewPage.tsx` | Read-only rubric display |
| `FacilitatorDashboard.tsx` | Rubric summary for facilitators |
| `JudgeTuningPage.tsx` | Criteria shown during judge tuning |

## API Endpoints

### Create Rubric

```
POST /workshops/{workshop_id}/rubric
{
  "question": "Accuracy: Is the response factually correct?|||JUDGE_TYPE|||binary|||QUESTION_SEPARATOR|||Helpfulness: Does the response address the user's need?|||JUDGE_TYPE|||likert",
  "created_by": "user-id",
  "judge_type": "likert"
}
```

### Get Rubric

```
GET /workshops/{workshop_id}/rubric

Response:
{
  "id": "uuid",
  "workshop_id": "uuid",
  "question": "Accuracy: Is the response factually correct?|||JUDGE_TYPE|||binary|||QUESTION_SEPARATOR|||...",
  "judge_type": "likert",
  "binary_labels": null,
  "rating_scale": 5,
  "created_by": "user-id",
  "created_at": "timestamp"
}
```

The API returns only the raw serialized `question` string — there is **no**
`parsed_questions` field. Clients parse the string themselves via
`parseRubricQuestions` in `rubricUtils.ts`.

## Rubric Lifecycle

### CRUD Operations

Only one rubric exists per workshop. Create and update are upsert — `POST` and `PUT /workshops/{id}/rubric` both call the same underlying method. If a rubric exists, it is updated; otherwise a new one is created.

**Create/Add Question**: Facilitator opens the "Add Criterion" dialog and provides:
- **Title** (required) — short label for the criterion
- **Description/Definition** (required) — what the criterion measures
- **Positive direction** (optional) — what a good response looks like
- **Negative direction** (optional) — what a poor response looks like
- **Examples** (optional) — concrete good/bad examples
- **Evaluation type** — Likert or Binary (per-question). The legacy Free-form type is no longer creatable; existing free-form criteria render as Likert.

The optional structured fields are serialized into the description text by the frontend.

**Edit Question**: Facilitator clicks the edit icon on an existing question card. The dialog pre-populates with the question's current data. Updates are sent via `PUT /workshops/{id}/rubric/questions/{question_id}`.

**Delete Question**: Facilitator clicks the delete icon. The question is removed from the serialized list and remaining questions are re-indexed sequentially (`q_1`, `q_2`, ...). If the last question is deleted, the entire rubric record is removed from the database. Annotation data for deleted questions is preserved in the database but excluded from IRR calculations and UI display.

**No phase restriction**: Rubric CRUD is allowed regardless of workshop phase — facilitators can refine criteria at any time.

### Phase Integration

- Workshop advances from Discovery to Rubric phase when at least one finding exists
- Rubric must exist before the workshop can advance from Rubric to Annotation phase
- `begin_annotation_phase()` also validates that a rubric exists before starting auto-evaluation

### MLflow Integration

On rubric create or update:
1. A workshop `judge_name` is auto-derived from the first rubric question title (e.g., "Response Accuracy" → `response_accuracy_judge`)
2. A background MLflow re-sync is triggered to update all annotation feedback entries with current judge names
3. MLflow sync is best-effort — failures are logged but do not block the rubric operation

### Rating Validation

Annotation submissions validate each rating against its question's judge type:
- **Binary**: only 0 or 1 accepted
- **Likert**: only 1–5 accepted
- If all ratings in a submission fail validation, existing annotation data is preserved (not overwritten)

## AI-Powered Rubric Generation

Facilitators can generate rubric suggestions using an AI model that analyzes discovery findings and participant notes.

### Workflow

1. Facilitator opens the suggestion panel and selects an AI model
2. System calls `POST /workshops/{id}/generate-rubric-suggestions` with endpoint name, temperature, and whether to include notes
3. Service fetches all discovery findings (grouped by trace, max 15) and participant notes (max 15)
4. AI returns a JSON array of suggested criteria
5. Facilitator can accept, reject, or edit each suggestion before adding it to the rubric

### Validation Rules

- At least one finding or note must exist (400 if both empty)
- Suggestions with title < 3 characters are filtered out
- Suggestions with description < 10 characters are filtered out
- Title truncated at 100 characters, description at 1000
- Invalid `judgeType` values default to `'likert'`; the legacy `freeform` type coerces to `'likert'`
- If zero suggestions pass validation, the request fails

### No Phase Restriction

AI generation is allowed at any workshop phase — facilitators can regenerate or refine criteria at any time.

## Migration Considerations

### Legacy Data

- Rubrics created before the delimiter change used `---` as the question separator.
  The canonical parser (`_parse_rubric_questions` / `parseRubricQuestions`) does **not**
  split on `---`; only a few read paths (e.g., MLflow sync judge-name mapping) fall back
  to the legacy separator when the new delimiter is absent.
- Rubrics containing the legacy `freeform` judge type remain readable: the type
  coerces to `likert` at the parse boundary on both client and server. Free-form
  criteria are no longer creatable.
- The recommended migration for old-format rubrics is to re-create them through the UI.

## Success Criteria

<SpecCoverage spec="RUBRIC_SPEC" />

### Parsing & Serialization

- [ ] Questions with multi-line descriptions parse correctly
- [ ] Delimiter never appears in user input (by design)
- [ ] Frontend and backend use same delimiter constant
- [ ] Per-question judge_type parsed from the `|||JUDGE_TYPE|||` delimiter
- [ ] Parsed questions get sequential `q_N` ids
- [ ] Legacy `freeform` judge type coerces to likert at the parse boundary
- [ ] Empty/whitespace-only parts filtered out

### Scale Rendering

- [ ] Likert scale shows 1-5 rating options
- [ ] Binary scale shows Pass/Fail buttons (not star ratings)
- [ ] Binary feedback logged as 0/1 to MLflow (not 3)
- [ ] Mixed rubrics support different scales per question

### CRUD Lifecycle

- [ ] Facilitator can create a rubric question with title and description
- [ ] Facilitator can edit an existing rubric question
- [ ] Facilitator can delete a rubric question
- [ ] Only one rubric exists per workshop (upsert semantics)
- [ ] Rubric persists and is retrievable via GET after creation

### Phase & Workflow Integration

- [ ] Rubric required before advancing to annotation phase
- [ ] No phase restriction on rubric CRUD
- [ ] Question IDs re-indexed sequentially after deletion
- [ ] Annotation data preserved when rubric questions are deleted

### MLflow Integration

- [ ] Judge name auto-derived from first rubric question title
- [ ] MLflow re-sync triggered on rubric create/update (best-effort)

### AI-Powered Generation

- [ ] AI suggestions generated from discovery findings and participant notes
- [ ] Suggestions validated: title >= 3 chars, description >= 10 chars
- [ ] Invalid judge type in suggestions defaults to likert
- [ ] Facilitator can accept, reject, or edit suggestions before adding to rubric

## Testing Scenarios

### Test 1: Simple Questions
```
Input:
"Question 1: Description 1|||QUESTION_SEPARATOR|||Question 2: Description 2"

Expected:
[
  { id: "q_1", title: "Question 1", description: "Description 1" },
  { id: "q_2", title: "Question 2", description: "Description 2" }
]
```

### Test 2: Multi-line Description
```
Input:
"Question 1: Line 1 of description\nLine 2 of description\n\nLine 3 after blank"

Expected:
[
  {
    id: "q_1",
    title: "Question 1",
    description: "Line 1 of description\nLine 2 of description\n\nLine 3 after blank"
  }
]
```

### Test 3: Binary Scale
```
Rubric question:
"Correct: Is this correct?|||JUDGE_TYPE|||binary"

UI shows: [Pass] [Fail] buttons (not star ratings)
Rating value for Pass: 1
Rating value for Fail: 0

MLflow feedback logged: 0 or 1 (NOT 3 for neutral)
```

### Test 4: Per-Question Judge Type
```
Input:
"Accuracy: Is the response factually correct?|||JUDGE_TYPE|||binary|||QUESTION_SEPARATOR|||Helpfulness: Rate helpfulness 1-5|||JUDGE_TYPE|||likert"

Expected:
[
  { id: "q_1", title: "Accuracy", description: "Is the response factually correct?", judgeType: "binary" },
  { id: "q_2", title: "Helpfulness", description: "Rate helpfulness 1-5", judgeType: "likert" }
]

UI shows:
- Question 1: Pass/Fail buttons
- Question 2: 1-5 rating controls
```

### Test 5: Mixed Rubric Evaluation
```
Rubric with binary Question 1 and likert Question 2

When evaluating:
- Question 1 uses binary judge (0/1 output)
- Question 2 uses likert judge (1-5 output)
- Results stored with correct scale per question
```

## Backwards Compatibility

- New rubrics use the `|||QUESTION_SEPARATOR|||` delimiter automatically
- Legacy `freeform` questions remain readable (coerced to likert on parse)
- The API returns only the raw serialized question string; parsing happens client-side
- Legacy single-rating annotations supported alongside multi-rating
