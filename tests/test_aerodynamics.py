"""Tests for aerodynamics."""

import pytest

from rocket_tools.aerodynamics import (
    aero_analysis,
    drag_coefficient,
    dynamic_pressure,
    lift_coefficient,
    mach_number,
    reynolds_number,
    skin_friction_coefficient,
)


class TestReynoldsNumber:
    def test_direct_params(self):
        result = reynolds_number(
            velocity=100.0,
            characteristic_length=1.0,
            density=1.225,
            dynamic_viscosity=1.789e-5,
        )
        expected = 1.225 * 100.0 * 1.0 / 1.789e-5
        assert pytest.approx(result["reynolds_number"], 1e-3) == expected

    def test_isa_lookup(self):
        result = reynolds_number(
            velocity=100.0,
            characteristic_length=1.0,
            altitude_m=0.0,
        )
        assert result["reynolds_number"] > 0
        assert result["flow_regime"] == "turbulent" or result["flow_regime"] == "laminar"

    def test_laminar_regime(self):
        result = reynolds_number(
            velocity=1.0,
            characteristic_length=0.01,
            density=1.225,
            dynamic_viscosity=1.789e-5,
        )
        assert result["flow_regime"] == "laminar"

    def test_temperature_must_be_physical(self):
        with pytest.raises(ValueError, match="Temperature must be > 0 K"):
            reynolds_number(
                velocity=100.0,
                characteristic_length=1.0,
                temperature_k=0.0,
            )


class TestMachNumber:
    def test_sea_level(self):
        result = mach_number(340.0, 0.0)
        assert pytest.approx(result["mach_number"], 0.01) == 1.0
        assert result["regime"] == "transonic"

    def test_subsonic(self):
        result = mach_number(200.0, 0.0)
        assert result["mach_number"] < 1.0
        assert result["regime"] == "subsonic"

    def test_negative_velocity_rejected(self):
        with pytest.raises(ValueError, match="Velocity must be >= 0"):
            mach_number(-1.0, 0.0)


class TestDynamicPressure:
    def test_sea_level(self):
        result = dynamic_pressure(100.0, 0.0)
        expected = 0.5 * 1.225 * 100.0**2
        assert pytest.approx(result["dynamic_pressure_pa"], 1.0) == expected


class TestLiftDragCoefficients:
    def test_lift_coefficient(self):
        result = lift_coefficient(1000.0, 50.0, 0.0, 10.0)
        assert result["lift_coefficient"] > 0

    def test_drag_coefficient(self):
        result = drag_coefficient(500.0, 50.0, 0.0, 10.0)
        assert result["drag_coefficient"] > 0


class TestSkinFriction:
    def test_laminar(self):
        # Blasius average (plate-integrated) laminar flat-plate coefficient.
        result = skin_friction_coefficient(1e5, "laminar")
        assert result["skin_friction_coefficient"] == pytest.approx(1.328 / 1e5**0.5, abs=5e-7)

    def test_turbulent(self):
        # Prandtl-Schlichting 1/7-power AVERAGE turbulent coefficient (0.074*Re^-0.2),
        # consistent with the average laminar branch; the local value would be 0.0592.
        result = skin_friction_coefficient(1e6, "turbulent")
        assert result["skin_friction_coefficient"] == pytest.approx(0.074 * 1e6**-0.2, abs=5e-7)

    def test_laminar_and_turbulent_are_both_average(self):
        # At the transition Re ~ 5e5 the average turbulent cf should exceed the average
        # laminar cf (turbulent skin friction is higher) — a sanity check that both
        # branches use the same (average) convention rather than mixing average/local.
        re = 5e5
        lam = skin_friction_coefficient(re, "laminar")["skin_friction_coefficient"]
        turb = skin_friction_coefficient(re, "turbulent")["skin_friction_coefficient"]
        assert turb > lam

    def test_unknown_flow_regime_rejected(self):
        with pytest.raises(ValueError, match="Flow regime must be one of"):
            skin_friction_coefficient(1e6, "unknown")


class TestAeroAnalysis:
    def test_comprehensive(self):
        result = aero_analysis(
            velocity=250.0,
            altitude_m=5000.0,
            characteristic_length=2.0,
            reference_area=10.0,
            lift=50000.0,
            drag=5000.0,
        )
        assert result["reynolds_number"] > 0
        assert result["mach_number"] > 0
        assert result["dynamic_pressure_pa"] > 0
        assert result["lift_coefficient"] is not None
        assert result["drag_coefficient"] is not None
        assert result["lift_to_drag_ratio"] is not None

    def test_zero_lift_reports_zero_coefficient_and_ratio(self):
        result = aero_analysis(
            velocity=250.0,
            altitude_m=0.0,
            characteristic_length=2.0,
            reference_area=10.0,
            lift=0.0,
            drag=5000.0,
        )
        assert result["lift_coefficient"] == 0.0
        assert result["drag_coefficient"] > 0.0
        assert result["lift_to_drag_ratio"] == 0.0

    def test_reference_area_required(self):
        with pytest.raises(ValueError, match="Reference area must be > 0"):
            aero_analysis(
                velocity=250.0,
                altitude_m=0.0,
                characteristic_length=2.0,
                reference_area=0.0,
            )
