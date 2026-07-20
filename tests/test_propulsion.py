"""Tests for propulsion thermochemistry tools (Sutter & Biblarz Ch. 3)."""

import math

import pytest

from rocket_tools.aerodynamics import (
    characteristic_velocity,
    ideal_specific_impulse,
    throat_mass_flux,
)

R_UNIVERSAL = 8314.462
G0 = 9.80665


class TestCharacteristicVelocity:
    def test_lox_rp1(self):
        # Tc=3500 K, gamma=1.22, M=23.3 kg/kmol -> c* = 1713.04 m/s (Sutton Eq. 3-32).
        res = characteristic_velocity(3500.0, 1.22, 23.3)
        assert res["characteristic_velocity_ms"] == pytest.approx(1713.043, rel=1e-4)

    def test_matches_vandenkerckhove_form(self):
        # c* = sqrt(R*Tc)/Gamma must equal sqrt(R*Tc/g)*((g+1)/2)^((g+1)/(2(g-1))).
        tc, g, m = 3200.0, 1.24, 20.0
        r = R_UNIVERSAL / m
        alt = math.sqrt(r * tc / g) * ((g + 1) / 2) ** ((g + 1) / (2 * (g - 1)))
        got = characteristic_velocity(tc, g, m)["characteristic_velocity_ms"]
        assert got == pytest.approx(alt, rel=1e-6)

    def test_bad_gamma_rejected(self):
        with pytest.raises(ValueError):
            characteristic_velocity(3000.0, 1.0, 22.0)


class TestIdealSpecificImpulse:
    def test_lox_rp1_pressure_ratio(self):
        # Tc=3500, gamma=1.22, M=23.3, pe/pc=0.01 -> v_e=2795.45 m/s, Isp=285.06 s.
        res = ideal_specific_impulse(3500.0, 0.01, 1.22, 23.3)
        assert res["exhaust_velocity_ms"] == pytest.approx(2795.447, rel=1e-4)
        assert res["specific_impulse_s"] == pytest.approx(285.056, rel=1e-4)

    def test_vacuum_limit_is_upper_bound(self):
        res = ideal_specific_impulse(3500.0, 0.01, 1.22, 23.3)
        assert res["max_exhaust_velocity_ms"] > res["exhaust_velocity_ms"]

    def test_pressure_ratio_out_of_range_rejected(self):
        with pytest.raises(ValueError):
            ideal_specific_impulse(3500.0, 1.5, 1.22, 23.3)


class TestThroatMassFlux:
    def test_reference_case(self):
        # pc=7 MPa, Tc=3500, gamma=1.22, M=23.3 -> 4086.30 kg/s/m^2 (Sutton Eq. 3-24).
        res = throat_mass_flux(7.0e6, 3500.0, 1.22, 23.3)
        assert res["mass_flux_kg_s_m2"] == pytest.approx(4086.296, rel=1e-4)

    def test_scales_linearly_with_pressure(self):
        q1 = throat_mass_flux(7.0e6, 3500.0, 1.22, 23.3)["mass_flux_kg_s_m2"]
        q2 = throat_mass_flux(14.0e6, 3500.0, 1.22, 23.3)["mass_flux_kg_s_m2"]
        assert q2 / q1 == pytest.approx(2.0, rel=1e-6)

    def test_negative_pressure_rejected(self):
        with pytest.raises(ValueError):
            throat_mass_flux(-1.0, 3500.0, 1.22, 23.3)
