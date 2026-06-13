#!/usr/bin/env python3
"""Docs health gate: refuse to publish docs that describe broken features.

Scans the prose docs (doc/*.md) for spec references — inline <SpecLink
spec="..."> components and /specs/<NAME> links — then checks the latest test
results (.test-results/*.json, the same reports `test-summary` reads). If any
referenced spec has failing tagged tests, the gate fails with a listing of
which pages reference which failing specs.

Intended for CI before building/publishing the docs site:

    just test ... && just docs-gate && just docs-build

Exit codes:
    0  all referenced specs are green (or have no tagged tests failing)
    1  one or more referenced specs have failing tests — do not publish
    2  no test reports found — run the test suite before gating
"""

import re
import sys
from pathlib import Path

from test_summary import (
    RESULTS_DIR,
    parse_playwright_report,
    parse_pytest_report,
    parse_vitest_report,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
DOC_DIR = REPO_ROOT / "doc"

SPEC_REF_PATTERNS = [
    re.compile(r'<SpecLink\s+spec="([A-Z0-9_]+_SPEC)"'),
    re.compile(r"/specs/([A-Z0-9_]+_SPEC)"),
]


def spec_references() -> dict[str, set[str]]:
    """Map spec name -> set of doc pages (relative paths) referencing it."""
    refs: dict[str, set[str]] = {}
    for doc_path in sorted(DOC_DIR.glob("*.md")):
        text = doc_path.read_text(encoding="utf-8")
        for pattern in SPEC_REF_PATTERNS:
            for spec in pattern.findall(text):
                refs.setdefault(spec, set()).add(str(doc_path.relative_to(REPO_ROOT)))
    return refs


def main() -> int:
    report_paths = [RESULTS_DIR / name for name in ("pytest.json", "playwright.json", "vitest.json")]
    if not any(p.exists() for p in report_paths):
        print("docs-gate: no test reports found in .test-results/ — run the test suite first.")
        return 2

    summaries = [
        parse_pytest_report(report_paths[0]),
        parse_playwright_report(report_paths[1]),
        parse_vitest_report(report_paths[2]),
    ]

    failures_by_spec: dict[str, list[str]] = {}
    for summary in summaries:
        for failure in summary.failures:
            spec = failure.spec or "UNTAGGED"
            label = f"{failure.file_path}{f' ({failure.name})' if failure.name else ''} [{summary.runner}]"
            failures_by_spec.setdefault(spec, []).append(label)

    refs = spec_references()
    stale = {spec: pages for spec, pages in refs.items() if spec in failures_by_spec}

    if not stale:
        total_failed = sum(s.failed for s in summaries)
        suffix = "" if total_failed == 0 else f" ({total_failed} failures exist, but none tagged to a doc-referenced spec)"
        print(f"docs-gate: OK — {len(refs)} referenced specs are green{suffix}.")
        return 0

    print("docs-gate: FAIL — docs reference specs whose tests are failing. Do not publish.")
    for spec in sorted(stale):
        print(f"\n  {spec} — referenced by: {', '.join(sorted(stale[spec]))}")
        for test in failures_by_spec[spec]:
            print(f"    failing: {test}")
    print("\nFix the tests (or the docs) before publishing.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
