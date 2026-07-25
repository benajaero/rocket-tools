"""FastMCP server exposing aerospace engineering tools with Pydantic validation."""

from typing import Literal

from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError as PydanticValidationError

from rocket_tools.schemas import (
    AeroAnalysisInput,
    AscentSimInput,
    BallisticEntryInput,
    BeamDiagramInput,
    BreguetEnduranceInput,
    BreguetRangeInput,
    CenterOfPressureInput,
    CharacteristicVelocityInput,
    CiteToolInput,
    ColumnBucklingInput,
    CombinedMarginInput,
    CompositeCGInput,
    DeflectionMarginInput,
    DesignOptimizerInput,
    DesignReviewInput,
    DragCoefficientInput,
    DragPolarInput,
    DragPolarPlotInput,
    DynamicPressureInput,
    FMEAInput,
    HohmannTransferInput,
    IdealSpecificImpulseInput,
    ISAAtmosphereInput,
    ISAProfileInput,
    IsentropicFlowInput,
    LambertSolverInput,
    LiftCoefficientInput,
    LiftCurveSlopeInput,
    MachNumberInput,
    MarginOfSafetyInput,
    MaterialLookupInput,
    MultiStageDeltaVInput,
    NormalShockInput,
    NozzleContourInput,
    NozzlePerformanceInput,
    ObliqueShockInput,
    OptimalAreaRatioInput,
    OrbitalElementsFromStateInput,
    OrbitalPeriodInput,
    OrbitalVelocityInput,
    ParachuteAreaInput,
    ParachuteDescentInput,
    ParameterSweepInput,
    PayloadFractionInput,
    PlaneChangeInput,
    PlateBucklingInput,
    PrandtlMeyerFromAngleInput,
    PrandtlMeyerInput,
    PropagateUncertaintyInput,
    PropellantTankSizingInput,
    RecoveryTemperatureInput,
    ReynoldsNumberInput,
    RocketDeltaVInput,
    SkinFrictionInput,
    StagingOptimizerInput,
    StagnationTemperatureInput,
    StaticMarginInput,
    SuttonGravesInput,
    ThroatMassFluxInput,
    ThrustToWeightInput,
    TrajectoryPlotInput,
    TrussAnalysisInput,
    UnitConvertInput,
    ValidateResultInput,
    VehicleSizingInput,
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


# ---- Research / Provenance Tools ----


@mcp.tool()
def cite_tool(tool_name: str) -> dict:
    """Provenance for a rocket-tools computation, for citing or auditing a result.

    Given a tool name (e.g. "normal_shock"), returns its authoritative reference(s),
    governing formula, modelling assumptions, and any curated validation benchmark(s)
    that pin it to published values (with a `validated` flag). Use this to defend or
    trace any number the server produces. Call `list_references` for the full bibliography.
    """
    from rocket_tools.provenance import get_provenance

    try:
        validated = CiteToolInput(tool_name=tool_name)
        return get_provenance(validated.tool_name)
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def propagate_uncertainty(
    tool_name: str,
    params: dict,
    samples: int = 1000,
    seed: int = 42,
    sensitivity: bool = True,
) -> dict:
    """Monte-Carlo uncertainty propagation and sensitivity ranking for any tool.

    Run `tool_name` many times with uncertain inputs and report each output's
    mean, std, min, max, and 95% CI, plus a sensitivity ranking of which inputs
    drive each output (Pearson correlation).

    `params` maps the tool's arguments to fixed numbers or distribution dicts:
    {"distribution":"normal","mean":M,"std":S}; "uniform" with low/high;
    "lognormal" with mean/sigma; "truncated_normal" with mean/std/low/high.
    Example: propagate_uncertainty("rocket_delta_v",
      {"specific_impulse_s":{"distribution":"normal","mean":320,"std":5},
       "initial_mass_kg":10000, "final_mass_kg":2000}).
    """
    from rocket_tools.uncertainty import run_with_uncertainty

    try:
        validated = PropagateUncertaintyInput(
            tool_name=tool_name,
            params=params,
            samples=samples,
            seed=seed,
            sensitivity=sensitivity,
        )
        return run_with_uncertainty(
            validated.tool_name,
            validated.params,
            validated.samples,
            validated.seed,
            validated.sensitivity,
        )
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def list_validation_benchmarks() -> dict:
    """List curated validation benchmarks available for self-checking a result.

    Each entry gives the benchmark name, the tool it validates, its inputs, and
    the authoritative reference. Pass a name and your tool output to `validate_result`.
    """
    from rocket_tools.validation import get_benchmark, list_benchmarks

    try:
        benchmarks = []
        for name in list_benchmarks():
            bm = get_benchmark(name)
            benchmarks.append(
                {
                    "name": name,
                    "tool_name": bm["tool_name"],
                    "inputs": bm["inputs"],
                    "reference": bm["reference"],
                }
            )
        return {"benchmarks": benchmarks, "count": len(benchmarks)}
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def validate_result(benchmark_name: str, result: dict) -> dict:
    """Check a computed result against a curated, reference-backed benchmark.

    Given a benchmark name (from `list_validation_benchmarks`) and a tool's output
    dict, returns whether each expected value is within tolerance, the per-key
    errors, and the authoritative reference. Use it to self-verify a number.
    """
    from rocket_tools.validation import validate_benchmark

    try:
        validated = ValidateResultInput(benchmark_name=benchmark_name, result=result)
        return validate_benchmark(validated.benchmark_name, validated.result)
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def parameter_sweep(
    tool_name: str, params: dict, sweep_parameter: str, values: list[float]
) -> dict:
    """Trade study: run a tool across a series of values for one input.

    Returns one row per value with the tool's numeric outputs, so you can see how
    an output responds to a design variable (e.g. sweep `altitude_m` for
    `isa_atmosphere`, or `mach` for `isentropic_flow`). A value that errors is
    reported per-row without aborting the sweep. tool_name must be a computational
    tool (see the tools list); sweep_parameter is one of its inputs.
    """
    from rocket_tools.workflows.engine import parameter_sweep as _sweep

    try:
        validated = ParameterSweepInput(
            tool_name=tool_name,
            params=params,
            sweep_parameter=sweep_parameter,
            values=values,
        )
        return _sweep(
            validated.tool_name,
            validated.params,
            validated.sweep_parameter,
            validated.values,
        )
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def list_references() -> dict:
    """List the authoritative sources behind rocket-tools and which tools are documented.

    Returns the de-duplicated bibliography (textbooks, NACA/NASA reports, standards)
    and the tool names that have provenance available via `cite_tool`.
    """
    from rocket_tools.provenance import list_documented_tools
    from rocket_tools.provenance import list_references as _lr

    try:
        return {
            "references": _lr(),
            "documented_tools": list_documented_tools(),
            "documented_tool_count": len(list_documented_tools()),
        }
    except Exception as e:
        return _format_error(e)


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
    thickness_to_chord: float = 0.12,
    sweep_deg: float = 0.0,
    technology_factor: float = 0.87,
) -> dict:
    """Drag coefficient CD = CD0 + K*CL^2 + wave drag (Korn drag-divergence)."""
    from rocket_tools.aerodynamics import drag_polar as _dp

    try:
        v = DragPolarInput(
            cl=cl,
            cd0=cd0,
            aspect_ratio=aspect_ratio,
            oswald_efficiency=oswald_efficiency,
            mach=mach,
            thickness_to_chord=thickness_to_chord,
            sweep_deg=sweep_deg,
            technology_factor=technology_factor,
        )
        return _dp(
            v.cl,
            v.cd0,
            v.aspect_ratio,
            v.oswald_efficiency,
            v.mach,
            v.thickness_to_chord,
            v.sweep_deg,
            v.technology_factor,
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


# ---- Static Stability Tools ----


@mcp.tool()
def center_of_pressure(
    nose_shape: str,
    nose_length_m: float,
    body_diameter_m: float,
    fin_count: int,
    fin_root_chord_m: float,
    fin_tip_chord_m: float,
    fin_semi_span_m: float,
    fin_sweep_length_m: float,
    fin_position_from_nose_m: float,
    reference_diameter_m: float | None = None,
) -> dict:
    """Subsonic center of pressure of a fin-stabilized rocket (Barrowman method).

    Combines a nose cone (cone/ogive/parabolic) and trapezoidal fins on a straight
    body tube, returning the CP location from the nose tip and the total normal-force
    slope. Pair with static_margin and a CG estimate to check flyability.
    """
    from rocket_tools.aerodynamics import center_of_pressure as _cp

    try:
        validated = CenterOfPressureInput(
            nose_shape=nose_shape,  # type: ignore[arg-type]
            nose_length_m=nose_length_m,
            body_diameter_m=body_diameter_m,
            fin_count=fin_count,
            fin_root_chord_m=fin_root_chord_m,
            fin_tip_chord_m=fin_tip_chord_m,
            fin_semi_span_m=fin_semi_span_m,
            fin_sweep_length_m=fin_sweep_length_m,
            fin_position_from_nose_m=fin_position_from_nose_m,
            reference_diameter_m=reference_diameter_m,
        )
        return _cp(
            validated.nose_shape,
            validated.nose_length_m,
            validated.body_diameter_m,
            validated.fin_count,
            validated.fin_root_chord_m,
            validated.fin_tip_chord_m,
            validated.fin_semi_span_m,
            validated.fin_sweep_length_m,
            validated.fin_position_from_nose_m,
            validated.reference_diameter_m,
        )
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def static_margin(
    cp_from_nose_m: float,
    cg_from_nose_m: float,
    reference_diameter_m: float,
) -> dict:
    """Static margin in calibers: (X_cp - X_cg)/d.

    Positive (CP aft of CG) is statically stable; a common target for fin-stabilized
    rockets is 1-2 calibers. cp/cg positions are measured from the nose tip.
    """
    from rocket_tools.aerodynamics import static_margin as _sm

    try:
        validated = StaticMarginInput(
            cp_from_nose_m=cp_from_nose_m,
            cg_from_nose_m=cg_from_nose_m,
            reference_diameter_m=reference_diameter_m,
        )
        return _sm(
            validated.cp_from_nose_m,
            validated.cg_from_nose_m,
            validated.reference_diameter_m,
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
def lambert_solver(
    r1_m: list[float],
    r2_m: list[float],
    time_of_flight_s: float,
    mu: float = 3.986004418e14,
    prograde: bool = True,
) -> dict:
    """Solve Lambert's problem: velocities of the orbit joining two positions in a time.

    Universal-variable formulation (Curtis Algorithm 5.2). Given start/end position
    vectors [x,y,z] in m and a transfer time, returns the departure and arrival velocity
    vector components (m/s), their speeds, and the transfer angle. mu in m^3/s^2 (default
    Earth). Use for interplanetary/orbital targeting and rendezvous first cuts.
    """
    from rocket_tools.design import lambert_solver as _ls

    try:
        validated = LambertSolverInput(
            r1_m=r1_m,
            r2_m=r2_m,
            time_of_flight_s=time_of_flight_s,
            mu=mu,
            prograde=prograde,
        )
        return _ls(
            validated.r1_m,
            validated.r2_m,
            validated.time_of_flight_s,
            validated.mu,
            validated.prograde,
        )
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def orbital_elements_from_state(
    position_m: list[float],
    velocity_ms: list[float],
    mu: float = 3.986004418e14,
) -> dict:
    """Classical orbital elements from an inertial state vector (Curtis Algorithm 4.2).

    Given position [x,y,z] in m and velocity [vx,vy,vz] in m/s, returns eccentricity,
    inclination, RAAN, argument of perigee, and true anomaly (degrees), plus specific
    angular momentum, semi-major axis, and apoapsis/periapsis radii. mu in m^3/s^2
    (default Earth). Circular/equatorial special cases collapse undefined angles to 0.
    """
    from rocket_tools.design import orbital_elements_from_state as _oe

    try:
        validated = OrbitalElementsFromStateInput(
            position_m=position_m,
            velocity_ms=velocity_ms,
            mu=mu,
        )
        return _oe(validated.position_m, validated.velocity_ms, validated.mu)
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
def composite_cg(
    masses: list[float],
    positions: list[list[float]],
    inertias: list[list[float]] | None = None,
) -> dict:
    """Compute center of gravity and mass moments of inertia for a composite body.

    Pass `inertias` (each component's own [Ixx,Iyy,Izz,Ixy,Ixz,Iyz] about its CG) for a
    correct roll/pitch inertia of slender bodies; omit it to treat components as point masses.
    """
    from rocket_tools.design import composite_cg as _ccg

    try:
        validated = CompositeCGInput(masses=masses, positions=positions, inertias=inertias)
        return _ccg(validated.masses, validated.positions, validated.inertias)
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
    design_pressure_pa: float | None = None,
    material_yield_pa: float | None = None,
    safety_factor: float = 1.5,
) -> dict:
    """Size a propellant tank and estimate mass (hemispherical domes; hoop-stress wall sizing).

    Provide design_pressure_pa (MEOP) and material_yield_pa to size the wall from hoop stress
    (t = P*r*SF/sigma_y); otherwise wall_thickness_m is used as given.
    """
    from rocket_tools.design import propellant_tank_sizing as _pts

    try:
        v = PropellantTankSizingInput(
            propellant_volume_m3=propellant_volume_m3,
            ullage_fraction=ullage_fraction,
            tank_shape=tank_shape,
            aspect_ratio=aspect_ratio,
            wall_thickness_m=wall_thickness_m,
            material_density_kg_m3=material_density_kg_m3,
            design_pressure_pa=design_pressure_pa,
            material_yield_pa=material_yield_pa,
            safety_factor=safety_factor,
        )
        return _pts(
            v.propellant_volume_m3,
            v.ullage_fraction,
            v.tank_shape,
            v.aspect_ratio,
            v.wall_thickness_m,
            v.material_density_kg_m3,
            v.design_pressure_pa,
            v.material_yield_pa,
            v.safety_factor,
        )
    except Exception as e:
        return _format_error(e)


# ---- Trajectory & Vehicle Sizing ----


@mcp.tool()
def simulate_ascent(
    initial_mass_kg: float,
    dry_mass_kg: float,
    specific_impulse_s: float,
    mass_flow_rate_kg_s: float,
    reference_area_m2: float,
    drag_coefficient: float = 0.5,
    launch_angle_deg: float = 90.0,
    initial_altitude_m: float = 0.0,
    initial_velocity_ms: float = 0.0,
    dt: float = 0.05,
    max_time: float = 2000.0,
    include_drag: bool = True,
    gravity_model: Literal["inverse_square", "constant"] = "inverse_square",
) -> dict:
    """Simulate a launch-vehicle ascent with a fixed-step RK4 integrator.

    Planar point-mass gravity-turn model: thrust F = mdot*Isp*g0 along the velocity
    vector while propellant remains, drag 0.5*rho*V^2*Cd*A with ISA density, and
    inverse-square (or constant) gravity. launch_angle_deg=90 is a vertical launch.
    Returns `events` (burnout, apogee), summary scalars (apogee_m, burnout_velocity_ms,
    max_dynamic_pressure_pa, max_accel_g, ideal_delta_v_ms, total_losses_ms, ...), and
    downsampled `series` arrays for plotting. Set gravity_model="constant",
    include_drag=False for an analytic vacuum comparison.
    """
    from rocket_tools.trajectory import simulate_ascent as _sim

    try:
        v = AscentSimInput(
            initial_mass_kg=initial_mass_kg,
            dry_mass_kg=dry_mass_kg,
            specific_impulse_s=specific_impulse_s,
            mass_flow_rate_kg_s=mass_flow_rate_kg_s,
            reference_area_m2=reference_area_m2,
            drag_coefficient=drag_coefficient,
            launch_angle_deg=launch_angle_deg,
            initial_altitude_m=initial_altitude_m,
            initial_velocity_ms=initial_velocity_ms,
            dt=dt,
            max_time=max_time,
            include_drag=include_drag,
            gravity_model=gravity_model,
        )
        return _sim(
            v.initial_mass_kg,
            v.dry_mass_kg,
            v.specific_impulse_s,
            v.mass_flow_rate_kg_s,
            v.reference_area_m2,
            v.drag_coefficient,
            v.launch_angle_deg,
            v.initial_altitude_m,
            v.initial_velocity_ms,
            v.dt,
            v.max_time,
            v.include_drag,
            v.gravity_model,
        )
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def size_vehicle(
    payload_mass_kg: float,
    delta_v_target_ms: float,
    specific_impulse_s: float,
    inert_mass_fraction: float,
    thrust_to_weight_liftoff: float = 1.3,
    propellant_density_kg_m3: float = 1000.0,
) -> dict:
    """Preliminary single-stage vehicle sizing from a delta-v budget.

    Solves the rocket equation for gross liftoff mass and the propellant/inert/payload
    breakdown given a payload, delta-v target, Isp, and structural fraction epsilon,
    then chains rocket_delta_v, thrust_to_weight, and propellant_tank_sizing. Returns
    achievable=False (with the max achievable delta-v) when the structural fraction is
    too high for the target.
    """
    from rocket_tools.trajectory import size_vehicle as _sv

    try:
        v = VehicleSizingInput(
            payload_mass_kg=payload_mass_kg,
            delta_v_target_ms=delta_v_target_ms,
            specific_impulse_s=specific_impulse_s,
            inert_mass_fraction=inert_mass_fraction,
            thrust_to_weight_liftoff=thrust_to_weight_liftoff,
            propellant_density_kg_m3=propellant_density_kg_m3,
        )
        return _sv(
            v.payload_mass_kg,
            v.delta_v_target_ms,
            v.specific_impulse_s,
            v.inert_mass_fraction,
            v.thrust_to_weight_liftoff,
            v.propellant_density_kg_m3,
        )
    except Exception as e:
        return _format_error(e)


# ---- Recovery ----


@mcp.tool()
def parachute_descent_rate(
    mass_kg: float,
    canopy_diameter_m: float,
    drag_coefficient: float = 0.75,
    altitude_m: float = 0.0,
    air_density_kg_m3: float | None = None,
) -> dict:
    """Terminal descent rate of a recovered mass under a round parachute.

    Drag balance mg = 0.5*rho*V^2*Cd*S gives V = sqrt(2*m*g/(rho*Cd*S)), S = pi*D^2/4.
    Density defaults to ISA at altitude_m unless air_density_kg_m3 is given. Also returns
    the landing kinetic energy, the usual recovery acceptance metric.
    """
    from rocket_tools.trajectory import parachute_descent_rate as _pdr

    try:
        v = ParachuteDescentInput(
            mass_kg=mass_kg,
            canopy_diameter_m=canopy_diameter_m,
            drag_coefficient=drag_coefficient,
            altitude_m=altitude_m,
            air_density_kg_m3=air_density_kg_m3,
        )
        return _pdr(
            v.mass_kg,
            v.canopy_diameter_m,
            v.drag_coefficient,
            v.altitude_m,
            v.air_density_kg_m3,
        )
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def parachute_area_for_descent_rate(
    mass_kg: float,
    target_descent_rate_ms: float,
    drag_coefficient: float = 0.75,
    altitude_m: float = 0.0,
    air_density_kg_m3: float | None = None,
) -> dict:
    """Canopy area and diameter needed to hit a target descent (landing) rate.

    Inverts the drag balance: S = 2*m*g/(rho*Cd*V_target^2), D = sqrt(4*S/pi). A common
    hobby-rocket landing-speed target is roughly 3-6 m/s.
    """
    from rocket_tools.trajectory import parachute_area_for_descent_rate as _pafd

    try:
        v = ParachuteAreaInput(
            mass_kg=mass_kg,
            target_descent_rate_ms=target_descent_rate_ms,
            drag_coefficient=drag_coefficient,
            altitude_m=altitude_m,
            air_density_kg_m3=air_density_kg_m3,
        )
        return _pafd(
            v.mass_kg,
            v.target_descent_rate_ms,
            v.drag_coefficient,
            v.altitude_m,
            v.air_density_kg_m3,
        )
    except Exception as e:
        return _format_error(e)


# ---- Optimization ----


@mcp.tool()
def optimize_staging(
    delta_v_target_ms: float,
    stages: list[dict],
    payload_mass_kg: float = 1.0,
    gravity: float = 9.80665,
) -> dict:
    """Optimal delta-v split across stages that maximizes overall payload fraction.

    Each stage dict needs `specific_impulse_s` and `structural_ratio` (epsilon in (0,1)).
    Solves the restricted staging problem via a Lagrange multiplier (robust bisection),
    returning per-stage optimal delta-v/mass ratio, total delta-v, the overall
    `optimal_payload_fraction`, and `max_achievable_delta_v_ms`. Returns achievable=False
    when the target exceeds the theoretical ceiling. (Curtis Ch. 11.)
    """
    from rocket_tools.optimization import optimize_staging as _os

    try:
        v = StagingOptimizerInput(
            delta_v_target_ms=delta_v_target_ms,
            stages=stages,
            payload_mass_kg=payload_mass_kg,
            gravity=gravity,
        )
        return _os(v.delta_v_target_ms, v.stages, v.payload_mass_kg, v.gravity)
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def optimize_design(
    tool_name: str,
    fixed_params: dict,
    variable: str,
    bounds: list[float],
    objective_key: str,
    sense: Literal["max", "min"] = "max",
    iterations: int = 40,
) -> dict:
    """Optimize one output of any computational tool over a single input variable.

    Generalizes `parameter_sweep` from a grid scan to a golden-section search over the
    same tool dispatch registry. Give the tool name, the fixed arguments, the variable
    to vary, its [low, high] bounds, the output key to optimize, and the sense
    ("max"/"min"). Returns the optimal variable value, the objective there, the tool's
    full output at the optimum, and the evaluated `trace` (inspect it if the response
    may be non-unimodal).
    """
    from rocket_tools.optimization import optimize_design as _od

    try:
        v = DesignOptimizerInput(
            tool_name=tool_name,
            fixed_params=fixed_params,
            variable=variable,
            bounds=bounds,
            objective_key=objective_key,
            sense=sense,
            iterations=iterations,
        )
        return _od(
            v.tool_name,
            v.fixed_params,
            v.variable,
            v.bounds,
            v.objective_key,
            v.sense,
            v.iterations,
        )
    except Exception as e:
        return _format_error(e)


# ---- Standards & Reliability ----


@mcp.tool()
def design_review_report(items: list[dict], min_acceptable_margin: float = 0.0) -> dict:
    """Roll up margins of safety across design items into a go/no-go review.

    Each item needs `name` and either a precomputed `margin_of_safety` or an
    `allowable_stress_pa`/`actual_stress_pa` pair (optional `factor_of_safety`,
    default 1.5). Returns a per-item table, the governing (minimum) margin and item,
    the failing count, and a PASS/FAIL verdict.
    """
    from rocket_tools.standards import design_review_report as _drr

    try:
        v = DesignReviewInput.model_validate(
            {"items": items, "min_acceptable_margin": min_acceptable_margin}
        )
        return _drr([it.model_dump() for it in v.items], v.min_acceptable_margin)
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def fmea_report(items: list[dict], rpn_threshold: int = 100) -> dict:
    """Rank failure modes by Risk Priority Number (RPN = Severity x Occurrence x Detection).

    Each item needs `failure_mode` and integer `severity`, `occurrence`, `detection`
    on 1-10 scales (optional `function`, `effect`, `cause`). Returns the modes ranked by
    RPN, the max/mean RPN, and the high-priority subset (RPN >= threshold or severity >= 9).
    MIL-STD-1629A / SAE J1739.
    """
    from rocket_tools.standards import fmea_report as _fmea

    try:
        v = FMEAInput.model_validate({"items": items, "rpn_threshold": rpn_threshold})
        return _fmea([it.model_dump() for it in v.items], v.rpn_threshold)
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def list_standards() -> dict:
    """List the aerospace design standards catalog (id, title, domain, scope, factors).

    Covers the standards informing rocket-tools' factors of safety and reliability
    methods (FAR 25.303, FAA AC 25.571-1D, NASA-STD-5001, MMPDS-15, MIL-STD-1629A,
    SAE J1739). Also available as the `rocket-tools://standards` resource.
    """
    from rocket_tools.standards import list_standards as _ls

    try:
        return _ls()
    except Exception as e:
        return _format_error(e)


# ---- Visualization (optional; requires the `viz` extra: matplotlib) ----
#
# Dual-return contract: render="data" (default) returns a JSON dict with a base64 PNG
# plus the underlying `series`; render="image" returns a native MCP image. Errors always
# return the structured dict error, never an image.


@mcp.tool()
def plot_beam_diagrams(
    load: float,
    length: float,
    youngs_modulus: float,
    cross_section: dict,
    load_type: Literal["point_midspan", "point_tip", "distributed"] = "point_midspan",
    support_type: Literal["simply_supported", "cantilever", "fixed_ends"] = "simply_supported",
    render: Literal["data", "image"] = "data",
    output_path: str | None = None,
) -> dict:
    """Shear, bending-moment, and deflection diagrams along a beam span (Roark Table 8.1).

    Returns a base64 PNG plus the x/shear/moment/deflection `series`, or a native MCP
    image when render="image".
    """
    from rocket_tools.viz import plot_beam_diagrams as _fn

    try:
        v = BeamDiagramInput(
            load=load,
            length=length,
            youngs_modulus=youngs_modulus,
            cross_section=cross_section,
            load_type=load_type,
            support_type=support_type,
            render=render,
            output_path=output_path,
        )
        return _fn(
            v.load,
            v.length,
            v.youngs_modulus,
            v.cross_section,
            v.load_type,
            v.support_type,
            v.render,
            v.output_path,
        )
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def plot_drag_polar(
    cd0: float,
    aspect_ratio: float,
    oswald_efficiency: float = 0.85,
    mach: float = 0.0,
    cl_max: float = 1.5,
    render: Literal["data", "image"] = "data",
    output_path: str | None = None,
) -> dict:
    """Drag polar (C_D vs C_L) and L/D vs C_L for an aircraft configuration."""
    from rocket_tools.viz import plot_drag_polar as _fn

    try:
        v = DragPolarPlotInput(
            cd0=cd0,
            aspect_ratio=aspect_ratio,
            oswald_efficiency=oswald_efficiency,
            mach=mach,
            cl_max=cl_max,
            render=render,
            output_path=output_path,
        )
        return _fn(
            v.cd0, v.aspect_ratio, v.oswald_efficiency, v.mach, v.cl_max, v.render, v.output_path
        )
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def plot_nozzle_contour(
    throat_radius_m: float,
    area_ratio: float,
    half_angle_deg: float = 15.0,
    render: Literal["data", "image"] = "data",
    output_path: str | None = None,
) -> dict:
    """Conical convergent-divergent nozzle wall contour from throat radius and A_e/A*."""
    from rocket_tools.viz import plot_nozzle_contour as _fn

    try:
        v = NozzleContourInput(
            throat_radius_m=throat_radius_m,
            area_ratio=area_ratio,
            half_angle_deg=half_angle_deg,
            render=render,
            output_path=output_path,
        )
        return _fn(v.throat_radius_m, v.area_ratio, v.half_angle_deg, v.render, v.output_path)
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def plot_isa_profile(
    max_altitude_m: float = 84000.0,
    render: Literal["data", "image"] = "data",
    output_path: str | None = None,
) -> dict:
    """Temperature, pressure, and density vs altitude (US Standard Atmosphere 1976)."""
    from rocket_tools.viz import plot_isa_profile as _fn

    try:
        v = ISAProfileInput(max_altitude_m=max_altitude_m, render=render, output_path=output_path)
        return _fn(v.max_altitude_m, v.render, v.output_path)
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def plot_trajectory(
    initial_mass_kg: float,
    dry_mass_kg: float,
    specific_impulse_s: float,
    mass_flow_rate_kg_s: float,
    reference_area_m2: float,
    drag_coefficient: float = 0.5,
    launch_angle_deg: float = 90.0,
    dt: float = 0.1,
    render: Literal["data", "image"] = "data",
    output_path: str | None = None,
) -> dict:
    """Run an ascent simulation and plot altitude, velocity, dynamic pressure, and g-load."""
    from rocket_tools.viz import plot_trajectory as _fn

    try:
        v = TrajectoryPlotInput(
            initial_mass_kg=initial_mass_kg,
            dry_mass_kg=dry_mass_kg,
            specific_impulse_s=specific_impulse_s,
            mass_flow_rate_kg_s=mass_flow_rate_kg_s,
            reference_area_m2=reference_area_m2,
            drag_coefficient=drag_coefficient,
            launch_angle_deg=launch_angle_deg,
            dt=dt,
            render=render,
            output_path=output_path,
        )
        return _fn(
            v.initial_mass_kg,
            v.dry_mass_kg,
            v.specific_impulse_s,
            v.mass_flow_rate_kg_s,
            v.reference_area_m2,
            v.drag_coefficient,
            v.launch_angle_deg,
            v.dt,
            v.render,
            v.output_path,
        )
    except Exception as e:
        return _format_error(e)


# ---- MCP Resources (readable datasets for research context) ----
#
# Resources let an agent pull the reference bibliography, the curated validation
# dataset, the materials database, and per-tool provenance as context, rather
# than discovering them one tool call at a time.


@mcp.resource(
    "rocket-tools://references",
    mime_type="application/json",
    description="Authoritative bibliography behind rocket-tools and the documented tool list.",
)
def references_resource() -> str:
    import json

    from rocket_tools.provenance import list_documented_tools, list_references

    return json.dumps(
        {"references": list_references(), "documented_tools": list_documented_tools()}, indent=2
    )


@mcp.resource(
    "rocket-tools://benchmarks",
    mime_type="application/json",
    description="Curated validation benchmarks: inputs, expected values, tolerance, and source.",
)
def benchmarks_resource() -> str:
    import json

    from rocket_tools.validation.benchmarks import get_benchmark, list_benchmarks

    return json.dumps({name: get_benchmark(name) for name in list_benchmarks()}, indent=2)


@mcp.resource(
    "rocket-tools://provenance",
    mime_type="application/json",
    description="Per-tool provenance: reference(s), governing formula, assumptions, validation.",
)
def provenance_resource() -> str:
    import json

    from rocket_tools.provenance import get_provenance, list_documented_tools

    return json.dumps({t: get_provenance(t) for t in list_documented_tools()}, indent=2)


@mcp.resource(
    "rocket-tools://standards",
    mime_type="application/json",
    description="Catalog of aerospace design standards (factors of safety, FMEA, allowables).",
)
def standards_resource() -> str:
    import json

    from rocket_tools.standards import list_standards

    return json.dumps(list_standards(), indent=2)


@mcp.resource(
    "rocket-tools://materials",
    mime_type="application/json",
    description="Full aerospace materials database with mechanical and thermal properties.",
)
def materials_resource() -> str:
    import json

    from rocket_tools.materials import list_materials, material_lookup

    return json.dumps({name: material_lookup(name) for name in list_materials()}, indent=2)


@mcp.resource(
    "rocket-tools://materials/{name}",
    mime_type="application/json",
    description="Properties of a single material by name (e.g. rocket-tools://materials/6061-T6).",
)
def material_resource(name: str) -> str:
    import json

    from rocket_tools.materials import material_lookup

    try:
        return json.dumps(material_lookup(name), indent=2)
    except Exception as e:
        return json.dumps(_format_error(e), indent=2)


# ---- Server Entry Point ----


def main():
    mcp.run()


if __name__ == "__main__":
    main()
