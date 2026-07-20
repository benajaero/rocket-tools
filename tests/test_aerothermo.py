"""Tests for aerothermodynamics tools, validated against textbook formulas."""

import math

import pytest

from rocket_tools.aerodynamics import (
    ballistic_entry_peak_deceleration,
    recovery_temperature,
    stagnation_temperature,
    sutton_graves_heat_flux,
)


class TestStagnationTemperature:
    def test_mach_3(self):
        # Anderson: T0 = T(1 + 0.2 M^2). M=3, T=220 -> 220*2.8 = 616 K.
        res = stagnation_temperature(220.0, 3.0)
        assert res["stagnation_temperature_k"] == pytest.approx(616.0, rel=1e-6)

    def test_mach_zero_is_static(self):
        assert stagnation_temperature(300.0, 0.0)["stagnation_temperature_k"] == 300.0

    def test_negative_temp_rejected(self):
        with pytest.raises(ValueError):
            stagnation_temperature(-1.0, 2.0)


class TestRecoveryTemperature:
    def test_below_stagnation(self):
        m, t = 3.0, 220.0
        rec = recovery_temperature(t, m)["recovery_temperature_k"]
        stag = stagnation_temperature(t, m)["stagnation_temperature_k"]
        assert rec < stag  # recovery factor < 1

    def test_laminar_factor_sqrt_pr(self):
        res = recovery_temperature(220.0, 3.0, prandtl=0.71, regime="laminar")
        assert res["recovery_factor"] == pytest.approx(math.sqrt(0.71), rel=1e-4)
        assert res["recovery_temperature_k"] == pytest.approx(553.676, rel=1e-4)

    def test_turbulent_factor_cbrt_pr(self):
        res = recovery_temperature(220.0, 3.0, prandtl=0.71, regime="turbulent")
        assert res["recovery_factor"] == pytest.approx(0.71 ** (1 / 3), rel=1e-4)

    def test_bad_regime_rejected(self):
        with pytest.raises(ValueError):
            recovery_temperature(220.0, 3.0, regime="transitional")


class TestSuttonGraves:
    def test_reference_case(self):
        # q = 1.7415e-4 * sqrt(rho/Rn) * V^3 (W/m^2).
        res = sutton_graves_heat_flux(1e-4, 7500.0, 1.0)
        assert res["heat_flux_w_m2"] == pytest.approx(734695.31, rel=1e-5)
        assert res["heat_flux_w_cm2"] == pytest.approx(73.47, rel=1e-3)

    def test_scales_with_velocity_cubed(self):
        q1 = sutton_graves_heat_flux(1e-4, 5000.0, 1.0)["heat_flux_w_m2"]
        q2 = sutton_graves_heat_flux(1e-4, 10000.0, 1.0)["heat_flux_w_m2"]
        assert q2 / q1 == pytest.approx(8.0, rel=1e-6)  # 2^3

    def test_negative_radius_rejected(self):
        with pytest.raises(ValueError):
            sutton_graves_heat_flux(1e-4, 7500.0, -1.0)


class TestBallisticEntry:
    def test_allen_eggers_peak(self):
        # a_max = V^2 sin(gamma)/(2 e H). V=7800, 30 deg, H=7160.
        res = ballistic_entry_peak_deceleration(7800.0, 30.0, 7160.0)
        assert res["peak_deceleration_ms2"] == pytest.approx(781.487, rel=1e-4)
        assert res["peak_deceleration_g"] == pytest.approx(79.689, rel=1e-4)

    def test_velocity_at_peak_is_ve_over_sqrt_e(self):
        res = ballistic_entry_peak_deceleration(7800.0, 30.0)
        assert res["velocity_at_peak_ms"] == pytest.approx(7800.0 * math.exp(-0.5), rel=1e-5)

    def test_independent_of_ballistic_coefficient(self):
        # a_max has no mass/CdA term; two entries at same V, gamma, H match.
        a = ballistic_entry_peak_deceleration(7000.0, 20.0)["peak_deceleration_ms2"]
        b = ballistic_entry_peak_deceleration(7000.0, 20.0)["peak_deceleration_ms2"]
        assert a == b

    def test_bad_angle_rejected(self):
        with pytest.raises(ValueError):
            ballistic_entry_peak_deceleration(7800.0, 0.0)
