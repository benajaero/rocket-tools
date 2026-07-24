"""Pydantic schemas for aerodynamics tools."""

from typing import Literal

from pydantic import Field

from rocket_tools.schemas.base import StrictModel

# ---- Fundamental Aerodynamics ----


class ReynoldsNumberInput(StrictModel):
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


class ReynoldsNumberOutput(StrictModel):
    """Output from reynolds_number tool."""

    reynolds_number: float
    density_kg_m3: float
    dynamic_viscosity_pa_s: float
    velocity_m_s: float
    characteristic_length_m: float
    flow_regime: str


class MachNumberInput(StrictModel):
    """Input for mach_number tool."""

    velocity: float = Field(..., gt=0, description="Velocity in m/s")
    altitude_m: float = Field(..., ge=0, le=25_000, description="Altitude in meters")


class MachNumberOutput(StrictModel):
    """Output from mach_number tool."""

    mach_number: float
    velocity_m_s: float
    speed_of_sound_m_s: float
    altitude_m: float
    regime: str


class DynamicPressureInput(StrictModel):
    """Input for dynamic_pressure tool."""

    velocity: float = Field(..., gt=0, description="Velocity in m/s")
    altitude_m: float = Field(..., ge=0, le=25_000, description="Altitude in meters")


class DynamicPressureOutput(StrictModel):
    """Output from dynamic_pressure tool."""

    dynamic_pressure_pa: float
    dynamic_pressure_kpa: float
    velocity_m_s: float
    altitude_m: float
    density_kg_m3: float


class LiftCoefficientInput(StrictModel):
    """Input for lift_coefficient tool."""

    lift: float = Field(..., description="Lift force in Newtons")
    velocity: float = Field(..., gt=0, description="Velocity in m/s")
    altitude_m: float = Field(..., ge=0, le=25_000, description="Altitude in meters")
    reference_area: float = Field(..., gt=0, description="Reference area in m²")


class LiftCoefficientOutput(StrictModel):
    """Output from lift_coefficient tool."""

    lift_coefficient: float
    lift_n: float
    dynamic_pressure_pa: float
    reference_area_m2: float


class DragCoefficientInput(StrictModel):
    """Input for drag_coefficient tool."""

    drag: float = Field(..., description="Drag force in Newtons")
    velocity: float = Field(..., gt=0, description="Velocity in m/s")
    altitude_m: float = Field(..., ge=0, le=25_000, description="Altitude in meters")
    reference_area: float = Field(..., gt=0, description="Reference area in m²")


class DragCoefficientOutput(StrictModel):
    """Output from drag_coefficient tool."""

    drag_coefficient: float
    drag_n: float
    dynamic_pressure_pa: float
    reference_area_m2: float


class SkinFrictionInput(StrictModel):
    """Input for skin_friction_coefficient tool."""

    reynolds_number: float = Field(..., gt=0, description="Reynolds number")
    flow_regime: Literal["laminar", "transitional", "turbulent"] = Field(
        default="laminar", description="Flow regime for correlation selection"
    )


class SkinFrictionOutput(StrictModel):
    """Output from skin_friction_coefficient tool."""

    skin_friction_coefficient: float
    reynolds_number: float
    flow_regime: str
    correlation: str


class AeroAnalysisInput(StrictModel):
    """Input for comprehensive aero_analysis tool."""

    velocity: float = Field(..., gt=0, description="Velocity in m/s")
    altitude_m: float = Field(..., ge=0, le=25_000, description="Altitude in meters")
    characteristic_length: float = Field(..., gt=0, description="Characteristic length in meters")
    reference_area: float = Field(..., gt=0, description="Reference area in m²")
    lift: float = Field(default=0.0, description="Lift force in Newtons (optional)")
    drag: float = Field(default=0.0, description="Drag force in Newtons (optional)")


class AeroAnalysisOutput(StrictModel):
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


class IsentropicFlowInput(StrictModel):
    """Input for isentropic_flow tool."""

    mach: float = Field(..., gt=0, description="Mach number")
    gamma: float = Field(default=1.4, gt=1.0, description="Ratio of specific heats")


