"""Aircraft-specific aerodynamic analysis tools.

Covers subsonic and supersonic fixed-wing aircraft, as well as
applicable relations for high-speed drones and missiles.

References:
    - Anderson, "Aircraft Performance and Design" (Ch. 3, 6)
      Lift curve slope (lifting line theory), drag polar,
      Breguet range and endurance equations.
    - Anderson, "Fundamentals of Aerodynamics", 6th Ed. (Ch. 5)
      Subsonic: Prandtl-Glauert compressibility correction.
      Supersonic: linear thin airfoil theory.
    - Raymer, "Aircraft Design: A Conceptual Approach", 5th Ed.
      Wing loading and stall speed estimation.
"""

import numpy as np
from numba import njit

GAMMA = 1.4
R_AIR = 287.05


@njit(cache=True)
def _lift_curve_slope_2d(mach: float, gamma: float = GAMMA):
    """2D lift curve slope a0 (per radian)."""
    if mach < 1.0:
        # Prandtl-Glauert compressibility correction
        beta = np.sqrt(1.0 - mach**2)
        return 2.0 * np.pi / beta
    else:
        # Supersonic thin airfoil theory
        return 4.0 / np.sqrt(mach**2 - 1.0)


def lift_curve_slope(
    mach: float,
    aspect_ratio: float,
    taper_ratio: float = 1.0,
    sweep_deg: float = 0.0,
    oswald_efficiency: float = 0.85,
) -> dict:
    """Compute 3D wing lift curve slope CL_alpha.

    Used for: aircraft stability analysis, drone control surface sizing,
    and preliminary wing design.

    Args:
        mach: Freestream Mach number
        aspect_ratio: Wing aspect ratio (b^2 / S)
        taper_ratio: Tip chord / root chord (default 1.0 for rectangular)
        sweep_deg: Quarter-chord sweep angle in degrees
        oswald_efficiency: Oswald span efficiency factor (default 0.85)

    Returns:
        dict with cl_alpha_2d, cl_alpha_3d, and related parameters
    """
    if aspect_ratio <= 0:
        raise ValueError("aspect_ratio must be > 0")
    if mach < 0.0:
        raise ValueError("mach must be >= 0")
    # Prandtl-Glauert (subsonic) and linear supersonic theory both diverge at M = 1 and
    # are invalid through the transonic regime. Reject it rather than return a huge or
    # singular slope (the previous code returned inf at M = 1 with no error).
    if 0.8 < mach < 1.2:
        raise ValueError(
            "Transonic regime (0.8 < M < 1.2) is not modeled: Prandtl-Glauert and linear "
            "supersonic theory both break down near M = 1. Use a transonic method instead."
        )

    a0 = _lift_curve_slope_2d(mach, GAMMA)
    sweep_rad = np.radians(sweep_deg)

    # Helmbold correction for finite aspect ratio (subsonic)
    if mach < 1.0:
        # Modified lifting line theory with compressibility
        a = (a0 * np.cos(sweep_rad)) / (
            1.0 + (a0 * np.cos(sweep_rad)) / (np.pi * aspect_ratio * oswald_efficiency)
        )
    else:
        # Supersonic linear theory for finite wings. The tip correction is only valid for
        # a supersonic leading edge, i.e. 2*AR*sqrt(M^2-1) > 1; below that it goes to zero
        # or negative and the model does not apply.
        beta_suptip = 2.0 * aspect_ratio * np.sqrt(mach**2 - 1.0)
        if beta_suptip <= 1.0:
            raise ValueError(
                "Supersonic finite-wing lift slope is invalid here: 2*AR*sqrt(M^2-1) <= 1 "
                "(subsonic leading edge). Increase aspect ratio or Mach, or use a panel method."
            )
        a = (4.0 / np.sqrt(mach**2 - 1.0)) * (1.0 - 1.0 / beta_suptip)

    # Induced drag factor
    k_induced = 1.0 / (np.pi * aspect_ratio * oswald_efficiency)

    return {
        "mach": mach,
        "aspect_ratio": aspect_ratio,
        "taper_ratio": taper_ratio,
        "sweep_deg": sweep_deg,
        "oswald_efficiency": oswald_efficiency,
        "cl_alpha_2d_per_rad": round(a0, 4),
        "cl_alpha_3d_per_rad": round(a, 4),
        "cl_alpha_3d_per_deg": round(np.radians(a), 6),
        "induced_drag_factor_k": round(k_induced, 6),
    }


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
    """Compute drag coefficient: CD = CD0 + K*CL^2 + wave drag.

    Wave (compressibility) drag uses the Korn drag-divergence equation, which depends on
    thickness-to-chord, quarter-chord sweep, and CL:
        M_dd = kappa/cos(L) - (t/c)/cos^2(L) - CL/(10*cos^3(L))
    with a fourth-power drag rise for M > M_dd (Lock's approximation, cd_wave = 20*(M-M_dd)^4).
    kappa (technology_factor) is ~0.87 for conventional airfoils, ~0.95 for supercritical.
    (The previous code used an arbitrary 0.1*(M-0.7)^3 independent of the airfoil.)

    Used for: aircraft performance analysis, range/endurance calculations, and L/D optimization.
    """
    if aspect_ratio <= 0:
        raise ValueError("aspect_ratio must be > 0")
    if mach < 0.0:
        raise ValueError("mach must be >= 0")
    if not 0.0 < thickness_to_chord < 1.0:
        raise ValueError("thickness_to_chord must be in (0, 1)")

    k = 1.0 / (np.pi * aspect_ratio * oswald_efficiency)
    cd_induced = k * cl**2
    cd = cd0 + cd_induced

    # Wave drag via the Korn drag-divergence equation.
    cd_wave = 0.0
    m_dd = None
    if mach > 0.0:
        cos_sweep = np.cos(np.radians(sweep_deg))
        m_dd = (
            technology_factor / cos_sweep
            - thickness_to_chord / cos_sweep**2
            - abs(cl) / (10.0 * cos_sweep**3)
        )
        if mach > m_dd:
            cd_wave = 20.0 * (mach - m_dd) ** 4
            cd += cd_wave

    ld_ratio = cl / cd if cd > 0.0 else 0.0

    return {
        "lift_coefficient": cl,
        "drag_coefficient": round(cd, 6),
        "cd0": cd0,
        "cd_induced": round(cd_induced, 6),
        "cd_wave": round(cd_wave, 6),
        "cd_compressibility": round(cd_wave, 6),  # backward-compatible alias
        "drag_divergence_mach": round(float(m_dd), 4) if m_dd is not None else None,
        "lift_to_drag_ratio": round(ld_ratio, 2),
        "aspect_ratio": aspect_ratio,
        "oswald_efficiency": oswald_efficiency,
        "thickness_to_chord": thickness_to_chord,
        "sweep_deg": sweep_deg,
        "mach": mach,
    }


