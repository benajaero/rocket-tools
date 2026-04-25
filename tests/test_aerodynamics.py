"""Tests for aerodynamics."""

import pytest
from rocket_tools.aerodynamics import (
    reynolds_number,
    mach_number,
    dynamic_pressure,
    lift_coefficient,
    drag_coefficient,
    skin_friction_coefficient,
    aero_analysis,
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


class TestMachNumber:
    def test_sea_level(self):
        result = mach_number(340.0, 0.0)
        assert pytest.approx(result["mach_number"], 0.01) == 1.0
        assert result["regime"] == "transonic"

    def test_subsonic(self):
        result = mach_number(200.0, 0.0)
        assert result["mach_number"] < 1.0
        assert result["regime"] == "subsonic"


class TestDynamicPressure:
    def test_sea_level(self):
        result = dynamic_pressure(100.0, 0.0)
        expected = 0.5 * 1.225 * 100.0 ** 2
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
        result = skin_friction_coefficient(1e5, "laminar")
        assert result["skin_friction_coefficient"] > 0

    def test_turbulent(self):
        result = skin_friction_coefficient(1e6, "turbulent")
        assert result["skin_friction_coefficient"] > 0


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
