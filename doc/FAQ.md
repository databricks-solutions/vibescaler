# Frequently Asked Questions

Questions that come up repeatedly across real engagements, with the canonical answers.

## Do we need labeled data before a session?

**No — labels are an output of the session, not an input.** The general format is:

> Inputs/Outputs → SMEs decide on one or more rubric criteria → label based on those criteria → align the judge based on the labels.

Arriving with a pre-built labeled dataset and output schema usually means steps were skipped: the labels encode definitions of quality that the group never agreed on, which is exactly what the discovery and rubric phases exist to produce.

## How many traces do we need?

On the order of **50–200 traces** of the System Under Review. Traces in an MLflow experiment are the preferred path; traces from outside MLflow can come in through the CSV upload fallback. Only a small curated subset (4–5 per reviewer) is used in discovery — the rest feed annotation, alignment, and evaluation. See [Running a Facilitated Session](RUNNING_A_SESSION.md) for how to curate the discovery subset.

## Can one session cover multiple use cases?

**One use case per session.** Mixing use cases muddies the rubric — criteria elicited for one task rarely transfer cleanly to another. When a team has several use cases, run a facilitated session for the first; the team can typically self-serve the rest using the same deployment and these docs.

## How does VibeScaler relate to MLflow judge alignment and annotation?

They're layers, not alternatives. MLflow provides the primitives: `mlflow.genai.evaluate`, judge alignment via `align()` (SIMBA / MemAlign), and Feedback. VibeScaler orchestrates those primitives into a facilitated methodology — criteria elicitation, the discussion layer, multi-reviewer assessment, inter-rater reliability, and judge alignment in one flow. If you only need to align an existing judge against existing labels, the MLflow API alone may be enough; VibeScaler is for producing the rubric, the labels, and the shared definition of quality in the first place.

## Who should attend a session?

The **SME Reviewers** — the domain experts whose judgement defines quality, who are often non-technical — plus the **Developer** who owns the agent. A session attended only by technical staff misses the point: the goal is construct validity, and that requires the people who actually know what "good" means in the domain.

## When is this the right tool?

Two recurring situations:

- An agent is **stuck in pilot** because nobody can prove it's reliable enough to ship.
- An agent is **already in production** but quality work is anecdotal — there's no systematic, trusted way to measure whether changes make it better or worse.

In both cases the missing piece is an evaluation system the organization actually trusts, which is what the rubric-plus-aligned-judges loop produces.
