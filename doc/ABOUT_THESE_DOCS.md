# How These Docs Work

import SpecLink from '@site/src/components/SpecLink';
import useBaseUrl from '@docusaurus/useBaseUrl';

These docs are organized along the two axes of [Diátaxis](https://diataxis.fr/):

- **Cognition axis** (understanding how the system behaves) — the [Specifications](/specs/). This repository follows spec-driven development: specs are the source of truth, code follows them, and tests prove compliance. When you want to know exactly how a feature works, the spec is the most reliable document in this site.
- **Action axis** (getting things done) — the guides: the [Overview](/OVERVIEW) for orientation, [Lakebase Setup](/lakebase-setup) and the [Facilitator Guide](/FACILITATOR_GUIDE) for deployment and mechanics, and [Running a Facilitated Session](/RUNNING_A_SESSION) for live-session craft.

## Spec links are live, like doctests

The inspiration is Rust doctests: documentation shouldn't merely describe behavior — it should be directly associated with the tests that verify it, so you know how the system is *actually* working rather than how someone hoped it would.

Every test in this repository is tagged to its governing spec (`@pytest.mark.spec("SPEC_NAME")` in pytest, `@spec:SPEC_NAME` in Playwright/Vitest). A coverage analyzer turns those tags into per-spec verification data, and the docs render it two ways:

1. **Inline spec links**, like <SpecLink spec="DATASETS_SPEC">Datasets</SpecLink> — the bar shows what fraction of that spec's success criteria are verified by tests:

   | Bar | Coverage | Read it as |
   |-----|----------|------------|
   | Mostly full (green) | ≥ 70% | Well-tread — behavior is verified, rely on it |
   | Partial (amber) | 30–69% | Maturing — core works, edges may shift |
   | Low or empty (grey) | < 30% or no data | Early — treat the discussed behavior as speculative |

2. **Coverage blocks** at the top of every spec page — the full breakdown: each success criterion, whether it's covered, and exactly which tests verify it.

Coverage is regenerated from the test suite on every docs build, so the bars reflect the current state of verification — not aspiration.

## Stale docs can't publish

Freshness is enforced at publish time, not just displayed. `just docs-gate` cross-references every spec mentioned in these pages against the latest test results: if a page describes a feature whose spec-tagged tests are currently failing, the gate fails and the docs don't ship until either the tests or the docs are fixed. What you read here described a working feature when it was published.

## UI walkthroughs are generated, not hand-captured

The same idea extends to media. Screenshots and video walkthroughs in these docs are produced by Playwright **driving the real application** — the demo specs (`client/tests/demos/*.demo.ts`) reuse the E2E suite's scenario tooling to set up a workshop, log in as a reviewer, and perform the flow being documented, recording as they go:

```bash
just docs-demos   # regenerates docs/static/demos/<SPEC_NAME>/*.{png,webm}
```

Because the media is generated from the live app, it can't silently drift from reality the way hand-captured screenshots do: when the UI changes, rerunning one command re-captures every walkthrough. Artifacts are organized per spec, so each walkthrough sits next to the coverage data for the behavior it shows.

<img src={useBaseUrl('/demos/ANNOTATION_SPEC/annotation-interface.png')} alt="Generated screenshot of the SME annotation interface" width="100%" />

*Example: the SME annotation interface, captured by `just docs-demos`.*
