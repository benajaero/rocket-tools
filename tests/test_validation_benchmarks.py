"""Run curated validation benchmarks against published reference values.

References include NASA-TM-X-74335 (US Standard Atmosphere 1976),
Roark's Formulas, Sutton & Biblarz (Rocket Propulsion Elements),
Anderson (Fundamentals of Aerodynamics), and Vallado
(Fundamentals of Astrodynamics and Applications).
"""

import pytest

from rocket_tools.server import (
    aero_analysis,
    beam_analysis,
    isa_atmosphere,
    isentropic_flow,
    normal_shock,
    orbital_velocity,
    rocket_delta_v,
    section_properties,
    skin_friction_coefficient,
)
from rocket_tools.validation import list_benchmarks, validate_benchmark

# Map benchmark tool_name to the callable exposed by the package.
_TOOL_MAP = {
    "isa_atmosphere": isa_atmosphere,
    "beam_analysis": beam_analysis,
    "skin_friction_coefficient": skin_friction_coefficient,
    "rocket_delta_v": rocket_delta_v,
    "isentropic_flow": isentropic_flow,
    "normal_shock": normal_shock,
    "orbital_velocity": orbital_velocity,
    "section_properties": section_properties,
    "aero_analysis": aero_analysis,
}


@pytest.mark.parametrize("benchmark_name", list_benchmarks())
def test_validation_benchmark(benchmark_name: str) -> None:
    """Each curated benchmark must match its reference within tolerance."""
    from rocket_tools.validation import get_benchmark

    benchmark = get_benchmark(benchmark_name)
    tool_name = benchmark["tool_name"]
    tool_fn = _TOOL_MAP[tool_name]

    result = tool_fn(**benchmark["inputs"])

    # Benchmark tools return error dicts on failure, not exceptions.
    assert not isinstance(result, dict) or not result.get(
        "error"
    ), f"Tool {tool_name} returned an error for benchmark {benchmark_name}: {result}"

    validation = validate_benchmark(benchmark_name, result)
    assert validation["passed"], "; ".join(validation["errors"])
