"""Happy-path smoke test for every computational MCP tool.

Calls each tool through ``mcp.call_tool`` with valid inputs and asserts a
non-error structured result. This exercises the server tool wrappers (the actual
product surface) so wiring or response-key regressions fail immediately.
"""

import asyncio
import json

import pytest

from rocket_tools.server import mcp

# One valid call per computational tool. Meta/orchestration tools (cite_tool,
# list_references, propagate_uncertainty, parameter_sweep, validate_result,
# list_validation_benchmarks) and the list-returning list_materials are covered
# by their own test modules.
VALID_CALLS: dict[str, dict] = {
    "unit_convert": {"value": 1.0, "from_unit": "m", "to_unit": "mm"},
    "material_lookup": {"name": "6061-T6"},
    "isa_atmosphere": {"altitude_m": 5000.0},
    # structural
    "beam_analysis": {
        "load": 1000.0,
        "length": 2.0,
        "youngs_modulus": 200e9,
        "cross_section": {"type": "rectangle", "width": 0.05, "height": 0.01},
    },
    "section_properties": {"shape": "rectangle", "width": 0.1, "height": 0.2},
    "column_buckling": {
        "youngs_modulus": 69e9,
        "area_moment": 1e-8,
        "area": 1e-3,
        "length": 1.5,
        "yield_strength": 2.76e8,
    },
    "plate_buckling_coefficient": {"aspect_ratio": 1.0},
    "margin_of_safety": {"allowable_stress_pa": 276e6, "actual_stress_pa": 150e6},
    "combined_margin_of_safety": {
        "sigma_x": 100e6,
        "sigma_y": 50e6,
        "tau_xy": 20e6,
        "yield_strength_pa": 276e6,
    },
    "von_mises_stress": {"sigma_x": 100e6, "sigma_y": 50e6, "tau_xy": 20e6},
    "deflection_margin": {"actual_deflection_m": 0.004, "span_length_m": 2.0},
    "truss_analysis": {
        "nodes": [[0.0, 0.0], [1.0, 0.0], [0.5, 0.866]],
        "elements": [[0, 2], [1, 2]],
        "element_properties": [
            {"youngs_modulus_pa": 200e9, "area_m2": 0.001},
            {"youngs_modulus_pa": 200e9, "area_m2": 0.001},
        ],
        "constraints": [{"node": 0, "fixed_dof": [0, 1]}, {"node": 1, "fixed_dof": [0, 1]}],
        "loads": [{"node": 2, "force": [0.0, -10000.0]}],
    },
    # aerodynamics fundamentals
    "reynolds_number": {"velocity": 250.0, "characteristic_length": 2.0, "altitude_m": 5000.0},
    "mach_number": {"velocity": 250.0, "altitude_m": 5000.0},
    "dynamic_pressure": {"velocity": 250.0, "altitude_m": 5000.0},
    "lift_coefficient": {
        "lift": 50000.0,
        "velocity": 100.0,
        "altitude_m": 5000.0,
        "reference_area": 10.0,
    },
    "drag_coefficient": {
        "drag": 5000.0,
        "velocity": 100.0,
        "altitude_m": 5000.0,
        "reference_area": 10.0,
    },
    "skin_friction_coefficient": {"reynolds_number": 1e6, "flow_regime": "turbulent"},
    "aero_analysis": {
        "velocity": 100.0,
        "altitude_m": 5000.0,
        "characteristic_length": 2.0,
        "reference_area": 10.0,
    },
    # compressible
    "isentropic_flow": {"mach": 2.0},
    "normal_shock": {"mach1": 2.0},
    "oblique_shock": {"mach1": 2.0, "deflection_deg": 15.0},
    "prandtl_meyer": {"mach": 2.0},
    "prandtl_meyer_from_angle": {"angle_deg": 26.38},
    # aircraft
    "lift_curve_slope": {"mach": 0.3, "aspect_ratio": 8.0},
    "drag_polar": {"cl": 0.5, "cd0": 0.02, "aspect_ratio": 8.0},
    "breguet_range": {
        "lift_to_drag_ratio": 15.0,
        "specific_fuel_consumption": 2e-5,
        "velocity": 230.0,
        "initial_mass_kg": 10000.0,
        "final_mass_kg": 8000.0,
    },
    "breguet_endurance": {
        "lift_to_drag_ratio": 15.0,
        "specific_fuel_consumption": 2e-5,
        "initial_mass_kg": 10000.0,
        "final_mass_kg": 8000.0,
    },
    "wing_loading": {"weight_n": 50000.0, "wing_area_m2": 16.0},
    # nozzle & propulsion
    "nozzle_performance": {
        "chamber_pressure_pa": 7e6,
        "chamber_temperature_k": 3500.0,
        "ambient_pressure_pa": 101325.0,
        "throat_area_m2": 0.01,
        "exit_area_m2": 0.08,
    },
    "optimal_area_ratio": {"chamber_pressure_pa": 7e6, "ambient_pressure_pa": 101325.0},
    "characteristic_velocity": {
        "chamber_temperature_k": 3500.0,
        "gamma": 1.22,
        "molecular_weight": 23.3,
    },
    "ideal_specific_impulse": {
        "chamber_temperature_k": 3500.0,
        "pressure_ratio": 0.01,
        "gamma": 1.22,
        "molecular_weight": 23.3,
    },
    "throat_mass_flux": {
        "chamber_pressure_pa": 7e6,
        "chamber_temperature_k": 3500.0,
        "gamma": 1.22,
        "molecular_weight": 23.3,
    },
    # static stability
    "center_of_pressure": {
        "nose_shape": "ogive",
        "nose_length_m": 0.15,
        "body_diameter_m": 0.025,
        "fin_count": 3,
        "fin_root_chord_m": 0.05,
        "fin_tip_chord_m": 0.025,
        "fin_semi_span_m": 0.03,
        "fin_sweep_length_m": 0.02,
        "fin_position_from_nose_m": 0.5,
    },
    "static_margin": {
        "cp_from_nose_m": 0.442,
        "cg_from_nose_m": 0.35,
        "reference_diameter_m": 0.025,
    },
    # aerothermodynamics
    "stagnation_temperature": {"static_temperature_k": 220.0, "mach": 3.0},
    "recovery_temperature": {"static_temperature_k": 220.0, "mach": 3.0},
    "sutton_graves_heat_flux": {"density_kg_m3": 1e-4, "velocity_ms": 7500.0, "nose_radius_m": 1.0},
    "ballistic_entry_peak_deceleration": {
        "entry_velocity_ms": 7800.0,
        "flight_path_angle_deg": 30.0,
    },
    # mission design
    "rocket_delta_v": {
        "specific_impulse_s": 320.0,
        "initial_mass_kg": 10000.0,
        "final_mass_kg": 2000.0,
    },
    "multi_stage_delta_v": {
        "stages": [
            {
                "specific_impulse_s": 300.0,
                "dry_mass_kg": 1000.0,
                "propellant_mass_kg": 8000.0,
                "payload_mass_kg": 2000.0,
            },
            {
                "specific_impulse_s": 350.0,
                "dry_mass_kg": 500.0,
                "propellant_mass_kg": 1000.0,
                "payload_mass_kg": 500.0,
            },
        ]
    },
    "payload_fraction": {
        "delta_v_required_ms": 9000.0,
        "specific_impulse_s": 320.0,
        "inert_mass_fraction": 0.1,
    },
    "thrust_to_weight": {"thrust_n": 1e6, "mass_kg": 50000.0},
    "composite_cg": {"masses": [1.0, 2.0, 3.0], "positions": [[0, 0, 0], [1, 0, 0], [2, 0, 0]]},
    "propellant_tank_sizing": {"propellant_volume_m3": 10.0},
    # orbital mechanics
    "orbital_velocity": {"altitude_m": 400000.0},
    "hohmann_transfer": {"radius1_m": 6678137.0, "radius2_m": 42164137.0},
    "vis_viva_velocity": {"radius_m": 6778137.0, "semi_major_axis_m": 6778137.0},
    "plane_change_delta_v": {"velocity_ms": 7700.0, "inclination_change_deg": 28.5},
    "orbital_period": {"semi_major_axis_m": 6778137.0},
    # trajectory & vehicle sizing
    "simulate_ascent": {
        "initial_mass_kg": 1000.0,
        "dry_mass_kg": 400.0,
        "specific_impulse_s": 250.0,
        "mass_flow_rate_kg_s": 20.0,
        "reference_area_m2": 0.2,
        "dt": 0.1,
    },
    "size_vehicle": {
        "payload_mass_kg": 500.0,
        "delta_v_target_ms": 3000.0,
        "specific_impulse_s": 320.0,
        "inert_mass_fraction": 0.1,
    },
    # optimization
    "optimize_staging": {
        "delta_v_target_ms": 9000.0,
        "stages": [
            {"specific_impulse_s": 300.0, "structural_ratio": 0.1},
            {"specific_impulse_s": 340.0, "structural_ratio": 0.08},
        ],
    },
    "optimize_design": {
        "tool_name": "rocket_delta_v",
        "fixed_params": {"initial_mass_kg": 1000.0, "final_mass_kg": 400.0},
        "variable": "specific_impulse_s",
        "bounds": [200.0, 400.0],
        "objective_key": "delta_v_ms",
        "sense": "max",
    },
    # standards & reliability
    "design_review_report": {
        "items": [
            {"name": "spar", "allowable_stress_pa": 276e6, "actual_stress_pa": 150e6},
            {"name": "skin", "margin_of_safety": 0.2},
        ]
    },
    "fmea_report": {
        "items": [
            {"failure_mode": "seal leak", "severity": 8, "occurrence": 3, "detection": 4},
            {"failure_mode": "valve stuck", "severity": 9, "occurrence": 2, "detection": 6},
        ]
    },
}


async def _registered_names() -> set[str]:
    return {t.name for t in await mcp.list_tools()}


def test_valid_calls_cover_every_computational_tool():
    """Guard: if a new computational tool is added, it must get a happy-path call."""
    registered = asyncio.run(_registered_names())
    meta = {
        "cite_tool",
        "list_references",
        "list_validation_benchmarks",
        "validate_result",
        "parameter_sweep",
        "propagate_uncertainty",
        "list_materials",
        "list_standards",
        # visualization tools are covered by tests/test_viz.py (image/data outputs)
        "plot_beam_diagrams",
        "plot_drag_polar",
        "plot_nozzle_contour",
        "plot_isa_profile",
        "plot_trajectory",
    }
    missing = sorted(registered - meta - set(VALID_CALLS))
    assert not missing, f"tools without a happy-path call: {missing}"


@pytest.mark.parametrize("tool_name", sorted(VALID_CALLS))
def test_tool_happy_path(tool_name: str):
    result = asyncio.run(mcp.call_tool(tool_name, VALID_CALLS[tool_name]))
    data = json.loads(result[0].text)
    assert isinstance(data, dict)
    assert not data.get("error"), f"{tool_name} returned an error: {data}"
