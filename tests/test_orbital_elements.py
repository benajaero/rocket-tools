"""Tests for classical orbital elements from a state vector (audit Batch 6)."""

import numpy as np
import pytest

from rocket_tools.design import orbital_elements_from_state

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
