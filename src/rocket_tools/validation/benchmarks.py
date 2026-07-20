"""Curated validation benchmarks with expected values and references.

Each benchmark includes:
- tool_name: The rocket-tools function to validate
- inputs: Input parameters
- expected: Expected output values (with tolerance)
- reference: Primary source for the expected value
- tolerance: Acceptable error margin
"""

from typing import Any

_BENCHMARKS: dict[str, dict[str, Any]] = {
    # ---- ISA Atmosphere ----
    "isa_sea_level": {
        "tool_name": "isa_atmosphere",
        "inputs": {"altitude_m": 0.0},
        "expected": {
            "temperature_k": 288.15,
            "pressure_pa": 101325.0,
            "density_kg_m3": 1.225,
            "speed_of_sound_m_s": 340.29,
        },
        "tolerance": 0.01,
        "reference": "NASA-TM-X-74335: U.S. Standard Atmosphere 1976, Table 1 (Sea Level)",
    },
    "isa_11000m": {
        "tool_name": "isa_atmosphere",
        "inputs": {"altitude_m": 11000.0},
        "expected": {
            "temperature_k": 216.65,
            "pressure_pa": 22632.0,
            "density_kg_m3": 0.3639,
        },
        "tolerance": 0.01,
        "reference": "NASA-TM-X-74335: U.S. Standard Atmosphere 1976, Table 1 (Tropopause)",
    },
    "isa_25000m": {
        "tool_name": "isa_atmosphere",
        "inputs": {"altitude_m": 25000.0},
        "expected": {
            "temperature_k": 221.65,
            "pressure_pa": 2511.0,
            "density_kg_m3": 0.0395,
        },
        "tolerance": 0.01,
        "reference": (
            "NASA-TM-X-74335: U.S. Standard Atmosphere 1976, 20-32 km layer "
            "(base 20 km: T=216.65 K, P=5474.89 Pa, lapse +0.001 K/m). "
            "At 25 km: T=221.65 K, P=2511 Pa, rho=0.03947 kg/m^3"
        ),
    },
    "isa_47000m": {
        "tool_name": "isa_atmosphere",
        "inputs": {"altitude_m": 47000.0},
        "expected": {
            "temperature_k": 270.65,
            "pressure_pa": 110.91,
        },
        "tolerance": 0.01,
        "reference": "NASA-TM-X-74335: U.S. Standard Atmosphere 1976, Table 1 (47 km stratopause)",
    },
    "isa_71000m": {
        "tool_name": "isa_atmosphere",
        "inputs": {"altitude_m": 71000.0},
        "expected": {
            "temperature_k": 214.65,
            "pressure_pa": 3.9564,
        },
        "tolerance": 0.01,
        "reference": "NASA-TM-X-74335: U.S. Standard Atmosphere 1976, Table 1 (71 km layer base)",
    },
    # ---- Beam Deflection ----
    "beam_simply_supported_point": {
        "tool_name": "beam_analysis",
        "inputs": {
            "load": 1000.0,
            "length": 2.0,
            "youngs_modulus": 200e9,
            "cross_section": {"type": "rectangle", "width": 0.05, "height": 0.01},
            "load_type": "point_midspan",
            "support_type": "simply_supported",
        },
        "expected": {
            "max_deflection_m": 0.2,
            "bending_stress_pa": 600000000.0,
        },
        "tolerance": 0.005,
        "reference": (
            "Roark's Formulas, 8th Ed., Table 8.1, Case 1: "
            "Simply supported, center load. delta = PL^3 / (48EI), sigma = (PL/4)(c/I). "
            "P=1000 N, L=2 m, E=200 GPa, 50x10 mm rect (I=4.1667e-9 m^4): "
            "delta=0.2 m, sigma=600 MPa"
        ),
    },
    "beam_cantilever_point": {
        "tool_name": "beam_analysis",
        "inputs": {
            "load": 500.0,
            "length": 1.5,
            "youngs_modulus": 69e9,
            "cross_section": {"type": "rectangle", "width": 0.04, "height": 0.008},
            "load_type": "point_midspan",
            "support_type": "cantilever",
        },
        "expected": {
            "max_deflection_m": 4.776664,
            "bending_stress_pa": 1757812500.0,
        },
        "tolerance": 0.005,
        "reference": (
            "Roark's Formulas, 8th Ed., Table 8.1, Case 4: "
            "Cantilever, end load. delta = PL^3 / (3EI), sigma = (PL)(c/I). "
            "P=500 N, L=1.5 m, E=69 GPa, 40x8 mm rect (I=1.7067e-9 m^4): "
            "delta=4.7767 m, sigma=1757.8 MPa"
        ),
    },
    # ---- Skin Friction ----
    "skin_friction_laminar": {
        "tool_name": "skin_friction_coefficient",
        "inputs": {"reynolds_number": 1e5, "flow_regime": "laminar"},
        "expected": {"skin_friction_coefficient": 0.0042},
        "tolerance": 0.01,
        "reference": "Blasius (1908): cf = 1.328 / sqrt(Re) = 1.328 / sqrt(1e5) = 0.00420",
    },
    "skin_friction_turbulent": {
        "tool_name": "skin_friction_coefficient",
        "inputs": {"reynolds_number": 1e7, "flow_regime": "turbulent"},
        "expected": {"skin_friction_coefficient": 0.002357},
        "tolerance": 0.01,
        "reference": (
            "Prandtl 1/7-power turbulent local skin friction: "
            "cf = 0.0592 / Re^0.2 = 0.0592 / (1e7)^0.2 = 0.002357. "
            "(Do not confuse with the 0.074/Re^0.2 flat-plate average drag coefficient.)"
        ),
    },
    # ---- Rocket Equation ----
    "rocket_delta_v_standard": {
        "tool_name": "rocket_delta_v",
        "inputs": {
            "specific_impulse_s": 320,
            "initial_mass_kg": 10000,
            "final_mass_kg": 2000,
        },
        "expected": {
            "delta_v_ms": 5050.62,
            "mass_ratio": 5.0,
        },
        "tolerance": 0.005,
        "reference": 'Sutton & Biblarz, "Rocket Propulsion Elements", 9th Ed., Eq. 4-6. '
        "delta-v = Isp * g0 * ln(m0/mf) = 320 * 9.80665 * ln(5) = 5050.6 m/s",
    },
    # ---- Isentropic Flow ----
    "isentropic_mach_2": {
        "tool_name": "isentropic_flow",
        "inputs": {"mach": 2.0, "gamma": 1.4},
        "expected": {
            "temperature_ratio": 0.5556,
            "pressure_ratio": 0.1278,
            "density_ratio": 0.2300,
        },
        "tolerance": 0.005,
        "reference": 'Anderson, "Fundamentals of Aerodynamics", 6th Ed., Table A.1 (Appendix A). '
        "For M=2, gamma=1.4: T/T0=0.5556, P/P0=0.1278, rho/rho0=0.2300",
    },
    # ---- Normal Shock ----
    "normal_shock_mach_2": {
        "tool_name": "normal_shock",
        "inputs": {"mach1": 2.0, "gamma": 1.4},
        "expected": {
            "mach_downstream": 0.5774,
            "pressure_ratio": 4.500,
            "density_ratio": 2.667,
            "temperature_ratio": 1.687,
            "stagnation_pressure_ratio": 0.7209,
        },
        "tolerance": 0.005,
        "reference": 'Anderson, "Fundamentals of Aerodynamics", 6th Ed., Table A.2 / NACA 1135. '
        "For M1=2, gamma=1.4: M2=0.5774, P2/P1=4.50, rho2/rho1=2.667, T2/T1=1.687, p02/p01=0.7209",
    },
    # ---- Oblique Shock (weak solution) ----
    "oblique_shock_m2_theta15": {
        "tool_name": "oblique_shock",
        "inputs": {"mach1": 2.0, "deflection_deg": 15.0},
        "expected": {
            "wave_angle_deg": 45.34,
            "mach_downstream": 1.4457,
            "pressure_ratio": 2.1947,
        },
        "tolerance": 0.005,
        "reference": (
            'Anderson, "Fundamentals of Aerodynamics", 6th Ed., Ch. 9 (theta-beta-M). '
            "M1=2, theta=15 deg, gamma=1.4, WEAK solution: beta=45.34 deg, M2=1.446, p2/p1=2.195"
        ),
    },
    # ---- Orbital Velocity ----
    "orbital_velocity_leo": {
        "tool_name": "orbital_velocity",
        "inputs": {"altitude_m": 400e3},
        "expected": {
            "circular_velocity_kms": 7.6726,
            "orbital_period_min": 92.41,
        },
        "tolerance": 0.005,
        "reference": (
            'Vallado, "Fundamentals of Astrodynamics and Applications", '
            "4th Ed., Eq. 1-28. Mean Earth radius 6371 km + 400 km alt = r=6771 km. "
            "v_c = sqrt(mu/r) = sqrt(3.986004e14 / 6771000) = 7.6726 km/s; "
            "period = 2*pi*sqrt(r^3/mu) = 92.41 min"
        ),
    },
    # ---- Propulsion Thermochemistry ----
    "characteristic_velocity_lox_rp1": {
        "tool_name": "characteristic_velocity",
        "inputs": {"chamber_temperature_k": 3500.0, "gamma": 1.22, "molecular_weight": 23.3},
        "expected": {"characteristic_velocity_ms": 1713.043},
        "tolerance": 0.001,
        "reference": (
            'Sutton & Biblarz, "Rocket Propulsion Elements", 9th Ed., Eq. 3-32. '
            "c* = sqrt(R*Tc)/Gamma; Tc=3500 K, gamma=1.22, M=23.3 kg/kmol -> 1713.0 m/s"
        ),
    },
    # ---- Aerothermodynamics ----
    "stagnation_temperature_mach3": {
        "tool_name": "stagnation_temperature",
        "inputs": {"static_temperature_k": 220.0, "mach": 3.0},
        "expected": {"stagnation_temperature_k": 616.0},
        "tolerance": 0.001,
        "reference": (
            'Anderson, "Hypersonic and High-Temperature Gas Dynamics", 2nd Ed. '
            "T0 = T*(1 + (gamma-1)/2*M^2) = 220*(1 + 0.2*9) = 616 K"
        ),
    },
    "ballistic_entry_allen_eggers": {
        "tool_name": "ballistic_entry_peak_deceleration",
        "inputs": {"entry_velocity_ms": 7800.0, "flight_path_angle_deg": 30.0},
        "expected": {"peak_deceleration_g": 79.689, "velocity_at_peak_ms": 4730.94},
        "tolerance": 0.001,
        "reference": (
            "Allen & Eggers, NACA TR 1381 (1958). "
            "a_max = V^2*sin(gamma)/(2*e*H), V at peak = V/sqrt(e). "
            "V=7800 m/s, gamma=30 deg, H=7160 m: a_max=79.69 g, V_peak=4730.9 m/s"
        ),
    },
    # ---- Hohmann Transfer ----
    "hohmann_leo_to_geo": {
        "tool_name": "hohmann_transfer",
        "inputs": {"radius1_m": 6678137.0, "radius2_m": 42164137.0},
        "expected": {
            "delta_v1_ms": 2425.7,
            "delta_v2_ms": 1466.8,
            "total_delta_v_ms": 3892.5,
            "transfer_time_hr": 5.275,
        },
        "tolerance": 0.005,
        "reference": (
            'Curtis, "Orbital Mechanics for Engineering Students", 3rd Ed., Ch. 6. '
            "300 km LEO (r=6678.137 km) to GEO (r=42164.137 km), mu=3.986004418e14: "
            "dv1=2.4257, dv2=1.4668, total=3.8925 km/s, transfer time 5.275 h"
        ),
    },
    # ---- Section Properties ----
    "section_rectangle": {
        "tool_name": "section_properties",
        "inputs": {"shape": "rectangle", "width": 0.1, "height": 0.2},
        "expected": {
            "area_m2": 0.02,
            "i_xx_m4": 6.6667e-5,
            "s_xx_m3": 6.6667e-4,
        },
        "tolerance": 0.005,
        "reference": "Roark's Formulas, 8th Ed., Table A.1: Rectangular section. "
        "A=bh=0.02, I=bh^3/12=6.667e-5, S=bh^2/6=6.667e-4",
    },
    # ---- NACA Airfoil Drag Polar (Validation against wind tunnel) ----
    "naca_0012_drag_polar": {
        "tool_name": "aero_analysis",
        "inputs": {
            "velocity": 60.0,
            "altitude_m": 0,
            "characteristic_length": 0.6096,
            "reference_area": 0.0929,
            "lift": 0.0,
            "drag": 0.0,
        },
        "expected": {
            "reynolds_number": 2.5e6,
            "mach_number": 0.176,
        },
        "tolerance": 0.05,
        "reference": 'Abbott & von Doenhoff, "Theory of Wing Sections", Dover 1959. '
        "NACA 0012 drag data at Re ~ 3x10^6 (Langley wind tunnel). "
        "Note: This benchmark validates Re and Mach computation only; "
        "actual drag polar requires airfoil-specific data not in the generic tool.",
    },
}


