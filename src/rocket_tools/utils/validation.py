"""Input validation with aerospace-specific constraints."""


class ValidationError(ValueError):
    """Structured validation error for MCP responses."""

    def __init__(self, message: str, parameter: str, constraint: str, suggestion: str = ""):
        self.parameter = parameter
        self.constraint = constraint
        self.suggestion = suggestion
        super().__init__(message)

    def to_dict(self) -> dict:
        return {
            "error": True,
            "error_type": "validation_error",
            "message": str(self),
            "parameter": self.parameter,
            "constraint": self.constraint,
            "suggestion": self.suggestion,
        }


def validate_positive(value: float, name: str) -> None:
    if value <= 0:
        raise ValidationError(
            f"{name} must be greater than 0. Received: {value}",
            parameter=name,
            constraint="> 0",
            suggestion=f"Check your units. {name} is typically positive.",
        )


def validate_non_negative(value: float, name: str) -> None:
    if value < 0:
        raise ValidationError(
            f"{name} must be non-negative. Received: {value}",
            parameter=name,
            constraint=">= 0",
        )


def validate_range(value: float, name: str, min_val: float, max_val: float) -> None:
    if value < min_val or value > max_val:
        raise ValidationError(
            f"{name} must be between {min_val} and {max_val}. Received: {value}",
            parameter=name,
            constraint=f"{min_val} <= {name} <= {max_val}",
        )
