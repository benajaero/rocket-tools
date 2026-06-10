"""Tests for aircraft aerodynamics."""

import pytest

from rocket_tools.aerodynamics.aircraft import (
    breguet_endurance,
    breguet_range,
    drag_polar,
    lift_curve_slope,
    wing_loading,
)


class TestLiftCurveSlope:
    def test_subsonic(self):
        result = lift_curve_slope(mach=0.3, aspect_ratio=8.0)
        assert result["cl_alpha_2d_per_rad"] > 6.0
        assert result["cl_alpha_3d_per_rad"] > 4.0

    def test_supersonic(self):
        result = lift_curve_slope(mach=1.5, aspect_ratio=4.0)
        assert result["cl_alpha_2d_per_rad"] > 0
        assert result["cl_alpha_3d_per_rad"] > 0

    def test_invalid(self):
        with pytest.raises(ValueError):
            lift_curve_slope(mach=0.5, aspect_ratio=-1)


class TestDragPolar:
    def test_basic(self):
        result = drag_polar(cl=0.5, cd0=0.02, aspect_ratio=8.0)
        assert result["drag_coefficient"] > result["cd0"]
        assert result["lift_to_drag_ratio"] > 0

    def test_cd_increases_with_cl(self):
        r1 = drag_polar(cl=0.3, cd0=0.02, aspect_ratio=8.0)
        r2 = drag_polar(cl=0.6, cd0=0.02, aspect_ratio=8.0)
        assert r2["drag_coefficient"] > r1["drag_coefficient"]


class TestBreguetRange:
    def test_basic(self):
        result = breguet_range(
            lift_to_drag_ratio=15.0,
            specific_fuel_consumption=0.00002,
            velocity=250.0,
            initial_mass_kg=10000.0,
            final_mass_kg=8000.0,
        )
        assert result["range_m"] > 0
        assert result["fuel_fraction"] == pytest.approx(0.2, rel=1e-6)

    def test_invalid(self):
        with pytest.raises(ValueError):
            breguet_range(
                lift_to_drag_ratio=15.0,
                specific_fuel_consumption=0.00002,
                velocity=250.0,
                initial_mass_kg=1000.0,
                final_mass_kg=1000.0,
            )


class TestBreguetEndurance:
    def test_basic(self):
        result = breguet_endurance(
            lift_to_drag_ratio=15.0,
            specific_fuel_consumption=0.00002,
            initial_mass_kg=10000.0,
            final_mass_kg=8000.0,
        )
        assert result["endurance_s"] > 0


class TestWingLoading:
    def test_basic(self):
        result = wing_loading(weight_n=50000.0, wing_area_m2=25.0)
        assert result["wing_loading_pa"] == pytest.approx(2000.0, rel=1e-6)
        assert result["stall_speed_clean_ms"] > 0
        assert result["stall_speed_clean_knots"] > 0
