"""Pydantic schemas for design and performance tools."""

from pydantic import Field

from rocket_tools.schemas.base import StrictModel

# ---- Rocket Performance ----


class RocketDeltaVInput(StrictModel):
    """Input for rocket_delta_v tool."""

    specific_impulse_s: float = Field(..., gt=0, description="Specific impulse in seconds")
    initial_mass_kg: float = Field(..., gt=0, description="Initial mass in kg")
    final_mass_kg: float = Field(..., gt=0, description="Final mass in kg")
    gravity: float = Field(default=9.80665, gt=0, description="Gravity in m/s^2")


class MultiStageDeltaVInput(StrictModel):
    """Input for multi_stage_delta_v tool."""

    stages: list[dict] = Field(..., description="List of stage dicts")
    gravity: float = Field(default=9.80665, gt=0)


class OrbitalVelocityInput(StrictModel):
    """Input for orbital_velocity tool."""

    altitude_m: float = Field(..., ge=0, description="Altitude in meters")
    body_radius_m: float = Field(default=6_371_000.0, gt=0)
    body_mass_kg: float = Field(default=5.972e24, gt=0)
    gravity_constant: float = Field(default=6.67430e-11, gt=0)


class PayloadFractionInput(StrictModel):
    """Input for payload_fraction tool."""

    delta_v_required_ms: float = Field(..., gt=0)
    specific_impulse_s: float = Field(..., gt=0)
    inert_mass_fraction: float = Field(..., ge=0, lt=1.0)
    gravity: float = Field(default=9.80665, gt=0)


class ThrustToWeightInput(StrictModel):
    """Input for thrust_to_weight tool."""

    thrust_n: float = Field(..., gt=0, description="Thrust in Newtons")
    mass_kg: float = Field(..., gt=0, description="Mass in kg")
    gravity: float = Field(default=9.80665, gt=0)


# ---- Orbital Mechanics ----


class HohmannTransferInput(StrictModel):
    """Input for hohmann_transfer tool."""

    radius1_m: float = Field(..., gt=0, description="Initial circular orbit radius in meters")
    radius2_m: float = Field(..., gt=0, description="Target circular orbit radius in meters")
    mu: float = Field(
        default=3.986004418e14, gt=0, description="Gravitational parameter GM in m^3/s^2 (Earth)"
    )


class VisVivaInput(StrictModel):
    """Input for vis_viva_velocity tool."""

    radius_m: float = Field(..., gt=0, description="Distance from the body center in meters")
    semi_major_axis_m: float = Field(
        ..., gt=0, description="Orbit semi-major axis in meters (equals radius for a circle)"
    )
    mu: float = Field(
        default=3.986004418e14, gt=0, description="Gravitational parameter in m^3/s^2"
    )


class PlaneChangeInput(StrictModel):
    """Input for plane_change_delta_v tool."""

    velocity_ms: float = Field(..., gt=0, description="Orbital speed at the maneuver point in m/s")
    inclination_change_deg: float = Field(
        ..., ge=0, le=180, description="Inclination change in degrees"
    )


class OrbitalPeriodInput(StrictModel):
    """Input for orbital_period tool."""

    semi_major_axis_m: float = Field(..., gt=0, description="Semi-major axis in meters")
    mu: float = Field(
        default=3.986004418e14, gt=0, description="Gravitational parameter in m^3/s^2"
    )


class LambertSolverInput(StrictModel):
    """Input for lambert_solver tool."""

    r1_m: list[float] = Field(
        ..., min_length=3, max_length=3, description="Initial position vector [x,y,z] in m"
    )
    r2_m: list[float] = Field(
        ..., min_length=3, max_length=3, description="Final position vector [x,y,z] in m"
    )
    time_of_flight_s: float = Field(..., gt=0, description="Transfer time in seconds")
    mu: float = Field(
        default=3.986004418e14, gt=0, description="Gravitational parameter in m^3/s^2"
    )
    prograde: bool = Field(default=True, description="True for prograde transfer, False retrograde")


class OrbitalElementsFromStateInput(StrictModel):
    """Input for orbital_elements_from_state tool."""

    position_m: list[float] = Field(
        ..., min_length=3, max_length=3, description="Inertial position vector [x,y,z] in m"
    )
    velocity_ms: list[float] = Field(
        ..., min_length=3, max_length=3, description="Inertial velocity vector [vx,vy,vz] in m/s"
    )
    mu: float = Field(
        default=3.986004418e14, gt=0, description="Gravitational parameter in m^3/s^2"
    )


class StateFromOrbitalElementsInput(StrictModel):
    """Input for state_from_orbital_elements tool."""

    semi_major_axis_m: float = Field(
        ..., description="Semi-major axis in m (negative for hyperbolic orbits)"
    )
    eccentricity: float = Field(..., ge=0, description="Eccentricity (>= 0; e == 1 unsupported)")
    inclination_deg: float = Field(..., ge=0, le=180, description="Inclination in degrees")
    raan_deg: float = Field(..., description="Right ascension of the ascending node in degrees")
    argument_of_perigee_deg: float = Field(..., description="Argument of perigee in degrees")
    true_anomaly_deg: float = Field(..., description="True anomaly in degrees")
    mu: float = Field(
        default=3.986004418e14, gt=0, description="Gravitational parameter in m^3/s^2"
    )


# ---- Mass Properties ----


class CompositeCGInput(StrictModel):
    """Input for composite_cg tool."""

    masses: list[float] = Field(..., description="Component masses in kg")
    positions: list[list[float]] = Field(..., description="Component positions [x, y, z] in m")
    inertias: list[list[float]] | None = Field(
        default=None,
        description="Optional per-component own inertia [Ixx,Iyy,Izz,Ixy,Ixz,Iyz] in kg.m^2",
    )


class PropellantTankSizingInput(StrictModel):
    """Input for propellant_tank_sizing tool."""

    propellant_volume_m3: float = Field(..., gt=0)
    ullage_fraction: float = Field(default=0.1, ge=0)
    tank_shape: str = Field(default="cylinder")
    aspect_ratio: float = Field(default=2.0, gt=0)
    wall_thickness_m: float = Field(default=0.003, gt=0)
    material_density_kg_m3: float = Field(default=2700.0, gt=0)
    design_pressure_pa: float | None = Field(
        default=None,
        gt=0,
        description="Max expected operating pressure; enables hoop-stress sizing",
    )
    material_yield_pa: float | None = Field(
        default=None, gt=0, description="Material yield strength for hoop-stress sizing"
    )
    safety_factor: float = Field(default=1.5, gt=0, description="Factor of safety on pressure")
