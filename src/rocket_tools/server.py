"""FastMCP server exposing aerospace engineering tools with Pydantic validation."""

from mcp.server.fastmcp import FastMCP

from rocket_tools.schemas import (
    AeroAnalysisInput,
    BreguetEnduranceInput,
    BreguetRangeInput,
    ColumnBucklingInput,
    CombinedMarginInput,
    CompositeCGInput,
    DeflectionMarginInput,
    DragCoefficientInput,
    DragPolarInput,
    DynamicPressureInput,
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
    OrbitalVelocityInput,
    PayloadFractionInput,
    PlateBucklingInput,
    PrandtlMeyerFromAngleInput,
    PrandtlMeyerInput,
    PropellantTankSizingInput,
    ReynoldsNumberInput,
    RocketDeltaVInput,
    SkinFrictionInput,
    ThrustToWeightInput,
    TrussAnalysisInput,
    UnitConvertInput,
    VonMisesInput,
    WingLoadingInput,
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
def list_materials() -> list[str]:
    """List available bundled aerospace materials."""
    from rocket_tools.materials import list_materials as _lm

    try:
        return _lm()
    except Exception as e:
        return _format_error(e)  # type: ignore[return-value]


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
