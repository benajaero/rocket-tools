"""FastMCP server exposing aerospace engineering tools with Pydantic validation."""

from mcp.server.fastmcp import FastMCP

from rocket_tools.schemas import (
    AeroAnalysisInput,
    DragCoefficientInput,
    DynamicPressureInput,
    ISAAtmosphereInput,
    LiftCoefficientInput,
    MachNumberInput,
    MaterialLookupInput,
    ReynoldsNumberInput,
    SkinFrictionInput,
    UnitConvertInput,
)
from rocket_tools.schemas.structural import BeamAnalysisInput
from rocket_tools.utils.validation import ToolError

mcp = FastMCP("rocket-tools")


# ---- Structured Error Formatter ----


def _format_error(e: Exception) -> dict:
    """Format any exception into a structured MCP-compatible error response."""
    if isinstance(e, ToolError):
        return e.to_dict()
    return {
        "error": True,
        "error_code": "INTERNAL_ERROR",
        "message": str(e),
        "parameter": "",
        "constraint": "",
        "suggestion": (
            "Please check your inputs and try again. If the problem persists, report an issue."
        ),
    }


# ---- Utility Tools ----


@mcp.tool()
def unit_convert(value: float, from_unit: str, to_unit: str) -> dict:
    """Convert engineering units.

    Supports: m, mm, inch, ft, pa, kpa, mpa, psi, n, kn, lbf, c, k, f.
    """
    from rocket_tools.utils import unit_convert as _uc

    try:
        validated = UnitConvertInput(value=value, from_unit=from_unit, to_unit=to_unit)
        return _uc(validated.value, validated.from_unit, validated.to_unit)
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def material_lookup(name: str, property_filter: str = "all") -> dict:
    """Look up aerospace material properties by name.

    Examples: 6061-T6, Ti-6Al-4V, 7075-T6, 4130, Inconel-718.
    """
    from rocket_tools.materials import material_lookup as _ml

    try:
        validated = MaterialLookupInput(name=name, property_filter=property_filter)
        return _ml(validated.name, validated.property_filter)
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def isa_atmosphere(altitude_m: float) -> dict:
    """Get ISA atmosphere properties at a given altitude (0-25000 m)."""
    from rocket_tools.materials import isa_atmosphere as _isa

    try:
        validated = ISAAtmosphereInput(altitude_m=altitude_m)
        return _isa(validated.altitude_m)
    except Exception as e:
        return _format_error(e)


# ---- Structural Tools ----


@mcp.tool()
def beam_analysis(
    load: float,
    length: float,
    youngs_modulus: float,
    cross_section: dict,
    load_type: str = "point_midspan",
    support_type: str = "simply_supported",
) -> dict:
    """
    Analyze a beam under load.

    cross_section: {"type": "rectangle", "width": float, "height": float}
        or {"type": "circle", "diameter": float}
    load_type: "point_midspan", "distributed", "axial"
    support_type: "simply_supported", "cantilever", "fixed_ends"
    """
    from rocket_tools.structural import beam_analysis as _ba

    try:
        validated = BeamAnalysisInput(
            load=load,
            length=length,
            youngs_modulus=youngs_modulus,
            cross_section=cross_section,  # type: ignore[arg-type]
            load_type=load_type,  # type: ignore[arg-type]
            support_type=support_type,  # type: ignore[arg-type]
        )
        return _ba(
            validated.load,
            validated.length,
            validated.youngs_modulus,
            validated.cross_section.model_dump(),
            validated.load_type,
            validated.support_type,
        )
    except Exception as e:
        return _format_error(e)


# ---- Aerodynamics Tools ----


