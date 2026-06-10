"""Pydantic schemas for all rocket-tools inputs and outputs.

These models provide:
- Runtime validation with clear error messages
- JSON Schema generation for LLM tool calling
- Type safety across router, workflows, and MCP server
"""

from .aerodynamics import (
    AeroAnalysisInput,
    AeroAnalysisOutput,
    DragCoefficientInput,
    DragCoefficientOutput,
    DynamicPressureInput,
    DynamicPressureOutput,
    LiftCoefficientInput,
    LiftCoefficientOutput,
    MachNumberInput,
    MachNumberOutput,
    ReynoldsNumberInput,
    ReynoldsNumberOutput,
    SkinFrictionInput,
    SkinFrictionOutput,
)
from .materials import (
    ISAAtmosphereInput,
    ISAAtmosphereOutput,
    MaterialLookupInput,
    MaterialLookupOutput,
)
from .structural import (
    BeamAnalysisInput,
    BeamAnalysisOutput,
    CircleSection,
    RectangleSection,
)
from .utils import UnitConvertInput, UnitConvertOutput

__all__ = [
    # Structural
    "BeamAnalysisInput",
    "BeamAnalysisOutput",
    "RectangleSection",
    "CircleSection",
    # Materials
    "MaterialLookupInput",
    "MaterialLookupOutput",
    "ISAAtmosphereInput",
    "ISAAtmosphereOutput",
    # Aerodynamics
    "ReynoldsNumberInput",
    "ReynoldsNumberOutput",
    "MachNumberInput",
    "MachNumberOutput",
    "DynamicPressureInput",
    "DynamicPressureOutput",
    "LiftCoefficientInput",
    "LiftCoefficientOutput",
    "DragCoefficientInput",
    "DragCoefficientOutput",
    "SkinFrictionInput",
    "SkinFrictionOutput",
    "AeroAnalysisInput",
    "AeroAnalysisOutput",
    # Utils
    "UnitConvertInput",
    "UnitConvertOutput",
]
