"""Tests for spec coverage analyzer honesty behaviors (TESTING_SPEC).

Covers three behaviors:
1. Statically skipped/xfailed tests do not count toward requirement coverage,
   and skipped-only criteria are annotated as such in the coverage map.
2. Roadmap criteria ("(roadmap)" suffix or "### Roadmap" heading) are excluded
   from the coverage denominator and listed separately.
3. Tags referencing unknown specs are reported loudly with tagged test counts
   and never crash the analyzer.

Note: embedded pytest/Playwright source snippets are assembled with .format()
placeholders so the analyzer's regex-based source fallback never mistakes the
string literals in THIS file for real spec tags.
"""

import textwrap

import pytest

from tools.spec_coverage_analyzer import (
    KNOWN_SPECS,
    PytestSkipDetector,
    Requirement,
    RequirementCoverage,
    SpecCoverageScanner,
    SpecParser,
    TestCoverage,
    build_coverage,
    find_static_skip_ranges,
    generate_json_report,
    generate_markdown_report,
    offset_in_ranges,
    print_unknown_specs_warning,
)

SKIP_REQ = (
    "Coverage analyzer excludes skipped and xfail tests from requirement coverage "
    "and annotates skipped-only criteria"
)
ROADMAP_REQ = "Coverage analyzer excludes roadmap criteria from the coverage denominator and lists them separately"
UNKNOWN_REQ = "Coverage analyzer reports unknown spec tags with tagged test counts without crashing"

# A spec name that is guaranteed registered (build_coverage only keeps KNOWN_SPECS)
HOST_SPEC = "TESTING_SPEC"


def _requirement(text: str, roadmap: bool = False) -> Requirement:
    return Requirement(text=text, spec_name=HOST_SPEC, line_number=1, roadmap=roadmap)


def _test(requirement: str | None, skipped: bool = False, **overrides) -> TestCoverage:
    kwargs = {
        "file_path": "tests/unit/test_synthetic.py",
        "test_name": "test_synthetic",
        "spec_name": HOST_SPEC,
        "test_type": "unit",
        "requirement": requirement,
        "line_number": 1,
        "skipped": skipped,
    }
    kwargs.update(overrides)
    return TestCoverage(**kwargs)


# ---------------------------------------------------------------------------
# 1. Skip detection
# ---------------------------------------------------------------------------


@pytest.mark.spec("TESTING_SPEC")
@pytest.mark.req(SKIP_REQ)
class TestPytestSkipDetector:
    """Static detection of pytest skip/skipif/xfail markers."""

    PYTEST_SOURCE = textwrap.dedent(
        """
        import pytest

        pytestmark_unrelated = True


        @{mark}.skip(reason="wip")
        def test_skipped():
            pass


        @{mark}.xfail
        def test_xfailed():
            pass


        @{mark}.skipif(True, reason="conditional")
        def test_skipif():
            pass


        def test_active():
            pass


        @{mark}.skip
        class TestSkippedClass:
            def test_inside_skipped_class(self):
                pass


        class TestActiveClass:
            def test_inside_active_class(self):
                pass
        """
    ).format(mark="pytest.mark")

    @pytest.fixture
    def test_file(self, tmp_path):
        path = tmp_path / "test_sample.py"
        path.write_text(self.PYTEST_SOURCE)
        return str(path)

    def test_skip_marker_detected(self, test_file):
        detector = PytestSkipDetector()
        assert detector.is_skipped(f"{test_file}::test_skipped") is True

    def test_xfail_marker_detected(self, test_file):
        detector = PytestSkipDetector()
        assert detector.is_skipped(f"{test_file}::test_xfailed") is True

    def test_skipif_marker_detected(self, test_file):
        detector = PytestSkipDetector()
        assert detector.is_skipped(f"{test_file}::test_skipif") is True

    def test_active_test_not_skipped(self, test_file):
        detector = PytestSkipDetector()
        assert detector.is_skipped(f"{test_file}::test_active") is False

    def test_enclosing_class_skip_inherited(self, test_file):
        detector = PytestSkipDetector()
        assert detector.is_skipped(f"{test_file}::TestSkippedClass::test_inside_skipped_class") is True
        assert detector.is_skipped(f"{test_file}::TestActiveClass::test_inside_active_class") is False

    def test_parametrized_nodeid_resolved(self, test_file):
        detector = PytestSkipDetector()
        assert detector.is_skipped(f"{test_file}::test_skipped[case-a]") is True
        assert detector.is_skipped(f"{test_file}::test_active[case-a]") is False

    def test_module_level_pytestmark_skip(self, tmp_path):
        source = textwrap.dedent(
            """
            import pytest

            pytestmark = {mark}.skip(reason="module disabled")


            def test_anything():
                pass
            """
        ).format(mark="pytest.mark")
        path = tmp_path / "test_module_skip.py"
        path.write_text(source)
        detector = PytestSkipDetector()
        assert detector.is_skipped(f"{path}::test_anything") is True

    def test_missing_file_does_not_crash(self):
        detector = PytestSkipDetector()
        assert detector.is_skipped("tests/does/not/exist_test.py::test_x") is False

    def test_name_based_fallback_lookup(self, test_file):
        detector = PytestSkipDetector()
        assert detector.is_test_name_skipped(test_file, "test_skipped") is True
        assert detector.is_test_name_skipped(test_file, "test_active") is False
        assert detector.is_test_name_skipped(test_file, None) is False


