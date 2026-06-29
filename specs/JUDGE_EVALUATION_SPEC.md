---
id: JUDGE_EVALUATION_SPEC
title: Judge Evaluation Specification
---

import SpecCoverage from '@site/src/components/SpecCoverage';

# Judge Evaluation Specification

## Overview

This specification defines the LLM judge evaluation system for the Human Evaluation Workshop, including judge creation, evaluation execution, alignment optimization, auto-evaluation, re-evaluation, and inter-rater reliability (IRR) measurement. The system integrates with [MLflow GenAI](https://mlflow.org/docs/latest/genai/) for judge execution and alignment.

## MLflow Integration

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Judge Evaluation Flow                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Workshop   │    │    MLflow    │    │   Model      │  │
│  │   Rubric     │───▶│  make_judge  │───▶│  Endpoint    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │           │
│         │                   ▼                   │           │
│         │           ┌──────────────┐            │           │
│         │           │   evaluate   │◀───────────┘           │
│         │           └──────────────┘                        │
│         │                   │                               │
│         ▼                   ▼                               │
│  ┌──────────────┐    ┌──────────────┐                      │
│  │   Human      │    │   Judge      │                      │
│  │  Annotations │───▶│  Alignment   │                      │
│  │  (Feedback)  │    │  (MemAlign)  │                      │
│  └──────────────┘    └──────────────┘                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Key MLflow APIs

| API | Purpose |
|-----|---------|
| `mlflow.genai.make_judge()` | Create judge from prompt |
| `mlflow.genai.evaluate()` | Run judge on traces |
| `mlflow.genai.align()` | Optimize judge against human feedback |
| `mlflow.genai.Feedback` | Human annotation feedback |

## Judge Types

### Likert Scale (1-5)

```python
judge = mlflow.genai.make_judge(
    model="endpoints:/my-endpoint",
    name="quality_judge",
    prompt=LIKERT_PROMPT,
    feedback_value_type=float,  # Returns 1.0-5.0
)
```

Rating interpretation:
- 1: Very poor
- 2: Poor
- 3: Acceptable
- 4: Good
- 5: Excellent

### Binary Scale (Pass/Fail)

```python
judge = mlflow.genai.make_judge(
    model="endpoints:/my-endpoint",
    name="binary_judge",
    prompt=BINARY_PROMPT,
    feedback_value_type=float,  # Returns 0.0 or 1.0
)
```

Rating interpretation:
- 0: Fail
- 1: Pass

## Binary Judge Implementation

### The Problem

LLMs often ignore binary format instructions and return Likert-style values (e.g., 3.0) instead of 0/1.

### Solution: Three-Layer Approach

#### 1. Strong Prompt Instructions (Prepended)

```python
BINARY_PREFIX = """## CRITICAL OUTPUT FORMAT REQUIREMENT
You are a BINARY judge. You MUST output EXACTLY one of these values:
- Output "1" if the response meets the criteria (PASS)
- Output "0" if the response does NOT meet the criteria (FAIL)

DO NOT output any other values. DO NOT output 2, 3, 4, 5, or any decimals.
ONLY output "0" or "1".

Examples of VALID outputs: 0, 1
Examples of INVALID outputs: 0.5, 2, 3, 4, 5, "pass", "fail"
---

"""

# Prepend to prompt (models pay more attention to beginning)
full_prompt = BINARY_PREFIX + user_prompt
```

#### 2. Use Float Type (Not Bool)

```python
# DON'T use bool - unreliable parsing
feedback_value_type=bool  # ❌

# DO use float - more reliable 0/1 parsing
feedback_value_type=float  # ✅
```

#### 3. Fallback Threshold Conversion

```python
def normalize_binary_rating(value: float) -> float:
    """Convert Likert-style values to binary."""
    if value in (0.0, 1.0):
        return value  # Already binary

    if 1.0 <= value <= 5.0:
        # Likert to binary: >=3 = PASS, <3 = FAIL
        return 1.0 if value >= 3.0 else 0.0

    raise ValueError(f"Invalid rating: {value}")
```

### Expected Behavior

**Before fix**:
```
Raw MLflow response: value=3.0
ERROR: Invalid binary rating 3.0
Extracted 0/10 evaluations
```

**After fix**:
```
Raw MLflow response: value=3.0
FALLBACK: Converting 3.0 → 1.0 (>=3 = PASS)
Extracted 10/10 evaluations
```

## Auto-Evaluation

### Purpose

Automatically run LLM judge evaluation on traces in the background when the annotation phase begins. This enables immediate comparison of human ratings against LLM judge scores without requiring manual evaluation.

### Trigger

Auto-evaluation starts when the facilitator clicks "Start Annotation Phase" with auto-evaluation enabled.

### Flow

```
1. Facilitator configures annotation phase (trace count, randomization, model selection)
2. Facilitator enables auto-evaluation toggle and selects model
3. System derives judge prompt from rubric questions
4. Traces are tagged with 'eval' label in MLflow
5. Background evaluation job starts
6. Results appear in Judge Tuning / Results page
```

### Derived Judge Prompt

The system automatically generates a judge prompt from the rubric:

```python
def derive_judge_prompt_from_rubric(workshop_id: str) -> str:
    """Auto-derive judge prompt from rubric questions."""
    rubric = get_rubric(workshop_id)
    questions = parse_rubric_questions(rubric.question)

    # Build prompt from question title and description
    question = questions[0]  # Each question evaluated separately
    prompt = f"""Evaluate the response based on the following criterion:

**{question['title']}**
{question['description']}

{{ inputs }}
{{ outputs }}
"""
    return prompt
```

### Per-Question Judge Type

Rubric questions can have individual judge types (see [RUBRIC_SPEC](./RUBRIC_SPEC.md)):

```
Question 1 [JUDGE_TYPE:binary]
Is the response factually accurate?
|||QUESTION_SEPARATOR|||
Question 2 [JUDGE_TYPE:likert]
Rate the helpfulness of the response
```

The evaluation system parses `[JUDGE_TYPE:xxx]` from each question and uses the appropriate type for evaluation.

### Data Model Additions

```
Workshop:
  - auto_evaluation_job_id: Optional[string]   # Background job ID
  - auto_evaluation_prompt: Optional[string]   # Derived judge prompt
  - auto_evaluation_model: Optional[string]    # Model used (for re-evaluation consistency)
```

### API Endpoint

```
POST /workshops/{workshop_id}/begin-annotation
{
  "trace_limit": 10,
  "randomize": false,
  "evaluation_model_name": "databricks-gpt-5-2"  // null to disable auto-eval
}

Response:
{
  "message": "Annotation phase started",
  "auto_evaluation_started": true,
  "auto_evaluation_job_id": "uuid"
}
```

### Model Selection

Available models for auto-evaluation (via `MODEL_MAPPING`):

| Display Name | Endpoint Name |
|--------------|---------------|
| GPT-5.2 | `databricks-gpt-5-2` |
| GPT-5.1 | `databricks-gpt-5-1` |
| Claude Opus 4.5 | `databricks-claude-opus-4-5` |
| Claude Sonnet 4.5 | `databricks-claude-sonnet-4-5` |
| Claude Sonnet 4 | `databricks-claude-sonnet-4` |
| Gemini 3 Pro | `databricks-gemini-3-pro` |
| Gemini 2.5 Flash | `databricks-gemini-2-5-flash` |
| Llama 4 Maverick | `databricks-llama-4-maverick` |
| Llama 3.3 70B Instruct | `databricks-meta-llama-3-3-70b-instruct` |

## Re-Evaluation

### Purpose

Re-run LLM evaluation after alignment to compare pre-alignment and post-alignment judge accuracy. Uses the registered judge with aligned instructions (including semantic memory from MemAlign).

### Flow

```
1. Complete alignment (which registers optimized judge in MLflow)
2. Click "Re-evaluate" button in Judge Tuning page
3. System loads registered judge with aligned instructions
4. Evaluation runs on traces tagged with 'eval' label
5. Results update in UI with new accuracy metrics
```

### Registered Judge Loading

After alignment, the judge is registered in MLflow. Re-evaluation can load this registered judge:

```python
from mlflow.genai.scorers import get_scorer

# Load the aligned judge with semantic memory
judge = get_scorer(name=judge_name, experiment_id=experiment_id)

# Judge includes:
# - Original instructions + distilled guidelines (semantic memory)
# - Episodic trace IDs (episodic memory is rebuilt from these traces at evaluation time)
```

### API Endpoint

```
POST /workshops/{workshop_id}/re-evaluate
{
  "judge_prompt": "optional custom prompt",  // uses stored prompt if omitted
  "judge_name": "workshop_judge",
  "judge_type": "binary"  // auto-detected from rubric if omitted
}

Response:
{
  "job_id": "uuid",
  "message": "Re-evaluation started"
}
```

### Model Consistency

Re-evaluation uses the same model stored during initial auto-evaluation (`auto_evaluation_model` field) to ensure fair comparison between pre-align and post-align results.

### Human-Rating Agreement

Re-evaluation joins the **human ratings** for the evaluated traces and computes the aligned judge's agreement against them (Cohen's Kappa / accuracy), the same way the initial evaluation does. This is what makes the pre-align and post-align scores directly comparable, and it is why re-evaluation runs with human ratings required (`require_human_ratings=True`). Because re-evaluation is a post-annotation, post-alignment step, human ratings are expected to exist; if the trace set has no human-rated traces, re-evaluation fails with a clear error rather than reporting 0% agreement computed over an empty comparison set.

