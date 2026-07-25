"""Tests for compressible flow relations."""

import pytest

from rocket_tools.aerodynamics.compressible import (
    isentropic_flow,
    normal_shock,
    oblique_shock,
    prandtl_meyer,
    prandtl_meyer_from_angle,
)


class TestIsentropicFlow:
    def test_mach_1(self):
        result = isentropic_flow(1.0)
        assert result["temperature_ratio"] == pytest.approx(0.8333, rel=1e-3)
        assert result["pressure_ratio"] == pytest.approx(0.5283, rel=1e-3)
        assert result["area_ratio"] == pytest.approx(1.0, rel=1e-3)

    def test_mach_2(self):
        result = isentropic_flow(2.0)
        assert result["temperature_ratio"] == pytest.approx(0.5556, rel=1e-3)
        assert result["pressure_ratio"] == pytest.approx(0.1278, rel=1e-3)
        assert result["area_ratio"] > 1.0
        assert result["mach_angle_deg"] == pytest.approx(30.0, abs=0.5)

    def test_dynamic_pressure_ratios(self):
        # q = (gamma/2) p M^2, so q/p = (gamma/2) M^2 and q/p0 = (q/p)(p/p0).
        result = isentropic_flow(2.0, gamma=1.4)
        assert result["dynamic_pressure_over_static_pressure"] == pytest.approx(
            0.5 * 1.4 * 2.0**2, rel=1e-6
        )
        assert result["dynamic_pressure_over_stagnation_pressure"] == pytest.approx(
            0.5 * 1.4 * 2.0**2 * result["pressure_ratio"], rel=1e-4
        )

    def test_invalid_mach(self):
        with pytest.raises(ValueError):
            isentropic_flow(0.0)


class TestNormalShock:
    def test_mach_2(self):
        result = normal_shock(2.0)
        assert result["mach_downstream"] == pytest.approx(0.577, rel=1e-2)
        assert result["pressure_ratio"] == pytest.approx(4.5, rel=1e-2)
        assert result["density_ratio"] == pytest.approx(2.667, rel=1e-2)

    def test_invalid_mach(self):
        with pytest.raises(ValueError):
            normal_shock(0.5)
        with pytest.raises(ValueError):
            normal_shock(1.0)


class TestObliqueShock:
    def test_basic(self):
        result = oblique_shock(2.0, 10.0)
        assert result["mach_downstream"] < 2.0
        # Weak (attached) solution: beta ~ 39.3 deg, well below the strong root (~83.7 deg).
        assert result["wave_angle_deg"] == pytest.approx(39.31, abs=0.05)
        assert result["solution"] == "weak"
        assert result["deflection_angle_deg"] == 10.0

    def test_invalid(self):
        with pytest.raises(ValueError):
            oblique_shock(0.5, 10.0)
        with pytest.raises(ValueError):
            oblique_shock(2.0, 0.0)


class TestPrandtlMeyer:
    def test_mach_1(self):
        result = prandtl_meyer(1.0)
        assert result["prandtl_meyer_angle_deg"] == pytest.approx(0.0, abs=0.01)

    def test_mach_2(self):
        result = prandtl_meyer(2.0)
        assert result["prandtl_meyer_angle_deg"] > 20.0

    def test_from_angle(self):
        result = prandtl_meyer_from_angle(26.38)
        assert result["mach"] == pytest.approx(2.0, rel=1e-2)

    def test_invalid(self):
        with pytest.raises(ValueError):
            prandtl_meyer(0.5)
        with pytest.raises(ValueError):
            prandtl_meyer_from_angle(-1.0)


class TestAreaMachRelation:
    def test_area_ratio_at_mach_1(self):
        from rocket_tools.aerodynamics.compressible import _area_ratio

        assert _area_ratio(1.0, 1.4) == pytest.approx(1.0, abs=1e-6)

    def test_area_ratio_supersonic(self):
        from rocket_tools.aerodynamics.compressible import _area_ratio

        assert _area_ratio(2.0, 1.4) > 1.0

    def test_mach_from_area_ratio_invalid(self):
        from rocket_tools.aerodynamics.compressible import _mach_from_area_ratio

        with pytest.raises(ValueError):
            _mach_from_area_ratio(0.5, 1.4)

    def test_mach_from_area_ratio_round_trip(self):
        from rocket_tools.aerodynamics.compressible import _area_ratio, _mach_from_area_ratio

        for mach in [1.5, 2.0, 3.0, 5.0]:
            ar = _area_ratio(mach, 1.4)
            recovered = _mach_from_area_ratio(ar, 1.4)
            assert recovered == pytest.approx(mach, rel=1e-4)


class TestGammaVariation:
    def test_isentropic_with_different_gamma(self):
        result_air = isentropic_flow(2.0, gamma=1.4)
        result_he = isentropic_flow(2.0, gamma=1.67)
        assert result_air["pressure_ratio"] != result_he["pressure_ratio"]

    def test_normal_shock_with_different_gamma(self):
        result_air = normal_shock(2.0, gamma=1.4)
        result_he = normal_shock(2.0, gamma=1.67)
        assert result_air["pressure_ratio"] != result_he["pressure_ratio"]
