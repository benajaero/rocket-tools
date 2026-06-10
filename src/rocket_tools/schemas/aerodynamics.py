"""Pydantic schemas for aerodynamics tools."""

from typing import Literal

from pydantic import BaseModel, Field

# ---- Fundamental Aerodynamics ----


class ReynoldsNumberInput(BaseModel):
    """Input for reynolds_number tool."""

    velocity: float = Field(..., gt=0, description="Velocity in m/s")
    characteristic_length: float = Field(..., gt=0, description="Characteristic length in meters")
    density: float | None = Field(default=None, gt=0, description="Density in kg/m³ (optional)")
    dynamic_viscosity: float | None = Field(
        default=None, gt=0, description="Dynamic viscosity in Pa·s (optional)"
    )
    altitude_m: float | None = Field(
        default=None, ge=0, le=25_000, description="Altitude for ISA lookup (optional)"
    )
    temperature_k: float | None = Field(
        default=None, gt=0, description="Temperature in Kelvin for viscosity lookup (optional)"
    )


class ReynoldsNumberOutput(BaseModel):
    """Output from reynolds_number tool."""

    reynolds_number: float
    density_kg_m3: float
    dynamic_viscosity_pa_s: float
    velocity_m_s: float
    characteristic_length_m: float
    flow_regime: str


class MachNumberInput(BaseModel):
    """Input for mach_number tool."""

    velocity: float = Field(..., gt=0, description="Velocity in m/s")
    altitude_m: float = Field(..., ge=0, le=25_000, description="Altitude in meters")


class MachNumberOutput(BaseModel):
    """Output from mach_number tool."""

    mach_number: float
    velocity_m_s: float
    speed_of_sound_m_s: float
    altitude_m: float
    regime: str


class DynamicPressureInput(BaseModel):
    """Input for dynamic_pressure tool."""

    velocity: float = Field(..., gt=0, description="Velocity in m/s")
    altitude_m: float = Field(..., ge=0, le=25_000, description="Altitude in meters")


class DynamicPressureOutput(BaseModel):
    """Output from dynamic_pressure tool."""

    dynamic_pressure_pa: float
    dynamic_pressure_kpa: float
    velocity_m_s: float
    altitude_m: float
    density_kg_m3: float


class LiftCoefficientInput(BaseModel):
    """Input for lift_coefficient tool."""

    lift: float = Field(..., description="Lift force in Newtons")
    velocity: float = Field(..., gt=0, description="Velocity in m/s")
    altitude_m: float = Field(..., ge=0, le=25_000, description="Altitude in meters")
    reference_area: float = Field(..., gt=0, description="Reference area in m²")


class LiftCoefficientOutput(BaseModel):
    """Output from lift_coefficient tool."""

    lift_coefficient: float
    lift_n: float
    dynamic_pressure_pa: float
    reference_area_m2: float


class DragCoefficientInput(BaseModel):
    """Input for drag_coefficient tool."""

    drag: float = Field(..., description="Drag force in Newtons")
    velocity: float = Field(..., gt=0, description="Velocity in m/s")
    altitude_m: float = Field(..., ge=0, le=25_000, description="Altitude in meters")
    reference_area: float = Field(..., gt=0, description="Reference area in m²")


class DragCoefficientOutput(BaseModel):
    """Output from drag_coefficient tool."""

    drag_coefficient: float
    drag_n: float
    dynamic_pressure_pa: float
    reference_area_m2: float


class SkinFrictionInput(BaseModel):
    """Input for skin_friction_coefficient tool."""

    reynolds_number: float = Field(..., gt=0, description="Reynolds number")
    flow_regime: Literal["laminar", "turbulent"] = Field(
        default="laminar", description="Flow regime for correlation selection"
    )


class SkinFrictionOutput(BaseModel):
    """Output from skin_friction_coefficient tool."""

    skin_friction_coefficient: float
    reynolds_number: float
    flow_regime: str
    correlation: str


class AeroAnalysisInput(BaseModel):
    """Input for comprehensive aero_analysis tool."""

    velocity: float = Field(..., gt=0, description="Velocity in m/s")
    altitude_m: float = Field(..., ge=0, le=25_000, description="Altitude in meters")
    characteristic_length: float = Field(..., gt=0, description="Characteristic length in meters")
    reference_area: float = Field(..., gt=0, description="Reference area in m²")
    lift: float = Field(default=0.0, description="Lift force in Newtons (optional)")
    drag: float = Field(default=0.0, description="Drag force in Newtons (optional)")


class AeroAnalysisOutput(BaseModel):
    """Output from aero_analysis tool."""

    reynolds_number: float
    mach_number: float
    dynamic_pressure_pa: float
    dynamic_pressure_kpa: float
    flow_regime: str
    mach_regime: str
    lift_coefficient: float | None
    drag_coefficient: float | None
    lift_to_drag_ratio: float | None
    skin_friction_coefficient: float
    altitude_m: float
    velocity_m_s: float
    characteristic_length_m: float
    reference_area_m2: float