### Tag Types

| Tag | Purpose |
|-----|---------|
| `eval` | Traces for evaluation (applied when annotation starts) |
| `align` | Traces for alignment (applied when human annotations complete) |

Re-evaluation uses `tag_type='eval'` to evaluate the same trace set.

## Alignment (MemAlign Optimizer)

### Purpose

Align LLM judge outputs with human annotations using the MemAlign optimization algorithm with dual memory systems.

### MemAlign Architecture

MemAlign uses two types of memory to improve judge alignment:

```
┌─────────────────────────────────────────────────────────┐
│                    MemAlign System                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐    ┌──────────────────┐          │
│  │ Semantic Memory  │    │ Episodic Memory  │          │
│  │ (Guidelines)     │    │ (Examples)       │          │
│  └──────────────────┘    └──────────────────┘          │
│           │                        │                    │
│           │ Distills general       │ Retrieves similar │
│           │ principles from        │ past examples     │
│           │ human feedback         │ during evaluation │
│           │                        │                    │
│           └────────────┬───────────┘                   │
│                        ▼                                │
│              ┌──────────────────┐                       │
│              │  Aligned Judge   │                       │
│              │  (Instructions + │                       │
│              │   Guidelines)    │                       │
│              └──────────────────┘                       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Memory Types

| Memory Type | Purpose | Persistence |
|-------------|---------|-------------|
| **Semantic** | Distilled guidelines from feedback patterns | Included in registered judge instructions |
| **Episodic** | Similar examples retrieved during evaluation | Trace IDs persisted on the registered judge (`_episodic_trace_ids`); examples rebuilt from those traces at evaluation time |

### Episodic Memory Persistence and Re-Alignment (#161)

The aligned judge is persisted by calling `aligned_judge.update()` (or `register()` on
first registration) directly on the `MemoryAugmentedJudge` returned by `judge.align()`.
MLflow serializes the clean base instructions plus `semantic_memory` and
`episodic_trace_ids` — reconstructing the judge via `make_judge(instructions=...)` is
forbidden because it flattens the decorated prompt and duplicates guideline blocks.

Because `MemAlignOptimizer.align()` appends every trace it is given to episodic memory
without trace-ID dedup, re-alignment must dedup against the persisted trace IDs:

1. Load the registered judge via `get_scorer(name=judge_name, experiment_id=...)` before
   falling back to `make_judge()`
2. Dedup any duplicate IDs already persisted on the judge (legacy corruption repair)
3. Pass only traces whose IDs are **not** already in episodic memory to `align()`
4. If every labeled trace is already in episodic memory, skip `align()` entirely and
   report the existing memory counts

### Flow

```
1. Collect human annotations on traces
2. Mark traces with 'align' tag in MLflow
3. Run MemAlign optimizer
4. Distill semantic memory (guidelines)
5. Build episodic memory (examples)
6. Register aligned judge to MLflow
7. Re-evaluate to compare pre/post alignment
```

### Alignment API

```python
from mlflow.genai.judges.optimizers import MemAlignOptimizer

