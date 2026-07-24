"""Aerothermodynamics for high-speed flight and atmospheric entry.

Covers stagnation and recovery temperature, stagnation-point convective heat
flux (Sutton-Graves), and ballistic-entry peak deceleration (Allen-Eggers).

References:
    - Anderson, "Hypersonic and High-Temperature Gas Dynamics", 2nd Ed. (Ch. 6)
      Stagnation and adiabatic-wall (recovery) temperature; recovery factor
      r = Pr^0.5 (laminar), r = Pr^(1/3) (turbulent).
    - Sutton, K. & Graves, R. A., NASA TR R-376 (1971)
      Stagnation-point convective heating: q = C*sqrt(rho/Rn)*V^3,
      C = 1.7415e-4 for Earth air (SI inputs -> W/m^2).
    - Allen, H. J. & Eggers, A. J., NACA TR 1381 (1958)
      Ballistic entry: peak deceleration and the velocity at which it occurs.
"""

import numpy as np

# Sutton-Graves constant for Earth air, kg^0.5/m: q in W/m^2 with rho in
# kg/m^3, nose radius in m, velocity in m/s (Sutton & Graves, NASA TR R-376).
SUTTON_GRAVES_EARTH = 1.7415e-4
G_STD = 9.80665


def stagnation_temperature(static_temperature_k: float, mach: float, gamma: float = 1.4) -> dict:
    """Total (stagnation) temperature of an adiabatic compressible flow.

    T0 = T * (1 + (gamma-1)/2 * M^2). This is the temperature a perfectly
    insulated stagnation point would reach; the real wall sees the (lower)
    recovery temperature.
    """
    if static_temperature_k <= 0:
        raise ValueError("static_temperature_k must be > 0")
    if mach < 0:
        raise ValueError("mach must be >= 0")
    if gamma <= 1.0:
        raise ValueError("gamma must be > 1")

    ratio = 1.0 + 0.5 * (gamma - 1.0) * mach**2
    t0 = static_temperature_k * ratio
    return {
        "stagnation_temperature_k": round(float(t0), 3),
        "static_temperature_k": static_temperature_k,
        "temperature_ratio": round(float(ratio), 5),
        "mach": mach,
    }


def recovery_temperature(
    static_temperature_k: float,
    mach: float,
    gamma: float = 1.4,
    prandtl: float = 0.71,
    regime: str = "laminar",
) -> dict:
    """Adiabatic-wall (recovery) temperature seen by a real boundary layer.

    Tr = T * (1 + r*(gamma-1)/2 * M^2), with recovery factor r = Pr^0.5
    (laminar) or r = Pr^(1/3) (turbulent). Air Pr ~ 0.71.
    """
    if static_temperature_k <= 0:
        raise ValueError("static_temperature_k must be > 0")
    if mach < 0:
        raise ValueError("mach must be >= 0")
    if gamma <= 1.0:
        raise ValueError("gamma must be > 1")
    if prandtl <= 0:
        raise ValueError("prandtl must be > 0")
    if regime not in ("laminar", "turbulent"):
        raise ValueError("regime must be 'laminar' or 'turbulent'")

    recovery_factor = prandtl**0.5 if regime == "laminar" else prandtl ** (1.0 / 3.0)
    tr = static_temperature_k * (1.0 + recovery_factor * 0.5 * (gamma - 1.0) * mach**2)
    return {
        "recovery_temperature_k": round(float(tr), 3),
        "recovery_factor": round(float(recovery_factor), 4),
        "static_temperature_k": static_temperature_k,
        "regime": regime,
        "mach": mach,
    }


def sutton_graves_heat_flux(
    density_kg_m3: float,
    velocity_ms: float,
    nose_radius_m: float,
    constant: float = SUTTON_GRAVES_EARTH,
) -> dict:
    """Stagnation-point convective heat flux via the Sutton-Graves correlation.

    q = C * sqrt(rho / Rn) * V^3, C = 1.7415e-4 for Earth air (result in W/m^2).
    A cold-wall convective estimate for blunt-body entry; excludes radiative heating.
    """
    if density_kg_m3 <= 0:
        raise ValueError("density_kg_m3 must be > 0")
    if velocity_ms <= 0:
        raise ValueError("velocity_ms must be > 0")
    if nose_radius_m <= 0:
        raise ValueError("nose_radius_m must be > 0")

    q_wm2 = constant * np.sqrt(density_kg_m3 / nose_radius_m) * velocity_ms**3
    return {
        "heat_flux_w_m2": round(float(q_wm2), 2),
        "heat_flux_w_cm2": round(float(q_wm2) / 1.0e4, 4),
        "heat_flux_mw_m2": round(float(q_wm2) / 1.0e6, 5),
        "nose_radius_m": nose_radius_m,
        "velocity_ms": velocity_ms,
    }


def ballistic_entry_peak_deceleration(
    entry_velocity_ms: float,
    flight_path_angle_deg: float,
    scale_height_m: float = 7160.0,
) -> dict:
    """Peak deceleration of a steep, non-lifting (ballistic) entry: Allen-Eggers.

    a_max = V_e^2 * sin(gamma) / (2 * e * H), independent of ballistic coefficient.
    Peak deceleration always occurs at V = V_e / sqrt(e) ~ 0.6065 * V_e.
    scale_height_m defaults to Earth's ~7160 m.
    """
    if entry_velocity_ms <= 0:
        raise ValueError("entry_velocity_ms must be > 0")
    if not 0.0 < flight_path_angle_deg <= 90.0:
        raise ValueError("flight_path_angle_deg must be in (0, 90]")
    if scale_height_m <= 0:
        raise ValueError("scale_height_m must be > 0")

    gamma = np.radians(flight_path_angle_deg)
    a_max = entry_velocity_ms**2 * np.sin(gamma) / (2.0 * np.e * scale_height_m)
    velocity_at_peak = entry_velocity_ms * np.exp(-0.5)
    return {
        "peak_deceleration_ms2": round(float(a_max), 3),
        "peak_deceleration_g": round(float(a_max) / G_STD, 3),
        "velocity_at_peak_ms": round(float(velocity_at_peak), 2),
        "entry_velocity_ms": entry_velocity_ms,
        "flight_path_angle_deg": flight_path_angle_deg,
    }