@pytest.mark.spec("TESTING_SPEC")
@pytest.mark.req(SKIP_REQ)
class TestSkippedTestsExcludedFromCoverage:
    """Skipped tests never count toward coverage; skipped-only criteria are annotated."""

    def test_requirement_with_only_skipped_tests_is_uncovered(self):
        req_cov = RequirementCoverage(
            requirement=_requirement("some criterion"),
            tests=[_test("some criterion", skipped=True)],
        )
        assert req_cov.is_covered is False
        assert req_cov.is_skipped_only is True

    def test_requirement_with_active_test_is_covered(self):
        req_cov = RequirementCoverage(
            requirement=_requirement("some criterion"),
            tests=[_test("some criterion", skipped=True), _test("some criterion", skipped=False)],
        )
        assert req_cov.is_covered is True
        assert req_cov.is_skipped_only is False

    def test_requirement_with_no_tests_is_not_skipped_only(self):
        req_cov = RequirementCoverage(requirement=_requirement("some criterion"))
        assert req_cov.is_covered is False
        assert req_cov.is_skipped_only is False

    def test_skipped_tests_excluded_from_pyramid_counts(self):
        criterion = "skip-counted criterion"
        coverage = build_coverage(
            {HOST_SPEC: [_requirement(criterion)]},
            [_test(criterion, skipped=True), _test(criterion, skipped=False)],
        )
        cov = coverage[HOST_SPEC]
        assert cov.covered_requirements == 1
        # Only the active test is counted in the pyramid
        assert cov.count_by_type("unit") == 1

    def test_skipped_only_criterion_rendered_uncovered_with_annotation(self):
        criterion = "criterion with only skipped tests"
        coverage = build_coverage(
            {HOST_SPEC: [_requirement(criterion)]},
            [_test(criterion, skipped=True)],
        )
        cov = coverage[HOST_SPEC]
        assert cov.covered_requirements == 0
        assert cov.skipped_only_requirements == 1

        markdown = generate_markdown_report(coverage)
        assert f"- [ ] {criterion} **(skipped-only:" in markdown

        report = generate_json_report(coverage)
        spec_data = report["specs"][HOST_SPEC]
        assert spec_data["skipped_only"] == [criterion]
        assert criterion in spec_data["uncovered"]
        req_entry = next(r for r in spec_data["requirements"] if r["text"] == criterion)
        assert req_entry["covered"] is False
        assert req_entry["skipped_only"] is True

    def test_playwright_list_entry_with_expected_status_skipped(self):
        scanner = SpecCoverageScanner()
        assert scanner._playwright_spec_is_skipped({"tests": [{"expectedStatus": "skipped"}]}) is True
        assert scanner._playwright_spec_is_skipped({"tests": [{"expectedStatus": "expected"}]}) is False
        assert (
            scanner._playwright_spec_is_skipped(
                {"tests": [{"expectedStatus": "expected", "annotations": [{"type": "fixme"}]}]}
            )
            is True
        )
        assert scanner._playwright_spec_is_skipped({"tests": []}) is False

    def test_playwright_walk_marks_describe_skip_tests_as_skipped(self):
        scanner = SpecCoverageScanner()
        suites = [
            {
                "specs": [
                    {
                        "title": "skipped flow",
                        "file": "e2e/sample.spec.ts",
                        "line": 10,
                        "tags": [f"@spec:{HOST_SPEC}", "@req:some criterion"],
                        "tests": [{"expectedStatus": "skipped"}],
                    },
                    {
                        "title": "active flow",
                        "file": "e2e/sample.spec.ts",
                        "line": 30,
                        "tags": [f"@spec:{HOST_SPEC}", "@req:some criterion"],
                        "tests": [{"expectedStatus": "expected"}],
                    },
                ],
                "suites": [],
            }
        ]
        scanner._walk_playwright_suites(suites, set())
        by_title = {t.test_name: t for t in scanner.tests}
        assert by_title["skipped flow"].skipped is True
        assert by_title["active flow"].skipped is False

    def test_playwright_source_skip_ranges(self):
        content = textwrap.dedent(
            """
            {t}.describe.skip('disabled suite', () => {{
              {t}('inside skipped describe', {{ tag: ['INSIDE'] }}, async () => {{}});
            }});

            {t}('active test', {{ tag: ['OUTSIDE'] }}, async () => {{}});
            """
        ).format(t="test")
        ranges = find_static_skip_ranges(content, SpecCoverageScanner.PLAYWRIGHT_SKIP_CALL_PATTERN)
        assert ranges, "test.describe.skip block must produce a skip range"
        inside = content.index("INSIDE")
        outside = content.index("OUTSIDE")
        assert offset_in_ranges(inside, ranges) is True
        assert offset_in_ranges(outside, ranges) is False


