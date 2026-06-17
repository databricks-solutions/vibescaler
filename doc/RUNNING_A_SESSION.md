# Running a Facilitated Session

import SpecLink from '@site/src/components/SpecLink';
import useBaseUrl from '@docusaurus/useBaseUrl';

The [Facilitator Guide](FACILITATOR_GUIDE.md) covers deployment and the mechanics of each phase. This page covers the craft of the session itself — preparation, pacing, energy, and coaching reviewers — in session order.

## The opening pitch

Every session opens with some version of this. Read it aloud if it helps:

> Generic metrics — correctness, groundedness, helpfulness — don't transfer. They only become useful once they're defined in *your* domain's terms, and the only people who can define them are in this room. That's why you're here.
>
> And to be clear about what this is **not**: it's not data labeling. The frontier of AI runs on exactly what you have — expertise. Mercor became one of the fastest-growing startups ever by paying domain experts to codify their taste so models can learn from it; their CEO's framing is that ["rubrics are the new oil"](https://conversationswithtyler.com/episodes/brendan-foody/) — the most valuable input isn't more text, it's a way of *measuring success*, because a model that can score its attempts can improve. The way your domain judges its work isn't written down anywhere. It exists in your heads. Today we write it down.
>
> The rubric is the concrete mechanism: your observations become criteria, your scores calibrate a judge, and by the end of the session that judge evaluates the way you do. What makes VibeScaler different is that the rubric doesn't end as a document — it's a **living rubric**: judges aligned to it keep measuring production traffic, and it evolves as your agent and your experts do.

For the research behind rubric-based calibration (HealthBench, Mercor's ACE benchmark, the Rubric Gap), see [Grading Rubrics for AI Model Calibration](/v2/grading_rubrics_research) in the V2 section.

## Before the session: selecting discovery traces

Select for **behavioral diversity with representative samples**. The discovery set should cover the System Under Review's main trajectory types — not just its worst incidents — and include at least one clean success and one suspected failure so reviewers calibrate both ends of quality.

Just as important, the set must be **cleaned**: deduplicated, and free of traces with errors or broken outputs. An errored trace teaches the group nothing about quality and burns SME time, which is the scarcest resource in the room.

The recommended way to do this curation is with a **coding agent** (Claude Code, Cursor, or similar) rather than hand-picking traces in the UI:

1. Point the agent at the MLflow experiment and have it pull candidates with `mlflow.search_traces`.
2. Have it drop traces with error statuses, empty or truncated outputs, and obvious retries.
3. Have it deduplicate near-identical requests, then cluster what remains by observable behavior — task type, trajectory shape, tools invoked.
4. Sample across the clusters down to session size (4–5 examples per reviewer — see pacing below).
5. The output is a short list of trace IDs to select at intake, or a CSV for the upload fallback.

MLflow's issue-discovery tooling is another strong input: run [trace analysis over the experiment](https://docs.databricks.com/aws/en/mlflow3/genai/tracing/observe-with-traces/) (e.g. "discover issues with my agent's tool calling in this experiment") and use the surfaced issue clusters to decide which behaviors the discovery set must represent.

Go **targeted** instead of diverse when the Developer arrives with specific incidents they already distrust; otherwise default to diverse.

## Distributing discovery traces

VibeScaler can randomize which traces each reviewer sees in discovery, but a facilitated session is most efficient when **everyone reviews the same traces together**. The assisted-facilitation machinery feeds on several reviewers examining the same example — disagreements about the same trace are the raw material rubric criteria come from.

Per-reviewer randomization of *ordering* also exists, but it matters more in annotation (where it reduces position bias) than in discovery.

## Start with an open hand

Before reviewers split off to work independently, work the first example as an **open hand**: together, in person or on a screenshare bridge, with everyone looking at the same trace. The goal is to align SMEs on what kinds of observations are useful for rubric building — before they spend their limited energy producing the wrong kind.

## Directing reviewers to process-level feedback

For multi-agent systems, the most common question is at what depth reviewers should engage: single turn, full multi-turn trajectory, or individual sub-agent and tool-call steps.

The guidance varies by system, but the default is to direct SME attention toward the **highest-leverage feedback: process-level evaluation based on task results**. Reviewers should judge whether the overall task was accomplished well, not grade individual sub-agent hops or granular tool-call turns. The milestone view exists precisely so a reviewer can follow the trajectory's shape without descending into every call.

## Pacing the discovery phase

Budget discovery by examples, or by the clock — set a timer, or have each reviewer work through **4–5 discovery examples**.

That number comes from cognitive load, not screen time. Each example asks the reviewer for one overall rating with written feedback plus three follow-up questions — so 4–5 examples means 16–20 written responses per reviewer, and the follow-up questions in particular demand real thought. Brain power is the binding constraint of the session: conserve it deliberately.

Cut discovery early rather than letting energy die in the room. A reliable signal that the group is done is saturation — observations starting to repeat across reviewers and across traces.

## Coaching reviewers on follow-up questions

Tell reviewers up front that the generated follow-up questions are **steerable**. If a follow-up doesn't feel germane to what they actually noticed, they should say so and describe what they noticed instead — the application adapts its subsequent questions to their observation. Reviewers who don't know this will dutifully answer beside-the-point questions and burn their limited energy on them.

## From findings to rubric criteria

When discovery winds down, the facilitator's screen moves to the grouped findings: SME observations classified into themes, edge cases, boundary conditions, and failure modes, aggregated across reviewers and traces — <SpecLink spec="ASSISTED_FACILITATION_SPEC">Assisted Facilitation</SpecLink>. Walk the disagreements first; contested observations are what force the group to sharpen its definitions. The grouped findings that survive discussion are then promoted into draft rubric criteria.

Provenance travels with them: the milestone and reviewer Q&A deeplinks carry lineage from those upstream sources into the grading rubric and judge prompt, so a criterion stays traceable back to the trace milestones and question-and-answer exchanges that produced it.

## Annotation: open one hand first

When the session reaches the annotation phase, repeat the open-hand move once: label a single trace together before independent annotation begins, to remove any ambiguity about how the rubric's labels should be applied. Disagreement during one worked example is cheap; systematic mislabeling across the whole set is not.

What each reviewer then does independently — rate against the rubric criterion, explain the rating in the judge-alignment feedback box, complete the trace:

<video controls muted playsInline preload="metadata" width="100%" src={useBaseUrl('/demos/ANNOTATION_SPEC/annotation-flow.webm')} />

*This walkthrough is generated by Playwright driving the real app — see [How These Docs Work](ABOUT_THESE_DOCS.md).*

## Run judge alignment live in the room

Run the first judge alignment **live, in the room** — not after the session. Alignment takes seconds (~6s since v1.8.0), and watching a judge align to the labels they just produced is the payoff moment for SME Reviewers: the session closes with the group seeing their judgement become a working, measurable judge — <SpecLink spec="JUDGE_EVALUATION_SPEC">Judge Evaluation</SpecLink>.

## Interpreting agreement scores

When someone asks "is this agreement score good enough to trust the judge?", resist giving an absolute number. There are two distinct uncertainties in play, and the answer is comparative:

1. **Human uncertainty** — how well the SME Reviewers agree with *each other* (Krippendorff's α for Likert, Cohen's κ for binary). The application gates on κ ≥ 0.4 before judge alignment proceeds, but treat that as a floor, not a target — report the realized per-criterion agreement, not just "we passed."
2. **Judge noise** — how well the judge agrees with the SME consensus.

The human agreement is the ceiling: a judge that agrees with the SMEs about as well as the SMEs agree with each other is done, and chasing judge agreement beyond that ceiling is fitting noise. So the in-room answer sounds like "your judge is at 0.71 against a panel that agrees with itself at 0.74," not "0.7 is good."

Two practical consequences:

- **When human agreement is low, fix the rubric, not the judge.** Low IRR means the criterion is ambiguous — or that the disagreement is a genuine policy difference worth preserving rather than averaging away.
- **Sometimes another reviewer beats more traces.** Consensus over three reviewers is substantially more reliable than any individual reviewer, so adding a rater can raise the ceiling more cheaply than labeling another fifty traces.

These two scores are also what give the judge **statistical power** after the session — how much production data it takes for the judge to detect a real quality shift. Trust in any post-deployment conclusion is a function of four uncertainties: how representative the datasets are of real usage, human uncertainty, judge noise, and construct validity (whether the group picked the right criteria at all — which is why surfaced disagreement during the session matters). The production side of this loop — drift detection, re-engagement triggers — is the evaluation-ops layer; see the [Overview](OVERVIEW.md) for what's built versus coming.

## After the session: the handoff

What the Developer takes home is deliberately compact:

- **The judges** — domain-specific, calibrated, encoding the SMEs' expertise, registered in MLflow — <SpecLink spec="JUDGE_EVALUATION_SPEC">Judge Evaluation</SpecLink>.
- **An eval, created implicitly.** The rubric and the labeled traces the session produced *are* an evaluation: re-runnable against the agent as it evolves, without reassembling the SMEs.
- **Confidence you can point to.** The improvement in agreement scores (Cohen's κ, Krippendorff's α) from baseline to aligned judge is quantitative evidence that the judge reflects SME judgement rather than a prompt author's guess.

The engagement worked if, in the weeks after, the team runs evaluations on their own and comes back to the app unprompted — the SME feedback loop continuing without anyone holding their hand. One more signal worth a debrief note: whether the session surfaced genuine SME disagreement. If every reviewer agreed from the start, the use case probably didn't need a rubric.

The longer post-session loop — rubric lineage, drift detection, structured SME re-engagement — is the evaluation-ops layer, which is still maturing; see the [Overview](OVERVIEW.md) for what's built versus coming.

## When things break

The two failure sources that break sessions most often are **Lakebase** and **LLM calls hitting rate limits** — not application bugs. Triage in this order, cheapest first:

1. **Refresh the page.** Frontend state issues are the most common symptom ("the button didn't do anything", a stuck view, stale progress). A reload fixes most of them; tell reviewers this up front so they self-serve.
2. **Suspect LLM rate limits** when follow-up question generation, summarization, or findings distillation hangs or trickles. The model endpoints behind the app are shared resources — mid-session is exactly when a burst of parallel reviewers will hit limits. Pause the room for two minutes rather than letting everyone mash retry.
3. **Suspect Lakebase** when writes fail or data seems to vanish — check the database connection before debugging the app.
4. **Redeploy the app wholesale.** Some states are only recoverable by redeployment. It costs minutes, not hours — if you've spent ten minutes debugging mid-session, redeploy and use an open-hand discussion to keep the room engaged while it comes back.

## Self-serving the next use case

Teams running follow-on use cases without an external facilitator keep the tool but lose the convening power: a facilitated workshop gives an organization permission to put a cross-functional group in one room for a day with a single objective. That mandate — not any feature of the app — is what the format quietly depends on, and it diffuses once the external occasion is gone.

So when self-serving, treat the format as non-negotiable:

- **Block a contiguous session with one objective** — one use case, one rubric. Don't let it become a standing 30-minute meeting.
- **Get the actual SMEs**, synchronously, in a room or on a bridge — not delegates, not async comments.
- **Appoint a facilitator.** The role matters even when it isn't an outsider: someone must own pacing, the open hands, and cutting discovery at saturation.

The biggest self-service risk isn't operating the app — it's letting the session dissolve into drive-by, asynchronous feedback. The methodology assumes synchronized attention.
