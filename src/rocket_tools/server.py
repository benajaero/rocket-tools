"""FastMCP server exposing aerospace engineering tools with Pydantic validation."""

from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError as PydanticValidationError

from rocket_tools.schemas import (
    AeroAnalysisInput,
    BallisticEntryInput,
    BreguetEnduranceInput,
    BreguetRangeInput,
    CharacteristicVelocityInput,
    ColumnBucklingInput,
    CombinedMarginInput,
    CompositeCGInput,
    DeflectionMarginInput,
    DragCoefficientInput,
    DragPolarInput,
    DynamicPressureInput,
    HohmannTransferInput,
    IdealSpecificImpulseInput,
    ISAAtmosphereInput,
    IsentropicFlowInput,
    LiftCoefficientInput,
    LiftCurveSlopeInput,
    MachNumberInput,
    MarginOfSafetyInput,
    MaterialLookupInput,
    MultiStageDeltaVInput,
    NormalShockInput,
    NozzlePerformanceInput,
    ObliqueShockInput,
    OptimalAreaRatioInput,
    OrbitalPeriodInput,
    OrbitalVelocityInput,
    PayloadFractionInput,
    PlaneChangeInput,
    PlateBucklingInput,
    PrandtlMeyerFromAngleInput,
    PrandtlMeyerInput,
    PropellantTankSizingInput,
    RecoveryTemperatureInput,
    ReynoldsNumberInput,
    RocketDeltaVInput,
    SkinFrictionInput,
    StagnationTemperatureInput,
    SuttonGravesInput,
    ThroatMassFluxInput,
    ThrustToWeightInput,
    TrussAnalysisInput,
    UnitConvertInput,
    VisVivaInput,
    VonMisesInput,
    WingLoadingInput,
)
from rocket_tools.schemas.structural import BeamAnalysisInput
from rocket_tools.utils.validation import ToolError

mcp = FastMCP("rocket-tools")


# ---- Structured Error Formatter ----
#
# Every tool returns the SAME error schema so an agent can branch on it reliably:
#   {error, error_code, error_type, message, parameter, constraint, suggestion}
# error_code is the machine identifier (INVALID_PARAMETER / INTERNAL_ERROR / ...);
# error_type is its lowercase form, kept for backwards compatibility.


def _format_pydantic_error(e: PydanticValidationError) -> dict:
    """Turn a Pydantic ValidationError into a clean, actionable structured error.

    An invalid argument is the agent's fault, not an internal fault, so it is
    reported as INVALID_PARAMETER with the offending field name(s) and constraint
    surfaced directly instead of a raw multi-line Pydantic dump.
    """
    errors = e.errors()
    parameters = [".".join(str(p) for p in err["loc"]) for err in errors]
    parameter = ", ".join(dict.fromkeys(parameters))  # de-duped, order-preserving
    constraint = "; ".join(f"{p}: {err['msg']}" for p, err in zip(parameters, errors))
    message = f"Invalid input for {parameter}: " + "; ".join(err["msg"] for err in errors)
    return {
        "error": True,
        "error_code": "INVALID_PARAMETER",
        "error_type": "invalid_parameter",
        "message": message,
        "parameter": parameter,
        "constraint": constraint,
        "suggestion": (
            f"Correct the '{parameter}' argument(s) and retry. "
            "Check units and allowed ranges in the tool description."
        ),
    }