@mcp.tool()
def reynolds_number(
    velocity: float,
    characteristic_length: float,
    density: float | None = None,
    dynamic_viscosity: float | None = None,
    altitude_m: float | None = None,
    temperature_k: float | None = None,
) -> dict:
    """Compute Reynolds number. Provide (density + viscosity) or altitude_m or temperature_k."""
    from rocket_tools.aerodynamics import reynolds_number as _re

    try:
        validated = ReynoldsNumberInput(
            velocity=velocity,
            characteristic_length=characteristic_length,
            density=density,
            dynamic_viscosity=dynamic_viscosity,
            altitude_m=altitude_m,
            temperature_k=temperature_k,
        )
        kwargs = {
            "velocity": validated.velocity,
            "characteristic_length": validated.characteristic_length,
        }
        if validated.density is not None:
            kwargs["density"] = validated.density
        if validated.dynamic_viscosity is not None:
            kwargs["dynamic_viscosity"] = validated.dynamic_viscosity
        if validated.altitude_m is not None:
            kwargs["altitude_m"] = validated.altitude_m
        if validated.temperature_k is not None:
            kwargs["temperature_k"] = validated.temperature_k
        return _re(**kwargs)
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def mach_number(velocity: float, altitude_m: float) -> dict:
    """Compute Mach number at given altitude."""
    from rocket_tools.aerodynamics import mach_number as _ma

    try:
        validated = MachNumberInput(velocity=velocity, altitude_m=altitude_m)
        return _ma(validated.velocity, validated.altitude_m)
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def dynamic_pressure(velocity: float, altitude_m: float) -> dict:
    """Compute dynamic pressure q = 0.5 * rho * V^2 at given altitude."""
    from rocket_tools.aerodynamics import dynamic_pressure as _q

    try:
        validated = DynamicPressureInput(velocity=velocity, altitude_m=altitude_m)
        return _q(validated.velocity, validated.altitude_m)
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def lift_coefficient(
    lift: float, velocity: float, altitude_m: float, reference_area: float
) -> dict:
    """Compute lift coefficient CL = L / (q * S)."""
    from rocket_tools.aerodynamics import lift_coefficient as _cl

    try:
        validated = LiftCoefficientInput(
            lift=lift, velocity=velocity, altitude_m=altitude_m, reference_area=reference_area
        )
        return _cl(
            validated.lift,
            validated.velocity,
            validated.altitude_m,
            validated.reference_area,
        )
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def drag_coefficient(
    drag: float, velocity: float, altitude_m: float, reference_area: float
) -> dict:
    """Compute drag coefficient CD = D / (q * S)."""
    from rocket_tools.aerodynamics import drag_coefficient as _cd

    try:
        validated = DragCoefficientInput(
            drag=drag, velocity=velocity, altitude_m=altitude_m, reference_area=reference_area
        )
        return _cd(
            validated.drag,
            validated.velocity,
            validated.altitude_m,
            validated.reference_area,
        )
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def skin_friction_coefficient(reynolds_number: float, flow_regime: str = "laminar") -> dict:
    """Compute skin friction coefficient using Blasius correlation."""
    from rocket_tools.aerodynamics import skin_friction_coefficient as _cf

    try:
        validated = SkinFrictionInput(
            reynolds_number=reynolds_number,
            flow_regime=flow_regime,  # type: ignore[arg-type]
        )
        return _cf(validated.reynolds_number, validated.flow_regime)
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def aero_analysis(
    velocity: float,
    altitude_m: float,
    characteristic_length: float,
    reference_area: float,
    lift: float = 0.0,
    drag: float = 0.0,
) -> dict:
    """Comprehensive aerodynamic analysis (Re, Mach, q, CL, CD, Cf) in one call."""
    from rocket_tools.aerodynamics import aero_analysis as _aa

    try:
        validated = AeroAnalysisInput(
            velocity=velocity,
            altitude_m=altitude_m,
            characteristic_length=characteristic_length,
            reference_area=reference_area,
            lift=lift,
            drag=drag,
        )
        return _aa(
            validated.velocity,
            validated.altitude_m,
            validated.characteristic_length,
            validated.reference_area,
            validated.lift,
            validated.drag,
        )
    except Exception as e:
        return _format_error(e)


# ---- Server Entry Point ----


def main():
    mcp.run()


if __name__ == "__main__":
    main()
