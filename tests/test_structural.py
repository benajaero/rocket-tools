"""Tests for structural analysis."""

import pytest

from rocket_tools.structural import beam_analysis


class TestBeamAnalysis:
    def test_simply_supported_point_load(self):
        # 6061-T6 beam: 1m span, 100N point load, 50x10mm rectangle
        result = beam_analysis(
            load=100.0,
            length=1.0,
            youngs_modulus=68.9e9,
            cross_section={"type": "rectangle", "width": 0.05, "height": 0.01},
            load_type="point_midspan",
            support_type="simply_supported",
        )
        assert result["max_bending_moment_n_m"] > 0
        assert result["max_deflection_m"] > 0
        assert result["bending_stress_pa"] > 0
        assert result["area_moment_m4"] == pytest.approx(0.05 * 0.01**3 / 12.0)
        assert result["area_moment_m4"] > 0.0

    def test_yield_safety_factor_when_strength_provided(self):
        result = beam_analysis(
            load=100.0,
            length=1.0,
            youngs_modulus=68.9e9,
            cross_section={"type": "rectangle", "width": 0.05, "height": 0.01},
            yield_strength=276e6,
        )
        assert result["yield_strength_pa"] == 276e6
        assert result["safety_factor_yield"] == pytest.approx(
            276e6 / result["bending_stress_pa"], rel=0.01
        )

    def test_invalid_yield_strength_rejected(self):
        with pytest.raises(ValueError, match="Yield strength must be > 0"):
            beam_analysis(
                load=100.0,
                length=1.0,
                youngs_modulus=68.9e9,
                cross_section={"type": "rectangle", "width": 0.05, "height": 0.01},
                yield_strength=0.0,
            )

    def test_cantilever_point_load(self):
        result = beam_analysis(
            load=100.0,
            length=1.0,
            youngs_modulus=68.9e9,
            cross_section={"type": "rectangle", "width": 0.05, "height": 0.01},
            load_type="point_midspan",
            support_type="cantilever",
        )
        # Cantilever has larger deflection
        cantilever_defl = result["max_deflection_m"]

        ss_result = beam_analysis(
            load=100.0,
            length=1.0,
            youngs_modulus=68.9e9,
            cross_section={"type": "rectangle", "width": 0.05, "height": 0.01},
            load_type="point_midspan",
            support_type="simply_supported",
        )
        assert cantilever_defl > ss_result["max_deflection_m"]

    def test_axial_compression(self):
        result = beam_analysis(
            load=1000.0,
            length=1.0,
            youngs_modulus=200e9,
            cross_section={"type": "circle", "diameter": 0.05},
            load_type="axial",
            support_type="simply_supported",
        )
        assert result["critical_buckling_load_n"] > 0
        assert result["safety_factor_euler_buckling"] is not None
        expected_stress = 1000.0 / (3.141592653589793 * 0.025**2)
        assert result["bending_stress_pa"] == pytest.approx(expected_stress, abs=1.0)
        assert result["shear_stress_pa"] == 0.0

    def test_axial_tension_reports_normal_stress_without_buckling_factor(self):
        result = beam_analysis(
            load=-1000.0,
            length=1.0,
            youngs_modulus=200e9,
            cross_section={"type": "rectangle", "width": 0.05, "height": 0.01},
            load_type="axial",
            support_type="simply_supported",
        )
        assert result["bending_stress_pa"] < 0
        assert result["shear_stress_pa"] == 0.0
        assert result["safety_factor_euler_buckling"] is None

    def test_axial_buckling_uses_effective_length_factor(self):
        common = {
            "load": 1000.0,
            "length": 1.0,
            "youngs_modulus": 200e9,
            "cross_section": {"type": "circle", "diameter": 0.05},
            "load_type": "axial",
        }
        simply_supported = beam_analysis(**common, support_type="simply_supported")
        fixed_ends = beam_analysis(**common, support_type="fixed_ends")
        cantilever = beam_analysis(**common, support_type="cantilever")

        assert fixed_ends["critical_buckling_load_n"] == pytest.approx(
            simply_supported["critical_buckling_load_n"] * 4, rel=1e-4
        )
        assert cantilever["critical_buckling_load_n"] == pytest.approx(
            simply_supported["critical_buckling_load_n"] / 4, rel=1e-4
        )

    def test_invalid_length(self):
        with pytest.raises(ValueError, match="Length must be > 0"):
            beam_analysis(
                load=100.0,
                length=-1.0,
                youngs_modulus=68.9e9,
                cross_section={"type": "rectangle", "width": 0.05, "height": 0.01},
            )

    def test_nonfinite_load_rejected(self):
        with pytest.raises(ValueError, match="Load must be finite"):
            beam_analysis(
                load=float("nan"),
                length=1.0,
                youngs_modulus=68.9e9,
                cross_section={"type": "rectangle", "width": 0.05, "height": 0.01},
            )

    def test_non_mapping_cross_section_rejected(self):
        with pytest.raises(ValueError, match="Cross-section must be a mapping"):
            beam_analysis(
                load=100.0,
                length=1.0,
                youngs_modulus=68.9e9,
                cross_section=None,
            )

    def test_nonfinite_cross_section_dimension_rejected(self):
        with pytest.raises(ValueError, match="Width must be > 0"):
            beam_analysis(
                load=100.0,
                length=1.0,
                youngs_modulus=68.9e9,
                cross_section={"type": "rectangle", "width": float("inf"), "height": 0.01},
            )

    def test_invalid_cross_section(self):
        with pytest.raises(ValueError):
            beam_analysis(
                load=100.0,
                length=1.0,
                youngs_modulus=68.9e9,
                cross_section={"type": "triangle", "base": 0.05, "height": 0.01},
            )
