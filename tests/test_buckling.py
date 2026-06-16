"""Tests for column buckling and plate buckling."""

import pytest

from rocket_tools.structural.buckling import column_buckling, plate_buckling_coefficient


class TestColumnBuckling:
    def test_euler_regime(self):
        # Long slender column -> elastic buckling
        result = column_buckling(
            youngs_modulus=70e9,
            area_moment=1e-8,
            area=1e-4,
            length=5.0,
            yield_strength=276e6,
            end_condition="pinned_pinned",
        )
        assert result["regime"] == "elastic"
        assert result["critical_load_n"] > 0
        assert result["slenderness_ratio"] > result["transition_slenderness"]

    def test_johnson_regime(self):
        # Short column -> inelastic buckling
        result = column_buckling(
            youngs_modulus=70e9,
            area_moment=1e-5,
            area=1e-3,
            length=0.1,
            yield_strength=276e6,
            end_condition="pinned_pinned",
        )
        assert result["regime"] == "inelastic"
        assert result["critical_load_n"] > 0
        assert result["slenderness_ratio"] < result["transition_slenderness"]

    def test_end_conditions(self):
        for ec in ["pinned_pinned", "fixed_free", "fixed_pinned", "fixed_fixed"]:
            result = column_buckling(
                youngs_modulus=70e9,
                area_moment=1e-6,
                area=1e-4,
                length=1.0,
                yield_strength=276e6,
                end_condition=ec,
            )
            assert result["end_condition"] == ec
            assert result["critical_load_n"] > 0

    def test_invalid_input(self):
        with pytest.raises(ValueError):
            column_buckling(youngs_modulus=-1, area_moment=1, area=1, length=1, yield_strength=1)


class TestPlateBuckling:
    def test_compression_ss(self):
        k = plate_buckling_coefficient(2.0, "simply_supported", "compression")
        assert k == pytest.approx(4.0, rel=0.1)

    def test_shear(self):
        k = plate_buckling_coefficient(1.0, "simply_supported", "shear")
        assert k > 5.0

    def test_bending(self):
        k = plate_buckling_coefficient(2.0, "simply_supported", "bending")
        assert k > 20.0

    def test_clamped(self):
        k_ss = plate_buckling_coefficient(2.0, "simply_supported", "compression")
        k_cl = plate_buckling_coefficient(2.0, "clamped", "compression")
        assert k_cl > k_ss

    def test_invalid_aspect_ratio(self):
        with pytest.raises(ValueError):
            plate_buckling_coefficient(-1.0)