def breguet_range(
    lift_to_drag_ratio: float,
    specific_fuel_consumption: float,
    velocity: float,
    initial_mass_kg: float,
    final_mass_kg: float,
) -> dict:
    """Compute aircraft range using the Breguet range equation.

    Range = (V / SFC) * (L/D) * ln(Wi / Wf)

    Used for: aircraft mission planning, fuel load estimation,
    and UAV endurance calculations.

    Args:
        lift_to_drag_ratio: L/D (dimensionless)
        specific_fuel_consumption: SFC in kg/(N·s) or lb/(lbf·hr)
        velocity: True airspeed in m/s
        initial_mass_kg: Initial mass including fuel in kg
        final_mass_kg: Final mass (burned out) in kg

    Returns:
        dict with range_m, range_km, range_nm, endurance_s, endurance_hr
    """
    if lift_to_drag_ratio <= 0:
        raise ValueError("L/D must be > 0")
    if specific_fuel_consumption <= 0:
        raise ValueError("SFC must be > 0")
    if velocity <= 0:
        raise ValueError("velocity must be > 0")
    if initial_mass_kg <= 0 or final_mass_kg <= 0:
        raise ValueError("masses must be > 0")
    if final_mass_kg >= initial_mass_kg:
        raise ValueError("final_mass must be less than initial_mass")

    # Convert SFC if given in imperial units (lb/(lbf·hr))
    # Typical jet SFC: ~0.00002 kg/(N·s) or ~0.6 lb/(lbf·hr)
    sfc_si = specific_fuel_consumption
    if specific_fuel_consumption > 1e-3:  # Likely imperial lb/(lbf·hr)
        sfc_si = specific_fuel_consumption * 2.832e-5  # Convert to kg/(N·s)

    # Jet Breguet range with thrust (mass-specific) SFC in kg/(N.s):
    #   R = (V / (g * SFC)) * (L/D) * ln(Wi / Wf).
    # The g was previously missing, overstating range by ~9.8x and making the units
    # velocity^2 rather than length; it also broke range == V * endurance.
    range_m = (
        (velocity / (9.80665 * sfc_si))
        * lift_to_drag_ratio
        * np.log(initial_mass_kg / final_mass_kg)
    )
    endurance_s = range_m / velocity

    return {
        "range_m": round(range_m, 1),
        "range_km": round(range_m / 1000.0, 2),
        "range_nm": round(range_m / 1852.0, 2),
        "endurance_s": round(endurance_s, 1),
        "endurance_hr": round(endurance_s / 3600.0, 2),
        "fuel_fraction": round(1.0 - final_mass_kg / initial_mass_kg, 4),
        "lift_to_drag_ratio": lift_to_drag_ratio,
        "sfc_kg_ns": round(sfc_si, 8),
    }


