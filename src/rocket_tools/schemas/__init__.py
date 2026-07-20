"""Pydantic schemas for all rocket-tools inputs and outputs.

These models provide:
- Runtime validation with clear error messages
- JSON Schema generation for LLM tool calling
- Type safety across router, workflows, and MCP server
"""

from .aerodynamics import (
    AeroAnalysisInput,
    AeroAnalysisOutput,
    BreguetEnduranceInput,
    BreguetRangeInput,
    DragCoefficientInput,
    DragCoefficientOutput,
    DragPolarInput,
    DynamicPressureInput,
    DynamicPressureOutput,
    IsentropicFlowInput,
    LiftCoefficientInput,
    LiftCoefficientOutput,
    LiftCurveSlopeInput,
    MachNumberInput,
    MachNumberOutput,
    NormalShockInput,
    NozzlePerformanceInput,
    ObliqueShockInput,
    OptimalAreaRatioInput,
    PrandtlMeyerFromAngleInput,
    PrandtlMeyerInput,
    ReynoldsNumberInput,
    ReynoldsNumberOutput,
    SkinFrictionInput,
    SkinFrictionOutput,
    WingLoadingInput,
)
from .design import (
    CompositeCGInput,
    HohmannTransferInput,
    MultiStageDeltaVInput,
    OrbitalPeriodInput,
    OrbitalVelocityInput,
    PayloadFractionInput,
    PlaneChangeInput,
    PropellantTankSizingInput,
    RocketDeltaVInput,
    ThrustToWeightInput,
    VisVivaInput,
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
    ColumnBucklingInput,
    CombinedMarginInput,
    DeflectionMarginInput,
    MarginOfSafetyInput,
    PlateBucklingInput,
    RectangleSection,
    SectionPropertiesInput,
    TrussAnalysisInput,
    VonMisesInput,
)
from .utils import UnitConvertInput, UnitConvertOutput

__all__ = [
    # Structural
    "BeamAnalysisInput",
    "BeamAnalysisOutput",
    "RectangleSection",
    "CircleSection",
    "SectionPropertiesInput",
    "ColumnBucklingInput",
    "PlateBucklingInput",
    "MarginOfSafetyInput",
    "VonMisesInput",
    "CombinedMarginInput",
    "DeflectionMarginInput",
    "TrussAnalysisInput",
    # Materials
    "MaterialLookupInput",
    "MaterialLookupOutput",
    "ISAAtmosphereInput",
    "ISAAtmosphereOutput",
    # Aerodynamics - Fundamentals
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
    # Aerodynamics - Compressible
    "IsentropicFlowInput",
    "NormalShockInput",
    "ObliqueShockInput",
    "PrandtlMeyerInput",
    "PrandtlMeyerFromAngleInput",
    # Aerodynamics - Aircraft
    "LiftCurveSlopeInput",
    "DragPolarInput",
    "BreguetRangeInput",
    "BreguetEnduranceInput",
    "WingLoadingInput",
    # Aerodynamics - Nozzle
    "NozzlePerformanceInput",
    "OptimalAreaRatioInput",
    # Design
    "RocketDeltaVInput",
    "MultiStageDeltaVInput",
    "OrbitalVelocityInput",
    "PayloadFractionInput",
    "ThrustToWeightInput",
    "CompositeCGInput",
    "PropellantTankSizingInput",
    "HohmannTransferInput",
    "VisVivaInput",
    "PlaneChangeInput",
    "OrbitalPeriodInput",
    # Utils
    "UnitConvertInput",
    "UnitConvertOutput",
]
