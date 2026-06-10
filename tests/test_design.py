"""Tests for design and performance tools."""

import pytest

from rocket_tools.design.mass import composite_cg, propellant_tank_sizing
from rocket_tools.design.performance import (
    multi_stage_delta_v,
    orbital_velocity,
    payload_fraction,
    rocket_delta_v,
    thrust_to_weight,
)


class TestRocketDeltaV:
    def test_basic(self):
        result = rocket_delta_v(
            specific_impulse_s=300.0,
            initial_mass_kg=10000.0,
            final_mass_kg=2000.0,
        )
        assert result["delta_v_ms"] > 0
        assert result["mass_ratio"] == 5.0
        assert result["propellant_fraction"] == 0.8

    def test_invalid(self):
        with pytest.raises(ValueError):
            rocket_delta_v(specific_impulse_s=300, initial_mass_kg=1000, final_mass_kg=1000)


class TestMultiStageDeltaV:
    def test_two_stage(self):
        stages = [
            {
                "specific_impulse_s": 300.0,
                "dry_mass_kg": 1000.0,
                "propellant_mass_kg": 8000.0,
                "payload_mass_kg": 2000.0,
            },
            {
                "specific_impulse_s": 350.0,
                "dry_mass_kg": 500.0,
                "propellant_mass_kg": 1000.0,
                "payload_mass_kg": 500.0,
            },
        ]
        result = multi_stage_delta_v(stages)
        assert result["total_delta_v_ms"] > 0
        assert len(result["stages"]) == 2

    def test_invalid(self):
        with pytest.raises(ValueError):
            multi_stage_delta_v([])


class TestOrbitalVelocity:
    def test_leo(self):
        result = orbital_velocity(altitude_m=400_000.0)
        assert result["circular_velocity_ms"] == pytest.approx(7668, rel=0.02)
        assert result["orbital_period_min"] == pytest.approx(92.6, rel=0.05)

    def test_escape(self):
        result = orbital_velocity(altitude_m=0.0)
        assert result["escape_velocity_ms"] == pytest.approx(11186, rel=0.02)


class TestPayloadFraction:
    def test_achievable(self):
        result = payload_fraction(
            delta_v_required_ms=5000.0,
            specific_impulse_s=350.0,
            inert_mass_fraction=0.1,
        )
        assert result["achievable"] is True
        assert result["payload_fraction"] > 0

    def test_unachievable(self):
        result = payload_fraction(
            delta_v_required_ms=20000.0,
            specific_impulse_s=300.0,
            inert_mass_fraction=0.3,
        )
        assert result["achievable"] is False


class TestThrustToWeight:
    def test_basic(self):
        result = thrust_to_weight(thrust_n=50000.0, mass_kg=3000.0)
        assert result["thrust_to_weight_ratio"] == pytest.approx(1.7, rel=0.01)
        assert result["can_hover"] is True

    def test_cant_hover(self):
        result = thrust_to_weight(thrust_n=10000.0, mass_kg=3000.0)
        assert result["can_hover"] is False


class TestCompositeCG:
    def test_basic(self):
        masses = [100.0, 200.0, 50.0]
        positions = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [2.0, 0.0, 0.0]]
        result = composite_cg(masses, positions)
        assert result["total_mass_kg"] == 350.0
        assert result["cg_x_m"] == pytest.approx(0.857, rel=1e-3)
        assert result["cg_y_m"] == 0.0
        assert result["cg_z_m"] == 0.0

    def test_invalid(self):
        with pytest.raises(ValueError):
            composite_cg([], [])


class TestPropellantTankSizing:
    def test_cylinder(self):
        result = propellant_tank_sizing(
            propellant_volume_m3=10.0,
            tank_shape="cylinder",
            aspect_ratio=3.0,
        )
        assert result["tank_shape"] == "cylinder"
        assert result["total_volume_m3"] == 11.0  # 10% ullage
        assert result["length_m"] > result["diameter_m"]
        assert result["tank_mass_kg"] > 0

    def test_sphere(self):
        result = propellant_tank_sizing(
            propellant_volume_m3=5.0,
            tank_shape="sphere",
        )
        assert result["tank_shape"] == "sphere"
        assert result["length_m"] == result["diameter_m"]

    def test_invalid(self):
        with pytest.raises(ValueError):
            propellant_tank_sizing(propellant_volume_m3=-1.0)
