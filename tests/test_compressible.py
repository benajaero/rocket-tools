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
        assert result["wave_angle_deg"] > 30.0  # Mach angle for M=2 is 30°
        assert result["wave_angle_deg"] < 90.0
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