optimizer = MemAlignOptimizer(
    reflection_lm=alignment_model_uri,  # Same model used for judge evaluation
    retrieval_k=5,  # Examples to retrieve
    embedding_model="databricks:/databricks-gte-large-en",  # Configurable, defaults to GTE Large
)

aligned_judge = judge.align(traces, optimizer)

# Aligned judge has:
# - aligned_judge.instructions (original + distilled guidelines)
# - aligned_judge._semantic_memory (list of guidelines)
# - aligned_judge._episodic_memory (list of examples; persisted as _episodic_trace_ids)
```

### Scale-Specific Behavior

MemAlign works universally across all judge types (binary, likert) without requiring type-specific configuration. The optimizer automatically adapts to the feedback patterns.

### Feedback Aggregation

When multiple annotators rate the same trace:

```python
def aggregate_feedback(annotations: List[Annotation]) -> float:
    """Aggregate multiple ratings for same trace."""
    ratings = [a.rating for a in annotations]

    # For Likert: use mean
    # For Binary: use majority vote
    if scale == 'likert':
        return statistics.mean(ratings)
    else:
        return 1.0 if sum(ratings) > len(ratings) / 2 else 0.0
```

## Inter-Rater Reliability (IRR)

### Metrics

| Metric | Use Case | Range |
|--------|----------|-------|
| **Krippendorff's Alpha** | Multiple raters, any scale | -1 to 1 |
| **Cohen's Kappa** | Two raters, categorical | -1 to 1 |

### Interpretation

| Value | Interpretation |
|-------|----------------|
| < 0 | Less than chance agreement |
| 0.0 - 0.20 | Slight agreement |
| 0.21 - 0.40 | Fair agreement |
| 0.41 - 0.60 | Moderate agreement |
| 0.61 - 0.80 | Substantial agreement |
| 0.81 - 1.00 | Almost perfect agreement |

### Calculation

```python
from server.services.krippendorff_alpha import calculate_krippendorff_alpha
from server.services.cohens_kappa import calculate_cohens_kappa

