"""Pydantic schemas for utility tools."""

from pydantic import BaseModel, Field


class UnitConvertInput(BaseModel):
    """Input for unit_convert tool."""

    value: float = Field(..., description="Value to convert")
    from_unit: str = Field(..., min_length=1, description="Source unit")
    to_unit: str = Field(..., min_length=1, description="Target unit")


class UnitConvertOutput(BaseModel):
    """Output from unit_convert tool."""

    original_value: float
    original_unit: str
    converted_value: float
    converted_unit: str
    conversion_factor: float