def list_benchmarks() -> list[str]:
    """Return a list of all available benchmark names."""
    return sorted(_BENCHMARKS.keys())


def get_benchmark(name: str) -> dict[str, Any]:
    """Get a specific benchmark by name.

    Args:
        name: Benchmark identifier (e.g., "isa_sea_level", "beam_simply_supported_point")

    Returns:
        dict with tool_name, inputs, expected, tolerance, reference

    Raises:
        ValueError: If benchmark name is not found.
    """
    if name not in _BENCHMARKS:
        available = ", ".join(list_benchmarks())
        raise ValueError(f"Unknown benchmark '{name}'. Available: {available}")
    return _BENCHMARKS[name].copy()


def validate_benchmark(
    name: str,
    actual_result: dict[str, Any],
) -> dict[str, Any]:
    """Compare an actual tool result against a benchmark.

    Args:
        name: Benchmark name
        actual_result: Output dict from the tool

    Returns:
        dict with pass/fail status, errors, and reference
    """
    benchmark = get_benchmark(name)
    expected = benchmark["expected"]
    tolerance = benchmark["tolerance"]
    reference = benchmark["reference"]

    errors = []
    passed = True

    for key, expected_value in expected.items():
        if key not in actual_result:
            errors.append(f"Missing key: {key}")
            passed = False
            continue

        actual_value = actual_result[key]
        if expected_value == 0:
            relative_error = abs(actual_value)
        else:
            relative_error = abs((actual_value - expected_value) / expected_value)

        if relative_error > tolerance:
            errors.append(
                f"{key}: expected {expected_value}, got {actual_value}, "
                f"relative error {relative_error:.4f} > tolerance {tolerance}"
            )
            passed = False

    return {
        "benchmark": name,
        "tool_name": benchmark["tool_name"],
        "passed": passed,
        "errors": errors,
        "reference": reference,
        "tolerance": tolerance,
    }