# Krippendorff's Alpha (multiple raters)
alpha = calculate_krippendorff_alpha(
    annotations=all_annotations,
    scale='ordinal'  # or 'nominal' for binary
)

# Cohen's Kappa (two raters)
kappa = calculate_cohens_kappa(
    rater1_annotations=user_a_annotations,
    rater2_annotations=user_b_annotations
)
```

## Data Model

There is no standalone `Judge` entity. A judge is identified by the workshop's
`judge_name` column plus a versioned `JudgePrompt`; the aligned judge artifact itself
lives in MLflow (registered scorer).

### JudgePrompt (`judge_prompts` table)

```
JudgePrompt:
  - id: UUID
  - workshop_id: UUID
  - prompt_text: string
  - judge_type: 'likert' | 'binary' | 'freeform'
  - version: int                       # Incremented per workshop; re-eval creates a new version
  - few_shot_examples: JSON
  - model_name: string
  - model_parameters: Optional[JSON]   # e.g. {"aligned": true, "alignment_model": ...}
  - binary_labels: Optional[JSON]      # {"pass": "Pass", "fail": "Fail"}
  - rating_scale: int (default 5)
  - created_by: string
  - created_at: timestamp
  - performance_metrics: Optional[JSON]
```

### JudgeEvaluation (`judge_evaluations` table)

```
JudgeEvaluation:
  - id: UUID
  - workshop_id: UUID
  - prompt_id: UUID                    # FK to judge_prompts (results versioned by prompt)
  - trace_id: string
  - predicted_rating / human_rating: Optional[int]      # Likert judges
  - predicted_binary / human_binary: Optional[bool]     # Binary judges
  - predicted_feedback / human_feedback: Optional[str]  # Freeform judges
  - confidence: Optional[float]
  - reasoning: Optional[string]
  - created_at: timestamp
```

### AlignmentJob (file-backed, not a DB table)

Background alignment/evaluation jobs are dataclasses persisted as JSON under
`/tmp/workshop_jobs/{job_id}.json` (+ `.logs`), shared between alignment, evaluation,
and auto-evaluation flows:

```
AlignmentJob:
  - job_id: UUID
  - workshop_id: UUID
  - status: 'pending' | 'running' | 'completed' | 'failed'
  - logs: list[string]
  - result: Optional[JSON]             # e.g. {success, guideline_count, example_count, ...}
  - error: Optional[string]
  - created_at / updated_at: timestamp
