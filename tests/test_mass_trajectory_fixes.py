"""Regression tests for propulsion/trajectory/mass fixes (audit Batch 3)."""

import pytest

from rocket_tools.aerodynamics import stagnation_temperature
from rocket_tools.design import composite_cg, propellant_tank_sizing
from rocket_tools.trajectory import simulate_ascent


class TestCompositeCG:
    def test_own_inertia_included(self):
        # Two bodies on the x-axis; their own roll inertia (Ixx) must be added, not dropped.
        no_own = composite_cg([10, 10], [[0, 0, 0], [2, 0, 0]])
        with_own = composite_cg(
            [10, 10], [[0, 0, 0], [2, 0, 0]], inertias=[[5, 20, 20, 0, 0, 0]] * 2
        )
        assert no_own["i_xx_kg_m2"] == pytest.approx(0.0)
        assert with_own["i_xx_kg_m2"] == pytest.approx(10.0)  # 5 + 5

    def test_bad_inertia_shape_rejected(self):
        with pytest.raises(ValueError, match="inertia"):
            composite_cg([1], [[0, 0, 0]], inertias=[[1, 2, 3]])


class TestTankSizing:
    def test_hoop_stress_sizing(self):
        t = propellant_tank_sizing(
            propellant_volume_m3=5.0,
            tank_shape="cylinder",
            design_pressure_pa=3e6,
            material_yield_pa=280e6,
            safety_factor=1.5,
        )
        assert t["wall_thickness_sizing"] == "hoop_stress"
        # hoop stress at the sized thickness equals yield / safety_factor
        assert t["hoop_stress_pa"] == pytest.approx(280e6 / 1.5, rel=1e-3)

    def test_sphere_sized_on_membrane_stress(self):
        # A sphere carries pressure biaxially: sigma = P*r/(2t), so it needs half the
        # wall of a hoop-sized cylinder of the same radius (and about half the mass).
        common = dict(
            propellant_volume_m3=10.0,
            design_pressure_pa=3e6,
            material_yield_pa=2.7e8,
            safety_factor=1.5,
        )
        sph = propellant_tank_sizing(tank_shape="sphere", **common)
        assert sph["wall_thickness_sizing"] == "membrane_stress"
        # wall stress at the sized thickness still reaches yield / safety_factor
        assert sph["hoop_stress_pa"] == pytest.approx(2.7e8 / 1.5, rel=1e-3)
        # sphere wall is exactly half the hoop-sized wall at the same radius
        r = sph["diameter_m"] / 2.0
        hoop_t = 3e6 * r * 1.5 / 2.7e8
        assert sph["wall_thickness_m"] == pytest.approx(hoop_t / 2.0, rel=1e-3)

    def test_ellipsoid_area_not_sphere(self):
        e = propellant_tank_sizing(
            propellant_volume_m3=5.0, tank_shape="ellipsoid", aspect_ratio=2.0
        )
        sphere_area = 4 * 3.141592653589793 * (e["diameter_m"] / 2) ** 2
        assert e["surface_area_m2"] != pytest.approx(sphere_area, rel=1e-3)

    def test_cylinder_aspect_ratio_guard(self):
        with pytest.raises(ValueError, match="aspect_ratio"):
            propellant_tank_sizing(
                propellant_volume_m3=1.0, tank_shape="cylinder", aspect_ratio=1.0
            )


class TestHypersonicGuard:
    def test_perfect_gas_flag(self):
        assert stagnation_temperature(220.0, 3.0)["perfect_gas_valid"] is True
        hyper = stagnation_temperature(220.0, 8.0)
        assert hyper["perfect_gas_valid"] is False
        assert "note" in hyper


class TestApogeeDetection:
    def test_apogee_reached_flag_suborbital(self):
        # A suborbital hop that comes back down within max_time -> apogee reached.
        s = simulate_ascent(
            initial_mass_kg=1000.0,
            dry_mass_kg=400.0,
            specific_impulse_s=250.0,
            mass_flow_rate_kg_s=20.0,
            reference_area_m2=0.2,
            dt=0.1,
        )
        assert s["apogee_reached"] is True

    def test_apogee_not_reached_when_truncated(self):
        # Very short max_time -> still ascending at cutoff -> apogee not reached.
        s = simulate_ascent(
            initial_mass_kg=1000.0,
            dry_mass_kg=400.0,
            specific_impulse_s=250.0,
            mass_flow_rate_kg_s=20.0,
            reference_area_m2=0.2,
            dt=0.1,
            max_time=5.0,
        )
        assert s["apogee_reached"] is False
