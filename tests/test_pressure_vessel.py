"""Tests for thin-wall pressure-vessel stress (Batch 8)."""

import math

import pytest

from rocket_tools.structural import pressure_vessel_stress


class TestPressureVesselStress:
    def test_cylinder_hand_computed(self):
        # p=10 MPa, r=1 m, t=0.01 m: hoop=1000 MPa, long=500 MPa, vM=1000*sqrt(0.75).
        r = pressure_vessel_stress(10e6, 1.0, 0.01, "cylinder")
        assert r["hoop_stress_mpa"] == pytest.approx(1000.0)
        assert r["longitudinal_stress_mpa"] == pytest.approx(500.0)
        assert r["von_mises_stress_mpa"] == pytest.approx(1000.0 * math.sqrt(0.75), rel=1e-5)
        assert r["hoop_stress_pa"] == pytest.approx(2 * r["longitudinal_stress_pa"])
        assert r["radius_to_thickness_ratio"] == pytest.approx(100.0)
        assert r["thin_wall_valid"] is True

    def test_sphere_is_half_cylinder_hoop(self):
        r = pressure_vessel_stress(10e6, 1.0, 0.01, "sphere")
        assert r["hoop_stress_mpa"] == pytest.approx(500.0)
        assert r["longitudinal_stress_mpa"] == pytest.approx(500.0)
        # Equal biaxial stress -> von Mises equals the membrane stress.
        assert r["von_mises_stress_mpa"] == pytest.approx(500.0)

    def test_margin_of_safety_against_yield(self):
        r = pressure_vessel_stress(10e6, 1.0, 0.01, "cylinder", material_yield_pa=1200e6)
        # MS = yield / vonMises - 1 = 1200 / 866.025 - 1 ~= 0.3856
        expected = 1200.0 / (1000.0 * math.sqrt(0.75)) - 1.0
        assert r["margin_of_safety"] == pytest.approx(expected, abs=1e-3)
        assert r["yields"] is False

    def test_yield_exceeded_flagged(self):
        r = pressure_vessel_stress(10e6, 1.0, 0.01, "cylinder", material_yield_pa=500e6)
        assert r["margin_of_safety"] < 0
        assert r["yields"] is True

    def test_thick_wall_flagged(self):
        r = pressure_vessel_stress(10e6, 0.05, 0.01, "cylinder")
        assert r["radius_to_thickness_ratio"] == pytest.approx(5.0)
        assert r["thin_wall_valid"] is False
        assert "note" in r

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"internal_pressure_pa": 0.0},
            {"inner_radius_m": -1.0},
            {"wall_thickness_m": 0.0},
            {"geometry": "cone"},
            {"material_yield_pa": 0.0},
        ],
    )
    def test_invalid_inputs_rejected(self, kwargs):
        args = {
            "internal_pressure_pa": 5e6,
            "inner_radius_m": 0.5,
            "wall_thickness_m": 0.005,
        }
        args.update(kwargs)
        with pytest.raises(ValueError):
            pressure_vessel_stress(**args)
