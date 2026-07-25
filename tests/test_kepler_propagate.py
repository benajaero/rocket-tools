"""Tests for universal-variable Kepler propagation (audit Batch 6)."""

import numpy as np
import pytest

from rocket_tools.design import kepler_propagate, orbital_elements_from_state

MU_EARTH = 3.986004418e14


class TestKeplerPropagate:
    def test_curtis_example_3_7(self):
        # Curtis, Orbital Mechanics for Engineering Students, 3rd Ed., Example 3.7.
        r = kepler_propagate(
            position_m=[7.0e6, -12.124e6, 0.0],
            velocity_ms=[2667.9, 4621.0, 0.0],
            time_of_flight_s=3600.0,
        )
        assert r["position_x_m"] == pytest.approx(-3.2978e6, abs=200)
        assert r["position_y_m"] == pytest.approx(7.4134e6, abs=200)
        assert r["position_z_m"] == pytest.approx(0.0, abs=1)
        assert r["velocity_x_ms"] == pytest.approx(-8297.7, abs=2)
        assert r["velocity_y_ms"] == pytest.approx(-963.09, abs=5)

    def test_backward_propagation_recovers_start(self):
        r0 = [7.0e6, -12.124e6, 0.0]
        v0 = [2667.9, 4621.0, 0.0]
        fwd = kepler_propagate(position_m=r0, velocity_ms=v0, time_of_flight_s=3600.0)
        back = kepler_propagate(
            position_m=[fwd["position_x_m"], fwd["position_y_m"], fwd["position_z_m"]],
            velocity_ms=[fwd["velocity_x_ms"], fwd["velocity_y_ms"], fwd["velocity_z_ms"]],
            time_of_flight_s=-3600.0,
        )
        assert back["position_x_m"] == pytest.approx(r0[0], abs=1)
        assert back["position_y_m"] == pytest.approx(r0[1], abs=1)

    def test_full_period_returns_to_start(self):
        # Propagating exactly one orbital period must return to the initial state.
        r0 = [7.0e6, 0.0, 0.0]
        v0 = [0.0, 8000.0, 0.0]
        coe = orbital_elements_from_state(r0, v0)
        a = coe["semi_major_axis_m"]
        period = 2 * np.pi * np.sqrt(a**3 / MU_EARTH)
        r = kepler_propagate(position_m=r0, velocity_ms=v0, time_of_flight_s=period)
        assert r["position_x_m"] == pytest.approx(r0[0], rel=1e-4)
        assert r["position_y_m"] == pytest.approx(r0[1], abs=1000)

    def test_zero_time_is_identity(self):
        r0 = [7.0e6, -12.124e6, 0.0]
        v0 = [2667.9, 4621.0, 0.0]
        r = kepler_propagate(position_m=r0, velocity_ms=v0, time_of_flight_s=0.0)
        assert r["position_x_m"] == pytest.approx(r0[0], abs=1)
        assert r["position_y_m"] == pytest.approx(r0[1], abs=1)
        assert r["velocity_x_ms"] == pytest.approx(v0[0], abs=0.1)

    def test_hyperbolic_orbit_propagates(self):
        # Above escape speed -> hyperbolic; propagation must still converge.
        radius = 7.0e6
        v_esc = np.sqrt(2 * MU_EARTH / radius)
        r = kepler_propagate(
            position_m=[radius, 0.0, 0.0],
            velocity_ms=[0.0, 1.3 * v_esc, 0.0],
            time_of_flight_s=1800.0,
        )
        assert r["radius_m"] > radius  # moving outward on an escape trajectory

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"position_m": [1.0, 2.0], "velocity_ms": [1.0, 2.0, 3.0], "time_of_flight_s": 10.0},
            {
                "position_m": [7e6, 0, 0],
                "velocity_ms": [0, 8000, 0],
                "time_of_flight_s": 10.0,
                "mu": 0.0,
            },
            {"position_m": [0.0, 0.0, 0.0], "velocity_ms": [0, 8000, 0], "time_of_flight_s": 10.0},
        ],
    )
    def test_invalid_inputs_rejected(self, kwargs):
        with pytest.raises(ValueError):
            kepler_propagate(**kwargs)
