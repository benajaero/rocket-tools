"""Input validation with aerospace-specific constraints and structured error codes."""


class ToolError(ValueError):
    """Structured validation error for MCP responses with error codes.

    Attributes:
        message: Human-readable error description
        error_code: Machine-readable error identifier (e.g., "INVALID_PARAMETER")
        parameter: Name of the parameter that failed validation
        constraint: Description of the violated constraint
        suggestion: Hint to the user on how to fix the error
    """

    def __init__(
        self,
        message: str,
        error_code: str = "VALIDATION_ERROR",
        parameter: str = "",
        constraint: str = "",
        suggestion: str = "",
    ):
        self.error_code = error_code
        self.parameter = parameter
        self.constraint = constraint
        self.suggestion = suggestion
        super().__init__(message)

    def to_dict(self) -> dict:
        return {
            "error": True,
            "error_code": self.error_code,
            "error_type": self.error_code.lower(),  # backwards compatibility
            "message": str(self),
            "parameter": self.parameter,
            "constraint": self.constraint,
            "suggestion": self.suggestion,
        }


# Backwards compatibility alias
ValidationError = ToolError


def validate_positive(value: float, name: str) -> None:
    if value <= 0:
        raise ToolError(
            f"{name} must be greater than 0. Received: {value}",
            error_code="INVALID_PARAMETER",
            parameter=name,
            constraint="> 0",
            suggestion=f"Check your units. {name} is typically positive.",
        )


def validate_non_negative(value: float, name: str) -> None:
    if value < 0:
        raise ToolError(
            f"{name} must be non-negative. Received: {value}",
            error_code="INVALID_PARAMETER",
            parameter=name,
            constraint=">= 0",
        )


def validate_range(value: float, name: str, min_val: float, max_val: float) -> None:
    if value < min_val or value > max_val:
        raise ToolError(
            f"{name} must be between {min_val} and {max_val}. Received: {value}",
            error_code="INVALID_PARAMETER",
            parameter=name,
            constraint=f"{min_val} <= {name} <= {max_val}",
            suggestion=f"Valid range: {min_val} to {max_val}",
        )
