# How this project works

import SpecLink from '@site/src/components/SpecLink';
import useBaseUrl from '@docusaurus/useBaseUrl';

VibeScaler is built **spec-first**. A small set of specifications in the [Specifications](/specs/) section is the source of truth for how the product behaves: the code follows the specs, automated tests prove the code matches them, and these docs render that proof inline. The same loop is what lets coding agents extend the product without drifting from intent.

```
Specs (/specs) ──define──▶ Code (/server, /client) ◀──verify── Tests (/tests)
        └──────────── linked by spec markers ───────────┘
                   @pytest.mark.spec("SPEC_NAME")
```

## Specs are the source of truth

Every behavior is governed by a spec — a short, declarative document with explicit success criteria — in the [Specifications](/specs/) section. Code in `/server` and `/client` implements those specs; it doesn't invent behavior. When a spec is silent on a case, that's a gap to resolve *in the spec*, not a guess to bury in code. If you want to know exactly how a feature is meant to work, the spec is the most reliable document on this site.

## Tests verify it — and these docs show the proof

The inspiration is Rust doctests: documentation shouldn't merely *describe* behavior, it should be tied to the tests that *verify* it — so you see how the system actually works, not how someone hoped it would.

- **Every test is tagged to its spec** — `@pytest.mark.spec("SPEC_NAME")` in pytest, `@spec:SPEC_NAME` in Playwright, `// @spec SPEC_NAME` in Vitest.
- A **coverage analyzer** turns those tags into per-spec verification data, regenerated on every docs build — so the numbers reflect the current state of verification, not aspiration.

The docs surface that data two ways:

1. **Inline spec links** like <SpecLink spec="DATASETS_SPEC">Datasets</SpecLink> — the bar shows what fraction of that spec's success criteria are verified by tests:

   | Bar | Coverage | Read it as |
   |-----|----------|------------|
   | Mostly full (green) | ≥ 70% | Well-tread — behavior is verified, rely on it |
   | Partial (amber) | 30–69% | Maturing — core works, edges may shift |
   | Low or empty (grey) | < 30% or no data | Early — treat the discussed behavior as speculative |

2. **Coverage blocks** at the top of every spec page — each success criterion, whether it's covered, and exactly which tests verify it.

**Stale docs can't publish.** `just docs-gate` cross-references every spec mentioned in these pages against the latest test results: if a page describes a feature whose spec-tagged tests are failing, the gate fails and the docs don't ship until either the tests or the docs are fixed. What you read here described a working feature when it was published.

**Walkthroughs are generated, not hand-captured.** Screenshots and videos are produced by Playwright *driving the real application* (`client/tests/demos/*.demo.ts`), so they can't silently drift from reality — when the UI changes, one command re-captures every asset:

```bash
just docs-demos   # regenerates docs/static/demos/<SPEC_NAME>/*.{png,webm}
```

<img src={useBaseUrl('/demos/ANNOTATION_SPEC/annotation-interface.png')} alt="Generated screenshot of the SME annotation interface" width="100%" />

*Example: the SME annotation interface, captured by `just docs-demos`.*

## Coding agents close the loop

This repository is built to be worked on — and operated — with coding agents like Claude Code and Cursor, using the same loop:

- **Agents read the governing spec before writing code**, and stop to ask rather than guess at undefined behavior.
- **Guardrails are explicit.** Editing specs, creating migrations, changing auth, deleting files, and `git push` require human approval; running tests, linting, and reads are pre-approved. Agent instructions live in `.claude/CLAUDE.md`; repo-specific skills (brainstorming from specs, coverage auditing, verification testing) ship in `.claude/skills/`.
- **`just` is the shared toolbelt.** `just spec-coverage`, `just test-affected`, `just e2e-spec SPEC_NAME`, `just docs-gate` — agents verify their own work with the same recipes humans use.
- **These docs double as agent context.** Feed an agent the relevant spec (small, declarative, with checkable success criteria) rather than the implementation — it's better grounding, and anything it reads here inherits the freshness guarantee above.

The full contributor workflow — implementing a feature, the test-tagging syntax, and verification commands — lives in [CONTRIBUTING.md](https://github.com/databrickslabs/vibescaler/blob/main/CONTRIBUTING.md).
