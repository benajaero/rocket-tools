"""Non-finite inputs (NaN, +/-inf) must be rejected, not propagated.

Pydantic's gt/ge constraints accept infinity on their own (inf > 0 is True), so
without the StrictModel base an inf input would flow through to an inf output.
Every tool must instead return a structured INVALID_PARAMETER error.
"""

import asyncio
import json

import pytest

from rocket_tools.server import mcp

INF = float("inf")
NAN = float("nan")

_DV = {"initial_mass_kg": 10000, "final_mass_kg": 2000}
CASES = [
    ("rocket_delta_v", {"specific_impulse_s": INF, **_DV}),
    ("rocket_delta_v", {"specific_impulse_s": NAN, **_DV}),
    ("mach_number", {"velocity": INF, "altitude_m": 0}),
    ("mach_number", {"velocity": -INF, "altitude_m": 0}),
    ("dynamic_pressure", {"velocity": NAN, "altitude_m": 0}),
    ("isentropic_flow", {"mach": INF}),
    ("hohmann_transfer", {"radius1_m": INF, "radius2_m": 42164137.0}),
    ("stagnation_temperature", {"static_temperature_k": NAN, "mach": 3}),
    # Nested field (cross_section) must be validated too.
    (
        "beam_analysis",
        {
            "load": INF,
            "length": 2.0,
            "youngs_modulus": 200e9,
            "cross_section": {"type": "rectangle", "width": 0.05, "height": 0.01},
        },
    ),
    (
        "beam_analysis",
        {
            "load": 1000.0,
            "length": 2.0,
            "youngs_modulus": 200e9,
            "cross_section": {"type": "rectangle", "width": INF, "height": 0.01},
        },
    ),
]


@pytest.mark.parametrize(("tool_name", "params"), CASES)
def test_nonfinite_input_rejected(tool_name: str, params: dict):
    result = asyncio.run(mcp.call_tool(tool_name, params))
    data = json.loads(result[0].text)
    assert data.get("error") is True, f"{tool_name} accepted a non-finite input: {data}"
    assert data["error_code"] == "INVALID_PARAMETER"
    assert data["parameter"]  # the offending field is named
