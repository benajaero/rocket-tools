"""Pydantic schemas for utility tools."""

from pydantic import Field

from rocket_tools.schemas.base import StrictModel


class UnitConvertInput(StrictModel):
    """Input for unit_convert tool."""

    value: float = Field(..., description="Value to convert")
    from_unit: str = Field(..., min_length=1, description="Source unit")
    to_unit: str = Field(..., min_length=1, description="Target unit")


class CiteToolInput(StrictModel):
    """Input for cite_tool provenance lookup."""

    tool_name: str = Field(
        ...,
        min_length=1,
        description="Name of the rocket-tools MCP tool to cite (e.g. 'normal_shock')",
    )


class PropagateUncertaintyInput(StrictModel):
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


class ValidateResultInput(StrictModel):
    """Input for validate_result self-check tool."""

    benchmark_name: str = Field(
        ...,
        min_length=1,
        description="Curated benchmark to check against (see list_validation_benchmarks)",
    )
    result: dict = Field(..., description="A tool's output dict to compare against the benchmark")


class ParameterSweepInput(StrictModel):
    """Input for parameter_sweep trade-study tool."""

    tool_name: str = Field(..., min_length=1, description="Computational tool to sweep")
    params: dict = Field(
        ..., description="Base inputs for the tool (the swept param is overridden)"
    )
    sweep_parameter: str = Field(..., min_length=1, description="Name of the input to vary")
    values: list[float] = Field(
        ..., min_length=1, max_length=1000, description="Values of sweep_parameter to evaluate"
    )


class UnitConvertOutput(StrictModel):
    """Output from unit_convert tool."""

    original_value: float
    original_unit: str
    converted_value: float
    converted_unit: str
    conversion_factor: float
