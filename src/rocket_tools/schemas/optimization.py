"""Pydantic schemas for optimization tools."""

from typing import Literal

from pydantic import Field

from rocket_tools.schemas.base import StrictModel


class StagingOptimizerInput(StrictModel):
    """Input for optimize_staging tool."""

    delta_v_target_ms: float = Field(..., gt=0, description="Total mission delta-v target in m/s")
    stages: list[dict] = Field(
        ..., min_length=1, description="Per-stage {specific_impulse_s, structural_ratio}"
    )
    payload_mass_kg: float = Field(default=1.0, gt=0, description="Payload mass in kg")
    gravity: float = Field(default=9.80665, gt=0, description="g0 in m/s^2 for c = Isp*g0")


class DesignOptimizerInput(StrictModel):
    """Input for optimize_design tool."""

    tool_name: str = Field(..., description="A computational tool in the dispatch registry")
    fixed_params: dict = Field(..., description="The tool's other arguments held constant")
    variable: str = Field(..., description="Name of the input to vary")
    bounds: list[float] = Field(..., min_length=2, max_length=2, description="[low, high]")
    objective_key: str = Field(..., description="Output-dict key to optimize")
    sense: Literal["max", "min"] = Field(default="max")
    iterations: int = Field(default=40, ge=1, le=200, description="Golden-section iterations")
