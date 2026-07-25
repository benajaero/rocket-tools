"""Tests for the universal-variable Lambert solver (audit Batch 5)."""

import numpy as np
import pytest

from rocket_tools.design import lambert_solver

MU_EARTH = 3.986004418e14


class TestLambertSolver:
    def test_curtis_example_5_2(self):
        # Curtis, Orbital Mechanics for Engineering Students, 3rd Ed., Example 5.2.
        r = lambert_solver(
            r1_m=[5.0e6, 1.0e7, 2.1e6],
            r2_m=[-1.46e7, 2.5e6, 7.0e6],
            time_of_flight_s=3600.0,
            prograde=True,
        )
        # Published km/s values, compared in m/s.
        assert r["v1_x_ms"] == pytest.approx(-5992.5, abs=1.0)
        assert r["v1_y_ms"] == pytest.approx(1925.4, abs=1.0)
        assert r["v1_z_ms"] == pytest.approx(3245.6, abs=1.0)
        assert r["v2_x_ms"] == pytest.approx(-3312.5, abs=1.0)
        assert r["v2_y_ms"] == pytest.approx(-4196.6, abs=1.0)
        assert r["v2_z_ms"] == pytest.approx(-385.29, abs=1.0)
        assert r["transfer_angle_deg"] == pytest.approx(100.29, abs=0.05)

    def test_velocities_produce_consistent_energy(self):
        # The transfer orbit's specific energy from v1@r1 must equal that from v2@r2.
        r1 = [7.0e6, 0.0, 0.0]
        r2 = [0.0, 8.0e6, 0.0]
        out = lambert_solver(r1_m=r1, r2_m=r2, time_of_flight_s=2000.0)
        v1 = np.array([out["v1_x_ms"], out["v1_y_ms"], out["v1_z_ms"]])
        v2 = np.array([out["v2_x_ms"], out["v2_y_ms"], out["v2_z_ms"]])
        e1 = 0.5 * v1.dot(v1) - MU_EARTH / np.linalg.norm(r1)
        e2 = 0.5 * v2.dot(v2) - MU_EARTH / np.linalg.norm(r2)
        assert e1 == pytest.approx(e2, rel=1e-4)

    def test_retrograde_differs_from_prograde(self):
        r1 = [7.0e6, 0.0, 0.0]
        r2 = [0.0, 8.0e6, 1.0e6]
        pro = lambert_solver(r1_m=r1, r2_m=r2, time_of_flight_s=2500.0, prograde=True)
        retro = lambert_solver(r1_m=r1, r2_m=r2, time_of_flight_s=2500.0, prograde=False)
        assert pro["transfer_angle_deg"] != retro["transfer_angle_deg"]

    def test_collinear_180_deg_rejected(self):
        # Antiparallel position vectors -> 180 deg transfer, plane undefined.
        with pytest.raises(ValueError, match="180"):
            lambert_solver(r1_m=[7.0e6, 0.0, 0.0], r2_m=[-8.0e6, 0.0, 0.0], time_of_flight_s=3000.0)

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"r1_m": [1.0, 2.0], "r2_m": [1.0, 2.0, 3.0], "time_of_flight_s": 100.0},
            {"r1_m": [1e6, 0, 0], "r2_m": [0, 1e6, 0], "time_of_flight_s": 0.0},
            {"r1_m": [1e6, 0, 0], "r2_m": [0, 1e6, 0], "time_of_flight_s": 100.0, "mu": 0.0},
            {"r1_m": [0.0, 0.0, 0.0], "r2_m": [0, 1e6, 0], "time_of_flight_s": 100.0},
        ],
    )
    def test_invalid_inputs_rejected(self, kwargs):
        with pytest.raises(ValueError):
            lambert_solver(**kwargs)
