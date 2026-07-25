"""Intent pattern registry for aerospace queries."""

from collections.abc import Callable
from dataclasses import dataclass, field

from .extractors import (
    extract_altitude,
    extract_angle,
    extract_aspect_ratio,
    extract_conversion_value,
    extract_deflection,
    extract_drag,
    extract_flow_regime,
    extract_from_unit,
    extract_gamma,
    extract_length,
    extract_lift,
    extract_load,
    extract_mach,
    extract_mass,
    extract_material,
    extract_number,
    extract_pressure,
    extract_reference_area,
    extract_reynolds_number,
    extract_stress,
    extract_sweep,
    extract_temperature,
    extract_thrust,
    extract_to_unit,
    extract_velocity,
    extract_youngs_modulus,
)


@dataclass
class IntentConfig:
    patterns: list[str]
    param_extractors: dict[str, Callable]
    defaults: dict = field(default_factory=dict)
    required_params: list[str] = field(default_factory=list)


INTENT_REGISTRY = {
    # ---- Utility Tools ----
    "unit_convert": IntentConfig(
        patterns=[
            r"convert",
            r"(\d+\.?\d*)\s*\w+\s+(to|into|in)\s+\w+",
        ],
        param_extractors={
            "value": extract_conversion_value,
            "from_unit": extract_from_unit,
            "to_unit": extract_to_unit,
        },
        defaults={},
        required_params=["value", "from_unit", "to_unit"],
    ),
    "material_lookup": IntentConfig(
        patterns=[
            r"(properties|property|specs|material data)",
            r"look up.*material",
            r"what is.*(6061|7075|titanium|inconel|steel|aluminum|aluminium)",
            r"(6061|7075|ti-6al-4v|inconel|4130)",
        ],
        param_extractors={
            "name": extract_material,
        },
        defaults={},
        required_params=["name"],
    ),
    "isa_atmosphere": IntentConfig(
        patterns=[
            r"(ISA|atmosphere|atmospheric)",
            r"(density|pressure|temperature).*at.*(altitude|height)",
            r"at\s+(\d+).*m.*(altitude|height)",
        ],
        param_extractors={
            "altitude_m": extract_altitude,
        },
        defaults={},
        required_params=["altitude_m"],
    ),
    # ---- Structural Tools ----
    "beam_analysis": IntentConfig(
        patterns=[
            r"beam",
            r"(load|force|weight|carry|support|handle|design|calculate|find).*beam",
            r"beam.*(load|force|weight|carry|support|handle|design|calculate|find)",
            r"(deflection|bending stress|bending moment|section modulus)",
        ],
        param_extractors={
            "load": extract_load,
            "length": extract_length,
            "material": extract_material,
        },
        defaults={
            "cross_section": {"type": "rectangle", "width": 0.05, "height": 0.01},
            "support_type": "simply_supported",
            "load_type": "point_midspan",
        },
        required_params=["load", "length"],
    ),
    "section_properties": IntentConfig(
        patterns=[
            r"section\s*properties",
            r"(area\s*moment|moment\s*of\s*inertia|Ixx|I_yy|section\s*modulus)",
            r"(ibeam|i-beam|c-channel|t-section|hollow).*properties",
        ],
        param_extractors={
            "width": extract_length,
            "height": extract_length,
            "diameter": extract_length,
            "wall_thickness": extract_length,
            "outer_diameter": extract_length,
            "inner_diameter": extract_length,
            "flange_width": extract_length,
            "flange_thickness": extract_length,
            "web_thickness": extract_length,
        },
        defaults={"shape": "rectangle"},
        required_params=["shape"],
    ),
    "column_buckling": IntentConfig(
        patterns=[
            r"column\s*buckling",
            r"(buckling\s*load|euler\s*buckling|critical\s*load).*column",
            r"column.*(buckling|critical\s*load)",
        ],
        param_extractors={
            "youngs_modulus": extract_youngs_modulus,
            "length": extract_length,
            "area": extract_length,
        },
        defaults={
            "end_condition": "pinned_pinned",
        },
        required_params=["youngs_modulus", "area_moment", "area", "length", "yield_strength"],
    ),
    "plate_buckling_coefficient": IntentConfig(
        patterns=[
            r"plate\s*buckling",
            r"buckling\s*coefficient",
            r"k\s*buckling",
        ],
        param_extractors={
            "aspect_ratio": extract_aspect_ratio,
        },
        defaults={
            "boundary_condition": "simply_supported",
            "load_type": "compression",
        },
        required_params=["aspect_ratio"],
    ),
    "margin_of_safety": IntentConfig(
        patterns=[
            r"margin\s*of\s*safety",
            r"MS\s*=",
            r"safety\s*margin",
        ],
        param_extractors={
            "allowable_stress_pa": extract_stress,
            "actual_stress_pa": extract_stress,
            "allowable_load_n": extract_load,
            "actual_load_n": extract_load,
        },
        defaults={
            "factor_of_safety": 1.5,
            "failure_mode": "yield",
        },
        required_params=[],
    ),
    "von_mises_stress": IntentConfig(
        patterns=[
            r"von\s*mises",
            r"equivalent\s*stress",
        ],
        param_extractors={
            "sigma_x": extract_stress,
            "sigma_y": extract_stress,
            "tau_xy": extract_stress,
        },
        defaults={
            "sigma_y": 0.0,
            "tau_xy": 0.0,
        },
        required_params=["sigma_x"],
    ),
    "combined_margin_of_safety": IntentConfig(
        patterns=[
            r"combined\s*margin",
            r"combined\s*stress.*margin",
        ],
        param_extractors={
            "sigma_x": extract_stress,
            "sigma_y": extract_stress,
            "tau_xy": extract_stress,
            "yield_strength_pa": extract_stress,
            "ultimate_strength_pa": extract_stress,
        },
        defaults={
            "sigma_y": 0.0,
            "tau_xy": 0.0,
            "factor_of_safety_yield": 1.5,
            "factor_of_safety_ultimate": 1.5,
        },
        required_params=["sigma_x"],
    ),
    "deflection_margin": IntentConfig(
        patterns=[
            r"deflection\s*margin",
            r"deflection.*limit",
            r"L/\d+\s*deflection",
        ],
        param_extractors={
            "actual_deflection_m": extract_deflection,
            "span_length_m": extract_length,
        },
        defaults={
            "deflection_limit_ratio": 360.0,
        },
        required_params=["actual_deflection_m"],
    ),
    "truss_analysis": IntentConfig(
        patterns=[
            r"truss",
            r"pin-jointed",
            r"direct\s*stiffness",
        ],
        param_extractors={},
        defaults={},
        required_params=["nodes", "elements", "element_properties", "constraints", "loads"],
    ),
    # ---- Aerodynamics Tools ----
    "aero_analysis": IntentConfig(
        patterns=[
            r"(aerodynamic|flow|Reynolds|Mach|dynamic pressure|lift|drag)",
            r"(subsonic|transonic|supersonic|hypersonic)",
            r"(velocity|speed|altitude|height).*analysis",
        ],
        param_extractors={
            "velocity": extract_velocity,
            "altitude_m": extract_altitude,
            "characteristic_length": extract_length,
        },
        defaults={
            "reference_area": 1.0,
            "lift": 0.0,
            "drag": 0.0,
        },
        required_params=["velocity", "altitude_m"],
    ),
    "reynolds_number": IntentConfig(
        patterns=[
            r"Reynolds\s*number",
            r"\bRe\s*\d",
            r"Re\s*=",
        ],
        param_extractors={
            "velocity": extract_velocity,
            "characteristic_length": extract_length,
            "altitude_m": extract_altitude,
        },
        defaults={},
        required_params=["velocity", "characteristic_length"],
    ),
    "mach_number": IntentConfig(
        patterns=[
            r"Mach\s*number",
            r"Mach\s*\d",
        ],
        param_extractors={
            "velocity": extract_velocity,
            "altitude_m": extract_altitude,
        },
        defaults={},
        required_params=["velocity", "altitude_m"],
    ),
    "dynamic_pressure": IntentConfig(
        patterns=[
            r"dynamic\s*pressure",
            r"q\s*=",
        ],
        param_extractors={
            "velocity": extract_velocity,
            "altitude_m": extract_altitude,
        },
        defaults={},
        required_params=["velocity", "altitude_m"],
    ),
    "lift_coefficient": IntentConfig(
        patterns=[
            r"lift\s*coefficient",
            r"CL\s*=",
            r"CL\s*\d",
        ],
        param_extractors={
            "lift": extract_lift,
            "velocity": extract_velocity,
            "altitude_m": extract_altitude,
            "reference_area": extract_reference_area,
        },
        defaults={},
        required_params=["lift", "velocity", "altitude_m", "reference_area"],
    ),
    "drag_coefficient": IntentConfig(
        patterns=[
            r"drag\s*coefficient",
            r"CD\s*=",
            r"CD\s*\d",
        ],
        param_extractors={
            "drag": extract_drag,
            "velocity": extract_velocity,
            "altitude_m": extract_altitude,
            "reference_area": extract_reference_area,
        },
        defaults={},
        required_params=["drag", "velocity", "altitude_m", "reference_area"],
    ),
    "skin_friction_coefficient": IntentConfig(
        patterns=[
            r"skin\s*friction",
            r"friction\s*coefficient",
            r"Cf\s*=",
            r"Cf\s*\d",
        ],
        param_extractors={
            "reynolds_number": extract_reynolds_number,
            "flow_regime": extract_flow_regime,
        },
        defaults={"flow_regime": "laminar"},
        required_params=["reynolds_number"],
    ),
    # ---- Compressible Flow Tools ----
    "isentropic_flow": IntentConfig(
        patterns=[
            r"isentropic",
            r"(T/T0|P/P0|rho/rho0|A/A\*|pressure\s*ratio|temperature\s*ratio|density\s*ratio)",
            r"gamma.*mach",
        ],
        param_extractors={
            "mach": extract_mach,
            "gamma": extract_gamma,
        },
        defaults={"gamma": 1.4},
        required_params=["mach"],
    ),
    "normal_shock": IntentConfig(
        patterns=[
            r"normal\s*shock",
            r"shock\s*wave.*normal",
            r"(normal|shock)\s*(relation|ratio)",
        ],
        param_extractors={
            "mach1": extract_mach,
            "gamma": extract_gamma,
        },
        defaults={"gamma": 1.4},
        required_params=["mach1"],
    ),
    "oblique_shock": IntentConfig(
        patterns=[
            r"oblique\s*shock",
            r"shock\s*angle",
        ],
        param_extractors={
            "mach1": extract_mach,
            "deflection_deg": extract_angle,
            "gamma": extract_gamma,
        },
        defaults={"gamma": 1.4},
        required_params=["mach1", "deflection_deg"],
    ),
    "prandtl_meyer": IntentConfig(
        patterns=[
            r"prandtl\s*meyer",
            r"expansion\s*angle",
            r"(prandtl|meyer).*angle",
        ],
        param_extractors={
            "mach": extract_mach,
            "gamma": extract_gamma,
        },
        defaults={"gamma": 1.4},
        required_params=["mach"],
    ),
    "prandtl_meyer_from_angle": IntentConfig(
        patterns=[
            r"prandtl\s*meyer.*angle",
            r"mach\s*from\s*expansion\s*angle",
        ],
        param_extractors={
            "angle_deg": extract_angle,
            "gamma": extract_gamma,
        },
        defaults={"gamma": 1.4},
        required_params=["angle_deg"],
    ),
    # ---- Aircraft Performance Tools ----
    "lift_curve_slope": IntentConfig(
        patterns=[
            r"lift\s*curve\s*slope",
            r"CL\s*alpha",
            r"dCL/dalpha",
        ],
        param_extractors={
            "mach": extract_mach,
            "aspect_ratio": extract_aspect_ratio,
            "sweep_deg": extract_sweep,
        },
        defaults={
            "taper_ratio": 1.0,
            "sweep_deg": 0.0,
            "oswald_efficiency": 0.85,
        },
        required_params=["mach", "aspect_ratio"],
    ),
    "drag_polar": IntentConfig(
        patterns=[
            r"drag\s*polar",
            r"CD\s*=\s*CD0",
        ],
        param_extractors={
            "cl": extract_number,
            "cd0": extract_number,
            "aspect_ratio": extract_aspect_ratio,
            "mach": extract_mach,
        },
        defaults={
            "oswald_efficiency": 0.85,
            "mach": 0.0,
        },
        required_params=["cl", "cd0", "aspect_ratio"],
    ),
    "breguet_range": IntentConfig(
        patterns=[
            r"breguet\s*range",
            r"aircraft\s*range",
        ],
        param_extractors={
            "lift_to_drag_ratio": extract_number,
            "specific_fuel_consumption": extract_number,
            "velocity": extract_velocity,
            "initial_mass_kg": extract_mass,
            "final_mass_kg": extract_mass,
        },
        defaults={},
        required_params=[
            "lift_to_drag_ratio",
            "specific_fuel_consumption",
            "velocity",
            "initial_mass_kg",
            "final_mass_kg",
        ],
    ),
    "breguet_endurance": IntentConfig(
        patterns=[
            r"breguet\s*endurance",
            r"aircraft\s*endurance",
        ],
        param_extractors={
            "lift_to_drag_ratio": extract_number,
            "specific_fuel_consumption": extract_number,
            "initial_mass_kg": extract_mass,
            "final_mass_kg": extract_mass,
        },
        defaults={},
        required_params=[
            "lift_to_drag_ratio",
            "specific_fuel_consumption",
            "initial_mass_kg",
            "final_mass_kg",
        ],
    ),
    "wing_loading": IntentConfig(
        patterns=[
            r"wing\s*loading",
            r"stall\s*speed",
        ],
        param_extractors={
            "weight_n": extract_load,
            "wing_area_m2": extract_reference_area,
        },
        defaults={},
        required_params=["weight_n", "wing_area_m2"],
    ),
    # ---- Nozzle / Inlet Tools ----
    "nozzle_performance": IntentConfig(
        patterns=[
            r"nozzle",
            r"(thrust|isp|thrust\s*coefficient).*nozzle",
            r"rocket\s*engine\s*performance",
        ],
        param_extractors={
            "chamber_pressure_pa": extract_pressure,
            "chamber_temperature_k": extract_temperature,
            "ambient_pressure_pa": extract_pressure,
        },
        defaults={
            "throat_area_m2": 0.01,
            "exit_area_m2": 0.1,
            "gamma": 1.4,
            "molecular_weight": 28.97,
        },
        required_params=[
            "chamber_pressure_pa",
            "chamber_temperature_k",
            "ambient_pressure_pa",
            "throat_area_m2",
            "exit_area_m2",
        ],
    ),
    "optimal_area_ratio": IntentConfig(
        patterns=[
            r"optimal\s*area\s*ratio",
            r"expansion\s*ratio",
            r"A/A\*",
        ],
        param_extractors={
            "chamber_pressure_pa": extract_pressure,
            "ambient_pressure_pa": extract_pressure,
            "gamma": extract_gamma,
        },
        defaults={"gamma": 1.4},
        required_params=["chamber_pressure_pa", "ambient_pressure_pa"],
    ),
    # ---- Mission Design Tools ----
    "rocket_delta_v": IntentConfig(
        patterns=[
            r"rocket\s*delta[- ]?v",
            r"tsiolkovsky",
            r"delta[- ]?v.*rocket",
            r"delta\s*v.*isp",
        ],
        param_extractors={
            "specific_impulse_s": extract_number,
            "initial_mass_kg": extract_mass,
            "final_mass_kg": extract_mass,
        },
        defaults={"gravity": 9.80665},
        required_params=["specific_impulse_s", "initial_mass_kg", "final_mass_kg"],
    ),
    "multi_stage_delta_v": IntentConfig(
        patterns=[
            r"multi\s*stage",
            r"staging",
        ],
        param_extractors={},
        defaults={"gravity": 9.80665},
        required_params=["stages"],
    ),
    "orbital_velocity": IntentConfig(
        patterns=[
            r"orbital\s*velocity",
            r"circular\s*orbit",
            r"escape\s*velocity",
        ],
        param_extractors={
            "altitude_m": extract_altitude,
        },
        defaults={},
        required_params=["altitude_m"],
    ),
    "payload_fraction": IntentConfig(
        patterns=[
            r"payload\s*fraction",
            r"payload\s*mass",
        ],
        param_extractors={
            "delta_v_required_ms": extract_velocity,
            "specific_impulse_s": extract_number,
        },
        defaults={"gravity": 9.80665},
        required_params=["delta_v_required_ms", "specific_impulse_s", "inert_mass_fraction"],
    ),
    "thrust_to_weight": IntentConfig(
        patterns=[
            r"thrust\s*to\s*weight",
            r"T/W",
        ],
        param_extractors={
            "thrust_n": extract_thrust,
            "mass_kg": extract_mass,
        },
        defaults={"gravity": 9.80665},
        required_params=["thrust_n", "mass_kg"],
    ),
    "composite_cg": IntentConfig(
        patterns=[
            r"center\s*of\s*gravity",
            r"CG",
            r"composite\s*CG",
        ],
        param_extractors={},
        defaults={},
        required_params=["masses", "positions"],
    ),
    "propellant_tank_sizing": IntentConfig(
        patterns=[
            r"propellant\s*tank",
            r"tank\s*sizing",
            r"fuel\s*tank",
        ],
        param_extractors={
            "propellant_volume_m3": extract_number,
        },
        defaults={
            "tank_shape": "cylinder",
            "aspect_ratio": 2.0,
            "wall_thickness_m": 0.003,
            "material_density_kg_m3": 2700.0,
            "ullage_fraction": 0.1,
        },
        required_params=["propellant_volume_m3"],
    ),
    # ---- Astrodynamics (route by name; radii/elements are hard to extract from free
    # text, so these correctly ask for the missing parameters rather than guessing). ----
    "hohmann_transfer": IntentConfig(
        patterns=[r"hohmann"],
        param_extractors={},
        defaults={},
        required_params=["radius1_m", "radius2_m"],
    ),
    "bi_elliptic_transfer": IntentConfig(
        patterns=[r"bi[\s-]?elliptic"],
        param_extractors={},
        defaults={},
        required_params=["radius1_m", "radius2_m", "intermediate_radius_m"],
    ),
    "orbital_period": IntentConfig(
        patterns=[r"orbital\s*period", r"period\s+of\s+(the\s+)?orbit"],
        param_extractors={},
        defaults={},
        required_params=["semi_major_axis_m"],
    ),
    "vis_viva_velocity": IntentConfig(
        patterns=[r"vis[\s-]?viva"],
        param_extractors={},
        defaults={},
        required_params=["radius_m", "semi_major_axis_m"],
    ),
    "plane_change_delta_v": IntentConfig(
        patterns=[r"plane\s*change", r"inclination\s*change"],
        param_extractors={
            "velocity_ms": extract_velocity,
            "inclination_change_deg": extract_angle,
        },
        defaults={},
        required_params=["velocity_ms", "inclination_change_deg"],
    ),
}
