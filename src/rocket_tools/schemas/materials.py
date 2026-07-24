"""Pydantic schemas for materials and atmosphere tools."""

from pydantic import Field

from rocket_tools.schemas.base import StrictModel


class MaterialLookupInput(StrictModel):
    """Input for material_lookup tool."""

    name: str = Field(..., min_length=1, description="Material name, e.g. 6061-T6")
    property_filter: str = Field(
        default="all",
        description=(
            "Filter to a specific property: "
            "youngs_modulus, density, yield_strength, ultimate_strength, poisson_ratio"
        ),
    )


class MaterialLookupOutput(StrictModel):
    """Output from material_lookup tool."""

    material_name: str
    youngs_modulus_gpa: float | None = None
    youngs_modulus_pa: float | None = None
    density_kg_m3: float | None = None
    yield_strength_mpa: float | None = None
    yield_strength_pa: float | None = None
    ultimate_strength_mpa: float | None = None
    ultimate_strength_pa: float | None = None
    poisson_ratio: float | None = None
    thermal_expansion_1_k: float | None = None
    thermal_conductivity_w_m_k: float | None = None
    specific_heat_j_kg_k: float | None = None
    source: str | None = None
    warning: str | None = None


class ISAAtmosphereInput(StrictModel):
    """Input for isa_atmosphere tool."""

    altitude_m: float = Field(
        ...,
        ge=0,
        le=84_852,
        description="Geopotential altitude in meters (0–84,852 m ≈ 0–86 km geometric)",
    )


class ISAAtmosphereOutput(StrictModel):
    """Output from isa_atmosphere tool."""

    altitude_m: float
    temperature_k: float
    temperature_c: float
    pressure_pa: float
    pressure_kpa: float
    density_kg_m3: float
    speed_of_sound_m_s: float