# ---- Compressible Flow ----


class IsentropicFlowInput(BaseModel):
    """Input for isentropic_flow tool."""

    mach: float = Field(..., gt=0, description="Mach number")
    gamma: float = Field(default=1.4, gt=1.0, description="Ratio of specific heats")


class NormalShockInput(BaseModel):
    """Input for normal_shock tool."""

    mach1: float = Field(..., gt=1.0, description="Upstream Mach number")
    gamma: float = Field(default=1.4, gt=1.0, description="Ratio of specific heats")


class ObliqueShockInput(BaseModel):
    """Input for oblique_shock tool."""

    mach1: float = Field(..., gt=1.0, description="Upstream Mach number")
    deflection_deg: float = Field(..., gt=0, lt=90, description="Flow deflection angle in degrees")
    gamma: float = Field(default=1.4, gt=1.0, description="Ratio of specific heats")


class PrandtlMeyerInput(BaseModel):
    """Input for prandtl_meyer tool."""

    mach: float = Field(..., ge=1.0, description="Mach number")
    gamma: float = Field(default=1.4, gt=1.0, description="Ratio of specific heats")


class PrandtlMeyerFromAngleInput(BaseModel):
    """Input for prandtl_meyer_from_angle tool."""

    angle_deg: float = Field(..., ge=0, description="Prandtl-Meyer angle in degrees")
    gamma: float = Field(default=1.4, gt=1.0, description="Ratio of specific heats")


# ---- Aircraft Aerodynamics ----


class LiftCurveSlopeInput(BaseModel):
    """Input for lift_curve_slope tool."""

    mach: float = Field(..., ge=0, description="Freestream Mach number")
    aspect_ratio: float = Field(..., gt=0, description="Wing aspect ratio")
    taper_ratio: float = Field(default=1.0, gt=0, description="Tip chord / root chord")
    sweep_deg: float = Field(default=0.0, description="Quarter-chord sweep in degrees")
    oswald_efficiency: float = Field(default=0.85, gt=0, le=1.0)


class DragPolarInput(BaseModel):
    """Input for drag_polar tool."""

    cl: float = Field(..., description="Lift coefficient")
    cd0: float = Field(..., ge=0, description="Zero-lift drag coefficient")
    aspect_ratio: float = Field(..., gt=0, description="Wing aspect ratio")
    oswald_efficiency: float = Field(default=0.85, gt=0, le=1.0)
    mach: float = Field(default=0.0, ge=0, description="Mach number")


class BreguetRangeInput(BaseModel):
    """Input for breguet_range tool."""

    lift_to_drag_ratio: float = Field(..., gt=0, description="L/D ratio")
    specific_fuel_consumption: float = Field(..., gt=0, description="SFC")
    velocity: float = Field(..., gt=0, description="True airspeed in m/s")
    initial_mass_kg: float = Field(..., gt=0, description="Initial mass in kg")
    final_mass_kg: float = Field(..., gt=0, description="Final mass in kg")


class BreguetEnduranceInput(BaseModel):
    """Input for breguet_endurance tool."""

    lift_to_drag_ratio: float = Field(..., gt=0, description="L/D ratio")
    specific_fuel_consumption: float = Field(..., gt=0, description="SFC")
    initial_mass_kg: float = Field(..., gt=0, description="Initial mass in kg")
    final_mass_kg: float = Field(..., gt=0, description="Final mass in kg")


class WingLoadingInput(BaseModel):
    """Input for wing_loading tool."""

    weight_n: float = Field(..., gt=0, description="Weight in Newtons")
    wing_area_m2: float = Field(..., gt=0, description="Wing area in m^2")


# ---- Nozzle / Inlet ----


class NozzlePerformanceInput(BaseModel):
    """Input for nozzle_performance tool."""

    chamber_pressure_pa: float = Field(..., gt=0, description="Chamber total pressure in Pa")
    chamber_temperature_k: float = Field(..., gt=0, description="Chamber total temperature in K")
    ambient_pressure_pa: float = Field(..., gt=0, description="Ambient pressure in Pa")
    throat_area_m2: float = Field(..., gt=0, description="Throat area in m^2")
    exit_area_m2: float = Field(..., gt=0, description="Exit area in m^2")
    gamma: float = Field(default=1.4, gt=1.0)
    molecular_weight: float = Field(default=28.97, gt=0, description="Molecular weight in kg/kmol")


class OptimalAreaRatioInput(BaseModel):
    """Input for optimal_area_ratio tool."""

    chamber_pressure_pa: float = Field(..., gt=0)
    ambient_pressure_pa: float = Field(..., gt=0)
    gamma: float = Field(default=1.4, gt=1.0)
