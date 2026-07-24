"""Tests for staging optimization and the single-variable design optimizer."""

import math

import pytest

from rocket_tools.optimization import optimize_design, optimize_staging

G0 = 9.80665


def _brute_force_two_stage(target, stages, n=200000):
    """Independent grid search for the optimal 2-stage delta-v split (max payload frac)."""
    c = [s["specific_impulse_s"] * G0 for s in stages]
    eps = [s["structural_ratio"] for s in stages]
    best = (-1.0, None)
    for k in range(1, n):
        dv1 = target * k / n
        dv2 = target - dv1
        n1, n2 = math.exp(dv1 / c[0]), math.exp(dv2 / c[1])
        if n1 >= 1 / eps[0] or n2 >= 1 / eps[1]:
            continue
        pf = ((1 / n1 - eps[0]) / (1 - eps[0])) * ((1 / n2 - eps[1]) / (1 - eps[1]))
        if pf > best[0]:
            best = (pf, (dv1, dv2))
    return best


class TestOptimizeStaging:
    def test_symmetric_stages_split_equally(self):
        stages = [{"specific_impulse_s": 300.0, "structural_ratio": 0.1}] * 2
        r = optimize_staging(9000.0, stages)
        assert r["achievable"] is True
        assert r["total_delta_v_ms"] == pytest.approx(9000.0, rel=1e-4)
        dv = [s["delta_v_ms"] for s in r["stages"]]
        assert dv[0] == pytest.approx(dv[1], rel=1e-3)  # equal split
        # analytic payload fraction
        c = 300.0 * G0
        n = math.exp(4500.0 / c)
        pf = ((1 / n - 0.1) / 0.9) ** 2
        assert r["optimal_payload_fraction"] == pytest.approx(pf, rel=1e-3)

    def test_heterogeneous_matches_brute_force(self):
        stages = [
            {"specific_impulse_s": 280.0, "structural_ratio": 0.12},
            {"specific_impulse_s": 340.0, "structural_ratio": 0.08},
        ]
        r = optimize_staging(8000.0, stages)
        pf_brute, dv_brute = _brute_force_two_stage(8000.0, stages)
        assert r["optimal_payload_fraction"] == pytest.approx(pf_brute, rel=1e-3)
        dv = [s["delta_v_ms"] for s in r["stages"]]
        assert dv[0] == pytest.approx(dv_brute[0], rel=2e-3)
        assert dv[1] == pytest.approx(dv_brute[1], rel=2e-3)

    def test_infeasible_target_reports_ceiling(self):
        stages = [
            {"specific_impulse_s": 280.0, "structural_ratio": 0.12},
            {"specific_impulse_s": 340.0, "structural_ratio": 0.08},
        ]
        r = optimize_staging(20000.0, stages)
        assert r["achievable"] is False
        assert r["max_achievable_delta_v_ms"] < 20000.0

    def test_optimum_beats_uneven_split(self):
        """The reported optimum must have >= payload fraction than a lopsided split."""
        stages = [
            {"specific_impulse_s": 300.0, "structural_ratio": 0.1},
            {"specific_impulse_s": 300.0, "structural_ratio": 0.1},
        ]
        r = optimize_staging(9000.0, stages)
        # A 3000/6000 lopsided split payload fraction:
        c = 300.0 * G0
        n1, n2 = math.exp(3000 / c), math.exp(6000 / c)
        pf_uneven = ((1 / n1 - 0.1) / 0.9) * ((1 / n2 - 0.1) / 0.9)
        assert r["optimal_payload_fraction"] >= pf_uneven

    def test_invalid_structural_ratio_raises(self):
        with pytest.raises(ValueError):
            optimize_staging(5000.0, [{"specific_impulse_s": 300.0, "structural_ratio": 1.5}])


class TestOptimizeDesign:
    def test_monotonic_objective_hits_bound(self):
        r = optimize_design(
            "rocket_delta_v",
            {"initial_mass_kg": 1000.0, "final_mass_kg": 400.0},
            "specific_impulse_s",
            [200.0, 400.0],
            "delta_v_ms",
            "max",
        )
        assert r["optimal_value"] == pytest.approx(400.0, rel=1e-3)

    def test_min_sense(self):
        r = optimize_design(
            "rocket_delta_v",
            {"initial_mass_kg": 1000.0, "final_mass_kg": 400.0},
            "specific_impulse_s",
            [200.0, 400.0],
            "delta_v_ms",
            "min",
        )
        assert r["optimal_value"] == pytest.approx(200.0, rel=1e-3)

    def test_unimodal_interior_optimum(self):
        """thrust_to_weight vs mass has (tw-1)*g maximized at min mass — use an interior
        peak instead. Optimize dynamic pressure ratio? Use a concave objective:
        maximize -(x-3)^2 style via drag_polar L/D over cl (interior max)."""
        r = optimize_design(
            "drag_polar",
            {"cd0": 0.02, "aspect_ratio": 8.0},
            "cl",
            [0.1, 1.5],
            "lift_to_drag_ratio",
            "max",
            iterations=60,
        )
        # (L/D)max occurs at cl = sqrt(cd0 * pi * AR * e), value = 1/(2*sqrt(cd0*k)).
        cd0, ar, e = 0.02, 8.0, 0.85
        k = 1.0 / (math.pi * ar * e)
        cl_opt = math.sqrt(cd0 / k)
        ld_max = 1.0 / (2.0 * math.sqrt(cd0 * k))
        # The objective is rounded to 2 decimals (flat top), so cl converges to a few %,
        # but the achieved L/D must be essentially the analytic maximum.
        assert r["optimal_value"] == pytest.approx(cl_opt, rel=0.05)
        assert r["optimal_objective"] == pytest.approx(ld_max, rel=0.01)
        assert r["evaluations"] > 0

    def test_bad_objective_key_raises(self):
        from rocket_tools.utils.validation import ToolError

        with pytest.raises(ToolError):
            optimize_design(
                "rocket_delta_v",
                {"initial_mass_kg": 1000.0, "final_mass_kg": 400.0},
                "specific_impulse_s",
                [200.0, 400.0],
                "nonexistent_key",
                "max",
            )
