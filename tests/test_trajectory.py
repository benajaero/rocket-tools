"""Tests for the ascent trajectory simulator and vehicle sizing."""

import math

import pytest

from rocket_tools.materials.isa import isa_atmosphere
from rocket_tools.trajectory import simulate_ascent, size_vehicle
from rocket_tools.trajectory.integrator import G0, _isa_rho


class TestISAKernelParity:
    @pytest.mark.parametrize(
        "h", [0.0, 500.0, 1000.0, 11000.0, 20000.0, 32000.0, 47000.0, 60000.0, 71000.0, 84000.0]
    )
    def test_isa_rho_matches_reference_model(self, h):
        """The njit density kernel must match materials/isa.py (rounding-limited)."""
        expected = isa_atmosphere(h)["density_kg_m3"]
        got = _isa_rho(h)
        assert abs(got - expected) / expected < 1e-5

    def test_above_ceiling_is_vacuum(self):
        assert _isa_rho(90000.0) == 0.0

    def test_below_ground_clamps_to_sea_level(self):
        assert abs(_isa_rho(-100.0) - _isa_rho(0.0)) < 1e-12


class TestAnalyticVacuumAscent:
    """Vertical, no drag, constant gravity => closed-form rocket ascent."""

    def _run(self, dt=0.01):
        return simulate_ascent(
            initial_mass_kg=1000.0,
            dry_mass_kg=400.0,
            specific_impulse_s=250.0,
            mass_flow_rate_kg_s=20.0,
            reference_area_m2=1.0,
            include_drag=False,
            gravity_model="constant",
            dt=dt,
            launch_angle_deg=90.0,
        )

    def test_burnout_velocity_matches_tsiolkovsky_minus_gravity_loss(self):
        r = self._run()
        tb = (1000.0 - 400.0) / 20.0
        v_bo = 250.0 * G0 * math.log(1000.0 / 400.0) - G0 * tb
        assert abs(r["burnout_velocity_ms"] - v_bo) / v_bo < 2e-3

    def test_apogee_matches_ballistic_coast(self):
        r = self._run()
        assert abs(r["apogee_m"] - 218526.61) / 218526.61 < 2e-3

    def test_ideal_dv_and_losses(self):
        r = self._run()
        assert r["ideal_delta_v_ms"] > r["burnout_velocity_ms"]
        assert r["total_losses_ms"] > 0  # gravity loss present

    def test_finer_step_reduces_error(self):
        coarse = self._run(dt=0.2)
        fine = self._run(dt=0.01)
        target = 218526.61
        assert abs(fine["apogee_m"] - target) <= abs(coarse["apogee_m"] - target)


class TestAscentPhysics:
    def test_drag_lowers_apogee(self):
        common = dict(
            initial_mass_kg=1000.0,
            dry_mass_kg=400.0,
            specific_impulse_s=250.0,
            mass_flow_rate_kg_s=20.0,
            reference_area_m2=0.5,
            dt=0.05,
        )
        with_drag = simulate_ascent(include_drag=True, **common)
        no_drag = simulate_ascent(include_drag=False, **common)
        assert with_drag["apogee_m"] < no_drag["apogee_m"]

    def test_gravity_turn_produces_downrange(self):
        r = simulate_ascent(
            initial_mass_kg=1000.0,
            dry_mass_kg=400.0,
            specific_impulse_s=250.0,
            mass_flow_rate_kg_s=20.0,
            reference_area_m2=0.2,
            launch_angle_deg=80.0,
            dt=0.1,
        )
        assert r["series"]["downrange_m"][-1] > 0.0

    def test_near_vertical_launch_reaches_altitude(self):
        """Regression: the gravity-turn EOM is singular at v->0; a near-vertical (89 deg)
        launch must still reach a substantial apogee, not immediately pitch to the ground."""
        common = dict(
            initial_mass_kg=50000.0,
            dry_mass_kg=15000.0,
            specific_impulse_s=280.0,
            mass_flow_rate_kg_s=350.0,
            reference_area_m2=1.2,
            dt=0.1,
        )
        vertical = simulate_ascent(launch_angle_deg=90.0, **common)
        near_vert = simulate_ascent(launch_angle_deg=89.0, **common)
        assert vertical["apogee_km"] > 100.0
        # 1 degree off vertical should stay within ~25% of the vertical apogee, not ~0.
        assert near_vert["apogee_m"] > 0.75 * vertical["apogee_m"]
        assert near_vert["series"]["downrange_m"][-1] > 0.0

    def test_series_shapes_and_events(self):
        r = simulate_ascent(
            initial_mass_kg=1000.0,
            dry_mass_kg=400.0,
            specific_impulse_s=250.0,
            mass_flow_rate_kg_s=20.0,
            reference_area_m2=0.2,
            dt=0.1,
        )
        s = r["series"]
        n = len(s["time_s"])
        assert n > 1
        assert all(len(v) == n for v in s.values())
        assert r["events"]["apogee"]["altitude_m"] == pytest.approx(r["apogee_m"])
        assert r["max_dynamic_pressure_pa"] > 0

    def test_invalid_dry_mass_raises(self):
        with pytest.raises(ValueError):
            simulate_ascent(
                initial_mass_kg=400.0,
                dry_mass_kg=400.0,
                specific_impulse_s=250.0,
                mass_flow_rate_kg_s=20.0,
                reference_area_m2=0.2,
            )


class TestSizeVehicle:
    def test_feasible_sizing_closes_rocket_equation(self):
        r = size_vehicle(
            payload_mass_kg=500.0,
            delta_v_target_ms=3000.0,
            specific_impulse_s=320.0,
            inert_mass_fraction=0.1,
        )
        assert r["achievable"] is True
        # achieved delta-v (via rocket_delta_v) must hit the target
        assert abs(r["achieved_delta_v_ms"] - 3000.0) / 3000.0 < 1e-3
        # mass balance
        assert (
            abs(
                r["gross_liftoff_mass_kg"]
                - (r["propellant_mass_kg"] + r["inert_mass_kg"] + r["payload_mass_kg"])
            )
            < 1.0
        )

    def test_infeasible_when_structural_fraction_too_high(self):
        r = size_vehicle(
            payload_mass_kg=500.0,
            delta_v_target_ms=9000.0,
            specific_impulse_s=250.0,
            inert_mass_fraction=0.3,
        )
        assert r["achievable"] is False
        assert r["max_achievable_delta_v_ms"] < 9000.0

    def test_chains_tank_sizing(self):
        r = size_vehicle(
            payload_mass_kg=500.0,
            delta_v_target_ms=3000.0,
            specific_impulse_s=320.0,
            inert_mass_fraction=0.1,
        )
        assert r["tank_mass_kg"] > 0
        assert r["tank_length_m"] > 0
