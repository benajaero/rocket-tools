"""Pydantic schemas for all rocket-tools inputs and outputs.

These models provide:
- Runtime validation with clear error messages
- JSON Schema generation for LLM tool calling
- Type safety across router, workflows, and MCP server
"""

from .aerodynamics import (
    AeroAnalysisInput,
    AeroAnalysisOutput,
    BallisticEntryInput,
    BreguetEnduranceInput,
    BreguetRangeInput,
    CenterOfPressureInput,
    CharacteristicVelocityInput,
    DragCoefficientInput,
    DragCoefficientOutput,
    DragPolarInput,
    DynamicPressureInput,
    DynamicPressureOutput,
    IdealSpecificImpulseInput,
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
    RecoveryTemperatureInput,
    ReynoldsNumberInput,
    ReynoldsNumberOutput,
    SkinFrictionInput,
    SkinFrictionOutput,
    StagnationTemperatureInput,
    StaticMarginInput,
    SuttonGravesInput,
    ThroatMassFluxInput,
    WingLoadingInput,
)
from .design import (
    CompositeCGInput,
    HohmannTransferInput,
    LambertSolverInput,
    MultiStageDeltaVInput,
    OrbitalElementsFromStateInput,
    OrbitalPeriodInput,
    OrbitalVelocityInput,
    PayloadFractionInput,
    PlaneChangeInput,
    PropellantTankSizingInput,
    RocketDeltaVInput,
    StateFromOrbitalElementsInput,
    ThrustToWeightInput,
    VisVivaInput,
)
from .materials import (
    ISAAtmosphereInput,
    ISAAtmosphereOutput,
    MaterialLookupInput,
    MaterialLookupOutput,
)
from .optimization import (
    DesignOptimizerInput,
    StagingOptimizerInput,
)
from .standards import (
    DesignReviewInput,
    DesignReviewItem,
    FMEAInput,
    FMEAItem,
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
from .trajectory import (
    AscentSimInput,
    ParachuteAreaInput,
    ParachuteDescentInput,
    VehicleSizingInput,
)
from .utils import (
    CiteToolInput,
    ParameterSweepInput,
    PropagateUncertaintyInput,
    UnitConvertInput,
    UnitConvertOutput,
    ValidateResultInput,
)
from .viz import (
    BeamDiagramInput,
    DragPolarPlotInput,
    ISAProfileInput,
    NozzleContourInput,
    TrajectoryPlotInput,
)

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
    # Aerodynamics - Aerothermodynamics
    "StagnationTemperatureInput",
    "RecoveryTemperatureInput",
    "SuttonGravesInput",
    "BallisticEntryInput",
    # Aerodynamics - Propulsion
    "CharacteristicVelocityInput",
    "IdealSpecificImpulseInput",
    "ThroatMassFluxInput",
    # Aerodynamics - Static stability
    "CenterOfPressureInput",
    "StaticMarginInput",
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
    "LambertSolverInput",
    "OrbitalElementsFromStateInput",
    "StateFromOrbitalElementsInput",
    # Trajectory
    "AscentSimInput",
    "VehicleSizingInput",
    "ParachuteDescentInput",
    "ParachuteAreaInput",
    # Optimization
    "StagingOptimizerInput",
    "DesignOptimizerInput",
    # Standards & reliability
    "DesignReviewInput",
    "DesignReviewItem",
    "FMEAInput",
    "FMEAItem",
    # Visualization
    "BeamDiagramInput",
    "DragPolarPlotInput",
    "NozzleContourInput",
    "ISAProfileInput",
    "TrajectoryPlotInput",
    # Utils
    "CiteToolInput",
    "ParameterSweepInput",
    "PropagateUncertaintyInput",
    "ValidateResultInput",
    "UnitConvertInput",
    "UnitConvertOutput",
]
