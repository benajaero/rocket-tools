"""Tests for the site-count sync logic in scripts/_sync_site.py.

The pipeline rewrites the marketing site's tool/test/benchmark counts from the
live code, so the substitution rules must hit the real count strings and leave
unrelated numbers (material counts, altitudes, versions) alone.
"""

import importlib.util
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "_sync_site", Path(__file__).resolve().parent.parent / "scripts" / "_sync_site.py"
)
assert _SPEC and _SPEC.loader
_sync_site = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_sync_site)

COUNTS = {"TOOLS": "81", "TESTS": "793", "BENCHMARKS": "31"}


def sync(text: str) -> str:
    return _sync_site.apply_rules(text, COUNTS)[0]


class TestToolCounts:
    def test_validated_tools(self):
        assert sync("80 validated tools for structures") == "81 validated tools for structures"

    def test_validated_aerospace_tools(self):
        assert sync("80 validated aerospace tools.") == "81 validated aerospace tools."

    def test_mcp_tools_lowercase(self):
        assert sync("80 MCP tools across") == "81 MCP tools across"

    def test_precision_tools(self):
        assert sync("We built 80 precision tools covering") == (
            "We built 81 precision tools covering"
        )

    def test_all_n_tools(self):
        assert sync("exposes all 80 tools to AI agents") == "exposes all 81 tools to AI agents"

    def test_metrics_value_object(self):
        src = '{ value: "80", label: "MCP tools", sub: "x" }'
        assert sync(src) == '{ value: "81", label: "MCP tools", sub: "x" }'

    def test_json_outcome_object(self):
        src = '"metric": "MCP Tools",\n      "value": "80"'
        assert sync(src) == '"metric": "MCP Tools",\n      "value": "81"'


class TestTestAndBenchmarkCounts:
    def test_tests_badge(self):
        assert sync("603 Tests") == "793 Tests"

    def test_tests_lowercase_json(self):
        assert sync("760 tests, 31 reference benchmarks") == "793 tests, 31 reference benchmarks"

    def test_tests_metric_value(self):
        assert sync('{ value: "760", label: "Tests" }') == '{ value: "793", label: "Tests" }'

    def test_reference_benchmarks(self):
        assert sync("27 reference benchmarks") == "31 reference benchmarks"

    def test_benchmarks_badge(self):
        assert sync("27 Benchmarks") == "31 Benchmarks"


class TestLeavesUnrelatedNumbersAlone:
    @pytest.mark.parametrize(
        "text",
        [
            "49 aerospace alloys and composites",
            "Full 7-layer U.S. Standard Atmosphere 1976 to 86 km",
            "version 0.6.0 released",
            "completes in about 54 ns",
            "run under 1 ms per call",
        ],
    )
    def test_untouched(self, text):
        assert sync(text) == text

    def test_idempotent(self):
        once = sync("80 validated tools, 760 tests, 27 benchmarks")
        assert sync(once) == once  # re-running changes nothing
        assert once == "81 validated tools, 793 tests, 31 benchmarks"
