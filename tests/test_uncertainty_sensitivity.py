"""Tests for sensitivity ranking, the expanded tool dispatch, and the MCP tool."""

import asyncio
import json

import numpy as np

from rocket_tools.uncertainty import run_with_uncertainty
from rocket_tools.uncertainty.engine import _aggregate_results, _compute_sensitivity
from rocket_tools.workflows.engine import _call_tool, list_callable_tools


class TestAggregationRobustness:
    def test_non_finite_samples_dropped(self):
        # One NaN and one inf must not poison mean/std/min/max/CI; they are dropped
        # and reported, not allowed to turn every statistic into NaN.
        results = [{"x": 1.0}, {"x": 2.0}, {"x": 3.0}, {"x": float("nan")}, {"x": float("inf")}]
        agg = _aggregate_results(results, samples=5)["results"]["x"]
        assert agg["mean"] == 2.0
        assert np.isfinite(agg["std"])
        assert agg["min"] == 1.0 and agg["max"] == 3.0
        assert all(np.isfinite(b) for b in agg["ci_95"])
        assert agg["non_finite_samples"] == 2

    def test_all_non_finite_key_skipped(self):
        agg = _aggregate_results([{"x": float("inf")}, {"x": float("nan")}], samples=2)
        assert "x" not in agg["results"]


class TestSensitivityRobustness:
    def test_non_numeric_later_sample_does_not_crash(self):
        # An output that is numeric in sample 0 but non-numeric later must not crash
        # the correlation path (the input/output arrays stay aligned).
        param_samples = {"a": np.array([1.0, 2.0, 3.0, 4.0, 5.0])}
        results = [{"y": 2.0}, {"y": 4.0}, {"y": 6.0}, {"y": "oops"}, {"y": 10.0}]
        out = _compute_sensitivity(param_samples, results)  # must not raise
        assert isinstance(out, dict)


class TestToolDispatch:
    def test_covers_all_computational_tools(self):
        # Was 11 hand-picked tools; now every library computation is reachable.
        tools = list_callable_tools()
        assert len(tools) >= 45
        for name in ("rocket_delta_v", "normal_shock", "hohmann_transfer", "column_buckling"):
            assert name in tools

    def test_optimization_and_standards_tools_dispatchable(self):
        # These modules were omitted from the dispatch loop, so their tools could not be
        # composed in a workflow despite the "any tool can be composed" contract.
        tools = list_callable_tools()
        for name in ("optimize_staging", "optimize_design", "fmea_report", "design_review_report"):
            assert name in tools

    def test_dispatch_calls_previously_unsupported_tool(self):
        out = _call_tool(
            "rocket_delta_v",
            {
                "specific_impulse_s": 320,
                "initial_mass_kg": 10000,
                "final_mass_kg": 2000,
            },
        )
        assert out["delta_v_ms"] > 0


class TestSensitivity:
    def test_dominant_input_ranks_first(self):
        # q = 0.5*rho*V^2: velocity (quadratic, large spread) must dominate altitude.
        r = run_with_uncertainty(
            "dynamic_pressure",
            {
                "velocity": {"distribution": "normal", "mean": 250, "std": 40},
                "altitude_m": {"distribution": "uniform", "low": 0, "high": 1000},
            },
            samples=2000,
            seed=7,
        )
        drivers = r["sensitivity"]["dynamic_pressure_pa"]
        assert drivers[0]["input"] == "velocity"
        assert drivers[0]["abs_correlation"] > 0.8

    def test_constant_input_not_ranked(self):
        r = run_with_uncertainty(
            "rocket_delta_v",
            {
                "specific_impulse_s": {"distribution": "normal", "mean": 320, "std": 5},
                "initial_mass_kg": 10000,  # fixed -> zero variance
                "final_mass_kg": 2000,
            },
            samples=1000,
            seed=3,
        )
        inputs = {d["input"] for d in r["sensitivity"]["delta_v_ms"]}
        assert "specific_impulse_s" in inputs
        assert "initial_mass_kg" not in inputs

    def test_sensitivity_can_be_disabled(self):
        r = run_with_uncertainty(
            "dynamic_pressure",
            {"velocity": {"distribution": "normal", "mean": 250, "std": 10}, "altitude_m": 0},
            samples=500,
            seed=1,
            sensitivity=False,
        )
        assert "sensitivity" not in r


class TestPropagateUncertaintyViaMCP:
    def _call(self, params):
        from rocket_tools.server import mcp

        result = asyncio.run(mcp.call_tool("propagate_uncertainty", params))
        return json.loads(result[0].text)

    def test_full_result(self):
        data = self._call(
            {
                "tool_name": "rocket_delta_v",
                "params": {
                    "specific_impulse_s": {"distribution": "normal", "mean": 320, "std": 5},
                    "initial_mass_kg": {"distribution": "normal", "mean": 10000, "std": 200},
                    "final_mass_kg": 2000,
                },
                "samples": 1500,
                "seed": 1,
            }
        )
        dv = data["results"]["delta_v_ms"]
        assert 4900 < dv["mean"] < 5200  # near the deterministic 5050 m/s
        assert dv["ci_95"][0] < dv["mean"] < dv["ci_95"][1]
        assert data["sensitivity"]["delta_v_ms"][0]["input"] == "specific_impulse_s"

    def test_unknown_tool_is_structured_error(self):
        data = self._call({"tool_name": "warp_drive", "params": {"x": 1}})
        assert data["error"] is True
        assert data["error_code"] == "UNKNOWN_TOOL"
        assert data["parameter"] == "tool_name"
