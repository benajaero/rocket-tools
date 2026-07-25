"""Tests for parachute recovery sizing (audit Batch 5)."""

import math

import pytest

from rocket_tools.trajectory import (
    parachute_area_for_descent_rate,
    parachute_descent_rate,
)


class TestParachuteDescentRate:
    def test_hand_computed_terminal_velocity(self):
        # m=5 kg, D=1.5 m -> S=1.76715 m^2, Cd=0.75, rho=1.225 (sea level).
        # V = sqrt(2*5*9.80665/(1.225*0.75*1.76715)) = sqrt(98.0665/1.62382) = 7.771 m/s
        r = parachute_descent_rate(
            mass_kg=5.0,
            canopy_diameter_m=1.5,
            drag_coefficient=0.75,
            air_density_kg_m3=1.225,
        )
        assert r["canopy_area_m2"] == pytest.approx(1.76715, abs=1e-4)
        assert r["descent_rate_ms"] == pytest.approx(7.771, abs=1e-2)
        # KE = 0.5*5*7.771^2 ~= 150.9 J
        assert r["landing_kinetic_energy_j"] == pytest.approx(150.9, abs=0.5)

    def test_denser_air_lowers_descent_rate(self):
        thin = parachute_descent_rate(mass_kg=5.0, canopy_diameter_m=1.5, altitude_m=3000.0)
        thick = parachute_descent_rate(mass_kg=5.0, canopy_diameter_m=1.5, altitude_m=0.0)
        assert thick["descent_rate_ms"] < thin["descent_rate_ms"]

    def test_isa_density_used_by_default(self):
        r = parachute_descent_rate(mass_kg=5.0, canopy_diameter_m=1.5)
        # Sea-level ISA density ~1.225 kg/m^3.
        assert r["air_density_kg_m3"] == pytest.approx(1.225, abs=1e-2)

    @pytest.mark.parametrize(
        "bad",
        [
            {"mass_kg": 0.0},
            {"canopy_diameter_m": -1.0},
            {"drag_coefficient": 0.0},
            {"air_density_kg_m3": -0.1},
        ],
    )
    def test_invalid_inputs_rejected(self, bad):
        args = {"mass_kg": 5.0, "canopy_diameter_m": 1.5}
        args.update(bad)
        with pytest.raises(ValueError):
            parachute_descent_rate(**args)


class TestParachuteAreaForDescentRate:
    def test_area_inverts_descent_rate(self):
        # Round-trip: sizing for a target rate, then computing that canopy's rate,
        # must reproduce the target.
        sized = parachute_area_for_descent_rate(
            mass_kg=5.0, target_descent_rate_ms=5.0, air_density_kg_m3=1.225
        )
        back = parachute_descent_rate(
            mass_kg=5.0,
            canopy_diameter_m=sized["canopy_diameter_m"],
            air_density_kg_m3=1.225,
        )
        assert back["descent_rate_ms"] == pytest.approx(5.0, abs=1e-2)

    def test_hand_computed_area(self):
        # S = 2*5*9.80665/(1.225*0.75*5^2) = 98.0665/22.96875 = 4.2696 m^2
        r = parachute_area_for_descent_rate(
            mass_kg=5.0, target_descent_rate_ms=5.0, air_density_kg_m3=1.225
        )
        assert r["canopy_area_m2"] == pytest.approx(4.2696, abs=1e-3)
        assert r["canopy_diameter_m"] == pytest.approx(math.sqrt(4 * 4.2696 / math.pi), abs=1e-3)

    def test_lower_target_rate_needs_bigger_canopy(self):
        slow = parachute_area_for_descent_rate(mass_kg=5.0, target_descent_rate_ms=3.0)
        fast = parachute_area_for_descent_rate(mass_kg=5.0, target_descent_rate_ms=6.0)
        assert slow["canopy_area_m2"] > fast["canopy_area_m2"]

    def test_invalid_target_rejected(self):
        with pytest.raises(ValueError):
            parachute_area_for_descent_rate(mass_kg=5.0, target_descent_rate_ms=0.0)
