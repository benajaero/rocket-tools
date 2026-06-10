"""Tests for Pydantic schemas and structured validation."""

import pytest
from pydantic import ValidationError

from rocket_tools.schemas import (
    AeroAnalysisInput,
    BeamAnalysisInput,
    CircleSection,
    DynamicPressureInput,
    ISAAtmosphereInput,
    MachNumberInput,
    RectangleSection,
    ReynoldsNumberInput,
    UnitConvertInput,
)


class TestBeamSchemas:
    def test_rectangle_section(self):
        s = RectangleSection(width=0.05, height=0.01)
        assert s.type == "rectangle"
        assert s.width == 0.05

    def test_circle_section(self):
        s = CircleSection(diameter=0.1)
        assert s.type == "circle"
        assert s.diameter == 0.1

    def test_beam_input_valid(self):
        inp = BeamAnalysisInput(
            load=1000.0,
            length=2.0,
            youngs_modulus=68.9e9,
            cross_section={"type": "rectangle", "width": 0.05, "height": 0.01},
        )
        assert inp.load == 1000.0
        assert inp.cross_section.type == "rectangle"

    def test_beam_input_invalid_load(self):
        with pytest.raises(ValidationError):
            BeamAnalysisInput(
                load=-100,
                length=2.0,
                youngs_modulus=68.9e9,
                cross_section={"type": "rectangle", "width": 0.05, "height": 0.01},
            )

    def test_beam_input_invalid_length(self):
        with pytest.raises(ValidationError):
            BeamAnalysisInput(
                load=1000.0,
                length=0,
                youngs_modulus=68.9e9,
                cross_section={"type": "rectangle", "width": 0.05, "height": 0.01},
            )

    def test_beam_input_invalid_cross_section_type(self):
        with pytest.raises(ValidationError):
            BeamAnalysisInput(
                load=1000.0,
                length=2.0,
                youngs_modulus=68.9e9,
                cross_section={"type": "triangle", "width": 0.05, "height": 0.01},
            )


class TestAerodynamicsSchemas:
    def test_reynolds_number_valid(self):
        inp = ReynoldsNumberInput(velocity=100.0, characteristic_length=2.0, altitude_m=5000.0)
        assert inp.velocity == 100.0

    def test_reynolds_number_invalid_velocity(self):
        with pytest.raises(ValidationError):
            ReynoldsNumberInput(velocity=-10, characteristic_length=2.0)

    def test_mach_number_valid(self):
        inp = MachNumberInput(velocity=250.0, altitude_m=10000.0)
        assert inp.altitude_m == 10000.0

    def test_mach_number_altitude_too_high(self):
        with pytest.raises(ValidationError):
            MachNumberInput(velocity=250.0, altitude_m=30000.0)

    def test_dynamic_pressure_valid(self):
        inp = DynamicPressureInput(velocity=150.0, altitude_m=0.0)
        assert inp.altitude_m == 0.0

    def test_aero_analysis_valid(self):
        inp = AeroAnalysisInput(
            velocity=100.0,
            altitude_m=5000.0,
            characteristic_length=2.0,
            reference_area=10.0,
            lift=50000.0,
            drag=5000.0,
        )
        assert inp.lift == 50000.0


class TestMaterialSchemas:
    def test_isa_valid(self):
        inp = ISAAtmosphereInput(altitude_m=5000.0)
        assert inp.altitude_m == 5000.0

    def test_isa_negative_altitude(self):
        with pytest.raises(ValidationError):
            ISAAtmosphereInput(altitude_m=-100.0)

    def test_isa_altitude_too_high(self):
        with pytest.raises(ValidationError):
            ISAAtmosphereInput(altitude_m=50000.0)


class TestUnitConvertSchema:
    def test_valid(self):
        inp = UnitConvertInput(value=1.0, from_unit="m", to_unit="mm")
        assert inp.value == 1.0
        assert inp.from_unit == "m"
        assert inp.to_unit == "mm"

    def test_empty_unit(self):
        with pytest.raises(ValidationError):
            UnitConvertInput(value=1.0, from_unit="", to_unit="mm")
