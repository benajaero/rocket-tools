"""Pydantic schemas for structural analysis tools."""

from typing import Literal

from pydantic import Field

from rocket_tools.schemas.base import StrictModel


class RectangleSection(StrictModel):
    """Rectangular cross-section for beam analysis."""

    type: Literal["rectangle"] = "rectangle"
    width: float = Field(..., gt=0, description="Width in meters")
    height: float = Field(..., gt=0, description="Height in meters")


class CircleSection(StrictModel):
    """Circular cross-section for beam analysis."""

    type: Literal["circle"] = "circle"
    diameter: float = Field(..., gt=0, description="Diameter in meters")


class BeamAnalysisInput(StrictModel):
    """Input parameters for beam_analysis tool."""

    load: float = Field(..., gt=0, description="Applied load in Newtons (N)")
    length: float = Field(..., gt=0, description="Beam span length in meters")
    youngs_modulus: float = Field(..., gt=0, description="Young's modulus in Pascals (Pa)")
    cross_section: RectangleSection | CircleSection = Field(
        ..., description="Cross-section geometry"
    )
    load_type: Literal["point_midspan", "point_tip", "distributed", "axial"] = Field(
        default="point_midspan",
        description="Type of loading applied to the beam",
    )
    support_type: Literal["simply_supported", "cantilever", "fixed_ends"] = Field(
        default="simply_supported",
        description="Support constraint type",
    )
    yield_strength: float | None = Field(
        default=None,
        gt=0,
        description="Optional material yield strength in Pa for yield safety factor",
    )


class BeamAnalysisOutput(StrictModel):
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
    effective_length_factor: float | None = None
    yield_strength_pa: float | None = None
    safety_factor_yield: float | None = None
    safety_factor_euler_buckling: float | None
    section_efficiency_m2: float
    load_type: str
    support_type: str


# ---- Section Properties ----


class SectionPropertiesInput(StrictModel):
    """Input for section_properties tool."""

    shape: Literal[
        "rectangle", "hollow_rectangle", "circle", "hollow_circle", "ibeam", "cchannel", "tsection"
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


class ColumnBucklingInput(StrictModel):
    """Input for column_buckling tool."""

    youngs_modulus: float = Field(..., gt=0, description="Young's modulus in Pa")
    area_moment: float = Field(..., gt=0, description="Area moment of inertia I in m^4")
    area: float = Field(..., gt=0, description="Cross-sectional area in m^2")
    length: float = Field(..., gt=0, description="Column length in m")
    yield_strength: float = Field(..., gt=0, description="Material yield strength in Pa")
    end_condition: Literal["pinned_pinned", "fixed_free", "fixed_pinned", "fixed_fixed"] = Field(
        default="pinned_pinned"
    )


# ---- Plate Buckling ----


class PlateBucklingInput(StrictModel):
    """Input for plate_buckling_coefficient tool."""

    aspect_ratio: float = Field(..., gt=0, description="Plate length / width")
    boundary_condition: Literal["simply_supported", "clamped", "free_edge"] = Field(
        default="simply_supported"
    )
    load_type: Literal["compression", "shear", "bending"] = Field(default="compression")


# ---- Margin of Safety ----


class MarginOfSafetyInput(StrictModel):
    """Input for margin_of_safety tool."""

    allowable_stress_pa: float | None = Field(None, gt=0)
    actual_stress_pa: float | None = Field(None, gt=0)
    allowable_load_n: float | None = Field(None, gt=0)
    actual_load_n: float | None = Field(None, gt=0)
    factor_of_safety: float = Field(default=1.5, gt=0)
    failure_mode: Literal["yield", "ultimate", "buckling", "fatigue", "custom"] = Field(
        default="yield"
    )


class VonMisesInput(StrictModel):
    """Input for von_mises_stress tool."""

    sigma_x: float
    sigma_y: float = 0.0
    tau_xy: float = 0.0
    sigma_z: float = 0.0
    tau_yz: float = 0.0
    tau_xz: float = 0.0


class CombinedMarginInput(StrictModel):
    """Input for combined_margin_of_safety tool."""

    sigma_x: float
    sigma_y: float = 0.0
    tau_xy: float = 0.0
    yield_strength_pa: float | None = Field(None, gt=0)
    ultimate_strength_pa: float | None = Field(None, gt=0)
    factor_of_safety_yield: float = Field(default=1.5, gt=0)
    factor_of_safety_ultimate: float = Field(default=1.5, gt=0)


class DeflectionMarginInput(StrictModel):
    """Input for deflection_margin tool."""

    actual_deflection_m: float = Field(..., ge=0)
    allowable_deflection_m: float | None = Field(None, gt=0)
    span_length_m: float | None = Field(None, gt=0)
    deflection_limit_ratio: float = Field(default=360.0, gt=0)


# ---- Truss Analysis ----


class TrussElementProperty(StrictModel):
    """Material and geometric properties for a truss element."""

    youngs_modulus_pa: float = Field(..., gt=0)
    area_m2: float = Field(..., gt=0)


class TrussConstraint(StrictModel):
    """Constraint (support) definition for a truss node."""

    node: int = Field(..., ge=0)
    fixed_dof: list[int] = Field(..., description="List of fixed DOF indices (0=x, 1=y, 2=z)")


class TrussLoad(StrictModel):
    """Load applied at a truss node."""

    node: int = Field(..., ge=0)
    force: list[float] = Field(..., description="Force vector [Fx, Fy] or [Fx, Fy, Fz]")


class TrussAnalysisInput(StrictModel):
    """Input for truss_analysis tool."""

    nodes: list[list[float]] = Field(..., min_length=2)
    elements: list[list[int]] = Field(..., min_length=1)
    element_properties: list[TrussElementProperty]
    constraints: list[TrussConstraint]
    loads: list[TrussLoad]


class ThermalStressInput(StrictModel):
    """Input for thermal_stress tool."""

    youngs_modulus_pa: float = Field(..., gt=0, description="Young's modulus E in Pa")
    cte_per_k: float = Field(..., description="Coefficient of thermal expansion alpha in 1/K")
    delta_temperature_k: float = Field(..., description="Temperature change dT in K")
    constraint_factor: float = Field(
        default=1.0, ge=0, le=1, description="Axial restraint fraction, 0 (free) to 1 (fixed)"
    )
    length_m: float | None = Field(default=None, gt=0, description="Member length in m (optional)")
    area_m2: float | None = Field(
        default=None, gt=0, description="Cross-sectional area in m^2 (optional)"
    )


class PressureVesselStressInput(StrictModel):
    """Input for pressure_vessel_stress tool."""

    internal_pressure_pa: float = Field(..., gt=0, description="Gauge internal pressure in Pa")
    inner_radius_m: float = Field(..., gt=0, description="Inner radius in m")
    wall_thickness_m: float = Field(..., gt=0, description="Wall thickness in m")
    geometry: Literal["cylinder", "sphere"] = Field(
        default="cylinder", description="Vessel geometry"
    )
    material_yield_pa: float | None = Field(
        default=None, gt=0, description="Yield strength in Pa (optional; enables margin)"
    )
