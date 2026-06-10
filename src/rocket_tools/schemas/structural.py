"""Pydantic schemas for structural analysis tools."""

from typing import Literal

from pydantic import BaseModel, Field


class RectangleSection(BaseModel):
    """Rectangular cross-section for beam analysis."""

    type: Literal["rectangle"] = "rectangle"
    width: float = Field(..., gt=0, description="Width in meters")
    height: float = Field(..., gt=0, description="Height in meters")


class CircleSection(BaseModel):
    """Circular cross-section for beam analysis."""

    type: Literal["circle"] = "circle"
    diameter: float = Field(..., gt=0, description="Diameter in meters")


class BeamAnalysisInput(BaseModel):
    """Input parameters for beam_analysis tool."""

    load: float = Field(..., gt=0, description="Applied load in Newtons (N)")
    length: float = Field(..., gt=0, description="Beam span length in meters")
    youngs_modulus: float = Field(..., gt=0, description="Young's modulus in Pascals (Pa)")
    cross_section: RectangleSection | CircleSection = Field(
        ..., description="Cross-section geometry"
    )
    load_type: Literal["point_midspan", "distributed", "axial"] = Field(
        default="point_midspan",
        description="Type of loading applied to the beam",
    )
    support_type: Literal["simply_supported", "cantilever", "fixed_ends"] = Field(
        default="simply_supported",
        description="Support constraint type",
    )


class BeamAnalysisOutput(BaseModel):
    """Output from beam_analysis tool."""

    max_bending_moment_n_m: float
    max_deflection_m: float
    bending_stress_pa: float
    shear_stress_pa: float
    max_normal_stress_pa: float
    section_modulus_m3: float
    area_moment_m4: float
    cross_sectional_area_m2: float
    critical_buckling_load_n: float
    safety_factor_euler_buckling: float | None
    section_efficiency_m2: float
    load_type: str
    support_type: str


# ---- Section Properties ----


class SectionPropertiesInput(BaseModel):
    """Input for section_properties tool."""

    shape: Literal[
        "rectangle", "hollow_rectangle", "circle", "hollow_circle",
        "ibeam", "cchannel", "tsection"
    ] = Field(..., description="Cross-section shape type")
    width: float | None = Field(None, gt=0)
    height: float | None = Field(None, gt=0)
    diameter: float | None = Field(None, gt=0)
    wall_thickness: float | None = Field(None, gt=0)
    outer_diameter: float | None = Field(None, gt=0)
    inner_diameter: float | None = Field(None, gt=0)
    flange_width: float | None = Field(None, gt=0)
    flange_thickness: float | None = Field(None, gt=0)
    web_thickness: float | None = Field(None, gt=0)


# ---- Column Buckling ----


class ColumnBucklingInput(BaseModel):
    """Input for column_buckling tool."""

    youngs_modulus: float = Field(..., gt=0, description="Young's modulus in Pa")
    area_moment: float = Field(..., gt=0, description="Area moment of inertia I in m^4")
    area: float = Field(..., gt=0, description="Cross-sectional area in m^2")
    length: float = Field(..., gt=0, description="Column length in m")
    yield_strength: float = Field(..., gt=0, description="Material yield strength in Pa")
    end_condition: Literal[
        "pinned_pinned", "fixed_free", "fixed_pinned", "fixed_fixed"
    ] = Field(default="pinned_pinned")


# ---- Plate Buckling ----


class PlateBucklingInput(BaseModel):
    """Input for plate_buckling_coefficient tool."""

    aspect_ratio: float = Field(..., gt=0, description="Plate length / width")
    boundary_condition: Literal["simply_supported", "clamped", "free_edge"] = Field(
        default="simply_supported"
    )
    load_type: Literal["compression", "shear", "bending"] = Field(default="compression")
