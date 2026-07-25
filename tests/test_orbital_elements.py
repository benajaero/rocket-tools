"""Tests for classical orbital elements from a state vector (audit Batch 6)."""

import numpy as np
import pytest

from rocket_tools.design import (
    orbital_elements_from_state,
    state_from_orbital_elements,
)

MU_EARTH = 3.986004418e14


class TestOrbitalElementsFromState:
    def test_curtis_example_4_3(self):
        # Curtis, Orbital Mechanics for Engineering Students, 3rd Ed., Example 4.3.
        r = orbital_elements_from_state(
            position_m=[-6.045e6, -3.49e6, 2.5e6],
            velocity_ms=[-3457.0, 6618.0, 2533.0],
        )
        assert r["eccentricity"] == pytest.approx(0.1712, abs=1e-3)
        assert r["inclination_deg"] == pytest.approx(153.2, abs=0.1)
        assert r["raan_deg"] == pytest.approx(255.3, abs=0.1)
        assert r["argument_of_perigee_deg"] == pytest.approx(20.07, abs=0.05)
        assert r["true_anomaly_deg"] == pytest.approx(28.45, abs=0.05)
        assert r["semi_major_axis_m"] == pytest.approx(8.788e6, rel=1e-3)
        assert r["specific_angular_momentum_m2_s"] == pytest.approx(58311e6, rel=1e-3)
        assert r["orbit_type"] == "closed"

    def test_circular_equatorial_orbit(self):
        # A circular equatorial orbit: e~0, i~0. Speed = sqrt(mu/r).
        radius = 7.0e6
        speed = np.sqrt(MU_EARTH / radius)
        r = orbital_elements_from_state(
            position_m=[radius, 0.0, 0.0],
            velocity_ms=[0.0, speed, 0.0],
        )
        assert r["eccentricity"] == pytest.approx(0.0, abs=1e-6)
        assert r["inclination_deg"] == pytest.approx(0.0, abs=1e-6)
        assert r["semi_major_axis_m"] == pytest.approx(radius, rel=1e-6)

    def test_polar_orbit_inclination(self):
        radius = 7.0e6
        speed = np.sqrt(MU_EARTH / radius)
        r = orbital_elements_from_state(
            position_m=[radius, 0.0, 0.0],
            velocity_ms=[0.0, 0.0, speed],
        )
        assert r["inclination_deg"] == pytest.approx(90.0, abs=1e-4)

    def test_hyperbolic_orbit_flagged(self):
        # Well above escape speed at 7000 km -> hyperbolic, a < 0, apoapsis undefined.
        radius = 7.0e6
        v_esc = np.sqrt(2 * MU_EARTH / radius)
        r = orbital_elements_from_state(
            position_m=[radius, 0.0, 0.0],
            velocity_ms=[0.0, 1.3 * v_esc, 0.0],
        )
        assert r["eccentricity"] > 1.0
        assert r["orbit_type"] == "hyperbolic"
        assert r["semi_major_axis_m"] < 0
        assert r["apoapsis_radius_m"] is None

    def test_periapsis_consistent_with_a_and_e(self):
        r = orbital_elements_from_state(
            position_m=[-6.045e6, -3.49e6, 2.5e6],
            velocity_ms=[-3457.0, 6618.0, 2533.0],
        )
        a = r["semi_major_axis_m"]
        e = r["eccentricity"]
        assert r["periapsis_radius_m"] == pytest.approx(a * (1 - e), rel=1e-4)
        assert r["apoapsis_radius_m"] == pytest.approx(a * (1 + e), rel=1e-4)

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"position_m": [1.0, 2.0], "velocity_ms": [1.0, 2.0, 3.0]},
            {"position_m": [7e6, 0, 0], "velocity_ms": [0, 1000, 0], "mu": 0.0},
            {"position_m": [0.0, 0.0, 0.0], "velocity_ms": [0, 1000, 0]},
        ],
    )
    def test_invalid_inputs_rejected(self, kwargs):
        with pytest.raises(ValueError):
            orbital_elements_from_state(**kwargs)


class TestStateFromOrbitalElements:
    def test_curtis_example_4_7(self):
        # Curtis Example 4.7: h=80000 km^2/s, e=1.4 -> a = (h^2/mu)/(1-e^2).
        h = 80000e6
        e = 1.4
        a = (h**2 / MU_EARTH) / (1 - e**2)
        r = state_from_orbital_elements(a, e, 30.0, 40.0, 60.0, 30.0)
        assert r["position_x_m"] == pytest.approx(-4.040e6, abs=2000)
        assert r["position_y_m"] == pytest.approx(4.815e6, abs=2000)
        assert r["position_z_m"] == pytest.approx(3.629e6, abs=2000)
        assert r["velocity_x_ms"] == pytest.approx(-10386.0, abs=5)
        assert r["velocity_y_ms"] == pytest.approx(-4772.0, abs=5)
        assert r["velocity_z_ms"] == pytest.approx(1744.0, abs=5)

    def test_round_trip_with_forward_tool(self):
        # COE -> state -> COE must recover the original state vector.
        r0 = [-6.045e6, -3.49e6, 2.5e6]
        v0 = [-3457.0, 6618.0, 2533.0]
        coe = orbital_elements_from_state(r0, v0)
        st = state_from_orbital_elements(
            coe["semi_major_axis_m"],
            coe["eccentricity"],
            coe["inclination_deg"],
            coe["raan_deg"],
            coe["argument_of_perigee_deg"],
            coe["true_anomaly_deg"],
        )
        assert st["position_x_m"] == pytest.approx(r0[0], abs=10)
        assert st["position_y_m"] == pytest.approx(r0[1], abs=10)
        assert st["position_z_m"] == pytest.approx(r0[2], abs=10)
        assert st["velocity_x_ms"] == pytest.approx(v0[0], abs=0.1)

    def test_circular_equatorial_radius(self):
        # Circular equatorial orbit at a=7000 km, theta=0 -> r on +x axis, |r|=a.
        st = state_from_orbital_elements(7.0e6, 0.0, 0.0, 0.0, 0.0, 0.0)
        assert st["radius_m"] == pytest.approx(7.0e6, rel=1e-6)
        assert st["position_x_m"] == pytest.approx(7.0e6, rel=1e-6)

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"eccentricity": 1.0},  # parabolic unsupported via (a, e)
            {"eccentricity": -0.1},  # negative e
            {"inclination_deg": 200.0},  # out of range
            {"semi_major_axis_m": 7.0e6, "eccentricity": 1.4},  # inconsistent a>0, e>1
            {"mu": 0.0},
        ],
    )
    def test_invalid_inputs_rejected(self, kwargs):
        args = {
            "semi_major_axis_m": 7.0e6,
            "eccentricity": 0.1,
            "inclination_deg": 30.0,
            "raan_deg": 40.0,
            "argument_of_perigee_deg": 60.0,
            "true_anomaly_deg": 30.0,
        }
        args.update(kwargs)
        with pytest.raises(ValueError):
            state_from_orbital_elements(**args)
