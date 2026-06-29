# VibeScaler Overview

import SpecLink from '@site/src/components/SpecLink';

VibeScaler turns subject-matter-expert judgement into calibrated LLM judges, inside a single Databricks App, driven by one input: an MLflow experiment ID. The Developer surface is a Workspace — an activity monitor for the four Evaluation Goals: **human agreement**, **judge agreement**, **construct validity**, and **judge confidence**.

The difference in one phrase: a **living rubric**. The rubric your experts produce doesn't end as a document — judges aligned to it keep measuring production traffic, and it evolves with your agent and your experts.

> VibeScaler was previously known as the Judge Builder Workshop; some screens and pages still use the older name.

Two roles appear throughout these docs: the **Developer**, who owns the agent under evaluation and operates the Workspace, and the **SME Reviewer**, the domain expert whose judgement the system captures. Judge optimization itself is algorithmic — today MemAlign and MLflow `align()`.

Spec links throughout these docs carry a completion bar showing how much of that feature's spec is verified by tests — an at-a-glance signal of whether the content under discussion is speculative or extremely well-tread. See [How These Docs Work](ABOUT_THESE_DOCS.md) for the full legend.

## What does VibeScaler support

Any system that produces MLflow traces — and, via CSV upload, systems that don't yet. What changes by agent type is the recommended setup:

| When you have | Do | Consider |
|---------------|----|----------|
| A single-turn agent (Q&A, RAG, extraction) | Ingest from the MLflow experiment and have reviewers read traces directly — full depth is affordable | <SpecLink spec="TRACE_DISPLAY_SPEC">JSONPath input/output extraction</SpecLink> so reviewers see the right fields, not raw payloads |
| A multi-turn conversational agent | Have reviewers judge at the task level: did the conversation accomplish the user's goal | <SpecLink spec="TRACE_SUMMARIZATION_SPEC">Trace summarization</SpecLink> if conversations run long |
| A multi-agent system with tool calling or Genie sub-agents | Enable <SpecLink spec="TRACE_SUMMARIZATION_SPEC">trace summarization</SpecLink> so reviewers work in the milestone view, and direct feedback at the process level — task results, not sub-agent turns | Curating shorter, representative trajectories; keeping the discovery set small to protect reviewer attention |
| A very complex agent on long-horizon tasks, where one rubric won't generalize across traces | Use <SpecLink spec="EVAL_MODE_SPEC">Eval Mode</SpecLink>: per-trace criteria evaluated benchmark-style | Hurdle and weighted criteria for composite scoring |
| An app not yet instrumented with MLflow tracing | Start with the <SpecLink spec="TRACE_INGESTION_SPEC">CSV upload fallback</SpecLink> | Adding [MLflow Tracing](https://docs.databricks.com/aws/en/mlflow3/genai/tracing/) so ingestion, lineage, and evaluation ops work end-to-end |

See [Running a Facilitated Session](/RUNNING_A_SESSION) for how these choices play out live.

## Select Evaluation Traces

The Developer defines the System Under Review and selects diverse or targeted traces to put in front of reviewers.

**Built today**

- Trace ingestion from an MLflow experiment ID, with CSV upload as a fallback — <SpecLink spec="TRACE_INGESTION_SPEC">Trace Ingestion</SpecLink>
- Milestone view that lets non-technical SME Reviewers follow multi-agent trajectories, including tool calling and Genie sub-agents — <SpecLink spec="TRACE_SUMMARIZATION_SPEC">Trace Summarization</SpecLink>

## Curate the Review Feed

The Developer builds an evolving Review Feed of traces and review questions. From the feed, Datasets emerge for criteria elicitation, judge alignment, monitoring, and audit.

**Built today**

- Manual and random trace selection, per-reviewer randomization, and dataset slicing — <SpecLink spec="DATASETS_SPEC">Datasets</SpecLink>
- Phase-aware trace assignment and visibility — <SpecLink spec="DISCOVERY_TRACE_ASSIGNMENT_SPEC">Trace Assignment</SpecLink>

**Coming**: agentic curation, disagreement-aware sampling, natural-language trace search, batch analytics for behavior distribution.

## Elicit Rubric Criteria

SME feedback becomes rubric Criteria, closing the gap between model-generated rubrics and what experts actually mean. In production use, a single facilitated session has turned 144 raw observations from 12 SME Reviewers into 3 calibrated rubric criteria with aligned judges.

**Built today**

- LLM-generated follow-up questions during trace review — <SpecLink spec="DISCOVERY_SPEC">Discovery</SpecLink>
- LLM distillation of SME observations into structured Findings — <SpecLink spec="ASSISTED_FACILITATION_SPEC">Assisted Facilitation</SpecLink>
- Multi-criteria rubric authoring (binary, scalar, Likert, weighted, hurdle, atomic, composite, and skills-based criteria) plus Markdown rubric authoring — <SpecLink spec="RUBRIC_SPEC">Rubric</SpecLink>

## Codify SME Judgement

SME Reviewers express domain judgement as rubric-contextual Assessments: scores, rationales, reactions, and Discussion Comments. The Discussion Layer is the native substrate for SME dialogue; MLflow Feedback is an export shape, not the full feedback model.

**Built today**

- Multi-reviewer assessment UI — <SpecLink spec="ANNOTATION_SPEC">Annotation</SpecLink>
- Krippendorff's α (Likert) and Cohen's κ (binary) agreement, with ranked surfacing of controversial traces — <SpecLink spec="JUDGE_EVALUATION_SPEC">Judge Evaluation</SpecLink>
- Per-reviewer Developer dashboard, randomization, and subset selection

## Improve Evaluation Confidence

The Developer measures and improves trust in the rubric-based evaluation system, assisted by the judge optimizer algorithms.

**Built today**

- Inline `mlflow.genai.evaluate` baseline and registered scorer output — <SpecLink spec="JUDGE_EVALUATION_SPEC">Judge Evaluation</SpecLink>
- Continuous Judge Alignment via `align()` (SIMBA / MemAlign) — alignment time reduced from 30 minutes to ~6 seconds as of v1.8.0
- Inter-rater reliability diagnostics
- One-click GEPA prompt optimization against the project rubric — <SpecLink spec="EVAL_MODE_SPEC">Eval Mode</SpecLink>

**Coming**: the judge as an active learner.

## Run Evaluation Ops

The Developer operates the rubric-based evaluation system in production: lineage, audit, drift detection, and ongoing SME Reviewer re-engagement. This is the foundational layer.

**Built today**

- Lakebase persistence — <SpecLink spec="BUILD_AND_DEPLOY_SPEC">Build & Deploy</SpecLink>

**Coming**: Rubric Lineage from each criterion back to its source traces, Discussion Comments, and SME judgement; a per-reviewer next-best feed.

## Where to go next

- [Running a Facilitated Session](RUNNING_A_SESSION.md) — preparation, pacing, and coaching for live sessions
- [Facilitator Guide](FACILITATOR_GUIDE.md) — deployment and phase-by-phase mechanics
- [The Discovery Stage](DISCOVERY.md) — the criteria-elicitation flow in depth
- [Specs Index](/specs/) — technical specifications for every feature
