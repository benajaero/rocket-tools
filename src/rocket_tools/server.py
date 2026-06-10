"""FastMCP server exposing aerospace engineering tools."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("rocket-tools")


# ---- Utility Tools ----


@mcp.tool()
def unit_convert(value: float, from_unit: str, to_unit: str) -> dict:
    """Convert engineering units.

    Supports: m, mm, inch, ft, pa, kpa, mpa, psi, n, kn, lbf, c, k, f.
    """
    from rocket_tools.utils import unit_convert as _uc

    return _uc(value, from_unit, to_unit)


@mcp.tool()
def material_lookup(name: str, property_filter: str = "all") -> dict:
    """Look up aerospace material properties by name.

    Examples: 6061-T6, Ti-6Al-4V, 7075-T6, 4130, Inconel-718.
    """
    from rocket_tools.materials import material_lookup as _ml

    return _ml(name, property_filter)


@mcp.tool()
def isa_atmosphere(altitude_m: float) -> dict:
    """Get ISA atmosphere properties at a given altitude (0-25000 m)."""
    from rocket_tools.materials import isa_atmosphere as _isa

    return _isa(altitude_m)


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

    return _ba(load, length, youngs_modulus, cross_section, load_type, support_type)  # type: ignore[arg-type]


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

    kwargs = {
        "velocity": velocity,
        "characteristic_length": characteristic_length,
    }
    if density is not None:
        kwargs["density"] = density
    if dynamic_viscosity is not None:
        kwargs["dynamic_viscosity"] = dynamic_viscosity
    if altitude_m is not None:
        kwargs["altitude_m"] = altitude_m
    if temperature_k is not None:
        kwargs["temperature_k"] = temperature_k
    return _re(**kwargs)


@mcp.tool()
def mach_number(velocity: float, altitude_m: float) -> dict:
    """Compute Mach number at given altitude."""
    from rocket_tools.aerodynamics import mach_number as _ma

    return _ma(velocity, altitude_m)


@mcp.tool()
def dynamic_pressure(velocity: float, altitude_m: float) -> dict:
    """Compute dynamic pressure q = 0.5 * rho * V^2 at given altitude."""
    from rocket_tools.aerodynamics import dynamic_pressure as _q

    return _q(velocity, altitude_m)


@mcp.tool()
def lift_coefficient(
    lift: float, velocity: float, altitude_m: float, reference_area: float
) -> dict:
    """Compute lift coefficient CL = L / (q * S)."""
    from rocket_tools.aerodynamics import lift_coefficient as _cl

    return _cl(lift, velocity, altitude_m, reference_area)


@mcp.tool()
def drag_coefficient(
    drag: float, velocity: float, altitude_m: float, reference_area: float
) -> dict:
    """Compute drag coefficient CD = D / (q * S)."""
    from rocket_tools.aerodynamics import drag_coefficient as _cd

    return _cd(drag, velocity, altitude_m, reference_area)


@mcp.tool()
def skin_friction_coefficient(reynolds_number: float, flow_regime: str = "laminar") -> dict:
    """Compute skin friction coefficient using Blasius correlation."""
    from rocket_tools.aerodynamics import skin_friction_coefficient as _cf

    return _cf(reynolds_number, flow_regime)


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

    return _aa(velocity, altitude_m, characteristic_length, reference_area, lift, drag)


# ---- Server Entry Point ----


def main():
    mcp.run()


if __name__ == "__main__":
    main()