class NormalShockInput(StrictModel):
    """Input for normal_shock tool."""

    mach1: float = Field(..., gt=1.0, description="Upstream Mach number")
    gamma: float = Field(default=1.4, gt=1.0, description="Ratio of specific heats")


class ObliqueShockInput(StrictModel):
    """Input for oblique_shock tool."""

    mach1: float = Field(..., gt=1.0, description="Upstream Mach number")
    deflection_deg: float = Field(..., gt=0, lt=90, description="Flow deflection angle in degrees")
    gamma: float = Field(default=1.4, gt=1.0, description="Ratio of specific heats")


class PrandtlMeyerInput(StrictModel):
    """Input for prandtl_meyer tool."""

    mach: float = Field(..., ge=1.0, description="Mach number")
    gamma: float = Field(default=1.4, gt=1.0, description="Ratio of specific heats")


class PrandtlMeyerFromAngleInput(StrictModel):
    """Input for prandtl_meyer_from_angle tool."""

    angle_deg: float = Field(..., ge=0, description="Prandtl-Meyer angle in degrees")
    gamma: float = Field(default=1.4, gt=1.0, description="Ratio of specific heats")


# ---- Aircraft Aerodynamics ----


class LiftCurveSlopeInput(StrictModel):
    """Input for lift_curve_slope tool."""

    mach: float = Field(..., ge=0, description="Freestream Mach number")
    aspect_ratio: float = Field(..., gt=0, description="Wing aspect ratio")
    taper_ratio: float = Field(default=1.0, gt=0, description="Tip chord / root chord")
    sweep_deg: float = Field(default=0.0, description="Quarter-chord sweep in degrees")
    oswald_efficiency: float = Field(default=0.85, gt=0, le=1.0)


class DragPolarInput(StrictModel):
    """Input for drag_polar tool."""

    cl: float = Field(..., description="Lift coefficient")
    cd0: float = Field(..., ge=0, description="Zero-lift drag coefficient")
    aspect_ratio: float = Field(..., gt=0, description="Wing aspect ratio")
    oswald_efficiency: float = Field(default=0.85, gt=0, le=1.0)
    mach: float = Field(default=0.0, ge=0, description="Mach number")
    thickness_to_chord: float = Field(
        default=0.12, gt=0, lt=1.0, description="Airfoil thickness-to-chord ratio (for wave drag)"
    )
    sweep_deg: float = Field(default=0.0, ge=0, lt=90, description="Quarter-chord sweep in degrees")
    technology_factor: float = Field(
        default=0.87, gt=0, le=1.0, description="Korn kappa (0.87 conventional, 0.95 supercritical)"
    )


class BreguetRangeInput(StrictModel):
    """Input for breguet_range tool."""

    lift_to_drag_ratio: float = Field(..., gt=0, description="L/D ratio")
    specific_fuel_consumption: float = Field(..., gt=0, description="SFC")
    velocity: float = Field(..., gt=0, description="True airspeed in m/s")
    initial_mass_kg: float = Field(..., gt=0, description="Initial mass in kg")
    final_mass_kg: float = Field(..., gt=0, description="Final mass in kg")


class BreguetEnduranceInput(StrictModel):
    """Input for breguet_endurance tool."""

    lift_to_drag_ratio: float = Field(..., gt=0, description="L/D ratio")
    specific_fuel_consumption: float = Field(..., gt=0, description="SFC")
    initial_mass_kg: float = Field(..., gt=0, description="Initial mass in kg")
    final_mass_kg: float = Field(..., gt=0, description="Final mass in kg")


class WingLoadingInput(StrictModel):
    """Input for wing_loading tool."""

    weight_n: float = Field(..., gt=0, description="Weight in Newtons")
    wing_area_m2: float = Field(..., gt=0, description="Wing area in m^2")


# ---- Nozzle / Inlet ----


