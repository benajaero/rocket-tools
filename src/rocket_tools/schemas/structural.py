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
