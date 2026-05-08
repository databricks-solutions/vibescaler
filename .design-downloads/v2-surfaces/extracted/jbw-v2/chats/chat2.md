# Facilitator Workshop Creation

_Started 2026-04-28 13:35 UTC_

---

## User

We need another view for the facilitator that's creating a new workshop + sprint. Interview me to understand the intent and how it relates to the other flows

## Assistant

Let me first explore the existing project to understand the context before interviewing you.

_[tool: list_files]_

_[tool: local_ls]_

_[tool: read_file]_

_[tool: read_file]_

_[tool: read_file]_

I have enough context now. Let me look briefly at the other flows to ground my questions, then interview you.

_[tool: read_file]_

_[tool: read_file]_

_[tool: read_file]_

Good — I've got the lay of the land. JBW v2 has three flows already: facilitator dashboard (running a live session), reviewer feed (rating), and rubric editor. The new view sits **upstream** of all of these: the moment a facilitator decides "I want to run a workshop/sprint" and assembles it before kickoff.

Some sharp questions before I design — answers will shape this a lot.

_[tool: questions_v2]_

## Assistant

I have enough context now. Here's what I understand about the existing flows:

- **Facilitator dashboard** — three variations of the live/orchestration view *during* a running session (Cockpit, Pass plan, Trace funnel)
- **Reviewer feed** — where raters do the actual rating work
- **Rubric editor** — crafting and calibrating rubric criteria

The new view sits **upstream** of all of these: the moment a facilitator decides "I want to evaluate something" and configures a workshop + sprint before any rater is invited. Let me ask focused questions before designing.

_[tool: questions_v2]_

## User

Questions timed out; go with defaults

## Assistant

_[tool: snip]_

## User

ask me the questions again

## Assistant

_[tool: questions_v2]_

## User

Actually read this and then ask again

## Assistant

Got it — that's a much cleaner model. The workshop is the persistent substrate (rubric + judge + trace pool + SMEs); a sprint is one parameterized run of the convergence loop. They're **distinctly different things** with very different lifespans, configs, and creation triggers.

This changes my questions significantly. Let me re-ask.

_[tool: questions_v2]_

## User

Questions answered:
- workshop_vs_sprint: Workshop = long-lived container (a project / domain like 'Healthcare-A'); Sprint = one rating pass inside it
- scope: Both -- I need to work through the UX for developers and how it impacts the rest of the flows 
- primary_target: The first-time / day-one path is most important — someone bootstrapping a brand new workshop
- workshop_inputs: Workshop name + short description (e.g. 'support-agent-eval'), What's being calibrated — the agent / system the judge will grade, Starter rubric — from template, AI-drafted from goals, imported, or empty, Starter judge — model + prompt template, Trace pool should be how does the developer get a representative sample from the mlflow experiment (we are using judges for this) and how do the generated summaries look, Participants — add facilitators / SMEs / devs with roles
- sprint_inputs: Participant subset — which SMEs from the pool join this sprint, Trace selection — N traces, sampling strategy (links to Trace Funnel), This depends on outcome! WE have eval mode and judge tuning mode - one is rubric per example the other is global rubrics. 
- variation_count: 3
- ai_role: Multiple levels across variations
- convergence_visibility: Decide for me
- trace_pool_handling: It's exactly right for them to overlap, if 3 traces are used in an initial sprint, they are the prior distribution and it's a critical job that as we see more traces we update the distribution based on that 
- rubric_handling_workshop: Show me options for this - it will be some combination of all
- first_sprint_after_workshop: Auto-create the first sprint right after the workshop is created — single combined flow ends in the dashboard
- tone_visual: Push — new view = chance for a more striking entry experience

## Assistant

_[tool: update_todos]_

_[tool: read_file]_

_[tool: read_file]_

_[tool: snip]_

I have what I need to design. Let me lay out my plan before writing code.

**Design system understanding:**
- Inter / Source Serif 4 / JetBrains Mono
- Calm paper canvas (oklch warm whites), indigo accent, organic blob avatars as DNA element
- Existing components: `Blob`, `Avatar`, `Dot`, `I.*` icons, chips, btn, card, eyebrow, dotline
- Each variation lives in a `<DCArtboard>` at 1280×820

**The two flows I'll build (3 variations each):**

**Workshop (day-one bootstrap)** — emphasis since user said it's primary
- **A · Conversational brief** — facilitator describes intent in plain English; right-pane live-builds the workshop config. AI-generative.
- **B · Recipe + canvas** — start from a domain template (support agent, clinical advice, translation, finance), then customize all four owned things (rubric, judge, trace pool, SMEs) on a single long-form page. Suggestive AI.
- **C · Foundation builder** — long-form, opinionated wizard-on-one-page that emphasizes the *trace pool sampling problem* (representative MLflow sampling + summary preview), since user explicitly called this out as a critical job.

**Sprint (recurring "push it forward")** — invoked from inside an existing workshop
- **A · Mode-first card pick** — pick "Eval mode" (rubric per example) vs "Judge tuning" (global rubric) up top, then preset (bootstrap / harden / recurring) shapes everything else.
- **B · Targets dial** — convergence-target-first; you set IRR + alignment goals, system reverse-engineers N traces, overlap, timebox.
- **C · Diff-from-last** — recurring case; shows last sprint's outcome and proposes "the same but with these 3 changes" — emphasizes how trace pool distribution updates.

System: warm paper, indigo accent, organic blobs as visual heroes for "create" moments. I'll push the entry experience with bigger serif type and more deliberate use of blob imagery, while keeping all chrome consistent.

Let me build it. I'll create two new files (`workshop-create.jsx` and `sprint-create.jsx`) to keep dashboard.jsx clean.

_[tool: write_file]_

_[tool: snip]_

Now the sprint-create file.

_[tool: write_file]_

_[tool: snip]_

_[tool: str_replace_edit]_

_[tool: str_replace_edit]_

_[tool: done]_

_[tool: snip]_

_[tool: fork_verifier_agent]_

Added two new sections to the canvas, upstream of the existing facilitator dashboard:

**Workshop — day-one bootstrap** (3 variations)
- **A · Conversational brief** — generative AI: describe intent in plain English, the right pane live-builds the workshop spec (rubric, judge, pool, SMEs)
- **B · Recipe + canvas** — suggestive AI: pick a domain recipe (support, clinical, translation, finance, blank), customize the four owned things on a single page. Trace pool gets a hero treatment with judge-written summary previews
- **C · Foundation builder** — opinionated 4-step ladder that puts the *representative MLflow sampling* problem front and center: funnel viz, topic-balance check, summary quality flagging

**Sprint — push it forward** (3 variations)
- **A · Mode + preset** — Eval mode (per-example rubric) vs Judge tuning (global rubric), then bootstrap/harden/recurring preset shapes everything; ends with a "loop" diagram
- **B · Targets-first dial** — set IRR + judge-alignment + confidence; system reverse-engineers N traces, k-overlap, timebox, with reasons
- **C · Diff from last** — recurring case: shows last sprint's outcome + 3 proposed changes, plus how the trace pool prior is updating across sprints (the critical feedback loop you flagged)

The first sprint is auto-staged after workshop creation in all three workshop variations. Trace-pool overlap with Trace Funnel is intentional — Variation C of sprint shows how the prior compounds across sprints.

