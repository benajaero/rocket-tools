"""Pydantic schemas for visualization tools.

Every viz tool shares a ``render`` field selecting the dual-return contract
("data" = JSON dict with base64 PNG + series; "image" = native MCP image).
"""

from typing import Literal

from pydantic import Field

from rocket_tools.schemas.base import StrictModel

Render = Literal["data", "image"]


class BeamDiagramInput(StrictModel):
    """Input for plot_beam_diagrams tool."""

    load: float = Field(..., description="Applied load (N point, or N/m distributed)")
    length: float = Field(..., gt=0, description="Beam span length in m")
    youngs_modulus: float = Field(..., gt=0, description="Young's modulus E in Pa")
    cross_section: dict = Field(
        ..., description="Cross-section dict, e.g. {'type':'rectangle',...}"
    )
    load_type: Literal["point_midspan", "distributed"] = Field(default="point_midspan")
    support_type: Literal["simply_supported", "cantilever", "fixed_ends"] = Field(
        default="simply_supported"
    )
    render: Render = Field(default="data")
    output_path: str | None = Field(default=None, description="Optional path to write the PNG")


class DragPolarPlotInput(StrictModel):
    """Input for plot_drag_polar tool."""

    cd0: float = Field(..., ge=0, description="Zero-lift drag coefficient")
    aspect_ratio: float = Field(..., gt=0, description="Wing aspect ratio")
    oswald_efficiency: float = Field(default=0.85, gt=0, le=1.0)
    mach: float = Field(default=0.0, ge=0)
    cl_max: float = Field(default=1.5, gt=0, description="Max lift coefficient to sweep to")
    render: Render = Field(default="data")
    output_path: str | None = Field(default=None)


class NozzleContourInput(StrictModel):
    """Input for plot_nozzle_contour tool."""

    throat_radius_m: float = Field(..., gt=0, description="Throat radius in m")
    area_ratio: float = Field(..., ge=1.0, description="Exit-to-throat area ratio A_e/A*")
    half_angle_deg: float = Field(default=15.0, gt=0, lt=90, description="Divergent half angle")
    render: Render = Field(default="data")
    output_path: str | None = Field(default=None)


class ISAProfileInput(StrictModel):
    """Input for plot_isa_profile tool."""

    max_altitude_m: float = Field(default=84000.0, gt=0, le=84852.0)
    render: Render = Field(default="data")
    output_path: str | None = Field(default=None)


class TrajectoryPlotInput(StrictModel):
    """Input for plot_trajectory tool."""

    initial_mass_kg: float = Field(..., gt=0)
    dry_mass_kg: float = Field(..., gt=0)
    specific_impulse_s: float = Field(..., gt=0)
    mass_flow_rate_kg_s: float = Field(..., gt=0)
    reference_area_m2: float = Field(..., gt=0)
    drag_coefficient: float = Field(default=0.5, ge=0)
    launch_angle_deg: float = Field(default=90.0, gt=0, le=90)
    dt: float = Field(default=0.1, gt=0, le=5.0)
    render: Render = Field(default="data")
    output_path: str | None = Field(default=None)
