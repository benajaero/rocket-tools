"""Pydantic schemas for standards & reliability tools."""

from pydantic import Field

from rocket_tools.schemas.base import StrictModel


class DesignReviewItem(StrictModel):
    """One structural item in a design review."""

    name: str = Field(..., description="Item name")
    margin_of_safety: float | None = Field(
        default=None, description="Precomputed margin of safety (else give allowable+actual)"
    )
    allowable_stress_pa: float | None = Field(default=None, gt=0)
    actual_stress_pa: float | None = Field(default=None, gt=0)
    factor_of_safety: float = Field(default=1.5, gt=0)
    failure_mode: str = Field(default="yield")


class DesignReviewInput(StrictModel):
    """Input for design_review_report tool."""

    items: list[DesignReviewItem] = Field(..., min_length=1, description="Design items to roll up")
    min_acceptable_margin: float = Field(
        default=0.0, description="Margins below this flag an item as failing"
    )


class FMEAItem(StrictModel):
    """One failure mode with severity/occurrence/detection on 1-10 scales."""

    failure_mode: str = Field(..., description="The failure mode")
    function: str = Field(default="", description="Affected function/component")
    effect: str = Field(default="", description="Effect of the failure")
    cause: str = Field(default="", description="Root cause")
    severity: int = Field(..., ge=1, le=10)
    occurrence: int = Field(..., ge=1, le=10)
    detection: int = Field(..., ge=1, le=10)


class FMEAInput(StrictModel):
    """Input for fmea_report tool."""

    items: list[FMEAItem] = Field(..., min_length=1, description="Failure modes to score")
    rpn_threshold: int = Field(
        default=100, ge=1, le=1000, description="RPN at/above which an item is high priority"
    )
