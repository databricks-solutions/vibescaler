---
draft: true
---

# Using VibeScaler with Coding Agents

This repository is built to be worked on — and operated — with coding agents like Claude Code and Cursor. This page covers both directions: how the repo is structured so agents can contribute safely, and how to use these docs as agent context when facilitating.

## How the repository is set up for agents

The full contract is [CONTRIBUTING.md](https://github.com/databricks-solutions/project-0xfffff/blob/main/CONTRIBUTING.md) in the repository. The short version — this repo follows **spec-driven development**:

```
Specs (/specs) ──define──▶ Code (/server, /client) ◀──verify── Tests (/tests)
        └──────────── linked via spec markers ────────────┘
                    @pytest.mark.spec("SPEC_NAME")
```

- **Specs are the source of truth.** Every behavior is governed by a spec in `/specs` (the same documents in this site's Specs tab). Agents read the spec before writing code, and stop to ask rather than guess at undefined behavior.
- **Every test is tagged to its spec** (`@pytest.mark.spec(...)` in pytest, `@spec:...` in Playwright, `// @spec` in Vitest). The coverage analyzer turns those tags into the verification data behind the spec-link bars throughout these docs.
- **Guardrails are explicit.** Spec edits, database migrations, and file deletion require human approval; tests, linting, and reads are pre-approved. Agent instructions live in `.claude/CLAUDE.md`, and repo-specific skills (brainstorming from specs, spec coverage auditing, verification testing, MLflow evaluation patterns) ship in `.claude/skills/` where Claude Code discovers them automatically.
- **`just` is the agent's toolbelt.** `just spec-coverage`, `just test-affected`, `just e2e-spec SPEC_NAME`, `just docs-demos`, `just docs-gate` — agents verify their own work with the same recipes humans use.

## Using these docs as agent context

The docs themselves are designed to be agent-legible: specs declare behavior with checkable success criteria, coverage data says what's actually verified, and the guides carry the operating knowledge. That makes them effective context for an agent helping you run an engagement:

- **Curating traces.** The recommended pre-session workflow *is* a coding agent — point it at the MLflow experiment and the curation recipe in [Running a Facilitated Session](RUNNING_A_SESSION.md), and have it produce the cleaned, behaviorally diverse discovery set.
- **Prepping to facilitate.** Give an agent [Running a Facilitated Session](RUNNING_A_SESSION.md), the [FAQ](FAQ.md), and the [Facilitator Guide](FACILITATOR_GUIDE.md) as context and rehearse: ask it to quiz you on pacing, the open-hand moves, and how you'll answer the agreement-score question.
- **Answering "how does X actually work."** Feed the relevant spec (linked inline throughout these docs) rather than the implementation — specs are smaller, declarative, and carry success criteria the agent can quote back.
- **Regenerating docs media.** UI screenshots and walkthrough videos are produced by Playwright demo specs (`client/tests/demos/`) — an agent can extend a demo and run `just docs-demos` to refresh every asset after a UI change.

A note on freshness: anything an agent reads here is held to the same standard as a human reader — `just docs-gate` blocks publishing when a page references a spec whose tests are failing, so agent answers grounded in these docs inherit that guarantee.
