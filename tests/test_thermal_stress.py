"""Tests for thermal stress of a restrained member (audit Batch 7)."""

import pytest

from rocket_tools.structural import thermal_stress


class TestThermalStress:
    def test_fully_constrained_aluminum(self):
        # E=70 GPa, alpha=23.6e-6/K, dT=100 K, fully constrained.
        # sigma = -E*alpha*dT = -70e9*23.6e-6*100 = -165.2 MPa (compressive).
        r = thermal_stress(70e9, 23.6e-6, 100.0, length_m=1.0, area_m2=1e-4)
        assert r["thermal_stress_mpa"] == pytest.approx(-165.2, abs=0.01)
        assert r["stress_type"] == "compressive"
        assert r["free_thermal_strain"] == pytest.approx(23.6e-4, rel=1e-6)
        assert r["free_elongation_m"] == pytest.approx(23.6e-4, rel=1e-6)  # L=1 m
        assert r["restraint_force_n"] == pytest.approx(-165.2e6 * 1e-4, rel=1e-4)

    def test_constraint_factor_scales_stress(self):
        full = thermal_stress(70e9, 23.6e-6, 100.0)["thermal_stress_mpa"]
        half = thermal_stress(70e9, 23.6e-6, 100.0, constraint_factor=0.5)["thermal_stress_mpa"]
        assert half == pytest.approx(full / 2.0, rel=1e-9)

    def test_free_member_has_no_stress(self):
        r = thermal_stress(70e9, 23.6e-6, 100.0, constraint_factor=0.0, length_m=2.0)
        assert r["thermal_stress_pa"] == pytest.approx(0.0)
        assert r["stress_type"] == "none"
        # Free expansion still happens: dL = alpha*dT*L.
        assert r["free_elongation_m"] == pytest.approx(23.6e-6 * 100.0 * 2.0, rel=1e-6)
        assert r["restrained_elongation_m"] == pytest.approx(r["free_elongation_m"], rel=1e-9)

    def test_cooling_is_tensile(self):
        r = thermal_stress(70e9, 23.6e-6, -50.0)
        assert r["stress_type"] == "tensile"
        assert r["thermal_stress_pa"] > 0

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"youngs_modulus_pa": 0.0},
            {"constraint_factor": 1.5},
            {"constraint_factor": -0.1},
            {"length_m": 0.0},
            {"area_m2": -1.0},
        ],
    )
    def test_invalid_inputs_rejected(self, kwargs):
        args = {"youngs_modulus_pa": 70e9, "cte_per_k": 23.6e-6, "delta_temperature_k": 100.0}
        args.update(kwargs)
        with pytest.raises(ValueError):
            thermal_stress(**args)
