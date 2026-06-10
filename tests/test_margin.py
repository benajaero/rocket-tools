"""Tests for margin of safety calculations."""

import pytest

from rocket_tools.structural.margin import (
    combined_margin_of_safety,
    deflection_margin,
    margin_of_safety,
    von_mises_stress,
)


class TestMarginOfSafety:
    def test_stress_based_pass(self):
        result = margin_of_safety(
            allowable_stress_pa=300e6,
            actual_stress_pa=100e6,
            factor_of_safety=1.5,
            failure_mode="yield",
        )
        assert result["margin_of_safety"] == pytest.approx(1.0, abs=0.01)
        assert result["status"] == "PASS"
        assert result["pass"] is True
        assert result["utilization_ratio"] == pytest.approx(0.333, abs=0.001)

    def test_stress_based_fail(self):
        result = margin_of_safety(
            allowable_stress_pa=300e6,
            actual_stress_pa=250e6,
            factor_of_safety=1.5,
            failure_mode="yield",
        )
        assert result["margin_of_safety"] < 0
        assert result["status"] == "FAIL"
        assert result["pass"] is False

    def test_load_based(self):
        result = margin_of_safety(
            allowable_load_n=10000,
            actual_load_n=5000,
            factor_of_safety=2.0,
            failure_mode="buckling",
        )
        assert result["margin_of_safety"] == pytest.approx(0.0, abs=0.01)
        assert result["status"] == "MARGINAL"

    def test_missing_inputs(self):
        with pytest.raises(ValueError, match="Must provide either"):
            margin_of_safety(factor_of_safety=1.5)

    def test_mixed_inputs(self):
        with pytest.raises(ValueError, match="Cannot mix"):
            margin_of_safety(
                allowable_stress_pa=300e6,
                actual_stress_pa=100e6,
                allowable_load_n=10000,
                actual_load_n=5000,
            )

    def test_negative_stress(self):
        with pytest.raises(ValueError, match="Stresses must be > 0"):
            margin_of_safety(
                allowable_stress_pa=-100e6,
                actual_stress_pa=50e6,
            )

    def test_failure_modes(self):
        for mode in ["yield", "ultimate", "buckling", "fatigue", "custom"]:
            result = margin_of_safety(
                allowable_stress_pa=400e6,
                actual_stress_pa=100e6,
                failure_mode=mode,
            )
            assert result["failure_mode"] == mode


class TestVonMisesStress:
    def test_uniaxial_tension(self):
        result = von_mises_stress(sigma_x=100e6)
        assert result["von_mises_stress_pa"] == pytest.approx(100e6, abs=1)
        assert result["sigma_1_pa"] == pytest.approx(100e6, abs=1)

    def test_pure_shear(self):
        result = von_mises_stress(sigma_x=0, sigma_y=0, tau_xy=100e6)
        assert result["von_mises_stress_pa"] == pytest.approx(173.2e6, abs=0.1e6)

    def test_biaxial_equal_tension(self):
        result = von_mises_stress(sigma_x=100e6, sigma_y=100e6)
        assert result["von_mises_stress_pa"] == pytest.approx(100e6, abs=1)

    def test_3d_stress(self):
        result = von_mises_stress(
            sigma_x=100e6, sigma_y=50e6, sigma_z=25e6,
            tau_xy=30e6, tau_yz=15e6, tau_xz=10e6,
        )
        assert result["von_mises_stress_pa"] > 0
        assert result["max_shear_stress_pa"] > 0


class TestCombinedMargin:
    def test_yield_only(self):
        result = combined_margin_of_safety(
            sigma_x=100e6,
            yield_strength_pa=276e6,
            factor_of_safety_yield=1.5,
        )
        assert "margin_of_safety_yield" in result
        assert result["margin_of_safety_yield"]["margin_of_safety"] > 0
        assert "margin_of_safety_ultimate" not in result

    def test_both(self):
        result = combined_margin_of_safety(
            sigma_x=100e6,
            yield_strength_pa=276e6,
            ultimate_strength_pa=310e6,
            factor_of_safety_yield=1.5,
            factor_of_safety_ultimate=1.5,
        )
        assert "margin_of_safety_yield" in result
        assert "margin_of_safety_ultimate" in result
        # Yield MS should be lower than ultimate MS
        ms_y = result["margin_of_safety_yield"]["margin_of_safety"]
        ms_u = result["margin_of_safety_ultimate"]["margin_of_safety"]
        assert ms_y < ms_u

    def test_pure_shear(self):
        result = combined_margin_of_safety(
            sigma_x=0, sigma_y=0, tau_xy=100e6,
            yield_strength_pa=276e6,
        )
        assert result["von_mises_stress_pa"] == pytest.approx(173.2e6, abs=0.1e6)
        assert result["margin_of_safety_yield"]["status"] == "PASS"


class TestDeflectionMargin:
    def test_pass(self):
        result = deflection_margin(
            actual_deflection_m=0.005,
            span_length_m=2.0,
            deflection_limit_ratio=360,
        )
        assert result["margin_of_safety"] > 0
        assert result["status"] == "PASS"
        assert result["deflection_ratio_l_over_d"] == pytest.approx(400.0, abs=1)

    def test_fail(self):
        result = deflection_margin(
            actual_deflection_m=0.01,
            span_length_m=2.0,
            deflection_limit_ratio=360,
        )
        assert result["margin_of_safety"] < 0
        assert result["status"] == "FAIL"

    def test_explicit_allowable(self):
        result = deflection_margin(
            actual_deflection_m=0.005,
            allowable_deflection_m=0.008,
        )
        assert result["margin_of_safety"] == pytest.approx(0.6, abs=0.01)

    def test_missing_inputs(self):
        with pytest.raises(ValueError, match="Must provide either"):
            deflection_margin(actual_deflection_m=0.005)
