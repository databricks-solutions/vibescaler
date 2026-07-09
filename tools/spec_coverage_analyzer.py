"""
Spec Coverage Analyzer

Scans test files for spec coverage markers/tags and generates a coverage report
showing requirement-level coverage across the full test pyramid.

Supported conventions:
- pytest:     @pytest.mark.spec("SPEC_NAME"), @pytest.mark.req("requirement text")
- Playwright: { tag: ['@spec:SPEC_NAME', '@req:requirement'] }
- Vitest:     // @spec SPEC_NAME, // @req requirement text

Test types are auto-detected:
- unit:        pytest in tests/unit/, Vitest *.test.ts
- integration: pytest in tests/integration/ or @pytest.mark.integration
- e2e-mocked:  Playwright tests (default)
- e2e-real:    Playwright tests with @e2e-real tag or withRealApi()

Usage:
    uv run spec-coverage-analyzer           # Console + markdown output
    uv run spec-coverage-analyzer --json    # JSON output to stdout
    uv run spec-coverage-analyzer --affected          # Only specs affected by changes since HEAD~1
    uv run spec-coverage-analyzer --affected abc123   # Only specs affected since commit abc123
    # or
    python -m tools.spec_coverage_analyzer

Output:
    - Console summary (pytest-cov style)
    - specs/SPEC_COVERAGE_MAP.md with detailed report
    - JSON to stdout when --json flag is used
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Literal

# Repo root (this file lives in tools/)
_REPO_ROOT = Path(__file__).resolve().parent.parent


def _discover_known_specs() -> list[str]:
    """Discover all spec names from specs/*_SPEC.md files.

    Specs are discovered dynamically so newly added spec files are picked up
    automatically (previously this was a hardcoded list that drifted out of
    sync with the specs/ directory).
    """
    specs_dir = _REPO_ROOT / "specs"
    return sorted(p.stem for p in specs_dir.glob("*_SPEC.md"))


# All known specs (without .md extension), discovered from specs/*_SPEC.md
KNOWN_SPECS = _discover_known_specs()

TestType = Literal["unit", "integration", "e2e-mocked", "e2e-real"]


@dataclass
class Requirement:
    """A success criterion from a spec file."""

    text: str
    spec_name: str
    line_number: int
    roadmap: bool = False  # True when criterion is roadmap-only (excluded from denominator)


@dataclass
class TestCoverage:
    """A test file/function that covers a spec."""

    file_path: str
    test_name: str | None  # None for file-level coverage
    spec_name: str
    test_type: TestType
    requirement: str | None = None  # Linked requirement text (if @req used)
    line_number: int | None = None
    skipped: bool = False  # True when test carries static skip/skipif/xfail markers


@dataclass
class RequirementCoverage:
    """Coverage information for a single requirement."""

    requirement: Requirement
    tests: list[TestCoverage] = field(default_factory=list)

    @property
    def active_tests(self) -> list[TestCoverage]:
        """Tests that actually run (not statically skipped/xfailed)."""
        return [t for t in self.tests if not t.skipped]

    @property
    def is_covered(self) -> bool:
        return len(self.active_tests) > 0

    @property
    def is_skipped_only(self) -> bool:
        """True when the only tests linked to this requirement are skipped."""
        return bool(self.tests) and not self.active_tests

    @property
    def test_types(self) -> set[TestType]:
        return {t.test_type for t in self.active_tests}

    @property
    def has_frontend_test(self) -> bool:
        """True if at least one active test is a frontend test (E2E or client/ unit)."""
        for t in self.active_tests:
            if t.test_type in ("e2e-mocked", "e2e-real"):
                return True
            if t.file_path.startswith("client/"):
                return True
        return False

    @property
    def is_backend_only(self) -> bool:
        """True if covered but all tests are backend (no frontend tests)."""
        return self.is_covered and not self.has_frontend_test


@dataclass
class SpecCoverage:
    """Coverage information for a single spec."""

    spec_name: str
    requirements: list[RequirementCoverage] = field(default_factory=list)
    unlinked_tests: list[TestCoverage] = field(default_factory=list)  # Tests without @req
    roadmap_requirements: list[Requirement] = field(default_factory=list)  # Excluded from denominator

    @property
    def total_requirements(self) -> int:
        return len(self.requirements)

    @property
    def covered_requirements(self) -> int:
        return sum(1 for r in self.requirements if r.is_covered)

    @property
    def skipped_only_requirements(self) -> int:
        """Count requirements whose only linked tests are skipped."""
        return sum(1 for r in self.requirements if r.is_skipped_only)

    @property
    def coverage_percent(self) -> int:
        if self.total_requirements == 0:
            has_active_unlinked = any(not t.skipped for t in self.unlinked_tests)
            return 100 if has_active_unlinked else 0
        return 100 * self.covered_requirements // self.total_requirements

    @property
    def all_tests(self) -> list[TestCoverage]:
        tests = []
        for req in self.requirements:
            tests.extend(req.tests)
        tests.extend(self.unlinked_tests)
        return tests

    def count_by_type(self, test_type: TestType) -> int:
        """Count active (non-skipped) tests of a given type."""
        return sum(1 for t in self.all_tests if t.test_type == test_type and not t.skipped)

    @property
    def backend_only_requirements(self) -> int:
        """Count requirements that are covered but lack any frontend test."""
        return sum(1 for r in self.requirements if r.is_backend_only)


class SpecParser:
    """Parses spec files to extract requirements (success criteria).

    Roadmap criteria (excluded from the coverage denominator) are detected when:
    - the criterion text ends with "(roadmap)" (case-insensitive), or
    - the criterion appears under a heading starting with "Roadmap"
      (e.g. "### Roadmap" or "### Roadmap (not shipping)").
    """

    SPECS_DIR = Path("specs")

    # Pattern for success criteria: - [ ] requirement text
    REQUIREMENT_PATTERN = re.compile(r"^- \[ \] (.+)$", re.MULTILINE)
    HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.*)$")
    ROADMAP_SUFFIX_PATTERN = re.compile(r"\(roadmap\)\s*$", re.IGNORECASE)
    ROADMAP_HEADING_PATTERN = re.compile(r"^roadmap\b", re.IGNORECASE)

    def parse_spec_text(self, content: str, spec_name: str) -> list[Requirement]:
        """Parse a single spec's markdown content into Requirements."""
        requirements: list[Requirement] = []
        in_roadmap_section = False

        for line_number, line in enumerate(content.splitlines(), start=1):
            heading_match = self.HEADING_PATTERN.match(line)
            if heading_match:
                heading_text = heading_match.group(2).strip()
                in_roadmap_section = bool(self.ROADMAP_HEADING_PATTERN.match(heading_text))
                continue

            criterion_match = re.match(r"^- \[ \] (.+)$", line)
            if criterion_match:
                text = criterion_match.group(1).strip()
                roadmap = in_roadmap_section or bool(self.ROADMAP_SUFFIX_PATTERN.search(text))
                requirements.append(
                    Requirement(
                        text=text,
                        spec_name=spec_name,
                        line_number=line_number,
                        roadmap=roadmap,
                    )
                )

        return requirements

    def parse_all(self) -> dict[str, list[Requirement]]:
        """Parse all spec files and return requirements by spec name."""
        requirements: dict[str, list[Requirement]] = {spec: [] for spec in KNOWN_SPECS}

        for spec_name in KNOWN_SPECS:
            spec_file = self.SPECS_DIR / f"{spec_name}.md"
            if spec_file.exists():
                content = spec_file.read_text()
                requirements[spec_name] = self.parse_spec_text(content, spec_name)

        return requirements


class PytestSkipDetector:
    """Statically detects pytest tests carrying skip/skipif/xfail markers.

    A test is considered skipped when the marker appears:
    - directly on the test function,
    - on an enclosing class, or
    - in a module-level ``pytestmark`` assignment.
    """

    SKIP_MARK_NAMES = frozenset({"skip", "skipif", "xfail"})

    def __init__(self):
        self._file_cache: dict[str, dict | None] = {}

    def is_skipped(self, nodeid: str) -> bool:
        """Return True when the test identified by a pytest nodeid is statically skipped."""
        file_path, _, rest = nodeid.partition("::")
        info = self._analyze_file(file_path)
        if info is None:
            return False
        if info["module_skipped"]:
            return True
        if not rest:
            return False

        # Strip parametrization suffixes: test_foo[case] -> test_foo
        parts = tuple(p.split("[")[0] for p in rest.split("::") if p)
        if parts in info["paths"]:
            return info["paths"][parts]
        return self._name_lookup(info, parts[-1]) if parts else False

    def is_test_name_skipped(self, file_path: str, test_name: str | None) -> bool:
        """Best-effort lookup by bare test function name (source-scan fallback path)."""
        info = self._analyze_file(file_path)
        if info is None:
            return False
        if info["module_skipped"]:
            return True
        if not test_name:
            return False
        return self._name_lookup(info, test_name.split("[")[0])

    @staticmethod
    def _name_lookup(info: dict, name: str) -> bool:
        # Conservative: only report skipped when every definition with this name is skipped
        flags = info["by_name"].get(name)
        return bool(flags) and all(flags)

    def _analyze_file(self, file_path: str) -> dict | None:
        if file_path in self._file_cache:
            return self._file_cache[file_path]

        info: dict | None
        try:
            tree = ast.parse(Path(file_path).read_text())
        except (OSError, SyntaxError, UnicodeDecodeError, ValueError):
            info = None
            self._file_cache[file_path] = info
            return info

        info = {"module_skipped": False, "paths": {}, "by_name": {}}

        # Module-level pytestmark = pytest.mark.skip(...) / [pytest.mark.xfail, ...]
        for node in tree.body:
            targets: list[ast.expr] = []
            if isinstance(node, ast.Assign):
                targets = node.targets
            elif isinstance(node, ast.AnnAssign) and node.value is not None:
                targets = [node.target]
            for target in targets:
                if isinstance(target, ast.Name) and target.id == "pytestmark":
                    value = node.value
                    if value is not None and self._contains_skip_mark(value):
                        info["module_skipped"] = True

        self._walk(tree, (), info["module_skipped"], info)
        self._file_cache[file_path] = info
        return info

    def _walk(self, node: ast.AST, path: tuple[str, ...], inherited: bool, info: dict):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                skipped = inherited or any(self._decorator_is_skip(d) for d in child.decorator_list)
                child_path = (*path, child.name)
                info["paths"][child_path] = skipped
                info["by_name"].setdefault(child.name, []).append(skipped)
            elif isinstance(child, ast.ClassDef):
                skipped = inherited or any(self._decorator_is_skip(d) for d in child.decorator_list)
                self._walk(child, (*path, child.name), skipped, info)

    @classmethod
    def _decorator_is_skip(cls, decorator: ast.expr) -> bool:
        """True for @pytest.mark.skip, @pytest.mark.skipif(...), @mark.xfail, etc."""
        target = decorator.func if isinstance(decorator, ast.Call) else decorator
        parts: list[str] = []
        while isinstance(target, ast.Attribute):
            parts.append(target.attr)
            target = target.value
        if isinstance(target, ast.Name):
            parts.append(target.id)
        # parts is leaf-first, e.g. ['skip', 'mark', 'pytest']
        return bool(parts) and parts[0] in cls.SKIP_MARK_NAMES and ("mark" in parts or "pytest" in parts)

    @classmethod
    def _contains_skip_mark(cls, expr: ast.expr) -> bool:
        return any(
            isinstance(node, ast.Attribute) and node.attr in cls.SKIP_MARK_NAMES for node in ast.walk(expr)
        )


def find_static_skip_ranges(content: str, skip_call_pattern: re.Pattern) -> list[tuple[int, int]]:
    """Find character ranges covered by static skip declarations in JS/TS test sources.

    ``skip_call_pattern`` must match up to and including the opening parenthesis of
    a skip call (e.g. ``test.describe.skip(`` or ``test.skip(``). The returned range
    spans the entire call (including the callback body), so any marker found inside
    belongs to a skipped test or describe block.
    """
    ranges: list[tuple[int, int]] = []
    for match in skip_call_pattern.finditer(content):
        open_paren = match.end() - 1
        depth = 0
        end = len(content)
        for i in range(open_paren, len(content)):
            char = content[i]
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        ranges.append((match.start(), end))
    return ranges


def offset_in_ranges(offset: int, ranges: list[tuple[int, int]]) -> bool:
    return any(start <= offset < end for start, end in ranges)


class SpecCoverageScanner:
    """Scans test files for spec coverage markers."""

    # Directories to scan
    PYTEST_DIR = Path("tests")
    PLAYWRIGHT_DIR = Path("client/tests/e2e")
    VITEST_DIR = Path("client/src")

    # Regex patterns for detecting spec markers
    # pytest: @pytest.mark.spec("SPEC_NAME")
    PYTEST_SPEC_PATTERN = re.compile(
        r'@pytest\.mark\.spec\(["\']([A-Z_]+)["\']\)',
        re.MULTILINE,
    )
    # pytest: @pytest.mark.req("requirement text")
    PYTEST_REQ_PATTERN = re.compile(
        r'@pytest\.mark\.req\(["\'](.+?)["\']\)',
        re.MULTILINE,
    )
    # pytest: @pytest.mark.integration
    PYTEST_INTEGRATION_PATTERN = re.compile(
        r"@pytest\.mark\.integration",
        re.MULTILINE,
    )

    # Playwright: { tag: ['@spec:SPEC_NAME'] }
    PLAYWRIGHT_SPEC_TAG_PATTERN = re.compile(
        r'tag:\s*\[?\s*["\']@spec:([A-Z_]+)["\']',
        re.MULTILINE,
    )
    # Playwright: @req:requirement text in tag
    PLAYWRIGHT_REQ_TAG_PATTERN = re.compile(
        r"[\"']@req:([^\"']+)[\"']",
        re.MULTILINE,
    )
    # Playwright: @e2e-real tag
    PLAYWRIGHT_REAL_TAG_PATTERN = re.compile(
        r"[\"']@e2e-real[\"']",
        re.MULTILINE,
    )
    # Playwright: withRealApi() call
    PLAYWRIGHT_REAL_API_PATTERN = re.compile(
        r"\.withRealApi\(\)",
        re.MULTILINE,
    )
    # Playwright: test title containing @spec:
    PLAYWRIGHT_TITLE_PATTERN = re.compile(
        r'test\(\s*["\']@spec:([A-Z_]+)',
        re.MULTILINE,
    )

    # Vitest: // @spec SPEC_NAME or /* @spec SPEC_NAME */
    VITEST_SPEC_COMMENT_PATTERN = re.compile(
        r"(?://|/\*)\s*@spec[:\s]+([A-Z_]+)",
        re.MULTILINE,
    )
    # Vitest: // @req requirement text
    VITEST_REQ_COMMENT_PATTERN = re.compile(
        r"(?://|/\*)\s*@req[:\s]+(.+?)(?:\*/|\n|$)",
        re.MULTILINE,
    )
    # Vitest: describe('@spec:SPEC_NAME', ...)
    VITEST_DESCRIBE_PATTERN = re.compile(
        r'describe\(\s*["\']@spec:([A-Z_]+)',
        re.MULTILINE,
    )

    # Static skip declarations in Playwright sources:
    # test.skip(, test.fixme(, test.describe.skip(, test.describe.fixme(
    PLAYWRIGHT_SKIP_CALL_PATTERN = re.compile(r"\btest\.(?:describe\.)?(?:skip|fixme)\s*\(")
    # Static skip declarations in Vitest sources: describe.skip(, it.skip(, test.todo(, ...
    VITEST_SKIP_CALL_PATTERN = re.compile(r"\b(?:describe|it|test)\.(?:skip|todo|fixme)\s*\(")

    def __init__(self):
        self.tests: list[TestCoverage] = []
        # Unknown spec name -> number of tagged tests referencing it
        self.unknown_specs: dict[str, int] = {}
        self._pytest_skip_detector = PytestSkipDetector()

    def _record_unknown_spec(self, spec_name: str):
        self.unknown_specs[spec_name] = self.unknown_specs.get(spec_name, 0) + 1

    def scan_all(self) -> list[TestCoverage]:
        """Scan all test directories and return all test coverage entries."""
        self._scan_pytest()
        self._scan_playwright()
        self._scan_vitest()
        return self.tests

    def _detect_pytest_test_type(self, file_path: str, content: str) -> TestType:
        """Detect test type for pytest based on path and markers."""
        if "tests/integration" in file_path or self.PYTEST_INTEGRATION_PATTERN.search(content):
            return "integration"
        return "unit"

    def _detect_playwright_test_type(self, content: str) -> TestType:
        """Detect test type for Playwright based on markers."""
        if self.PLAYWRIGHT_REAL_TAG_PATTERN.search(content) or self.PLAYWRIGHT_REAL_API_PATTERN.search(content):
            return "e2e-real"
        return "e2e-mocked"

    def _scan_pytest(self):
        """Scan pytest tests using pytest's collection API to extract markers.

        Runs pytest --collect-only with a custom plugin to extract @pytest.mark.spec
        and @pytest.mark.req marker values without executing tests.

        Falls back to source scanning if pytest collection fails.
        """
        if not self.PYTEST_DIR.exists():
            return

        try:
            items = self._collect_pytest_markers()
        except Exception:
            self._scan_pytest_source_fallback()
            return

        for item in items:
            spec_name = item["spec"]
            if spec_name not in KNOWN_SPECS:
                self._record_unknown_spec(spec_name)
                continue

            file_path = item["nodeid"].split("::")[0]
            test_name = item["nodeid"].split("::")[-1]
            test_type: TestType = "integration" if item.get("integration") else "unit"

            self.tests.append(
                TestCoverage(
                    file_path=file_path,
                    test_name=test_name,
                    spec_name=spec_name,
                    test_type=test_type,
                    requirement=item.get("req"),
                    line_number=item.get("lineno"),
                    skipped=self._pytest_skip_detector.is_skipped(item["nodeid"]),
                )
            )

    @staticmethod
    def _collect_pytest_markers() -> list[dict]:
        """Run tools/collect_pytest_markers.py to extract spec/req marker values."""
        result = subprocess.run(
            ["uv", "run", "--no-sync", "python", "tools/collect_pytest_markers.py"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        for line in result.stdout.splitlines():
            if line.startswith("MARKER_JSON:"):
                return json.loads(line[len("MARKER_JSON:") :])

        raise RuntimeError(f"pytest marker collection failed (rc={result.returncode}): {result.stderr[:500]}")

    def _scan_pytest_source_fallback(self):
        """Fallback: scan pytest source files directly for spec/req markers.

        Used when pytest collection API is not available.
        """
        for test_file in self.PYTEST_DIR.rglob("test_*.py"):
            content = test_file.read_text()
            file_path = str(test_file)
            test_type = self._detect_pytest_test_type(file_path, content)

            for spec_match in self.PYTEST_SPEC_PATTERN.finditer(content):
                spec_name = spec_match.group(1)
                if spec_name not in KNOWN_SPECS:
                    self._record_unknown_spec(spec_name)
                    continue
                line_number = content[: spec_match.start()].count("\n") + 1
                after_marker = content[spec_match.end() :]
                func_match = re.search(r"def (test_\w+)", after_marker)
                test_name = func_match.group(1) if func_match else None
                before_marker = content[max(0, spec_match.start() - 200) : spec_match.start()]
                req_match = self.PYTEST_REQ_PATTERN.search(before_marker)
                after_marker_small = content[spec_match.end() : spec_match.end() + 200]
                if not req_match:
                    req_match = self.PYTEST_REQ_PATTERN.search(after_marker_small)
                requirement = req_match.group(1) if req_match else None

                self.tests.append(
                    TestCoverage(
                        file_path=file_path,
                        test_name=test_name,
                        spec_name=spec_name,
                        test_type=test_type,
                        requirement=requirement,
                        line_number=line_number,
                        skipped=self._pytest_skip_detector.is_test_name_skipped(file_path, test_name),
                    )
                )

    def _scan_playwright(self):
        """Scan Playwright tests using the JSON reporter's --list mode.

        Runs `npx playwright test --list --reporter=json` which outputs full tag
        metadata (including inherited describe-level tags) without executing tests.
        This correctly handles tag inheritance where @spec is on a parent describe
        and @req tags are on child test() calls.

        Falls back to source scanning if the playwright CLI is not available.
        """
        if not self.PLAYWRIGHT_DIR.exists():
            return

        # Build a cache of which files use withRealApi() (not expressed as a tag)
        real_api_files: set[str] = set()
        for test_file in self.PLAYWRIGHT_DIR.glob("*.spec.ts"):
            content = test_file.read_text()
            if self.PLAYWRIGHT_REAL_API_PATTERN.search(content):
                real_api_files.add(str(test_file))

        # Run playwright --list to get test metadata with inherited tags
        client_dir = str(self.PLAYWRIGHT_DIR.parent.parent)  # client/
        try:
            result = subprocess.run(
                ["npx", "playwright", "test", "--list", "--reporter=json"],
                capture_output=True,
                text=True,
                cwd=client_dir,
                timeout=30,
            )
            if result.returncode != 0 or not result.stdout.strip():
                self._scan_playwright_source_fallback()
                return

            report = json.loads(result.stdout)
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            self._scan_playwright_source_fallback()
            return

        self._walk_playwright_suites(report.get("suites", []), real_api_files)

    def _walk_playwright_suites(self, suites: list[dict], real_api_files: set[str]):
        """Recursively walk Playwright JSON reporter suites to extract test coverage."""
        for suite in suites:
            for spec in suite.get("specs", []):
                tags = spec.get("tags", [])
                title = spec.get("title", "")
                reporter_file = spec.get("file", "")
                line = spec.get("line", 1)

                # Only process e2e tests (skip top-level non-e2e spec files)
                if not reporter_file.startswith("e2e/"):
                    continue

                # Normalize to project-relative path (reporter uses testDir-relative)
                file_path = f"client/tests/{reporter_file}"

                # Extract spec names and requirements from tags
                spec_names: set[str] = set()
                requirements: list[str] = []
                has_real_tag = False

                for tag in tags:
                    tag_clean = tag.lstrip("@")
                    if tag_clean.startswith("spec:"):
                        name = tag_clean[5:]
                        if name in KNOWN_SPECS:
                            spec_names.add(name)
                        else:
                            self._record_unknown_spec(name)
                    elif tag_clean.startswith("req:"):
                        requirements.append(tag_clean[4:])
                    elif tag_clean == "e2e-real":
                        has_real_tag = True

                if not spec_names:
                    continue

                # Determine test type from @e2e-real tag or withRealApi() in source
                is_real = has_real_tag or file_path in real_api_files
                test_type: TestType = "e2e-real" if is_real else "e2e-mocked"

                # Statically-skipped tests (test.skip/test.fixme declarations or
                # test.describe.skip blocks) report expectedStatus == "skipped"
                # or carry skip/fixme annotations even in --list mode.
                skipped = self._playwright_spec_is_skipped(spec)

                # Emit one TestCoverage per (spec, requirement) pair.
                # If no requirements, emit one with requirement=None.
                reqs_to_emit = requirements if requirements else [None]
                for spec_name in spec_names:
                    for req in reqs_to_emit:
                        self.tests.append(
                            TestCoverage(
                                file_path=file_path,
                                test_name=title,
                                spec_name=spec_name,
                                test_type=test_type,
                                requirement=req,
                                line_number=line,
                                skipped=skipped,
                            )
                        )

            self._walk_playwright_suites(suite.get("suites", []), real_api_files)

    @staticmethod
    def _playwright_spec_is_skipped(spec: dict) -> bool:
        """True when a Playwright reporter spec entry is statically skipped.

        Covers test.skip / test.fixme declarations and test.describe.skip blocks,
        which set expectedStatus == "skipped" (and skip/fixme annotations) at
        declaration time, so they are visible in --list mode.
        """
        tests_meta = spec.get("tests", [])
        if not tests_meta:
            return False
        return all(
            t.get("expectedStatus") == "skipped"
            or any(a.get("type") in ("skip", "fixme") for a in t.get("annotations", []))
            for t in tests_meta
        )

    def _scan_playwright_source_fallback(self):
        """Fallback: scan Playwright source files directly for spec tags.

        Used when `npx playwright test --list` is not available.
        """
        for test_file in self.PLAYWRIGHT_DIR.glob("*.spec.ts"):
            content = test_file.read_text()
            file_path = str(test_file)
            test_type = self._detect_playwright_test_type(content)
            skip_ranges = find_static_skip_ranges(content, self.PLAYWRIGHT_SKIP_CALL_PATTERN)

            for spec_match in self.PLAYWRIGHT_SPEC_TAG_PATTERN.finditer(content):
                spec_name = spec_match.group(1)
                if spec_name not in KNOWN_SPECS:
                    self._record_unknown_spec(spec_name)
                    continue
                line_number = content[: spec_match.start()].count("\n") + 1
                context = content[max(0, spec_match.start() - 100) : spec_match.end() + 100]
                req_match = self.PLAYWRIGHT_REQ_TAG_PATTERN.search(context)
                requirement = req_match.group(1) if req_match else None
                self.tests.append(
                    TestCoverage(
                        file_path=file_path,
                        test_name=None,
                        spec_name=spec_name,
                        test_type=test_type,
                        requirement=requirement,
                        line_number=line_number,
                        skipped=offset_in_ranges(spec_match.start(), skip_ranges),
                    )
                )

            for spec_match in self.PLAYWRIGHT_TITLE_PATTERN.finditer(content):
                spec_name = spec_match.group(1)
                if spec_name not in KNOWN_SPECS:
                    self._record_unknown_spec(spec_name)
                    continue
                line_number = content[: spec_match.start()].count("\n") + 1
                self.tests.append(
                    TestCoverage(
                        file_path=file_path,
                        test_name=None,
                        spec_name=spec_name,
                        test_type=test_type,
                        requirement=None,
                        line_number=line_number,
                        skipped=offset_in_ranges(spec_match.start(), skip_ranges),
                    )
                )

    def _scan_vitest(self):
        """Scan Vitest tests using `vitest list --json`.

        Extracts @spec: from describe block names in the test name field.
        For files that only use // @spec comments (not in describe names),
        falls back to scanning the source for the comment pattern.

        Falls back entirely to source scanning if the vitest CLI is not available.
        """
        if not self.VITEST_DIR.exists():
            return

        client_dir = str(self.VITEST_DIR.parent)  # client/
        try:
            result = subprocess.run(
                ["npx", "vitest", "list", "--json"],
                capture_output=True,
                text=True,
                cwd=client_dir,
                timeout=30,
            )
            if result.returncode != 0 or not result.stdout.strip():
                self._scan_vitest_source_fallback()
                return

            tests = json.loads(result.stdout)
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            self._scan_vitest_source_fallback()
            return

        # Track which files had @spec: in their test names (via describe blocks)
        files_with_spec_in_name: set[str] = set()
        # Cache for // @spec and // @req comments per file
        file_comment_cache: dict[str, tuple[str | None, str | None]] = {}

        for test in tests:
            name = test.get("name", "")
            abs_file = test.get("file", "")

            # Normalize to project-relative path
            if "client/" in abs_file:
                file_path = "client/" + abs_file.split("client/", 1)[1]
            else:
                file_path = abs_file

            # Extract @spec: from the test name (set by describe block names)
            spec_match = re.search(r"@spec:([A-Z_]+)", name)
            if spec_match:
                spec_name = spec_match.group(1)
                files_with_spec_in_name.add(file_path)

                if spec_name not in KNOWN_SPECS:
                    self._record_unknown_spec(spec_name)
                    continue

                # Extract the leaf test name (after the last " > ")
                test_name = name.rsplit(" > ", 1)[-1] if " > " in name else name

                # Check source for // @req comment (vitest has no tag-based @req)
                if file_path not in file_comment_cache:
                    file_comment_cache[file_path] = self._read_vitest_req(abs_file)
                requirement = file_comment_cache[file_path][1]

                self.tests.append(
                    TestCoverage(
                        file_path=file_path,
                        test_name=test_name,
                        spec_name=spec_name,
                        test_type="unit",
                        requirement=requirement,
                        line_number=None,
                    )
                )

        # For files that only use // @spec comments (not in describe names),
        # scan the source to pick up the spec association
        all_files = {
            "client/" + test.get("file", "").split("client/", 1)[1]
            for test in tests
            if "client/" in test.get("file", "")
        }
        comment_only_files = all_files - files_with_spec_in_name
        for file_path in comment_only_files:
            abs_path = Path(file_path)
            if not abs_path.exists():
                continue
            content = abs_path.read_text()
            for match in self.VITEST_SPEC_COMMENT_PATTERN.finditer(content):
                spec_name = match.group(1)
                if spec_name not in KNOWN_SPECS:
                    self._record_unknown_spec(spec_name)
                    continue
                # Read @req from source (same as describe-block path)
                req_data = self._read_vitest_req(str(abs_path.resolve()))
                requirement = req_data[1]

                # Count how many tests are in this file from the reporter
                file_tests = [t for t in tests if file_path in t.get("file", "")]
                for t in file_tests:
                    name = t.get("name", "")
                    test_name = name.rsplit(" > ", 1)[-1] if " > " in name else name
                    self.tests.append(
                        TestCoverage(
                            file_path=file_path,
                            test_name=test_name,
                            spec_name=spec_name,
                            test_type="unit",
                            requirement=requirement,
                            line_number=None,
                        )
                    )
                break  # One @spec per file

    def _read_vitest_req(self, abs_file: str) -> tuple[str | None, str | None]:
        """Read a vitest file for // @req comment. Returns (spec, req)."""
        try:
            content = Path(abs_file).read_text()
            req_match = self.VITEST_REQ_COMMENT_PATTERN.search(content)
            return (None, req_match.group(1).strip() if req_match else None)
        except (OSError, UnicodeDecodeError):
            return (None, None)

    def _scan_vitest_source_fallback(self):
        """Fallback: scan Vitest source files directly for spec comments/tags.

        Used when `npx vitest list` is not available.
        """
        for test_file in self.VITEST_DIR.rglob("*.test.ts"):
            content = test_file.read_text()
            file_path = str(test_file)
            skip_ranges = find_static_skip_ranges(content, self.VITEST_SKIP_CALL_PATTERN)

            for spec_match in self.VITEST_SPEC_COMMENT_PATTERN.finditer(content):
                spec_name = spec_match.group(1)
                if spec_name not in KNOWN_SPECS:
                    self._record_unknown_spec(spec_name)
                    continue
                line_number = content[: spec_match.start()].count("\n") + 1
                context = content[max(0, spec_match.start() - 100) : spec_match.end() + 100]
                req_match = self.VITEST_REQ_COMMENT_PATTERN.search(context)
                requirement = req_match.group(1).strip() if req_match else None
                self.tests.append(
                    TestCoverage(
                        file_path=file_path,
                        test_name=None,
                        spec_name=spec_name,
                        test_type="unit",
                        requirement=requirement,
                        line_number=line_number,
                        skipped=offset_in_ranges(spec_match.start(), skip_ranges),
                    )
                )

            for spec_match in self.VITEST_DESCRIBE_PATTERN.finditer(content):
                spec_name = spec_match.group(1)
                if spec_name not in KNOWN_SPECS:
                    self._record_unknown_spec(spec_name)
                    continue
                line_number = content[: spec_match.start()].count("\n") + 1
                self.tests.append(
                    TestCoverage(
                        file_path=file_path,
                        test_name=None,
                        spec_name=spec_name,
                        test_type="unit",
                        requirement=None,
                        line_number=line_number,
                        skipped=offset_in_ranges(spec_match.start(), skip_ranges),
                    )
                )


class RequirementMatcher:
    """Matches test requirements to spec requirements using fuzzy matching."""

    SIMILARITY_THRESHOLD = 0.6

    def __init__(self, requirements: dict[str, list[Requirement]]):
        self.requirements = requirements

    def match(self, test: TestCoverage) -> Requirement | None:
        """Find the best matching requirement for a test."""
        if not test.requirement:
            return None

        spec_reqs = self.requirements.get(test.spec_name, [])
        if not spec_reqs:
            return None

        best_match = None
        best_score = 0.0

        test_req_lower = test.requirement.lower()

        for req in spec_reqs:
            req_text_lower = req.text.lower()

            # Check for substring match first (most reliable)
            if test_req_lower in req_text_lower or req_text_lower in test_req_lower:
                return req

            # Fall back to fuzzy matching
            score = SequenceMatcher(None, test_req_lower, req_text_lower).ratio()
            if score > best_score and score >= self.SIMILARITY_THRESHOLD:
                best_score = score
                best_match = req

        return best_match


class AffectedSpecDetector:
    """Detects which specs are affected by file changes."""

    # File path patterns mapped to specs
    # Order matters - more specific patterns should come first
    FILE_TO_SPEC_PATTERNS: list[tuple[str, list[str]]] = [
        # Spec files themselves
        (r"specs/ANNOTATION_SPEC\.md", ["ANNOTATION_SPEC"]),
        (r"specs/ASSISTED_FACILITATION_SPEC\.md", ["ASSISTED_FACILITATION_SPEC"]),
        (r"specs/AUTHENTICATION_SPEC\.md", ["AUTHENTICATION_SPEC"]),
        (r"specs/BUILD_AND_DEPLOY_SPEC\.md", ["BUILD_AND_DEPLOY_SPEC"]),
        (r"specs/DATASETS_SPEC\.md", ["DATASETS_SPEC"]),
        (r"specs/DESIGN_SYSTEM_SPEC\.md", ["DESIGN_SYSTEM_SPEC"]),
        (r"specs/DISCOVERY_TRACE_ASSIGNMENT_SPEC\.md", ["DISCOVERY_TRACE_ASSIGNMENT_SPEC"]),
        (r"specs/JUDGE_EVALUATION_SPEC\.md", ["JUDGE_EVALUATION_SPEC"]),
        (r"specs/ROLE_PERMISSIONS_SPEC\.md", ["ROLE_PERMISSIONS_SPEC"]),
        (r"specs/RUBRIC_SPEC\.md", ["RUBRIC_SPEC"]),
        (r"specs/TRACE_DISPLAY_SPEC\.md", ["TRACE_DISPLAY_SPEC"]),
        (r"specs/UI_COMPONENTS_SPEC\.md", ["UI_COMPONENTS_SPEC"]),
        # Backend - specific services/routers
        (r"server/routers/annotations\.py", ["ANNOTATION_SPEC"]),
        (r"server/routers/users\.py", ["AUTHENTICATION_SPEC", "ROLE_PERMISSIONS_SPEC"]),
        (r"server/routers/databricks\.py", ["JUDGE_EVALUATION_SPEC"]),
        (
            r"server/routers/workshops\.py",
            ["DISCOVERY_TRACE_ASSIGNMENT_SPEC", "DATASETS_SPEC", "ROLE_PERMISSIONS_SPEC"],
        ),
        (r"server/services/alignment_service\.py", ["JUDGE_EVALUATION_SPEC"]),
        (r"server/services/irr.*\.py", ["JUDGE_EVALUATION_SPEC"]),
        (r"server/services/cohens_kappa\.py", ["JUDGE_EVALUATION_SPEC"]),
        (r"server/services/krippendorff_alpha\.py", ["JUDGE_EVALUATION_SPEC"]),
        (r"server/services/discovery.*\.py", ["ASSISTED_FACILITATION_SPEC", "DISCOVERY_TRACE_ASSIGNMENT_SPEC"]),
        (r"server/services/classification_service\.py", ["ASSISTED_FACILITATION_SPEC"]),
        (r"server/services/token_storage_service\.py", ["AUTHENTICATION_SPEC"]),
        (r"server/services/database_service\.py", KNOWN_SPECS),  # Affects many specs
        (r"server/database\.py", KNOWN_SPECS),  # Core DB affects all
        # Frontend - specific components/pages
        (r"client/src/pages/Annotation", ["ANNOTATION_SPEC"]),
        (r"client/src/pages/.*Login", ["AUTHENTICATION_SPEC"]),
        (r"client/src/pages/.*Facilitat", ["ASSISTED_FACILITATION_SPEC"]),
        (r"client/src/pages/.*Discovery", ["DISCOVERY_TRACE_ASSIGNMENT_SPEC", "ASSISTED_FACILITATION_SPEC"]),
        (r"client/src/context/UserContext", ["AUTHENTICATION_SPEC"]),
        (r"client/src/components/.*Rubric", ["RUBRIC_SPEC"]),
        (r"client/src/components/.*Trace", ["TRACE_DISPLAY_SPEC"]),
        (r"client/src/components/.*Pagination", ["UI_COMPONENTS_SPEC"]),
        (r"client/src/components/.*Json", ["TRACE_DISPLAY_SPEC", "UI_COMPONENTS_SPEC"]),
        (r"client/src/lib/", ["DESIGN_SYSTEM_SPEC"]),
        (r"client/src/utils/rubric", ["RUBRIC_SPEC"]),
        (r"client/src/utils/trace", ["TRACE_DISPLAY_SPEC", "DATASETS_SPEC"]),
        # Tests - detect spec from test file content or path
        (r"tests/.*annotation", ["ANNOTATION_SPEC"]),
        (r"tests/.*auth", ["AUTHENTICATION_SPEC"]),
        (r"tests/.*user", ["AUTHENTICATION_SPEC"]),
        (r"tests/.*irr", ["JUDGE_EVALUATION_SPEC"]),
        (r"tests/.*kappa", ["JUDGE_EVALUATION_SPEC"]),
        (r"tests/.*krippendorff", ["JUDGE_EVALUATION_SPEC"]),
        (r"tests/.*discovery", ["DISCOVERY_TRACE_ASSIGNMENT_SPEC", "ASSISTED_FACILITATION_SPEC"]),
        (r"tests/.*facilitation", ["ASSISTED_FACILITATION_SPEC"]),
        (r"client/tests/e2e/annotation", ["ANNOTATION_SPEC"]),
        (r"client/tests/e2e/auth", ["AUTHENTICATION_SPEC"]),
        (r"client/tests/e2e/facilitat", ["ASSISTED_FACILITATION_SPEC"]),
        (r"client/tests/e2e/discovery", ["DISCOVERY_TRACE_ASSIGNMENT_SPEC"]),
        (r"client/tests/e2e/jsonpath", ["TRACE_DISPLAY_SPEC"]),
        # Build/deploy
        (r"Dockerfile", ["BUILD_AND_DEPLOY_SPEC"]),
        (r"\.github/workflows/", ["BUILD_AND_DEPLOY_SPEC"]),
        (r"justfile", ["BUILD_AND_DEPLOY_SPEC"]),
        (r"pyproject\.toml", ["BUILD_AND_DEPLOY_SPEC"]),
        (r"package\.json", ["BUILD_AND_DEPLOY_SPEC"]),
    ]

    def __init__(self, base_ref: str = "HEAD~1"):
        self.base_ref = base_ref

    def get_changed_files(self) -> list[str]:
        """Get list of files changed since base_ref."""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", self.base_ref],
                capture_output=True,
                text=True,
                check=True,
            )
            files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
            return files
        except subprocess.CalledProcessError:
            # Fall back to comparing against HEAD (uncommitted changes)
            try:
                result = subprocess.run(
                    ["git", "diff", "--name-only", "HEAD"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
                # Also include staged changes
                result2 = subprocess.run(
                    ["git", "diff", "--name-only", "--cached"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                staged = [f.strip() for f in result2.stdout.strip().split("\n") if f.strip()]
                return list(set(files + staged))
            except subprocess.CalledProcessError:
                return []

    def detect_affected_specs(self, changed_files: list[str] | None = None) -> set[str]:
        """Detect which specs are affected by changed files."""
        if changed_files is None:
            changed_files = self.get_changed_files()

        affected: set[str] = set()

        for file_path in changed_files:
            # Check each pattern
            for pattern, specs in self.FILE_TO_SPEC_PATTERNS:
                if re.search(pattern, file_path, re.IGNORECASE):
                    affected.update(specs)
                    break  # First match wins for this file

            # If no pattern matched, try to detect spec from file content
            if not any(re.search(p, file_path, re.IGNORECASE) for p, _ in self.FILE_TO_SPEC_PATTERNS):
                # Check if it's a test file with spec markers
                specs_in_file = self._detect_specs_in_file(file_path)
                affected.update(specs_in_file)

        return affected

    def _detect_specs_in_file(self, file_path: str) -> set[str]:
        """Try to detect spec markers in a file."""
        specs: set[str] = set()
        path = Path(file_path)

        if not path.exists():
            return specs

        try:
            content = path.read_text()
            # Look for spec markers in the file
            for spec in KNOWN_SPECS:
                if spec in content:
                    specs.add(spec)
        except (OSError, UnicodeDecodeError):
            pass

        return specs


def build_coverage(requirements: dict[str, list[Requirement]], tests: list[TestCoverage]) -> dict[str, SpecCoverage]:
    """Build coverage data from requirements and tests.

    Roadmap criteria are excluded from the coverage denominator and tracked
    separately on SpecCoverage.roadmap_requirements. Tests tagged against a
    roadmap criterion fall back to the spec's unlinked tests list.
    """
    # Only active (non-roadmap) criteria participate in matching and the denominator
    active_requirements = {
        spec_name: [r for r in reqs if not r.roadmap] for spec_name, reqs in requirements.items()
    }
    matcher = RequirementMatcher(active_requirements)

    # Initialize coverage for all specs
    coverage: dict[str, SpecCoverage] = {}
    for spec_name in KNOWN_SPECS:
        spec_reqs = active_requirements.get(spec_name, [])
        roadmap_reqs = [r for r in requirements.get(spec_name, []) if r.roadmap]
        coverage[spec_name] = SpecCoverage(
            spec_name=spec_name,
            requirements=[RequirementCoverage(requirement=req) for req in spec_reqs],
            roadmap_requirements=roadmap_reqs,
        )

    # Match tests to requirements
    for test in tests:
        spec_cov = coverage.get(test.spec_name)
        if not spec_cov:
            continue

        matched_req = matcher.match(test)
        if matched_req:
            # Find the requirement coverage entry and add the test
            for req_cov in spec_cov.requirements:
                if req_cov.requirement.text == matched_req.text:
                    req_cov.tests.append(test)
                    break
        else:
            # No requirement match - add to unlinked tests
            spec_cov.unlinked_tests.append(test)

    return coverage


def print_console_summary(coverage: dict[str, SpecCoverage], verbose: bool = False):
    """Print a pytest-cov style console summary."""
    print("\nSPEC COVERAGE REPORT")
    print("=" * 90)
    print(f"{'Name':<35} {'Reqs':>5} {'Cover%':>7} {'Unit':>5} {'Int':>4} {'E2E-M':>6} {'E2E-R':>6} {'BE-only':>8}")
    print("-" * 90)

    total_reqs = 0
    total_covered = 0
    total_backend_only = 0
    total_by_type: dict[TestType, int] = {
        "unit": 0,
        "integration": 0,
        "e2e-mocked": 0,
        "e2e-real": 0,
    }

    # Iterate over specs in coverage dict (may be filtered)
    specs_to_show = [s for s in KNOWN_SPECS if s in coverage]
    for spec_name in specs_to_show:
        cov = coverage[spec_name]
        total_reqs += cov.total_requirements
        total_covered += cov.covered_requirements
        backend_only = cov.backend_only_requirements
        total_backend_only += backend_only

        unit_count = cov.count_by_type("unit")
        int_count = cov.count_by_type("integration")
        e2e_mocked_count = cov.count_by_type("e2e-mocked")
        e2e_real_count = cov.count_by_type("e2e-real")

        total_by_type["unit"] += unit_count
        total_by_type["integration"] += int_count
        total_by_type["e2e-mocked"] += e2e_mocked_count
        total_by_type["e2e-real"] += e2e_real_count

        # Determine status indicator
        if cov.total_requirements == 0:
            status = "   " if cov.unlinked_tests else " ! "
        elif cov.coverage_percent == 100 and backend_only == 0:
            status = "   "
        elif cov.coverage_percent == 100 and backend_only > 0:
            status = " ~ "  # 100% but has backend-only gaps
        elif cov.coverage_percent >= 50:
            status = " * "
        else:
            status = " ! "

        be_only_str = str(backend_only) if backend_only > 0 else ""
        print(
            f"{status}{spec_name:<32} {cov.total_requirements:>5} {cov.coverage_percent:>6}% "
            f"{unit_count:>5} {int_count:>4} {e2e_mocked_count:>6} {e2e_real_count:>6} {be_only_str:>8}"
        )

    print("-" * 90)
    total_percent = 100 * total_covered // total_reqs if total_reqs > 0 else 0
    print(
        f"{'TOTAL':<35} {total_reqs:>5} {total_percent:>6}% "
        f"{total_by_type['unit']:>5} {total_by_type['integration']:>4} "
        f"{total_by_type['e2e-mocked']:>6} {total_by_type['e2e-real']:>6} {total_backend_only:>8}"
    )
    print("")
    print("Legend: ! = low coverage (<50%), * = partial coverage (50-99%),")
    print("        ~ = 100% but has backend-only requirements (no frontend tests)")
    print("   BE-only = requirements covered exclusively by backend tests (no E2E/Vitest)")
    print("")

    # Skipped-only criteria: tests exist but are all statically skipped/xfailed
    skipped_only = {
        spec_name: coverage[spec_name].skipped_only_requirements
        for spec_name in specs_to_show
        if coverage[spec_name].skipped_only_requirements > 0
    }
    if skipped_only:
        print("Skipped-only criteria (only skip/xfail tests; NOT counted as covered):")
        for spec_name, count in sorted(skipped_only.items()):
            print(f"  - {spec_name}: {count}")
        print("")

    # Roadmap criteria excluded from the denominator
    roadmap = {
        spec_name: len(coverage[spec_name].roadmap_requirements)
        for spec_name in specs_to_show
        if coverage[spec_name].roadmap_requirements
    }
    if roadmap:
        print("Roadmap criteria (not shipping; excluded from coverage denominator):")
        for spec_name, count in sorted(roadmap.items()):
            print(f"  - {spec_name}: {count}")
        print("")


def print_unknown_specs_warning(unknown_specs: dict[str, int]):
    """Print a loud warning for tags referencing specs not in KNOWN_SPECS."""
    if not unknown_specs:
        return
    total = sum(unknown_specs.values())
    print("=" * 90)
    print(f"WARNING: {total} test tag(s) reference UNKNOWN specs (zero coverage credit):")
    for spec_name, count in sorted(unknown_specs.items()):
        print(f"  - {spec_name}: {count} tagged test(s)")
    print("Add a specs/<NAME>_SPEC.md file if they are valid (specs are discovered from specs/*_SPEC.md), or fix the tags.")
    print("=" * 90)
    print("")


def generate_json_report(coverage: dict[str, SpecCoverage], unknown_specs: dict[str, int] | None = None) -> dict:
    """Generate JSON report data."""
    total_reqs = 0
    total_covered = 0
    total_by_type: dict[str, int] = {
        "unit": 0,
        "integration": 0,
        "e2e-mocked": 0,
        "e2e-real": 0,
    }

    specs_data = {}
    specs_to_show = [s for s in KNOWN_SPECS if s in coverage]
    for spec_name in specs_to_show:
        cov = coverage[spec_name]
        total_reqs += cov.total_requirements
        total_covered += cov.covered_requirements

        for test_type in total_by_type:
            total_by_type[test_type] += cov.count_by_type(test_type)  # type: ignore

        requirements_data = []
        for req_cov in cov.requirements:
            tests_data = [
                {
                    "name": t.test_name or "file-level",
                    "type": t.test_type,
                    "file": t.file_path,
                    "skipped": t.skipped,
                }
                for t in req_cov.tests
            ]
            requirements_data.append(
                {
                    "text": req_cov.requirement.text,
                    "covered": req_cov.is_covered,
                    "backend_only": req_cov.is_backend_only,
                    "skipped_only": req_cov.is_skipped_only,
                    "tests": tests_data,
                }
            )

        uncovered = [req_cov.requirement.text for req_cov in cov.requirements if not req_cov.is_covered]

        backend_only = [req_cov.requirement.text for req_cov in cov.requirements if req_cov.is_backend_only]

        skipped_only = [req_cov.requirement.text for req_cov in cov.requirements if req_cov.is_skipped_only]

        roadmap = [req.text for req in cov.roadmap_requirements]

        unlinked_tests_data = [
            {
                "name": t.test_name or "file-level",
                "type": t.test_type,
                "file": t.file_path,
                "skipped": t.skipped,
            }
            for t in cov.unlinked_tests
        ]

        specs_data[spec_name] = {
            "total_requirements": cov.total_requirements,
            "covered_requirements": cov.covered_requirements,
            "coverage_percent": cov.coverage_percent,
            "by_type": {
                "unit": cov.count_by_type("unit"),
                "integration": cov.count_by_type("integration"),
                "e2e-mocked": cov.count_by_type("e2e-mocked"),
                "e2e-real": cov.count_by_type("e2e-real"),
            },
            "requirements": requirements_data,
            "uncovered": uncovered,
            "backend_only": backend_only,
            "backend_only_count": len(backend_only),
            "skipped_only": skipped_only,
            "skipped_only_count": len(skipped_only),
            "roadmap": roadmap,
            "roadmap_count": len(roadmap),
            "unlinked_tests": unlinked_tests_data,
        }

    return {
        "generated": datetime.now().isoformat(),
        "specs": specs_data,
        "summary": {
            "total_requirements": total_reqs,
            "covered_requirements": total_covered,
            "coverage_percent": 100 * total_covered // total_reqs if total_reqs > 0 else 0,
        },
        "pyramid": total_by_type,
        "unknown_specs": dict(sorted((unknown_specs or {}).items())),
    }


def generate_markdown_report(coverage: dict[str, SpecCoverage], unknown_specs: dict[str, int] | None = None) -> str:
    """Generate a markdown report of spec coverage."""
    lines = [
        "# Spec Test Coverage Map",
        "",
        f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "This report shows test coverage for each specification's success criteria.",
        "",
    ]

    # Unknown spec tags get reported loudly, up front
    if unknown_specs:
        total_unknown = sum(unknown_specs.values())
        lines.extend(
            [
                "## :rotating_light: Unknown Spec Tags",
                "",
                f"**{total_unknown} test tag(s) reference specs with no `specs/<NAME>_SPEC.md` file.**",
                "These tests earn ZERO coverage credit until the spec file is added or the tag is fixed:",
                "",
                "| Unknown Spec | Tagged Tests |",
                "|--------------|--------------|",
            ]
        )
        for spec_name, count in sorted(unknown_specs.items()):
            lines.append(f"| {spec_name} | {count} |")
        lines.append("")

    lines.extend(
        [
            "## Test Pyramid Summary",
            "",
            "| Type | Count | Description |",
            "|------|-------|-------------|",
        ]
    )

    # Calculate totals
    total_by_type: dict[str, int] = {
        "unit": 0,
        "integration": 0,
        "e2e-mocked": 0,
        "e2e-real": 0,
    }
    specs_to_show = [s for s in KNOWN_SPECS if s in coverage]
    for spec_name in specs_to_show:
        cov = coverage[spec_name]
        for test_type in total_by_type:
            total_by_type[test_type] += cov.count_by_type(test_type)  # type: ignore

    lines.append(f"| Unit | {total_by_type['unit']} | pytest unit tests, Vitest tests |")
    lines.append(f"| Integration | {total_by_type['integration']} | pytest with real DB/API |")
    lines.append(f"| E2E (Mocked) | {total_by_type['e2e-mocked']} | Playwright with mocked API |")
    lines.append(f"| E2E (Real) | {total_by_type['e2e-real']} | Playwright with real API |")
    lines.append("")

    # Coverage summary table
    lines.extend(
        [
            "## Coverage Summary",
            "",
            "| Spec | Reqs | Covered | Cover% | Unit | Int | E2E-M | E2E-R | BE-only |",
            "|------|------|---------|--------|------|-----|-------|-------|---------|",
        ]
    )

    total_reqs = 0
    total_covered = 0

    for spec_name in specs_to_show:
        cov = coverage[spec_name]
        total_reqs += cov.total_requirements
        total_covered += cov.covered_requirements

        anchor = spec_name.lower().replace("_", "-")
        status_icon = "   " if cov.coverage_percent == 100 else " ! " if cov.coverage_percent < 50 else " * "

        backend_only = cov.backend_only_requirements
        be_only_str = f"**{backend_only}**" if backend_only > 0 else "0"
        lines.append(
            f"| [{spec_name}](#{anchor}) | {cov.total_requirements} | "
            f"{cov.covered_requirements} | {cov.coverage_percent}% | "
            f"{cov.count_by_type('unit')} | {cov.count_by_type('integration')} | "
            f"{cov.count_by_type('e2e-mocked')} | {cov.count_by_type('e2e-real')} | {be_only_str} |"
        )

    total_percent = 100 * total_covered // total_reqs if total_reqs > 0 else 0
    lines.extend(
        [
            "",
            f"**Total**: {total_covered}/{total_reqs} requirements covered ({total_percent}%)",
            "",
            "---",
            "",
        ]
    )

    # Detailed per-spec sections
    for spec_name in specs_to_show:
        cov = coverage[spec_name]
        lines.append(f"## {spec_name}")
        lines.append("")

        if cov.total_requirements == 0 and not cov.unlinked_tests and not cov.roadmap_requirements:
            lines.append("No success criteria defined in spec.")
            lines.append("")
            continue

        if cov.total_requirements > 0:
            lines.append(
                f"**Coverage**: {cov.covered_requirements}/{cov.total_requirements} "
                f"requirements ({cov.coverage_percent}%)"
            )
            lines.append("")

            # Show uncovered requirements prominently.
            # Skipped-only criteria are uncovered too, but annotated so the reason is visible.
            uncovered = [req for req in cov.requirements if not req.is_covered]
            if uncovered:
                lines.append("### Uncovered Requirements")
                lines.append("")
                for req_cov in uncovered:
                    if req_cov.is_skipped_only:
                        n_skipped = len(req_cov.tests)
                        lines.append(
                            f"- [ ] {req_cov.requirement.text} "
                            f"**(skipped-only: {n_skipped} skipped/xfail test(s) — not counted)**"
                        )
                    else:
                        lines.append(f"- [ ] {req_cov.requirement.text}")
                lines.append("")

            # Show backend-only requirements (covered but no frontend tests)
            backend_only = [req for req in cov.requirements if req.is_backend_only]
            if backend_only:
                lines.append("### Backend-Only Requirements (no frontend tests)")
                lines.append("")
                lines.append("These requirements are covered by backend tests only. UI regressions won't be caught:")
                lines.append("")
                for req_cov in backend_only:
                    test_types = ", ".join(sorted(req_cov.test_types))
                    lines.append(f"- :warning: {req_cov.requirement.text} ({test_types})")
                lines.append("")

            # Show covered requirements
            covered = [req for req in cov.requirements if req.is_covered]
            if covered:
                lines.append("### Covered Requirements")
                lines.append("")
                for req_cov in covered:
                    test_types = ", ".join(sorted(req_cov.test_types))
                    be_flag = " **[BE-only]**" if req_cov.is_backend_only else ""
                    lines.append(f"- [x] {req_cov.requirement.text} ({test_types}){be_flag}")
                lines.append("")

        # Roadmap criteria: not shipping, excluded from the coverage denominator
        if cov.roadmap_requirements:
            lines.append("### Roadmap (not shipping)")
            lines.append("")
            lines.append("These criteria are roadmap-only and excluded from the coverage denominator:")
            lines.append("")
            for req in cov.roadmap_requirements:
                lines.append(f"- {req.text}")
            lines.append("")

        # Show unlinked tests (tests without @req markers)
        if cov.unlinked_tests:
            lines.append("### Tests Without Requirement Links")
            lines.append("")
            lines.append("These tests are tagged with the spec but don't link to specific requirements:")
            lines.append("")
            for test in cov.unlinked_tests:
                test_desc = test.test_name or "file-level"
                skipped_flag = " **[skipped — not counted]**" if test.skipped else ""
                lines.append(f"- `{test.file_path}` ({test_desc}) [{test.test_type}]{skipped_flag}")
            lines.append("")

    # Tagging instructions
    lines.extend(
        [
            "---",
            "",
            "## How to Tag Tests",
            "",
            "### pytest",
            "```python",
            '@pytest.mark.spec("SPEC_NAME")',
            '@pytest.mark.req("Requirement text from success criteria")',
            "def test_something(): ...",
            "```",
            "",
            "### Playwright",
            "```typescript",
            "test.use({ tag: ['@spec:SPEC_NAME', '@req:Requirement text'] });",
            "```",
            "",
            "### Vitest",
            "```typescript",
            "// @spec SPEC_NAME",
            "// @req Requirement text from success criteria",
            "```",
            "",
        ]
    )

    return "\n".join(lines)


def print_affected_specs(affected_specs: set[str], changed_files: list[str], json_output: bool = False):
    """Print affected specs information."""
    if json_output:
        print(
            json.dumps(
                {
                    "affected_specs": sorted(affected_specs),
                    "changed_files": changed_files,
                    "count": len(affected_specs),
                },
                indent=2,
            )
        )
    else:
        print(f"\nAffected specs ({len(affected_specs)}):")
        if affected_specs:
            for spec in sorted(affected_specs):
                print(f"  - {spec}")
        else:
            print("  (none detected)")
        print(f"\nChanged files ({len(changed_files)}):")
        for f in changed_files[:10]:  # Show first 10
            print(f"  - {f}")
        if len(changed_files) > 10:
            print(f"  ... and {len(changed_files) - 10} more")
        print("")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Analyze spec test coverage")
    parser.add_argument("--json", action="store_true", help="Output JSON to stdout instead of console summary")
    parser.add_argument("--no-markdown", action="store_true", help="Skip generating markdown report")
    parser.add_argument(
        "--affected",
        nargs="?",
        const="HEAD~1",
        metavar="REF",
        help="Only show specs affected by changes since REF (default: HEAD~1)",
    )
    parser.add_argument("--specs", nargs="+", metavar="SPEC", help="Only analyze specific specs (space-separated list)")
    args = parser.parse_args()

    # Determine which specs to analyze
    specs_to_analyze: set[str] | None = None
    changed_files: list[str] = []

    if args.affected:
        # Detect affected specs from git changes
        detector = AffectedSpecDetector(base_ref=args.affected)
        changed_files = detector.get_changed_files()
        specs_to_analyze = detector.detect_affected_specs(changed_files)

        if not specs_to_analyze:
            if args.json:
                print(
                    json.dumps(
                        {
                            "affected_specs": [],
                            "changed_files": changed_files,
                            "message": "No specs affected by changes",
                        },
                        indent=2,
                    )
                )
            else:
                print(f"No specs affected by changes since {args.affected}")
                print(f"Changed files: {len(changed_files)}")
                for f in changed_files[:5]:
                    print(f"  - {f}")
            return

    if args.specs:
        # Filter to specific specs
        requested_specs = set(args.specs)
        invalid_specs = requested_specs - set(KNOWN_SPECS)
        if invalid_specs:
            print(f"Unknown specs: {', '.join(sorted(invalid_specs))}")
            print(f"Valid specs: {', '.join(KNOWN_SPECS)}")
            return
        if specs_to_analyze:
            specs_to_analyze = specs_to_analyze & requested_specs
        else:
            specs_to_analyze = requested_specs

    # Parse specs for requirements
    spec_parser = SpecParser()
    requirements = spec_parser.parse_all()

    # Scan tests
    scanner = SpecCoverageScanner()
    tests = scanner.scan_all()

    # Filter to affected specs if specified
    if specs_to_analyze:
        requirements = {k: v for k, v in requirements.items() if k in specs_to_analyze}
        tests = [t for t in tests if t.spec_name in specs_to_analyze]

    # Build coverage data
    coverage = build_coverage(requirements, tests)

    # Filter coverage to only requested specs
    if specs_to_analyze:
        coverage = {k: v for k, v in coverage.items() if k in specs_to_analyze}

    if args.json:
        # JSON output mode
        report = generate_json_report(coverage, unknown_specs=scanner.unknown_specs)
        if args.affected:
            report["affected_mode"] = {
                "base_ref": args.affected,
                "changed_files": changed_files,
                "affected_specs": sorted(specs_to_analyze) if specs_to_analyze else [],
            }
        print(json.dumps(report, indent=2))
    else:
        # Console output mode
        if args.affected:
            print(f"Specs affected by changes since {args.affected}:")
            print_affected_specs(specs_to_analyze or set(), changed_files)

        print("Scanning for spec coverage markers...")

        # Report unknown spec tags loudly, before the summary table
        print_unknown_specs_warning(scanner.unknown_specs)

        print_console_summary(coverage)

        if not args.no_markdown and not args.affected:
            # Only write full markdown report when not in affected mode
            report = generate_markdown_report(coverage, unknown_specs=scanner.unknown_specs)
            output_path = Path("specs/SPEC_COVERAGE_MAP.md")
            output_path.write_text(report)
            print(f"Report written to: {output_path}")

        # Repeat unknown-spec warning at the end so it is not scrolled away
        print_unknown_specs_warning(scanner.unknown_specs)


if __name__ == "__main__":
    main()