class NozzlePerformanceInput(StrictModel):
    """Input for nozzle_performance tool."""

    chamber_pressure_pa: float = Field(..., gt=0, description="Chamber total pressure in Pa")
    chamber_temperature_k: float = Field(..., gt=0, description="Chamber total temperature in K")
    ambient_pressure_pa: float = Field(..., gt=0, description="Ambient pressure in Pa")
    throat_area_m2: float = Field(..., gt=0, description="Throat area in m^2")
    exit_area_m2: float = Field(..., gt=0, description="Exit area in m^2")
    gamma: float = Field(default=1.4, gt=1.0)
    molecular_weight: float = Field(default=28.97, gt=0, description="Molecular weight in kg/kmol")


class OptimalAreaRatioInput(StrictModel):
    """Input for optimal_area_ratio tool."""

    chamber_pressure_pa: float = Field(..., gt=0)
    ambient_pressure_pa: float = Field(..., gt=0)
    gamma: float = Field(default=1.4, gt=1.0)


# ---- Aerothermodynamics ----


class StagnationTemperatureInput(StrictModel):
    """Input for stagnation_temperature tool."""

    static_temperature_k: float = Field(..., gt=0, description="Static (free-stream) temp in K")
    mach: float = Field(..., ge=0, description="Mach number")
    gamma: float = Field(default=1.4, gt=1.0, description="Ratio of specific heats")


class RecoveryTemperatureInput(StrictModel):
    """Input for recovery_temperature tool."""

    static_temperature_k: float = Field(..., gt=0, description="Static (free-stream) temp in K")
    mach: float = Field(..., ge=0, description="Mach number")
    gamma: float = Field(default=1.4, gt=1.0, description="Ratio of specific heats")
    prandtl: float = Field(default=0.71, gt=0, description="Prandtl number (air ~0.71)")
    regime: Literal["laminar", "turbulent"] = Field(
        default="laminar", description="Boundary-layer regime setting the recovery factor"
    )


class SuttonGravesInput(StrictModel):
    """Input for sutton_graves_heat_flux tool."""

    density_kg_m3: float = Field(..., gt=0, description="Free-stream density in kg/m^3")
    velocity_ms: float = Field(..., gt=0, description="Free-stream velocity in m/s")
    nose_radius_m: float = Field(..., gt=0, description="Effective nose radius in m")


class BallisticEntryInput(StrictModel):
    """Input for ballistic_entry_peak_deceleration tool."""

    entry_velocity_ms: float = Field(..., gt=0, description="Atmospheric-interface velocity in m/s")
    flight_path_angle_deg: float = Field(
        ..., gt=0, le=90, description="Entry flight-path angle below horizontal, degrees"
    )
    scale_height_m: float = Field(
        default=7160.0, gt=0, description="Atmospheric scale height in m (Earth ~7160)"
    )


# ---- Propulsion Thermochemistry ----


class CharacteristicVelocityInput(StrictModel):
    """Input for characteristic_velocity tool."""

    chamber_temperature_k: float = Field(..., gt=0, description="Chamber temperature in K")
    gamma: float = Field(default=1.2, gt=1.0, description="Ratio of specific heats of exhaust")
    molecular_weight: float = Field(
        default=22.0, gt=0, description="Exhaust molecular weight in kg/kmol"
    )


class IdealSpecificImpulseInput(StrictModel):
    """Input for ideal_specific_impulse tool."""

    chamber_temperature_k: float = Field(..., gt=0, description="Chamber temperature in K")
    pressure_ratio: float = Field(
        ..., gt=0, lt=1, description="Exit/chamber pressure ratio pe/pc, in (0, 1)"
    )
    gamma: float = Field(default=1.2, gt=1.0, description="Ratio of specific heats of exhaust")
    molecular_weight: float = Field(
        default=22.0, gt=0, description="Exhaust molecular weight in kg/kmol"
    )


class ThroatMassFluxInput(StrictModel):
    """Input for throat_mass_flux tool."""

    chamber_pressure_pa: float = Field(..., gt=0, description="Chamber total pressure in Pa")
    chamber_temperature_k: float = Field(..., gt=0, description="Chamber temperature in K")
    gamma: float = Field(default=1.2, gt=1.0, description="Ratio of specific heats of exhaust")
    molecular_weight: float = Field(
        default=22.0, gt=0, description="Exhaust molecular weight in kg/kmol"
    )