def _format_error(e: Exception) -> dict:
    """Format any exception into a structured MCP-compatible error response."""
    if isinstance(e, ToolError):
        return e.to_dict()
    if isinstance(e, PydanticValidationError):
        return _format_pydantic_error(e)
    return {
        "error": True,
        "error_code": "INTERNAL_ERROR",
        "error_type": "internal_error",
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
def list_materials() -> list[str]:
    """List available bundled aerospace materials."""
    from rocket_tools.materials import list_materials as _lm

    try:
        return _lm()
    except Exception as e:
        return _format_error(e)  # type: ignore[return-value]


@mcp.tool()
def isa_atmosphere(altitude_m: float) -> dict:
    """Get ISA atmosphere properties (temperature, pressure, density, speed of sound).

    altitude_m is geopotential altitude, 0-84852 m (0-86 km geometric). Uses the
    full 7-layer U.S. Standard Atmosphere 1976 model.
    """
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
    yield_strength: float | None = None,
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
            yield_strength=yield_strength,
        )
        return _ba(
            validated.load,
            validated.length,
            validated.youngs_modulus,
            validated.cross_section.model_dump(),
            validated.load_type,
            validated.support_type,
            yield_strength=validated.yield_strength,
        )
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def section_properties(
    shape: str,
    width: float | None = None,
    height: float | None = None,
    diameter: float | None = None,
    wall_thickness: float | None = None,
    outer_diameter: float | None = None,
    inner_diameter: float | None = None,
    flange_width: float | None = None,
    flange_thickness: float | None = None,
    web_thickness: float | None = None,
) -> dict:
    """Compute cross-sectional properties for structural shapes.

    Shapes: rectangle, hollow_rectangle, circle, hollow_circle, ibeam, cchannel, tsection
    """
    from rocket_tools.structural import section_properties as _sp

    try:
        kwargs: dict[str, float | str] = {"shape": shape}
        for key, val in [
            ("width", width),
            ("height", height),
            ("diameter", diameter),
            ("wall_thickness", wall_thickness),
            ("outer_diameter", outer_diameter),
            ("inner_diameter", inner_diameter),
            ("flange_width", flange_width),
            ("flange_thickness", flange_thickness),
            ("web_thickness", web_thickness),
        ]:
            if val is not None:
                kwargs[key] = val
        return _sp(**kwargs)  # type: ignore[arg-type]
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def column_buckling(
    youngs_modulus: float,
    area_moment: float,
    area: float,
    length: float,
    yield_strength: float,
    end_condition: str = "pinned_pinned",
) -> dict:
    """Compute column buckling load using Euler-Johnson transition.

    end_condition: pinned_pinned, fixed_free, fixed_pinned, fixed_fixed
    """
    from rocket_tools.structural import column_buckling as _cb

    try:
        validated = ColumnBucklingInput(
            youngs_modulus=youngs_modulus,
            area_moment=area_moment,
            area=area,
            length=length,
            yield_strength=yield_strength,
            end_condition=end_condition,  # type: ignore[arg-type]
        )
        return _cb(
            validated.youngs_modulus,
            validated.area_moment,
            validated.area,
            validated.length,
            validated.yield_strength,
            validated.end_condition,
        )
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def plate_buckling_coefficient(
    aspect_ratio: float,
    boundary_condition: str = "simply_supported",
    load_type: str = "compression",
) -> dict:
    """Compute buckling coefficient k for flat rectangular plates.

    boundary_condition: simply_supported, clamped, free_edge
    load_type: compression, shear, bending
    """
    from rocket_tools.structural import plate_buckling_coefficient as _pb

    try:
        validated = PlateBucklingInput(
            aspect_ratio=aspect_ratio,
            boundary_condition=boundary_condition,  # type: ignore[arg-type]
            load_type=load_type,  # type: ignore[arg-type]
        )
        k = _pb(validated.aspect_ratio, validated.boundary_condition, validated.load_type)
        return {
            "buckling_coefficient_k": k,
            "aspect_ratio": validated.aspect_ratio,
            "boundary_condition": validated.boundary_condition,
            "load_type": validated.load_type,
        }
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def margin_of_safety(
    allowable_stress_pa: float | None = None,
    actual_stress_pa: float | None = None,
    allowable_load_n: float | None = None,
    actual_load_n: float | None = None,
    factor_of_safety: float = 1.5,
    failure_mode: str = "yield",
) -> dict:
    """Compute margin of safety for aerospace structural analysis.

    MS = (Allowable / (FOS * Actual)) - 1

    Provide either stress pair (allowable_stress_pa + actual_stress_pa)
    or load pair (allowable_load_n + actual_load_n), not both.

    failure_mode: yield, ultimate, buckling, fatigue, custom
    """
    from rocket_tools.structural import margin_of_safety as _ms

    try:
        validated = MarginOfSafetyInput(
            allowable_stress_pa=allowable_stress_pa,
            actual_stress_pa=actual_stress_pa,
            allowable_load_n=allowable_load_n,
            actual_load_n=actual_load_n,
            factor_of_safety=factor_of_safety,
            failure_mode=failure_mode,  # type: ignore[arg-type]
        )
        return _ms(
            allowable_stress_pa=validated.allowable_stress_pa,
            actual_stress_pa=validated.actual_stress_pa,
            allowable_load_n=validated.allowable_load_n,
            actual_load_n=validated.actual_load_n,
            factor_of_safety=validated.factor_of_safety,
            failure_mode=validated.failure_mode,
        )
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def von_mises_stress(
    sigma_x: float,
    sigma_y: float = 0.0,
    tau_xy: float = 0.0,
    sigma_z: float = 0.0,
    tau_yz: float = 0.0,
    tau_xz: float = 0.0,
) -> dict:
    """Compute von Mises equivalent stress and principal stresses.

    For plane stress, leave sigma_z, tau_yz, tau_xz as 0.
    """
    from rocket_tools.structural import von_mises_stress as _vm

    try:
        validated = VonMisesInput(
            sigma_x=sigma_x,
            sigma_y=sigma_y,
            tau_xy=tau_xy,
            sigma_z=sigma_z,
            tau_yz=tau_yz,
            tau_xz=tau_xz,
        )
        return _vm(
            validated.sigma_x,
            validated.sigma_y,
            validated.tau_xy,
            validated.sigma_z,
            validated.tau_yz,
            validated.tau_xz,
        )
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def combined_margin_of_safety(
    sigma_x: float,
    sigma_y: float = 0.0,
    tau_xy: float = 0.0,
    yield_strength_pa: float | None = None,
    ultimate_strength_pa: float | None = None,
    factor_of_safety_yield: float = 1.5,
    factor_of_safety_ultimate: float = 1.5,
) -> dict:
    """Compute margin of safety for combined stress state using von Mises.

    Checks both yield and ultimate margins if the corresponding strengths are provided.
    """
    from rocket_tools.structural import combined_margin_of_safety as _cms

    try:
        validated = CombinedMarginInput(
            sigma_x=sigma_x,
            sigma_y=sigma_y,
            tau_xy=tau_xy,
            yield_strength_pa=yield_strength_pa,
            ultimate_strength_pa=ultimate_strength_pa,
            factor_of_safety_yield=factor_of_safety_yield,
            factor_of_safety_ultimate=factor_of_safety_ultimate,
        )
        return _cms(
            sigma_x=validated.sigma_x,
            sigma_y=validated.sigma_y,
            tau_xy=validated.tau_xy,
            yield_strength_pa=validated.yield_strength_pa,
            ultimate_strength_pa=validated.ultimate_strength_pa,
            factor_of_safety_yield=validated.factor_of_safety_yield,
            factor_of_safety_ultimate=validated.factor_of_safety_ultimate,
        )
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def deflection_margin(
    actual_deflection_m: float,
    allowable_deflection_m: float | None = None,
    span_length_m: float | None = None,
    deflection_limit_ratio: float = 360.0,
) -> dict:
    """Compute margin of safety against deflection limits.

    Common limits: L/360 (general), L/500 (control surfaces), L/200 (frames).
    """
    from rocket_tools.structural import deflection_margin as _dm

    try:
        validated = DeflectionMarginInput(
            actual_deflection_m=actual_deflection_m,
            allowable_deflection_m=allowable_deflection_m,
            span_length_m=span_length_m,
            deflection_limit_ratio=deflection_limit_ratio,
        )
        return _dm(
            actual_deflection_m=validated.actual_deflection_m,
            allowable_deflection_m=validated.allowable_deflection_m,
            span_length_m=validated.span_length_m,
            deflection_limit_ratio=validated.deflection_limit_ratio,
        )
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def truss_analysis(
    nodes: list,
    elements: list,
    element_properties: list,
    constraints: list,
    loads: list,
) -> dict:
    """Analyze a pin-jointed truss using the direct stiffness method.

    nodes: List of [x, y] or [x, y, z] coordinates.
    elements: List of [node_i, node_j] pairs.
    element_properties: List of {"youngs_modulus_pa": float, "area_m2": float}.
    constraints: List of {"node": int, "fixed_dof": [0, 1]}.
    loads: List of {"node": int, "force": [Fx, Fy]}.
    """
    from rocket_tools.structural import truss_analysis as _ta

    try:
        validated = TrussAnalysisInput(
            nodes=nodes,
            elements=elements,
            element_properties=element_properties,
            constraints=constraints,
            loads=loads,
        )
        return _ta(
            nodes=validated.nodes,
            elements=validated.elements,
            element_properties=[p.model_dump() for p in validated.element_properties],
            constraints=[c.model_dump() for c in validated.constraints],
            loads=[load_item.model_dump() for load_item in validated.loads],
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


# ---- Compressible Flow Tools ----


@mcp.tool()
def isentropic_flow(mach: float, gamma: float = 1.4) -> dict:
    """Compute isentropic flow ratios (T/T0, P/P0, rho/rho0, A/A*) for given Mach number."""
    from rocket_tools.aerodynamics import isentropic_flow as _if

    try:
        validated = IsentropicFlowInput(mach=mach, gamma=gamma)
        return _if(validated.mach, validated.gamma)
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def normal_shock(mach1: float, gamma: float = 1.4) -> dict:
    """Compute normal shock relations for upstream Mach number > 1."""
    from rocket_tools.aerodynamics import normal_shock as _ns

    try:
        validated = NormalShockInput(mach1=mach1, gamma=gamma)
        return _ns(validated.mach1, validated.gamma)
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def oblique_shock(mach1: float, deflection_deg: float, gamma: float = 1.4) -> dict:
    """Compute oblique shock relations for upstream Mach and deflection angle."""
    from rocket_tools.aerodynamics import oblique_shock as _os

    try:
        validated = ObliqueShockInput(mach1=mach1, deflection_deg=deflection_deg, gamma=gamma)
        return _os(validated.mach1, validated.deflection_deg, validated.gamma)
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def prandtl_meyer(mach: float, gamma: float = 1.4) -> dict:
    """Compute Prandtl-Meyer expansion angle for Mach >= 1."""
    from rocket_tools.aerodynamics import prandtl_meyer as _pm

    try:
        validated = PrandtlMeyerInput(mach=mach, gamma=gamma)
        return _pm(validated.mach, validated.gamma)
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def prandtl_meyer_from_angle(angle_deg: float, gamma: float = 1.4) -> dict:
    """Compute Mach number from Prandtl-Meyer expansion angle."""
    from rocket_tools.aerodynamics import prandtl_meyer_from_angle as _pmfa

    try:
        validated = PrandtlMeyerFromAngleInput(angle_deg=angle_deg, gamma=gamma)
        return _pmfa(validated.angle_deg, validated.gamma)
    except Exception as e:
        return _format_error(e)


# ---- Aircraft Aerodynamics Tools ----


@mcp.tool()
def lift_curve_slope(
    mach: float,
    aspect_ratio: float,
    taper_ratio: float = 1.0,
    sweep_deg: float = 0.0,
    oswald_efficiency: float = 0.85,
) -> dict:
    """Compute 3D wing lift curve slope CL_alpha."""
    from rocket_tools.aerodynamics import lift_curve_slope as _lcs

    try:
        validated = LiftCurveSlopeInput(
            mach=mach,
            aspect_ratio=aspect_ratio,
            taper_ratio=taper_ratio,
            sweep_deg=sweep_deg,
            oswald_efficiency=oswald_efficiency,
        )
        return _lcs(
            validated.mach,
            validated.aspect_ratio,
            validated.taper_ratio,
            validated.sweep_deg,
            validated.oswald_efficiency,
        )
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def drag_polar(
    cl: float,
    cd0: float,
    aspect_ratio: float,
    oswald_efficiency: float = 0.85,
    mach: float = 0.0,
) -> dict:
    """Compute drag coefficient from drag polar equation CD = CD0 + K*CL^2."""
    from rocket_tools.aerodynamics import drag_polar as _dp

    try:
        validated = DragPolarInput(
            cl=cl,
            cd0=cd0,
            aspect_ratio=aspect_ratio,
            oswald_efficiency=oswald_efficiency,
            mach=mach,
        )
        return _dp(
            validated.cl,
            validated.cd0,
            validated.aspect_ratio,
            validated.oswald_efficiency,
            validated.mach,
        )
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def breguet_range(
    lift_to_drag_ratio: float,
    specific_fuel_consumption: float,
    velocity: float,
    initial_mass_kg: float,
    final_mass_kg: float,
) -> dict:
    """Compute aircraft range using Breguet range equation."""
    from rocket_tools.aerodynamics import breguet_range as _br

    try:
        validated = BreguetRangeInput(
            lift_to_drag_ratio=lift_to_drag_ratio,
            specific_fuel_consumption=specific_fuel_consumption,
            velocity=velocity,
            initial_mass_kg=initial_mass_kg,
            final_mass_kg=final_mass_kg,
        )
        return _br(
            validated.lift_to_drag_ratio,
            validated.specific_fuel_consumption,
            validated.velocity,
            validated.initial_mass_kg,
            validated.final_mass_kg,
        )
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def breguet_endurance(
    lift_to_drag_ratio: float,
    specific_fuel_consumption: float,
    initial_mass_kg: float,
    final_mass_kg: float,
) -> dict:
    """Compute aircraft endurance using Breguet endurance equation."""
    from rocket_tools.aerodynamics import breguet_endurance as _be

    try:
        validated = BreguetEnduranceInput(
            lift_to_drag_ratio=lift_to_drag_ratio,
            specific_fuel_consumption=specific_fuel_consumption,
            initial_mass_kg=initial_mass_kg,
            final_mass_kg=final_mass_kg,
        )
        return _be(
            validated.lift_to_drag_ratio,
            validated.specific_fuel_consumption,
            validated.initial_mass_kg,
            validated.final_mass_kg,
        )
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def wing_loading(weight_n: float, wing_area_m2: float) -> dict:
    """Compute wing loading and stall speed estimates."""
    from rocket_tools.aerodynamics import wing_loading as _wl

    try:
        validated = WingLoadingInput(weight_n=weight_n, wing_area_m2=wing_area_m2)
        return _wl(validated.weight_n, validated.wing_area_m2)
    except Exception as e:
        return _format_error(e)


# ---- Nozzle / Inlet Tools ----


@mcp.tool()
def nozzle_performance(
    chamber_pressure_pa: float,
    chamber_temperature_k: float,
    ambient_pressure_pa: float,
    throat_area_m2: float,
    exit_area_m2: float,
    gamma: float = 1.4,
    molecular_weight: float = 28.97,
) -> dict:
    """Analyze rocket nozzle performance (thrust, Isp, Cf, exit conditions)."""
    from rocket_tools.aerodynamics import nozzle_performance as _np

    try:
        validated = NozzlePerformanceInput(
            chamber_pressure_pa=chamber_pressure_pa,
            chamber_temperature_k=chamber_temperature_k,
            ambient_pressure_pa=ambient_pressure_pa,
            throat_area_m2=throat_area_m2,
            exit_area_m2=exit_area_m2,
            gamma=gamma,
            molecular_weight=molecular_weight,
        )
        return _np(
            validated.chamber_pressure_pa,
            validated.chamber_temperature_k,
            validated.ambient_pressure_pa,
            validated.throat_area_m2,
            validated.exit_area_m2,
            validated.gamma,
            validated.molecular_weight,
        )
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def optimal_area_ratio(
    chamber_pressure_pa: float, ambient_pressure_pa: float, gamma: float = 1.4
) -> dict:
    """Compute optimal nozzle area ratio for given pressure ratio."""
    from rocket_tools.aerodynamics import optimal_area_ratio as _oar

    try:
        validated = OptimalAreaRatioInput(
            chamber_pressure_pa=chamber_pressure_pa,
            ambient_pressure_pa=ambient_pressure_pa,
            gamma=gamma,
        )
        return _oar(
            validated.chamber_pressure_pa,
            validated.ambient_pressure_pa,
            validated.gamma,
        )
    except Exception as e:
        return _format_error(e)


# ---- Propulsion Thermochemistry Tools ----


@mcp.tool()
def characteristic_velocity(
    chamber_temperature_k: float, gamma: float = 1.2, molecular_weight: float = 22.0
) -> dict:
    """Characteristic velocity c* = sqrt(R*Tc)/Gamma (m/s), a propellant figure of merit.

    Geometry-free: measures how well the chamber converts propellant to throat
    mass flux (c* = p_c*A_t/mdot). gamma is exhaust ratio of specific heats,
    molecular_weight in kg/kmol. Typical c*: 1500-1800 (LOX/RP-1), ~2400 (LOX/LH2).
    """
    from rocket_tools.aerodynamics import characteristic_velocity as _cs

    try:
        validated = CharacteristicVelocityInput(
            chamber_temperature_k=chamber_temperature_k,
            gamma=gamma,
            molecular_weight=molecular_weight,
        )
        return _cs(validated.chamber_temperature_k, validated.gamma, validated.molecular_weight)
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def ideal_specific_impulse(
    chamber_temperature_k: float,
    pressure_ratio: float,
    gamma: float = 1.2,
    molecular_weight: float = 22.0,
) -> dict:
    """Ideal exhaust velocity and Isp from the exit/chamber pressure ratio.

    v_e = sqrt(2*g/(g-1)*R*Tc*(1-(pe/pc)^((g-1)/g))), Isp = v_e/g0. pressure_ratio
    is pe/pc in (0, 1); also returns the vacuum limit (pe/pc -> 0). Ideal (frozen,
    isentropic, 1-D) upper bound; real engines run a few percent below.
    """
    from rocket_tools.aerodynamics import ideal_specific_impulse as _isp

    try:
        validated = IdealSpecificImpulseInput(
            chamber_temperature_k=chamber_temperature_k,
            pressure_ratio=pressure_ratio,
            gamma=gamma,
            molecular_weight=molecular_weight,
        )
        return _isp(
            validated.chamber_temperature_k,
            validated.pressure_ratio,
            validated.gamma,
            validated.molecular_weight,
        )
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def throat_mass_flux(
    chamber_pressure_pa: float,
    chamber_temperature_k: float,
    gamma: float = 1.2,
    molecular_weight: float = 22.0,
) -> dict:
    """Choked mass flux mdot/At = pc*Gamma/sqrt(R*Tc), in kg/(s*m^2).

    Multiply by throat area to get the ideal choked mass flow. gamma is exhaust
    ratio of specific heats, molecular_weight in kg/kmol.
    """
    from rocket_tools.aerodynamics import throat_mass_flux as _tmf

    try:
        validated = ThroatMassFluxInput(
            chamber_pressure_pa=chamber_pressure_pa,
            chamber_temperature_k=chamber_temperature_k,
            gamma=gamma,
            molecular_weight=molecular_weight,
        )
        return _tmf(
            validated.chamber_pressure_pa,
            validated.chamber_temperature_k,
            validated.gamma,
            validated.molecular_weight,
        )
    except Exception as e:
        return _format_error(e)


# ---- Aerothermodynamics Tools ----


@mcp.tool()
def stagnation_temperature(static_temperature_k: float, mach: float, gamma: float = 1.4) -> dict:
    """Total (stagnation) temperature of an adiabatic compressible flow.

    T0 = T*(1 + (gamma-1)/2*M^2). The insulated-stagnation ceiling; a real wall
    sees the lower recovery_temperature. static_temperature_k in K, mach >= 0.
    """
    from rocket_tools.aerodynamics import stagnation_temperature as _st

    try:
        validated = StagnationTemperatureInput(
            static_temperature_k=static_temperature_k, mach=mach, gamma=gamma
        )
        return _st(validated.static_temperature_k, validated.mach, validated.gamma)
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def recovery_temperature(
    static_temperature_k: float,
    mach: float,
    gamma: float = 1.4,
    prandtl: float = 0.71,
    regime: str = "laminar",
) -> dict:
    """Adiabatic-wall (recovery) temperature: Tr = T*(1 + r*(gamma-1)/2*M^2).

    Recovery factor r = Pr^0.5 (laminar) or Pr^(1/3) (turbulent); air Pr ~ 0.71.
    regime is "laminar" or "turbulent".
    """
    from rocket_tools.aerodynamics import recovery_temperature as _rt

    try:
        validated = RecoveryTemperatureInput(
            static_temperature_k=static_temperature_k,
            mach=mach,
            gamma=gamma,
            prandtl=prandtl,
            regime=regime,  # type: ignore[arg-type]
        )
        return _rt(
            validated.static_temperature_k,
            validated.mach,
            validated.gamma,
            validated.prandtl,
            validated.regime,
        )
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def sutton_graves_heat_flux(density_kg_m3: float, velocity_ms: float, nose_radius_m: float) -> dict:
    """Stagnation-point convective heat flux for Earth entry (Sutton-Graves).

    q = 1.7415e-4*sqrt(rho/Rn)*V^3, result in W/m^2 (also returned as W/cm^2 and
    MW/m^2). Cold-wall convective estimate for a blunt body; excludes radiation.
    """
    from rocket_tools.aerodynamics import sutton_graves_heat_flux as _sg

    try:
        validated = SuttonGravesInput(
            density_kg_m3=density_kg_m3, velocity_ms=velocity_ms, nose_radius_m=nose_radius_m
        )
        return _sg(validated.density_kg_m3, validated.velocity_ms, validated.nose_radius_m)
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def ballistic_entry_peak_deceleration(
    entry_velocity_ms: float, flight_path_angle_deg: float, scale_height_m: float = 7160.0
) -> dict:
    """Peak deceleration of a steep non-lifting entry (Allen-Eggers, NACA TR 1381).

    a_max = V_e^2*sin(gamma)/(2*e*H), independent of ballistic coefficient; peak
    always occurs at V = V_e/sqrt(e). flight_path_angle_deg is below horizontal,
    (0, 90]; scale_height_m defaults to Earth ~7160 m.
    """
    from rocket_tools.aerodynamics import ballistic_entry_peak_deceleration as _be

    try:
        validated = BallisticEntryInput(
            entry_velocity_ms=entry_velocity_ms,
            flight_path_angle_deg=flight_path_angle_deg,
            scale_height_m=scale_height_m,
        )
        return _be(
            validated.entry_velocity_ms,
            validated.flight_path_angle_deg,
            validated.scale_height_m,
        )
    except Exception as e:
        return _format_error(e)


# ---- Design Tools ----


@mcp.tool()
def rocket_delta_v(
    specific_impulse_s: float,
    initial_mass_kg: float,
    final_mass_kg: float,
    gravity: float = 9.80665,
) -> dict:
    """Compute rocket delta-v using Tsiolkovsky equation."""
    from rocket_tools.design import rocket_delta_v as _rdv

    try:
        validated = RocketDeltaVInput(
            specific_impulse_s=specific_impulse_s,
            initial_mass_kg=initial_mass_kg,
            final_mass_kg=final_mass_kg,
            gravity=gravity,
        )
        return _rdv(
            validated.specific_impulse_s,
            validated.initial_mass_kg,
            validated.final_mass_kg,
            validated.gravity,
        )
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def multi_stage_delta_v(stages: list[dict], gravity: float = 9.80665) -> dict:
    """Compute total delta-v for multi-stage rocket."""
    from rocket_tools.design import multi_stage_delta_v as _msdv

    try:
        validated = MultiStageDeltaVInput(stages=stages, gravity=gravity)
        return _msdv(validated.stages, validated.gravity)
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def orbital_velocity(
    altitude_m: float,
    body_radius_m: float = 6_371_000.0,
    body_mass_kg: float = 5.972e24,
    gravity_constant: float = 6.67430e-11,
) -> dict:
    """Compute circular orbital velocity at given altitude."""
    from rocket_tools.design import orbital_velocity as _ov

    try:
        validated = OrbitalVelocityInput(
            altitude_m=altitude_m,
            body_radius_m=body_radius_m,
            body_mass_kg=body_mass_kg,
            gravity_constant=gravity_constant,
        )
        return _ov(
            validated.altitude_m,
            validated.body_radius_m,
            validated.body_mass_kg,
            validated.gravity_constant,
        )
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def hohmann_transfer(radius1_m: float, radius2_m: float, mu: float = 3.986004418e14) -> dict:
    """Two-impulse Hohmann transfer between coplanar circular orbits.

    radius1_m/radius2_m: orbital radii (body center to orbit) in meters, NOT altitude.
    mu: gravitational parameter GM in m^3/s^2 (default Earth 3.986004418e14).
    Returns delta_v1_ms, delta_v2_ms, total_delta_v_ms/_kms, and transfer_time_s/_hr.
    """
    from rocket_tools.design import hohmann_transfer as _ht

    try:
        validated = HohmannTransferInput(radius1_m=radius1_m, radius2_m=radius2_m, mu=mu)
        return _ht(validated.radius1_m, validated.radius2_m, validated.mu)
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def vis_viva_velocity(
    radius_m: float, semi_major_axis_m: float, mu: float = 3.986004418e14
) -> dict:
    """Orbital speed at a radius via the vis-viva equation v = sqrt(mu*(2/r - 1/a)).

    radius_m: distance from the body center in meters. semi_major_axis_m: orbit
    semi-major axis in meters (equals radius_m for a circular orbit). Returns
    velocity_ms and velocity_kms.
    """
    from rocket_tools.design import vis_viva_velocity as _vv

    try:
        validated = VisVivaInput(radius_m=radius_m, semi_major_axis_m=semi_major_axis_m, mu=mu)
        return _vv(validated.radius_m, validated.semi_major_axis_m, validated.mu)
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def plane_change_delta_v(velocity_ms: float, inclination_change_deg: float) -> dict:
    """Delta-v for a simple plane change: delta_v = 2*v*sin(delta_i/2).

    velocity_ms: orbital speed at the maneuver point. inclination_change_deg in
    [0, 180]. Cheapest where orbital speed is lowest (near apoapsis).
    """
    from rocket_tools.design import plane_change_delta_v as _pc

    try:
        validated = PlaneChangeInput(
            velocity_ms=velocity_ms, inclination_change_deg=inclination_change_deg
        )
        return _pc(validated.velocity_ms, validated.inclination_change_deg)
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def orbital_period(semi_major_axis_m: float, mu: float = 3.986004418e14) -> dict:
    """Keplerian orbital period T = 2*pi*sqrt(a^3/mu).

    semi_major_axis_m in meters; mu in m^3/s^2 (default Earth). Returns
    period_s, period_min, period_hr.
    """
    from rocket_tools.design import orbital_period as _op

    try:
        validated = OrbitalPeriodInput(semi_major_axis_m=semi_major_axis_m, mu=mu)
        return _op(validated.semi_major_axis_m, validated.mu)
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def payload_fraction(
    delta_v_required_ms: float,
    specific_impulse_s: float,
    inert_mass_fraction: float,
    gravity: float = 9.80665,
) -> dict:
    """Estimate payload mass fraction for given mission requirements."""
    from rocket_tools.design import payload_fraction as _pf

    try:
        validated = PayloadFractionInput(
            delta_v_required_ms=delta_v_required_ms,
            specific_impulse_s=specific_impulse_s,
            inert_mass_fraction=inert_mass_fraction,
            gravity=gravity,
        )
        return _pf(
            validated.delta_v_required_ms,
            validated.specific_impulse_s,
            validated.inert_mass_fraction,
            validated.gravity,
        )
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def thrust_to_weight(thrust_n: float, mass_kg: float, gravity: float = 9.80665) -> dict:
    """Compute thrust-to-weight ratio."""
    from rocket_tools.design import thrust_to_weight as _ttw

    try:
        validated = ThrustToWeightInput(thrust_n=thrust_n, mass_kg=mass_kg, gravity=gravity)
        return _ttw(validated.thrust_n, validated.mass_kg, validated.gravity)
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def composite_cg(masses: list[float], positions: list[list[float]]) -> dict:
    """Compute center of gravity and mass moments for composite body."""
    from rocket_tools.design import composite_cg as _ccg

    try:
        validated = CompositeCGInput(masses=masses, positions=positions)
        return _ccg(validated.masses, validated.positions)
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def propellant_tank_sizing(
    propellant_volume_m3: float,
    ullage_fraction: float = 0.1,
    tank_shape: str = "cylinder",
    aspect_ratio: float = 2.0,
    wall_thickness_m: float = 0.003,
    material_density_kg_m3: float = 2700.0,
) -> dict:
    """Size propellant tank and estimate mass."""
    from rocket_tools.design import propellant_tank_sizing as _pts

    try:
        validated = PropellantTankSizingInput(
            propellant_volume_m3=propellant_volume_m3,
            ullage_fraction=ullage_fraction,
            tank_shape=tank_shape,
            aspect_ratio=aspect_ratio,
            wall_thickness_m=wall_thickness_m,
            material_density_kg_m3=material_density_kg_m3,
        )
        return _pts(
            validated.propellant_volume_m3,
            validated.ullage_fraction,
            validated.tank_shape,
            validated.aspect_ratio,
            validated.wall_thickness_m,
            validated.material_density_kg_m3,
        )
    except Exception as e:
        return _format_error(e)


# ---- Server Entry Point ----


def main():
    mcp.run()


if __name__ == "__main__":
    main()
