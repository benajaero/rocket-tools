"""Regression tests for the structural correctness fixes (audit Batch 1).

Each test pins a previously-wrong output to its correct textbook value.
"""

import pytest

from rocket_tools.structural import (
    beam_analysis,
    plate_buckling_coefficient,
    section_properties,
    truss_analysis,
)

RECT = {"type": "rectangle", "width": 0.05, "height": 0.02}  # A = 1e-3 m^2


class TestTrussReactions:
    def test_symmetric_two_bar_reactions(self):
        # 1000 N down at the apex of a symmetric 2-bar truss -> +500 N vertical each support.
        r = truss_analysis(
            nodes=[[0, 0], [2, 0], [1, 1]],
            elements=[[0, 2], [1, 2]],
            element_properties=[{"youngs_modulus_pa": 200e9, "area_m2": 1e-3}] * 2,
            constraints=[{"node": 0, "fixed_dof": [0, 1]}, {"node": 1, "fixed_dof": [0, 1]}],
            loads=[{"node": 2, "force": [0, -1000]}],
        )
        ry = sum(rc["reaction_force_n"][1] for rc in r["reactions"])
        assert ry == pytest.approx(1000.0, abs=1e-6)  # balances the applied load
        # each vertical reaction ~ +500
        for rc in r["reactions"]:
            assert rc["reaction_force_n"][1] == pytest.approx(500.0, abs=1e-3)

    def test_zero_length_member_rejected(self):
        with pytest.raises(ValueError, match="coincident"):
            truss_analysis(
                nodes=[[0, 0], [0, 0]],
                elements=[[0, 1]],
                element_properties=[{"youngs_modulus_pa": 200e9, "area_m2": 1e-3}],
                constraints=[{"node": 0, "fixed_dof": [0, 1]}],
                loads=[{"node": 1, "force": [100, 0]}],
            )


class TestBeamShearAndCantilever:
    def test_cantilever_point_midspan_is_midspan(self):
        # P=500, L=2 -> mid-span load: M_root = P*L/2 = 500 (was 1000 tip-load bug).
        c = beam_analysis(500, 2, 200e9, RECT, load_type="point_midspan", support_type="cantilever")
        assert c["max_bending_moment_n_m"] == pytest.approx(500.0)

    def test_cantilever_point_tip(self):
        c = beam_analysis(500, 2, 200e9, RECT, load_type="point_tip", support_type="cantilever")
        assert c["max_bending_moment_n_m"] == pytest.approx(1000.0)

    def test_point_tip_only_on_cantilever(self):
        with pytest.raises(ValueError, match="cantilever"):
            beam_analysis(1, 1, 1, RECT, load_type="point_tip", support_type="simply_supported")

    def test_shear_simply_supported_point(self):
        # P=1000 -> V_max = P/2 = 500; tau = 1.5*V/A = 1.5*500/1e-3 = 7.5e5 Pa.
        b = beam_analysis(1000, 2, 200e9, RECT, load_type="point_midspan")
        assert b["max_shear_force_n"] == pytest.approx(500.0)
        assert b["shear_stress_pa"] == pytest.approx(750000.0)

    def test_shear_distributed(self):
        # w=1000 N/m, L=2 -> V_max = wL/2 = 1000; tau = 1.5*1000/1e-3 = 1.5e6 Pa.
        b = beam_analysis(1000, 2, 200e9, RECT, load_type="distributed")
        assert b["max_shear_force_n"] == pytest.approx(1000.0)
        assert b["shear_stress_pa"] == pytest.approx(1.5e6)


class TestBucklingAxis:
    def test_buckling_uses_weak_axis(self):
        # A column buckles about its axis of least I. For a 0.02 x 0.1 rectangle the
        # weak-axis I is 0.1*0.02^3/12 = 6.667e-8 m^4 (not the strong-axis 1.667e-6),
        # so P_cr = pi^2 E I_min / L^2. The old code used the strong axis and was 25x high.
        import math

        r = beam_analysis(
            1000.0,
            1.0,
            70e9,
            {"type": "rectangle", "width": 0.02, "height": 0.1},
            load_type="axial",
        )
        i_min = 0.1 * 0.02**3 / 12.0
        assert r["buckling_area_moment_m4"] == pytest.approx(i_min, rel=1e-9)
        assert r["critical_buckling_load_n"] == pytest.approx(
            math.pi**2 * 70e9 * i_min / 1.0**2, rel=1e-6
        )
        # strong-axis bending property is unchanged (still reports the full I_xx)
        assert r["area_moment_m4"] == pytest.approx(0.02 * 0.1**3 / 12.0, rel=1e-9)

    def test_square_section_buckling_unchanged(self):
        # For a square section weak and strong axes coincide, so P_cr is identical.
        sq = {"type": "rectangle", "width": 0.05, "height": 0.05}
        r = beam_analysis(1000.0, 1.0, 70e9, sq, load_type="axial")
        assert r["buckling_area_moment_m4"] == pytest.approx(r["area_moment_m4"], rel=1e-12)


class TestPlateBuckling:
    def test_compression_short_plate_is_conservative(self):
        # a/b = 0.5 uniaxial compression: k = (1/0.5 + 0.5)^2 = 6.25 (was ~1.0, 6x wrong).
        assert plate_buckling_coefficient(0.5, "simply_supported", "compression") == pytest.approx(
            6.25, rel=1e-3
        )

    def test_compression_unity_and_integer(self):
        assert plate_buckling_coefficient(1.0) == pytest.approx(4.0, rel=1e-3)
        assert plate_buckling_coefficient(2.0) == pytest.approx(4.0, rel=1e-3)

    def test_clamped_higher_than_ss_at_all_ar(self):
        for ar in (0.5, 1.0, 2.0):
            ss = plate_buckling_coefficient(ar, "simply_supported", "compression")
            cl = plate_buckling_coefficient(ar, "clamped", "compression")
            assert cl > ss


class TestSectionValidation:
    def test_ibeam_rejects_thick_flange(self):
        with pytest.raises(ValueError, match="flange_thickness"):
            section_properties(
                "ibeam", flange_width=0.1, height=0.02, flange_thickness=0.02, web_thickness=0.005
            )

    def test_tsection_rejects_thick_flange(self):
        with pytest.raises(ValueError, match="flange_thickness"):
            section_properties(
                "tsection",
                flange_width=0.1,
                height=0.02,
                flange_thickness=0.03,
                web_thickness=0.005,
            )

    def test_ibeam_rejects_thick_web(self):
        with pytest.raises(ValueError, match="web_thickness"):
            section_properties(
                "ibeam", flange_width=0.02, height=0.2, flange_thickness=0.01, web_thickness=0.05
            )
