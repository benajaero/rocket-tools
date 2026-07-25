"""Tests for motor thrust-curve analysis (audit Batch 7)."""

import pytest

from rocket_tools.aerodynamics import motor_thrust_curve_analysis
from rocket_tools.aerodynamics.propulsion import _nar_motor_class

G_STD = 9.80665


class TestMotorThrustCurveAnalysis:
    def test_constant_thrust_exact(self):
        # 10 N held for 1 s: I = 10 N*s (C class), average = peak = 10 N.
        r = motor_thrust_curve_analysis([0.0, 1.0], [10.0, 10.0], propellant_mass_kg=0.01)
        assert r["total_impulse_ns"] == pytest.approx(10.0)
        assert r["average_thrust_n"] == pytest.approx(10.0)
        assert r["peak_thrust_n"] == pytest.approx(10.0)
        assert r["burn_time_s"] == pytest.approx(1.0)
        assert r["motor_class"] == "C"
        assert r["motor_designation"] == "C10"
        # Isp = I / (m * g0)
        assert r["specific_impulse_s"] == pytest.approx(10.0 / (0.01 * G_STD), rel=1e-4)
        assert r["effective_exhaust_velocity_ms"] == pytest.approx(1000.0, rel=1e-4)

    def test_triangular_curve_exact(self):
        # Triangle 0 -> 20 -> 0 over 1 s: I = 10 N*s, peak = 20 N.
        r = motor_thrust_curve_analysis([0.0, 0.5, 1.0], [0.0, 20.0, 0.0], propellant_mass_kg=0.012)
        assert r["total_impulse_ns"] == pytest.approx(10.0)
        assert r["peak_thrust_n"] == pytest.approx(20.0)
        assert r["average_thrust_n"] == pytest.approx(10.0)
        assert r["motor_class"] == "C"

    @pytest.mark.parametrize(
        "impulse,letter",
        [
            (2.5, "A"),
            (2.6, "B"),
            (5.0, "B"),
            (10.0, "C"),
            (40.0, "E"),
            (160.0, "G"),
            (0.5, "1/4A"),
            (0.2, "sub-1/4A"),
        ],
    )
    def test_nar_class_boundaries(self, impulse, letter):
        assert _nar_motor_class(impulse) == letter

    def test_class_scales_with_impulse(self):
        # A 40 N*s motor is class E; designation reflects rounded average thrust.
        r = motor_thrust_curve_analysis([0.0, 2.0], [20.0, 20.0], propellant_mass_kg=0.02)
        assert r["total_impulse_ns"] == pytest.approx(40.0)
        assert r["motor_class"] == "E"
        assert r["motor_designation"] == "E20"

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"times_s": [0.0, 1.0], "thrusts_n": [10.0], "propellant_mass_kg": 0.01},  # length
            {"times_s": [0.0], "thrusts_n": [10.0], "propellant_mass_kg": 0.01},  # too short
            {"times_s": [1.0, 0.0], "thrusts_n": [10.0, 10.0], "propellant_mass_kg": 0.01},  # order
            {"times_s": [0.0, 1.0], "thrusts_n": [10.0, -1.0], "propellant_mass_kg": 0.01},  # neg
            {"times_s": [0.0, 1.0], "thrusts_n": [10.0, 10.0], "propellant_mass_kg": 0.0},  # mass
            {"times_s": [0.0, 1.0], "thrusts_n": [0.0, 0.0], "propellant_mass_kg": 0.01},  # zero I
        ],
    )
    def test_invalid_inputs_rejected(self, kwargs):
        with pytest.raises(ValueError):
            motor_thrust_curve_analysis(**kwargs)