# ---------------------------------------------------------------------------
# 2. Roadmap criteria
# ---------------------------------------------------------------------------


@pytest.mark.spec("TESTING_SPEC")
@pytest.mark.req(ROADMAP_REQ)
class TestRoadmapCriteria:
    """Roadmap criteria are excluded from the denominator and listed separately."""

    SPEC_CONTENT = textwrap.dedent(
        """
        # Sample Spec

        ## Success Criteria

        - [ ] shipped behavior works
        - [ ] future behavior (roadmap)

        ### Roadmap

        - [ ] planned behavior one
        - [ ] planned behavior two

        ### More Criteria

        - [ ] another shipped behavior
        """
    )

    def test_roadmap_suffix_detected(self):
        reqs = SpecParser().parse_spec_text(self.SPEC_CONTENT, HOST_SPEC)
        by_text = {r.text: r.roadmap for r in reqs}
        assert by_text["future behavior (roadmap)"] is True
        assert by_text["shipped behavior works"] is False

    def test_roadmap_heading_section_detected(self):
        reqs = SpecParser().parse_spec_text(self.SPEC_CONTENT, HOST_SPEC)
        by_text = {r.text: r.roadmap for r in reqs}
        assert by_text["planned behavior one"] is True
        assert by_text["planned behavior two"] is True

    def test_roadmap_section_ends_at_next_heading(self):
        reqs = SpecParser().parse_spec_text(self.SPEC_CONTENT, HOST_SPEC)
        by_text = {r.text: r.roadmap for r in reqs}
        assert by_text["another shipped behavior"] is False

    def test_roadmap_excluded_from_denominator(self):
        requirements = {
            HOST_SPEC: [
                _requirement("shipped criterion"),
                _requirement("future criterion (roadmap)", roadmap=True),
            ]
        }
        coverage = build_coverage(requirements, [_test("shipped criterion")])
        cov = coverage[HOST_SPEC]
        assert cov.total_requirements == 1
        assert cov.covered_requirements == 1
        assert cov.coverage_percent == 100
        assert [r.text for r in cov.roadmap_requirements] == ["future criterion (roadmap)"]

    def test_roadmap_rendered_in_separate_list(self):
        requirements = {
            HOST_SPEC: [
                _requirement("shipped criterion"),
                _requirement("future criterion (roadmap)", roadmap=True),
            ]
        }
        coverage = build_coverage(requirements, [])
        markdown = generate_markdown_report(coverage)
        assert "### Roadmap (not shipping)" in markdown
        assert "- future criterion (roadmap)" in markdown
        # Roadmap criteria must NOT appear as uncovered checkboxes
        assert "- [ ] future criterion (roadmap)" not in markdown

        report = generate_json_report(coverage)
        spec_data = report["specs"][HOST_SPEC]
        assert spec_data["roadmap"] == ["future criterion (roadmap)"]
        assert spec_data["roadmap_count"] == 1
        assert "future criterion (roadmap)" not in spec_data["uncovered"]

    def test_test_tagged_to_roadmap_criterion_becomes_unlinked(self):
        """Tests tagging a roadmap criterion must not vanish silently."""
        requirements = {HOST_SPEC: [_requirement("future criterion (roadmap)", roadmap=True)]}
        coverage = build_coverage(requirements, [_test("future criterion (roadmap)")])
        cov = coverage[HOST_SPEC]
        assert cov.total_requirements == 0
        assert len(cov.unlinked_tests) == 1