```

## API Endpoints

All judge/alignment routes are workshop-scoped (there are no `/judges/{judge_id}/*`
routes). Long-running work returns a `job_id` immediately and is polled.

| Route | Purpose |
|-------|---------|
| `POST /workshops/{workshop_id}/start-alignment` | Start background MemAlign job |
| `GET /workshops/{workshop_id}/alignment-job/{job_id}` | Poll alignment job status/logs/result |
| `GET /workshops/{workshop_id}/alignment-status` | Alignment readiness summary |
| `GET /workshops/{workshop_id}/traces-for-alignment` | Traces with human feedback for alignment |
| `POST /workshops/{workshop_id}/start-evaluation` | Start background MLflow evaluation job |
| `POST /workshops/{workshop_id}/start-simple-evaluation` | Direct endpoint-call evaluation job |
| `GET /workshops/{workshop_id}/evaluation-job/{job_id}` | Poll evaluation job |
| `POST /workshops/{workshop_id}/re-evaluate` | Re-evaluate with registered (aligned) judge |
| `POST /workshops/{workshop_id}/evaluate-judge` | Synchronous pipeline (demo model supported) |
| `POST /workshops/{workshop_id}/evaluate-judge-direct` | Synchronous direct evaluation |
| `GET/POST /workshops/{workshop_id}/judge-prompts` | List/create judge prompt versions |
| `PUT /workshops/{workshop_id}/judge-prompts/{prompt_id}/metrics` | Store performance metrics |
| `GET/POST /workshops/{workshop_id}/judge-evaluations/{prompt_id}` | Load/save results per prompt version |
| `GET /workshops/{workshop_id}/auto-evaluation-status` | Auto-eval job status |
| `GET /workshops/{workshop_id}/auto-evaluation-results` | Auto-eval results |
| `POST /workshops/{workshop_id}/restart-auto-evaluation` | Re-run auto-evaluation |
| `PUT /workshops/{workshop_id}/judge-name` | Set judge/feedback name |
| `GET /workshops/{workshop_id}/irr` | Calculate IRR |

### Start Alignment

```
POST /workshops/{workshop_id}/start-alignment
{
  "judge_name": "quality_judge",
  "judge_prompt": "...",
  "evaluation_model_name": "databricks-claude-sonnet-4",
  "alignment_model_name": "databricks-claude-sonnet-4",   // optional
  "embedding_model_name": "databricks-gte-large-en"       // optional
}

Response (returns immediately; work continues in a background thread):
{
  "job_id": "uuid",
  "status": "running",
  "message": "Alignment job started. Poll /alignment-job/{job_id} for status."
}
```

### Poll Alignment Job

```
GET /workshops/{workshop_id}/alignment-job/{job_id}?since_log_index=0

Response:
{
  "job_id": "uuid",
  "status": "running" | "completed" | "failed",
  "logs": ["..."],
  "log_count": 12,
  "updated_at": 1760000000.0,
  "result": { "success": true, "guideline_count": 3, "example_count": 10, ... },  // when completed
  "error": "..."                                                                  // when failed
}
```

### Calculate IRR

```
GET /workshops/{workshop_id}/irr

Response (IRRResult):
{
  "workshop_id": "uuid",
  "score": 0.72,
  "ready_to_proceed": true,
  "calculated_at": "...",
  "details": {
    "metric_used": "Cohen's Kappa" | "Krippendorff's Alpha",
    "per_metric_scores": { "q_1": { "score": 0.7, "interpretation": "...", ... } },
    "problematic_patterns": ["Trace abc... has extreme disagreement (range: 4)"],
    ...
  }
}
```

Only ratings for questions in the current rubric are included; the metric is selected
automatically (2 complete raters → Cohen's Kappa, otherwise Krippendorff's Alpha).

## UI Components

### Judge Tuning Page

**File**: `client/src/pages/JudgeTuningPage.tsx`

Features:
- Mode indicator (Demo, Simple, MLflow)
- Prompt editor
- Evaluation results table with pagination
- Alignment trigger and status
- IRR display

### Mode Indicator

| Mode | Description |
|------|-------------|
| Demo | Mock evaluations (no model call) |
| Simple | Direct model endpoint call |
| MLflow | Full MLflow GenAI integration |

## Success Criteria

<SpecCoverage spec="JUDGE_EVALUATION_SPEC" />

### Judge Evaluation
- [ ] Likert judges return values 1-5
- [ ] Binary judges return values 0 or 1
- [ ] Fallback conversion handles Likert-style returns for binary
- [ ] Evaluation results persisted to database
- [ ] Results reload correctly in UI

### Auto-Evaluation
- [ ] Auto-evaluation runs in background when annotation phase starts
- [ ] Judge prompt auto-derived from rubric questions
- [ ] Per-question judge_type parsed from rubric (`[JUDGE_TYPE:xxx]`)
- [ ] Binary rubrics evaluated with 0/1 scale (not 1-5)
- [ ] Auto-evaluation model stored for re-evaluation consistency
- [ ] Results appear in Judge Tuning page
- [ ] Facilitator can toggle auto-evaluation and select a model at annotation start
- [ ] Annotation phase can start with auto-evaluation disabled

### Re-Evaluation
- [ ] Re-evaluate loads registered judge with aligned instructions
- [ ] Uses same model as initial auto-evaluation
- [ ] Spinner stops when re-evaluation completes
- [ ] Results stored against correct prompt version
- [ ] Pre-align and post-align scores directly comparable
- [ ] Re-evaluation computes agreement against human ratings (Cohen's Kappa over human/judge pairs), not over an empty set (`require_human_ratings=True`)

### Alignment
- [ ] Alignment jobs run asynchronously
- [ ] MemAlign distills semantic memory (guidelines)
- [ ] Aligned judge registered to MLflow
- [ ] Episodic trace IDs persist on the registered judge across alignment runs
- [ ] Re-alignment skips traces already in the judge's episodic memory
- [ ] Metrics reported (guideline count, example count)
- [ ] Works for both Likert and Binary scales

### IRR
- [ ] Krippendorff's Alpha calculated correctly
- [ ] Cohen's Kappa calculated for rater pairs
- [ ] Handles edge cases (no variation, single rater)
- [ ] Updates when new annotations added
- [ ] Traces with extreme disagreement surfaced in IRR diagnostics

## Troubleshooting

### Binary Judge Returns Likert Values

Check that:
1. Binary prefix prepended to prompt
2. `feedback_value_type=float` (not bool)
3. Fallback conversion enabled

### IRR Shows NaN

Causes:
- Only one rater
- No overlapping traces between raters
- All ratings identical (no variation)

### Alignment Fails

Check that:
- Traces have 'align' tag in MLflow
- Human feedback exists for selected traces
- Model endpoint accessible

### Auto-Evaluation Not Starting

Check that:
1. MLflow configuration is set up (Databricks host, experiment ID) and SDK auth is working
2. Rubric exists for the workshop
3. Auto-evaluation toggle is enabled
4. Model is selected in dropdown

### Re-Evaluation Shows Wrong Scores

Check that:
1. Evaluations are stored against correct prompt version
2. Re-evaluate uses `tag_type='eval'` (same traces as initial evaluation)
3. Prompt version displayed matches expected version

### Guideline Distillation Fails

Databricks models may not support the JSON schema format required for guideline distillation. In this case:
1. Alignment still succeeds using episodic memory (example-based learning)
2. Semantic memory (distilled guidelines) will be empty
3. The aligned judge uses original instructions + retrieved examples at evaluation time

## Implementation Log

| Date | Plan | Status | Summary |
|------|------|--------|---------|
| 2026-03-13 | [Trace Tag Key Separation](../.claude/plans/2026-03-13-trace-tag-key-separation.md) | complete | Fix eval/align tag mutual destruction by using dedicated MLflow tag keys |
| 2026-04-10 | [SDK Auth Migration](../.claude/plans/2026-04-10-sdk-auth-migration.md) | complete | Replace PAT token fallback in judge/alignment services with SDK auth; remove `os.environ["DATABRICKS_TOKEN"]` mutations |
| 2026-04-13 | [Critical Judge Eval Fixes](../.claude/plans/2026-04-13-critical-judge-eval-fixes.md) | complete | Fix re-eval aligned judge, preserve eval history, reject unparseable output, consolidate storage into AlignmentService |
