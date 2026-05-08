# Version Control Strategy

_Started 2026-05-07 15:25 UTC_

---

## User



## Assistant

I'll explore the project structure first, then read the referenced docs to ground the design.

_[tool: list_files]_

_[tool: list_files]_

I'll explore the existing project structure to understand the design vocabulary already in use, then build the V2 Workspace prototype.

_[tool: read_file]_

_[tool: read_file]_

I'll continue exploring the existing project to understand the design vocabulary before building.

_[tool: read_file]_

I have a clear understanding of the project now. Let me check a couple more existing files to match the design vocabulary, then build the Workspace.

_[tool: read_file]_

I have plenty of context to build the Workspace prototype now. Let me look at one of the existing dashboard files quickly to match the visual idiom, then build.

_[tool: read_file]_

_[tool: read_file]_

I have enough context. Let me build the Workspace prototype with three design directions, plug it into the existing design canvas, and snip earlier exploration messages.

_[tool: snip]_

I'll build the Workspace prototype now. Three directions, registered as a new section in the design canvas.

_[tool: write_file]_

Now I'll wire the new Workspace section into the app and design canvas.

_[tool: str_replace_edit]_

Now I'll add the Workspace section to the app entry, near the top so it's the headline content.

_[tool: str_replace_edit]_

_[tool: snip]_

Now let me verify the prototype loads cleanly.

_[tool: done]_

_[tool: snip]_

_[tool: fork_verifier_agent]_

Built three Workspace directions wired into the design canvas at the top of `index.html`:

- **A · Control Room** — compact four-column spine with a metric ring strip up top; Data Source / Review Feed / Grading / Confidence each as a dense panel; lineage chip on c2; blocker card + readiness bar on the right.
- **B · Activity Monitor** — training-run trajectories chart for all four sprint metrics with dashed projections to target; left timeline rail; per-column activity feeds with mini metric bars.
- **C · Narrative** — hero "what needs to happen next" prescription up top; each column tells its part of the story (mood-coded headline, bullets, single next action); c2 lineage diagram in the Grading column.

How each direction answers the brief, briefly:

- **Knowing what to do next.** A surfaces it as a blocker card in column 4. B as the latest items in the timeline + flagged trajectory slope. C makes it the entire hero block — one prescription that names the rubric change and the SME route.
- **Four sprint metrics.** A: ring + sparkline strip. B: overlaid trajectories with target lines and now-marker. C: 2×2 grid where the stuck one (CV) tints red.
- **Lineage from source to criterion.** A: inline `↗N` link per criterion + a lineage callout. B: rubric events live in the Grading timeline column. C: a small dependency diagram (traces + threads + judgements → c2).
- **Discussion Layer.** A: dedicated card in Review Feed with an "open pane" affordance + lineage on c2 in Grading. B: discussion events appear as their own timeline kind. C: a "1 unresolved thread" bullet with a discussion-pane CTA.
- **When a metric is stuck.** All three flag CV explicitly (red tint, "stuck 36h"). A puts the recommended action in the blocker card; B shows the flat slope and a "propose" timeline event; C builds the whole top of the page around it.

Verifier is checking the layouts in the background.

## User

Verifier agent check completed

## Assistant

_[tool: snip]_

Verifier passed on all three directions. The minor IRR eyebrow wrapping note is fine to leave — it stays legible and the directions are meant to be compared side-by-side first, then refined.

## User



## Assistant

I'll snip earlier completed work and then plan this larger task.

_[tool: snip]_

I'll plan, then build the four surfaces in a single new file to keep things compact, registering each as a Workspace-adjacent section.

_[tool: update_todos]_

I'll build the four surfaces, splitting across files to keep them maintainable. Let me start with Review Feed and Grading.

_[tool: write_file]_

I'll continue building the remaining surfaces — Grading, Evaluation Ops, and Settings/Setup — and wire them in.

_[tool: write_file]_

_[tool: update_todos]_

_[tool: write_file]_

_[tool: write_file]_

_[tool: snip]_

_[tool: update_todos]_

_[tool: list_files]_

Let me check the existing index/app structure to wire in correctly.

_[tool: read_file]_

_[tool: read_file]_

_[tool: snip]_

_[tool: str_replace_edit]_

_[tool: str_replace_edit]_

_[tool: done]_

_[tool: snip]_

_[tool: update_todos]_

_[tool: fork_verifier_agent]_

Added four new surfaces to the canvas:

**Review Feed** — Reviewer cockpit (single-trace + Discussion companion) · Curator's stream (feed-as-operating-model with optimizer rail) · Pair view (blind | reaction).

**Grading** — Criterion deep-dive (alignment, lineage, proposals, underlying judges) · Rubric matrix (criteria × traces heatmap) · Versions & lineage (diff with downstream effects).

**Evaluation Ops** — Production console (signals + recommendations across the four levers) · Incident lineage (5-swimlane traceback to feed evidence) · Sprint trigger (production drafts the next sprint).

**Settings / Setup handoff** — Durable project settings · First-run setup that drains into a starter Workspace · Living settings as a Workspace sidebar (setup is just the first time you open it).

The workshop scenario (warfarin → c2 split → pediatric incident) runs as a continuous thread across all four surfaces so lineage is visible end-to-end.

## User

Verifier agent check completed

## Assistant

I'll fix the name collisions. The Sparkline collision in evalops crashes dashboard. Let me also rename the other helpers per the verifier's note.

_[tool: grep]_

I'll fix all the name collisions by prefixing helpers with file-specific tags.

_[tool: snip]_

I'll do find-and-replace via run_script to rename all collisions efficiently.

_[tool: run_script]_

_[tool: snip]_

_[tool: done]_

_[tool: fork_verifier_agent]_

Fixed the helper-name collisions by prefixing helpers with file-specific tags (RF / GR / EO / ST). Dashboard's `Sparkline` is no longer shadowed.

## User

This is good, are we able to distinguish the new components from the old or otherwise create a new version?

## Assistant

Yes — easiest path is to make a v2 of just the new surfaces in their own canvas file, so the old work stays intact. Want me to:

**Option A — separate file** · `index-v2-surfaces.html` that loads only the four new sections (Review Feed, Grading, Eval Ops, Settings). Cleanest separation, easy to share standalone.

**Option B — section toggle in current canvas** · keep one file but add a Tweak to filter to "new surfaces only" vs "all". Useful for compare.

**Option C — copy the four files to `*-v2.jsx`** · gives you a snapshot you can iterate on without touching what's there.

Which would you like? My recommendation is **A** for clarity — you can link the v2 file to reviewers without the older Workspace/Setup/Workshop sections in the way.

## User

Separate file

## Assistant

_[tool: snip]_

_[tool: write_file]_

_[tool: write_file]_

_[tool: done]_

_[tool: snip]_

Created `index-v2-surfaces.html` — a standalone canvas with only the four new surfaces (Review Feed, Grading, Evaluation Ops, Settings/Setup). The original `index.html` is untouched. Both files share the same source modules so edits to a surface stay in sync across both views.

