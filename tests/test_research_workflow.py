"""Tests for the research workflow tools: sweeps, benchmark listing, self-check."""

import asyncio
import json

import pytest

from rocket_tools.workflows.engine import parameter_sweep


def _call(name, params):
    from rocket_tools.server import mcp

    result = asyncio.run(mcp.call_tool(name, params))
    return json.loads(result[0].text)


class TestParameterSweep:
    def test_monotonic_pressure_ratio(self):
        sw = parameter_sweep("isentropic_flow", {"gamma": 1.4}, "mach", [1.0, 2.0, 3.0, 4.0])
        pr = [p["outputs"]["pressure_ratio"] for p in sw["points"]]
        assert pr == sorted(pr, reverse=True)  # p/p0 falls with Mach
        assert sw["sweep_parameter"] == "mach"

    def test_bad_point_recorded_not_aborted(self):
        # mach=0.5 is subsonic -> isentropic_flow is fine, but mach=0 errors.
        sw = parameter_sweep("isentropic_flow", {"gamma": 1.4}, "mach", [0.0, 2.0])
        assert "error" in sw["points"][0]
        assert "outputs" in sw["points"][1]

    def test_empty_values_rejected(self):
        with pytest.raises(Exception):
            parameter_sweep("isentropic_flow", {"gamma": 1.4}, "mach", [])


class TestResearchToolsViaMCP:
    def test_list_validation_benchmarks(self):
        data = _call("list_validation_benchmarks", {})
        assert data["count"] >= 15
        names = {b["name"] for b in data["benchmarks"]}
        assert "isentropic_mach_2" in names
        assert all("reference" in b for b in data["benchmarks"])

    def test_validate_result_pass(self):
        from rocket_tools.aerodynamics import isentropic_flow

        good = isentropic_flow(mach=2.0, gamma=1.4)
        data = _call("validate_result", {"benchmark_name": "isentropic_mach_2", "result": good})
        assert data["passed"] is True
        assert "Anderson" in data["reference"]

    def test_validate_result_fail_reports_errors(self):
        data = _call(
            "validate_result",
            {"benchmark_name": "isentropic_mach_2", "result": {"pressure_ratio": 0.9}},
        )
        assert data["passed"] is False
        assert data["errors"]

    def test_parameter_sweep_via_mcp(self):
        data = _call(
            "parameter_sweep",
            {
                "tool_name": "rocket_delta_v",
                "params": {"specific_impulse_s": 320, "final_mass_kg": 1000},
                "sweep_parameter": "initial_mass_kg",
                "values": [2000, 4000, 8000],
            },
        )
        dv = [p["outputs"]["delta_v_ms"] for p in data["points"]]
        assert dv == sorted(dv)  # more propellant -> more delta-v

    def test_parameter_sweep_unknown_tool_errors(self):
        data = _call(
            "parameter_sweep",
            {"tool_name": "warp", "params": {}, "sweep_parameter": "x", "values": [1, 2]},
        )
        # Every point fails with an unknown-tool error, but the call itself returns a table.
        assert all("error" in p for p in data["points"])
