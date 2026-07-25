"""Tests for Barrowman center of pressure and static margin (audit Batch 5)."""

import math

import pytest

from rocket_tools.aerodynamics import center_of_pressure, static_margin


class TestCenterOfPressure:
    def test_hand_computed_barrowman(self):
        # A small three-fin rocket, worked through the Barrowman equations by hand:
        #   nose: CNa=2, x_nose = 0.466*0.15 = 0.0699 m
        #   fins: CNa_fins ~= 9.740, x_fins ~= 0.51861 m
        #   x_cp = (2*0.069 + 9.740*0.51861)/11.740 ~= 0.442 m
        r = center_of_pressure(
            nose_shape="ogive",
            nose_length_m=0.15,
            body_diameter_m=0.025,
            fin_count=3,
            fin_root_chord_m=0.05,
            fin_tip_chord_m=0.025,
            fin_semi_span_m=0.03,
            fin_sweep_length_m=0.02,
            fin_position_from_nose_m=0.5,
        )
        assert r["cp_from_nose_m"] == pytest.approx(0.442, abs=1e-3)
        assert r["cn_alpha_fins"] == pytest.approx(9.740, abs=1e-2)
        assert r["cn_alpha_total_per_rad"] == pytest.approx(11.740, abs=1e-2)
        assert r["cp_nose_from_nose_m"] == pytest.approx(0.0699, abs=1e-4)

    def test_more_fin_area_moves_cp_aft(self):
        base = dict(
            nose_shape="ogive",
            nose_length_m=0.15,
            body_diameter_m=0.025,
            fin_count=3,
            fin_root_chord_m=0.05,
            fin_tip_chord_m=0.025,
            fin_semi_span_m=0.03,
            fin_sweep_length_m=0.02,
            fin_position_from_nose_m=0.5,
        )
        small = center_of_pressure(**base)
        bigger = center_of_pressure(**{**base, "fin_semi_span_m": 0.05})
        # Larger fins carry more normal force, pulling the CP further aft.
        assert bigger["cp_from_nose_m"] > small["cp_from_nose_m"]

    def test_cone_nose_cp_position(self):
        r = center_of_pressure(
            nose_shape="cone",
            nose_length_m=0.2,
            body_diameter_m=0.05,
            fin_count=4,
            fin_root_chord_m=0.06,
            fin_tip_chord_m=0.03,
            fin_semi_span_m=0.04,
            fin_sweep_length_m=0.03,
            fin_position_from_nose_m=0.8,
        )
        # Cone nose CP is at 2/3 of its length.
        assert r["cp_nose_from_nose_m"] == pytest.approx(0.666 * 0.2, abs=1e-4)

    def test_delta_fin_zero_tip_chord(self):
        # Triangular (delta) fin: tip chord 0 must not blow up.
        r = center_of_pressure(
            nose_shape="ogive",
            nose_length_m=0.15,
            body_diameter_m=0.025,
            fin_count=3,
            fin_root_chord_m=0.05,
            fin_tip_chord_m=0.0,
            fin_semi_span_m=0.03,
            fin_sweep_length_m=0.04,
            fin_position_from_nose_m=0.5,
        )
        assert math.isfinite(r["cp_from_nose_m"])
        assert r["cn_alpha_fins"] > 0

    @pytest.mark.parametrize(
        "bad",
        [
            {"nose_shape": "sphere"},
            {"nose_length_m": 0.0},
            {"body_diameter_m": -1.0},
            {"fin_count": 0},
            {"fin_root_chord_m": 0.0},
            {"fin_semi_span_m": 0.0},
            {"fin_tip_chord_m": -0.01},
        ],
    )
    def test_invalid_inputs_rejected(self, bad):
        args = dict(
            nose_shape="ogive",
            nose_length_m=0.15,
            body_diameter_m=0.025,
            fin_count=3,
            fin_root_chord_m=0.05,
            fin_tip_chord_m=0.025,
            fin_semi_span_m=0.03,
            fin_sweep_length_m=0.02,
            fin_position_from_nose_m=0.5,
        )
        args.update(bad)
        with pytest.raises(ValueError):
            center_of_pressure(**args)


class TestStaticMargin:
    def test_stable_positive_margin(self):
        r = static_margin(cp_from_nose_m=0.442, cg_from_nose_m=0.35, reference_diameter_m=0.025)
        # (0.442 - 0.35)/0.025 = 3.68 calibers
        assert r["static_margin_calibers"] == pytest.approx(3.68, abs=1e-2)
        assert r["stable"] is True

    def test_unstable_when_cp_ahead_of_cg(self):
        r = static_margin(cp_from_nose_m=0.30, cg_from_nose_m=0.40, reference_diameter_m=0.025)
        assert r["static_margin_calibers"] < 0
        assert r["stable"] is False

    def test_adequately_stable_band(self):
        # 1.5 calibers -> within the 1-2 rule-of-thumb band.
        r = static_margin(cp_from_nose_m=0.4375, cg_from_nose_m=0.40, reference_diameter_m=0.025)
        assert r["static_margin_calibers"] == pytest.approx(1.5, abs=1e-2)
        assert r["adequately_stable"] is True

    def test_zero_reference_diameter_rejected(self):
        with pytest.raises(ValueError):
            static_margin(cp_from_nose_m=0.4, cg_from_nose_m=0.3, reference_diameter_m=0.0)
