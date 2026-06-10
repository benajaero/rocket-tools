"""Pydantic schemas for aerodynamics tools."""

from typing import Literal

from pydantic import BaseModel, Field


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
