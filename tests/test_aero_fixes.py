"""Regression tests for the aerodynamics correctness fixes (audit Batch 2)."""

import pytest

from rocket_tools.aerodynamics import (
    aero_analysis,
    breguet_endurance,
    breguet_range,
    drag_polar,
    lift_curve_slope,
    nozzle_performance,
    skin_friction_coefficient,
)


class TestBreguet:
    def test_range_equals_velocity_times_endurance(self):
        common = dict(
            specific_fuel_consumption=1.7e-5,
            lift_to_drag_ratio=17,
            initial_mass_kg=50000,
            final_mass_kg=38000,
        )
        r = breguet_range(velocity=250, **common)
        e = breguet_endurance(**common)
        assert r["range_m"] == pytest.approx(250 * e["endurance_s"], rel=1e-3)
        # sanity: ~7000 km, not the old ~68000 km
        assert 6000 < r["range_km"] < 8000


class TestSkinFrictionAndAero:
    def test_transitional_regime_accepted(self):
        cf = skin_friction_coefficient(7e5, "transitional")
        assert cf["skin_friction_coefficient"] > 0

    def test_aero_analysis_transitional_no_crash(self):
        # Re ~ 7e5 lands in the transitional band; previously raised ValueError.
        r = aero_analysis(
            velocity=30,
            altitude_m=0,
            characteristic_length=0.35,
            reference_area=0.1,
            lift=100,
            drag=10,
        )
        assert not r.get("error")
        assert 5e5 <= r["reynolds_number"] < 1e6


class TestLiftCurveSlope:
    def test_transonic_rejected(self):
        with pytest.raises(ValueError, match="[Tt]ransonic"):
            lift_curve_slope(mach=1.0, aspect_ratio=8)

    def test_subsonic_and_supersonic_ok(self):
        assert lift_curve_slope(mach=0.5, aspect_ratio=8)["cl_alpha_3d_per_rad"] > 0
        assert lift_curve_slope(mach=2.0, aspect_ratio=8)["cl_alpha_3d_per_rad"] > 0

    def test_supersonic_subsonic_leading_edge_rejected(self):
        # low AR at low supersonic Mach -> 2*AR*sqrt(M^2-1) <= 1
        with pytest.raises(ValueError, match="subsonic leading edge"):
            lift_curve_slope(mach=1.25, aspect_ratio=0.5)


class TestDragPolarWaveDrag:
    def test_no_wave_drag_at_m0(self):
        d = drag_polar(cl=0.5, cd0=0.02, aspect_ratio=8, mach=0.0)
        assert d["cd_wave"] == 0.0

    def test_wave_drag_depends_on_thickness_and_sweep(self):
        thin_swept = drag_polar(
            cl=0.5, cd0=0.02, aspect_ratio=8, mach=0.85, thickness_to_chord=0.08, sweep_deg=30
        )
        thick_unswept = drag_polar(
            cl=0.5, cd0=0.02, aspect_ratio=8, mach=0.85, thickness_to_chord=0.15, sweep_deg=0
        )
        # thinner, more-swept wing has a higher drag-divergence Mach and less wave drag
        assert thin_swept["drag_divergence_mach"] > thick_unswept["drag_divergence_mach"]
        assert thin_swept["cd_wave"] < thick_unswept["cd_wave"]


class TestNozzleSeparationAndVacuum:
    def test_overexpanded_separation_gives_physical_thrust(self):
        # Vacuum-optimized nozzle fired at sea level -> separated, positive thrust.
        n = nozzle_performance(
            chamber_pressure_pa=7e6,
            chamber_temperature_k=3500,
            ambient_pressure_pa=101325,
            throat_area_m2=0.05,
            exit_area_m2=2.0,
        )
        assert n["flow_separated"] is True
        assert n["expansion_state"] == "overexpanded_separated"
        assert n["thrust_n"] > 0  # not a huge negative attached-flow value
        # exit pressure held at the ~0.4*ambient separation pressure
        assert n["exit_pressure_pa"] == pytest.approx(0.4 * 101325, rel=1e-6)

    def test_vacuum_no_crash(self):
        v = nozzle_performance(
            chamber_pressure_pa=7e6,
            chamber_temperature_k=3500,
            ambient_pressure_pa=0.0,
            throat_area_m2=0.05,
            exit_area_m2=2.0,
        )
        assert v["expansion_state"] == "vacuum"
        assert v["thrust_n"] > 0
