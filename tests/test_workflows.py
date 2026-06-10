"""Tests for workflow engine."""

from pathlib import Path

import pytest

from rocket_tools.workflows import load_all_workflows, load_workflow, run_workflow

BUILT_IN_DIR = Path(__file__).parent.parent / "src" / "rocket_tools" / "workflows" / "built_in"


class TestLoadWorkflow:
    def test_load_design_beam(self):
        wf = load_workflow(BUILT_IN_DIR / "design_beam.yaml")
        assert wf.name == "design_beam"
        assert len(wf.steps) == 2

    def test_load_all(self):
        wfs = load_all_workflows(BUILT_IN_DIR)
        assert "design_beam" in wfs
        assert "preliminary_aircraft_sizing" in wfs
        assert "launch_vehicle_max_q" in wfs
        assert "design_beam_with_conversion" in wfs
        assert "multi_load_beam" in wfs


class TestRunWorkflow:
    def test_design_beam(self):
        wfs = load_all_workflows(BUILT_IN_DIR)
        wf = wfs["design_beam"]
        result = run_workflow(
            wf,
            {
                "material": "6061-T6",
                "load": 500.0,
                "length": 2.0,
                "cross_section": {"type": "rectangle", "width": 0.05, "height": 0.01},
            },
        )
        assert "beam" in result.outputs
        assert result.outputs["beam"]["bending_stress_pa"] > 0
        assert len(result.trace) == 2

    def test_preliminary_aircraft_sizing(self):
        wfs = load_all_workflows(BUILT_IN_DIR)
        wf = wfs["preliminary_aircraft_sizing"]
        result = run_workflow(
            wf,
            {
                "cruise_altitude_m": 5000.0,
                "cruise_velocity_m_s": 100.0,
                "mean_aerodynamic_chord_m": 1.0,
                "wing_area_m2": 10.0,
                "mass_kg": 500.0,
            },
        )
        assert "re" in result.outputs
        assert "cl" in result.outputs

    def test_design_beam_with_conversion(self):
        wfs = load_all_workflows(BUILT_IN_DIR)
        wf = wfs["design_beam_with_conversion"]
        result = run_workflow(
            wf,
            {
                "material": "6061-T6",
                "load": 500.0,
                "length": 2.0,
                "cross_section": {"type": "rectangle", "width": 0.05, "height": 0.01},
            },
        )
        assert "beam" in result.outputs
        assert "deflection_mm" in result.outputs
        assert result.outputs["deflection_mm"]["converted_value"] > 0
        assert len(result.trace) == 3

    def test_interpolation_error(self):
        from rocket_tools.workflows.engine import resolve_interpolation

        with pytest.raises(Exception):
            resolve_interpolation("${missing.key}", {})