# ---------------------------------------------------------------------------
# 3. Unknown spec tags
# ---------------------------------------------------------------------------


@pytest.mark.spec("TESTING_SPEC")
@pytest.mark.req(UNKNOWN_REQ)
class TestUnknownSpecTags:
    """Unknown spec tags are reported loudly with counts and never crash."""

    def test_pytest_source_fallback_counts_unknown_tags(self, tmp_path, monkeypatch):
        unknown = "TOTALLY_UNKNOWN_SPEC"
        assert unknown not in KNOWN_SPECS
        source = textwrap.dedent(
            """
            import pytest


            @{mark}.spec("{unknown}")
            def test_one():
                pass


            @{mark}.spec("{unknown}")
            def test_two():
                pass


            @{mark}.spec("{known}")
            def test_three():
                pass
            """
        ).format(mark="pytest.mark", unknown=unknown, known=HOST_SPEC)
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_unknown_tags.py").write_text(source)

        monkeypatch.setattr(SpecCoverageScanner, "PYTEST_DIR", test_dir)
        scanner = SpecCoverageScanner()
        scanner._scan_pytest_source_fallback()

        assert scanner.unknown_specs == {unknown: 2}
        # Known-spec test is still collected normally
        assert [t.spec_name for t in scanner.tests] == [HOST_SPEC]

    def test_playwright_walk_counts_unknown_tags_without_crashing(self):
        scanner = SpecCoverageScanner()
        suites = [
            {
                "specs": [
                    {
                        "title": "mystery test",
                        "file": "e2e/mystery.spec.ts",
                        "line": 5,
                        "tags": ["@spec:NOT_A_REAL_SPEC"],
                        "tests": [{"expectedStatus": "expected"}],
                    }
                ],
                "suites": [],
            }
        ]
        scanner._walk_playwright_suites(suites, set())
        assert scanner.unknown_specs == {"NOT_A_REAL_SPEC": 1}
        assert scanner.tests == []

    def test_json_report_includes_unknown_spec_counts(self):
        coverage = build_coverage({HOST_SPEC: [_requirement("shipped criterion")]}, [])
        report = generate_json_report(coverage, unknown_specs={"GHOST_SPEC": 3, "ANOTHER_GHOST": 1})
        assert report["unknown_specs"] == {"ANOTHER_GHOST": 1, "GHOST_SPEC": 3}

    def test_json_report_defaults_to_empty_unknown_specs(self):
        coverage = build_coverage({HOST_SPEC: [_requirement("shipped criterion")]}, [])
        report = generate_json_report(coverage)
        assert report["unknown_specs"] == {}

    def test_markdown_report_renders_unknown_specs_loudly(self):
        coverage = build_coverage({HOST_SPEC: [_requirement("shipped criterion")]}, [])
        markdown = generate_markdown_report(coverage, unknown_specs={"GHOST_SPEC": 3})
        assert "Unknown Spec Tags" in markdown
        assert "| GHOST_SPEC | 3 |" in markdown

    def test_console_warning_includes_counts(self, capsys):
        print_unknown_specs_warning({"GHOST_SPEC": 3, "ANOTHER_GHOST": 1})
        out = capsys.readouterr().out
        assert "WARNING" in out
        assert "GHOST_SPEC: 3 tagged test(s)" in out
        assert "ANOTHER_GHOST: 1 tagged test(s)" in out

    def test_console_warning_silent_when_no_unknowns(self, capsys):
        print_unknown_specs_warning({})
        assert capsys.readouterr().out == ""
