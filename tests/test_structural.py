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

    def test_invalid_length(self):
        with pytest.raises(ValueError, match="Length must be > 0"):
            beam_analysis(
                load=100.0,
                length=-1.0,
                youngs_modulus=68.9e9,
                cross_section={"type": "rectangle", "width": 0.05, "height": 0.01},
            )

    def test_invalid_cross_section(self):
        with pytest.raises(ValueError):
            beam_analysis(
                load=100.0,
                length=1.0,
                youngs_modulus=68.9e9,
                cross_section={"type": "triangle", "base": 0.05, "height": 0.01},
            )