def breguet_endurance(
    lift_to_drag_ratio: float,
    specific_fuel_consumption: float,
    initial_mass_kg: float,
    final_mass_kg: float,
) -> dict:
    """Compute aircraft endurance using the Breguet endurance equation.

    Endurance = (1 / SFC) * (L/D) * ln(Wi / Wf)  [for propeller aircraft]
    or = (1 / SFC) * (L/D) * ln(Wi / Wf) / g  [for jet aircraft with thrust SFC]

    This version uses thrust SFC (kg/(N·s)) for jet aircraft.
    """
    if lift_to_drag_ratio <= 0:
        raise ValueError("L/D must be > 0")
    if specific_fuel_consumption <= 0:
        raise ValueError("SFC must be > 0")
    if initial_mass_kg <= 0 or final_mass_kg <= 0:
        raise ValueError("masses must be > 0")
    if final_mass_kg >= initial_mass_kg:
        raise ValueError("final_mass must be less than initial_mass")

    sfc_si = specific_fuel_consumption
    if specific_fuel_consumption > 1e-3:
        sfc_si = specific_fuel_consumption * 2.832e-5

    endurance_s = (
        (1.0 / sfc_si) * lift_to_drag_ratio * np.log(initial_mass_kg / final_mass_kg) / 9.80665
    )

    return {
        "endurance_s": round(endurance_s, 1),
        "endurance_hr": round(endurance_s / 3600.0, 2),
        "fuel_fraction": round(1.0 - final_mass_kg / initial_mass_kg, 4),
        "lift_to_drag_ratio": lift_to_drag_ratio,
        "sfc_kg_ns": round(sfc_si, 8),
    }


def wing_loading(
    weight_n: float,
    wing_area_m2: float,
) -> dict:
    """Compute wing loading and related performance metrics.

    Used for: aircraft conceptual design, takeoff performance estimation,
    and stall speed calculation.
    """
    if weight_n <= 0 or wing_area_m2 <= 0:
        raise ValueError("weight and wing_area must be > 0")

    ws = weight_n / wing_area_m2  # N/m²
    ws_psf = ws * 0.020885  # Convert to lb/ft²

    # Stall speed at sea level (CL_max ≈ 1.5 for clean, 2.0 with flaps)
    rho_sl = 1.225
    cl_max_clean = 1.5
    cl_max_flaps = 2.0
    v_stall_clean = np.sqrt(2.0 * ws / (rho_sl * cl_max_clean))
    v_stall_flaps = np.sqrt(2.0 * ws / (rho_sl * cl_max_flaps))

    return {
        "wing_loading_pa": round(ws, 2),
        "wing_loading_psf": round(ws_psf, 2),
        "wing_area_m2": wing_area_m2,
        "weight_n": weight_n,
        "stall_speed_clean_ms": round(v_stall_clean, 2),
        "stall_speed_clean_knots": round(v_stall_clean * 1.94384, 1),
        "stall_speed_flaps_ms": round(v_stall_flaps, 2),
        "stall_speed_flaps_knots": round(v_stall_flaps * 1.94384, 1),
    }
