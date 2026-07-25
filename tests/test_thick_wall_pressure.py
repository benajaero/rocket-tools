"""Tests for thick-wall (Lame) pressure-vessel stress (Batch 8)."""

import math

import pytest

from rocket_tools.structural import pressure_vessel_stress, thick_wall_pressure_vessel_stress


class TestThickWallCylinder:
    def test_lame_cylinder_hand_computed(self):
        # a=0.1, b=0.15, p=50 MPa. Lame: hoop_i=p(b^2+a^2)/(b^2-a^2)=130 MPa, radial_i=-50,
        # long=p*a^2/(b^2-a^2)=40, hoop_o=80, vM=sqrt(24300e12)=155.88, max shear=90.
        r = thick_wall_pressure_vessel_stress(50e6, 0.1, 0.15, "cylinder", material_yield_pa=250e6)
        assert r["hoop_stress_inner_mpa"] == pytest.approx(130.0, abs=0.01)
        assert r["hoop_stress_outer_mpa"] == pytest.approx(80.0, abs=0.01)
        assert r["radial_stress_inner_pa"] == pytest.approx(-50e6)
        assert r["longitudinal_stress_pa"] == pytest.approx(40e6, rel=1e-4)
        assert r["von_mises_stress_inner_mpa"] == pytest.approx(155.885, abs=0.01)
        assert r["max_shear_stress_inner_pa"] == pytest.approx(90e6, rel=1e-4)
        assert r["margin_of_safety"] == pytest.approx(250.0 / 155.885 - 1.0, abs=1e-3)

    def test_hoop_larger_at_inner_surface(self):
        r = thick_wall_pressure_vessel_stress(30e6, 0.08, 0.12, "cylinder")
        assert r["hoop_stress_inner_mpa"] > r["hoop_stress_outer_mpa"]

    def test_approaches_thin_wall_for_large_ratio(self):
        # For a thin wall (b/a near 1), Lame hoop approaches the membrane p*r/t.
        a, t = 1.0, 0.005
        thick = thick_wall_pressure_vessel_stress(1e6, a, a + t, "cylinder")
        thin = pressure_vessel_stress(1e6, a, t, "cylinder")
        assert thick["hoop_stress_inner_mpa"] == pytest.approx(thin["hoop_stress_mpa"], rel=0.01)


class TestThickWallSphere:
    def test_lame_sphere_hand_computed(self):
        # a=0.1, b=0.15, p=50 MPa. hoop_i=p(2a^3+b^3)/(2(b^3-a^3))=56.579, hoop_o=31.579,
        # vM = hoop_i + p = 106.579 (two equal tangential, radial=-p).
        r = thick_wall_pressure_vessel_stress(50e6, 0.1, 0.15, "sphere")
        assert r["hoop_stress_inner_mpa"] == pytest.approx(56.579, abs=0.01)
        assert r["hoop_stress_outer_mpa"] == pytest.approx(31.579, abs=0.01)
        assert r["von_mises_stress_inner_mpa"] == pytest.approx(106.579, abs=0.01)


class TestValidation:
    @pytest.mark.parametrize(
        "kwargs",
        [
            {"internal_pressure_pa": 0.0},
            {"inner_radius_m": -1.0},
            {"outer_radius_m": 0.1},  # not greater than inner (0.1)
            {"geometry": "cone"},
            {"material_yield_pa": 0.0},
        ],
    )
    def test_invalid_inputs_rejected(self, kwargs):
        args = {"internal_pressure_pa": 50e6, "inner_radius_m": 0.1, "outer_radius_m": 0.15}
        args.update(kwargs)
        with pytest.raises(ValueError):
            thick_wall_pressure_vessel_stress(**args)

    def test_von_mises_is_finite(self):
        r = thick_wall_pressure_vessel_stress(10e6, 0.05, 0.2, "cylinder")
        assert math.isfinite(r["von_mises_stress_inner_pa"])
