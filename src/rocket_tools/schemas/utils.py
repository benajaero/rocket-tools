"""Pydantic schemas for utility tools."""

from pydantic import BaseModel, Field


class UnitConvertInput(BaseModel):
    """Input for unit_convert tool."""

    value: float = Field(..., description="Value to convert")
    from_unit: str = Field(..., min_length=1, description="Source unit")
    to_unit: str = Field(..., min_length=1, description="Target unit")


class CiteToolInput(BaseModel):
    """Input for cite_tool provenance lookup."""

    tool_name: str = Field(
        ...,
        min_length=1,
        description="Name of the rocket-tools MCP tool to cite (e.g. 'normal_shock')",
    )


class PropagateUncertaintyInput(BaseModel):
    """Input for propagate_uncertainty tool."""

    tool_name: str = Field(
        ..., min_length=1, description="Computational tool to run under uncertainty"
    )
    params: dict = Field(
        ...,
        description=(
            "Tool inputs. Any value may be a fixed number OR a distribution dict: "
            '{"distribution":"normal","mean":M,"std":S}; '
            '{"distribution":"uniform","low":a,"high":b}; '
            '{"distribution":"lognormal","mean":M,"sigma":S}; '
            '{"distribution":"truncated_normal","mean":M,"std":S,"low":a,"high":b}'
        ),
    )
    samples: int = Field(default=1000, ge=10, le=100000, description="Monte-Carlo sample count")
    seed: int = Field(default=42, description="Random seed for reproducibility")
    sensitivity: bool = Field(
        default=True, description="Also rank inputs by correlation with each output"
    )


class UnitConvertOutput(BaseModel):
    """Output from unit_convert tool."""

    original_value: float
    original_unit: str
    converted_value: float
    converted_unit: str
    conversion_factor: float
