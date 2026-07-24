"""Pydantic schemas for trajectory simulation and vehicle sizing tools."""

from typing import Literal

from pydantic import Field

from rocket_tools.schemas.base import StrictModel


class AscentSimInput(StrictModel):
    """Input for simulate_ascent tool."""

    initial_mass_kg: float = Field(..., gt=0, description="Gross liftoff mass in kg")
    dry_mass_kg: float = Field(..., gt=0, description="Burnout (dry) mass in kg; must be < initial")
    specific_impulse_s: float = Field(..., gt=0, description="Engine specific impulse in seconds")
    mass_flow_rate_kg_s: float = Field(..., gt=0, description="Propellant mass flow rate in kg/s")
    reference_area_m2: float = Field(..., gt=0, description="Aerodynamic reference area in m^2")
    drag_coefficient: float = Field(default=0.5, ge=0, description="Drag coefficient Cd")
    launch_angle_deg: float = Field(
        default=90.0, gt=0, le=90, description="Initial flight-path angle (90 = vertical)"
    )
    initial_altitude_m: float = Field(default=0.0, ge=0, description="Launch altitude in m")
    initial_velocity_ms: float = Field(default=0.0, ge=0, description="Initial speed in m/s")
    dt: float = Field(default=0.05, gt=0, le=5.0, description="Integration time step in s")
    max_time: float = Field(default=2000.0, gt=0, description="Max simulated time in s")
    include_drag: bool = Field(default=True, description="Include atmospheric drag")
    gravity_model: Literal["inverse_square", "constant"] = Field(
        default="inverse_square", description="Gravity model"
    )


class VehicleSizingInput(StrictModel):
    """Input for size_vehicle tool."""

    payload_mass_kg: float = Field(..., gt=0, description="Payload mass in kg")
    delta_v_target_ms: float = Field(..., gt=0, description="Mission delta-v target in m/s")
    specific_impulse_s: float = Field(..., gt=0, description="Engine specific impulse in seconds")
    inert_mass_fraction: float = Field(
        ..., gt=0, lt=1.0, description="Structural fraction epsilon = inert/(inert+propellant)"
    )
    thrust_to_weight_liftoff: float = Field(
        default=1.3, gt=0, description="Required liftoff thrust-to-weight ratio"
    )
    propellant_density_kg_m3: float = Field(
        default=1000.0, gt=0, description="Bulk propellant density in kg/m^3"
    )
