"""Regression gate: every curated benchmark must match its cited reference value.

Each case in ``rocket_tools.validation`` pairs a tool call with an expected value
drawn from an authoritative source (NASA-TM-X-74335, Roark, Anderson, Sutton &
Biblarz, Vallado, Blasius). This test runs every benchmark through the actual MCP
server tool and asserts the output is within tolerance, so a numerical regression
against a published reference fails CI immediately.
"""

import pytest

import rocket_tools.server as server
from rocket_tools.validation import get_benchmark, list_benchmarks
from rocket_tools.validation.benchmarks import validate_benchmark


@pytest.mark.parametrize("name", list_benchmarks())
def test_benchmark_matches_reference(name: str) -> None:
    benchmark = get_benchmark(name)
    tool_name = benchmark["tool_name"]
    tool = getattr(server, tool_name, None)
    assert tool is not None, f"benchmark {name!r} references unknown tool {tool_name!r}"

    result = tool(**benchmark["inputs"])
    assert not result.get("error"), f"tool {benchmark['tool_name']} returned an error: {result}"

    verdict = validate_benchmark(name, result)
    assert verdict["passed"], f"{name} disagrees with {benchmark['reference']}: {verdict['errors']}"


def test_all_benchmarks_have_a_reference() -> None:
    """Every benchmark must cite a non-empty source so the gate is auditable."""
    for name in list_benchmarks():
        benchmark = get_benchmark(name)
        assert benchmark["reference"].strip(), f"benchmark {name!r} has no reference"
        assert benchmark["tolerance"] > 0, f"benchmark {name!r} has non-positive tolerance"
