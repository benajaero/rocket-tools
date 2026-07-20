"""Orbital mechanics for mission design: transfers, vis-viva, and plane changes.

All functions are two-body (patched-conic) and default to Earth's standard
gravitational parameter mu = GM = 3.986004418e14 m^3/s^2.

References:
    - Curtis, "Orbital Mechanics for Engineering Students", 3rd Ed. (Ch. 6)
      Hohmann transfer delta-v and transfer time (Example 6.1).
    - Vallado, "Fundamentals of Astrodynamics and Applications", 4th Ed. (Ch. 2, 6)
      Vis-viva equation (Eq. 2-70), orbital period, simple plane change (Eq. 6-19).
    - Bate, Mueller & White, "Fundamentals of Astrodynamics" (Ch. 3)
      Two-body energy and the vis-viva relation.
"""

import numpy as np

# Earth standard gravitational parameter, WGS-84 / EGM (m^3/s^2). Vallado App. D.
MU_EARTH = 3.986004418e14


def vis_viva_velocity(radius_m: float, semi_major_axis_m: float, mu: float = MU_EARTH) -> dict:
    """Orbital speed at a radius via the vis-viva equation: v = sqrt(mu*(2/r - 1/a)).

    radius_m: distance from the central body's center (m).
    semi_major_axis_m: orbit semi-major axis (m); equal to radius_m for a circular orbit.
    """
    if radius_m <= 0:
        raise ValueError("radius_m must be > 0")
    if semi_major_axis_m <= 0:
        raise ValueError("semi_major_axis_m must be > 0")

    term = 2.0 / radius_m - 1.0 / semi_major_axis_m
    if term <= 0:
        raise ValueError("radius_m exceeds the orbit's apoapsis (2/r - 1/a <= 0)")

    v = np.sqrt(mu * term)
    return {
        "velocity_ms": round(float(v), 3),
        "velocity_kms": round(float(v) / 1000.0, 5),
        "radius_m": radius_m,
        "semi_major_axis_m": semi_major_axis_m,
    }


def hohmann_transfer(radius1_m: float, radius2_m: float, mu: float = MU_EARTH) -> dict:
    """Minimum-energy two-impulse Hohmann transfer between coplanar circular orbits.

    Returns the two burns, total delta-v, and the transfer (half-ellipse) time.
    radius1_m / radius2_m are orbital radii (central-body center to orbit), in meters.
    """
    if radius1_m <= 0 or radius2_m <= 0:
        raise ValueError("orbital radii must be > 0")
    if radius1_m == radius2_m:
        raise ValueError("radius1_m and radius2_m must differ (no transfer needed)")

    v1_circ = np.sqrt(mu / radius1_m)
    v2_circ = np.sqrt(mu / radius2_m)
    a_transfer = 0.5 * (radius1_m + radius2_m)

    # Speeds on the transfer ellipse at the departure and arrival radii (vis-viva).
    v_peri = np.sqrt(mu * (2.0 / radius1_m - 1.0 / a_transfer))
    v_apo = np.sqrt(mu * (2.0 / radius2_m - 1.0 / a_transfer))

    delta_v1 = abs(v_peri - v1_circ)
    delta_v2 = abs(v2_circ - v_apo)
    total_delta_v = delta_v1 + delta_v2
    transfer_time_s = np.pi * np.sqrt(a_transfer**3 / mu)

    return {
        "delta_v1_ms": round(float(delta_v1), 3),
        "delta_v2_ms": round(float(delta_v2), 3),
        "total_delta_v_ms": round(float(total_delta_v), 3),
        "total_delta_v_kms": round(float(total_delta_v) / 1000.0, 5),
        "transfer_semi_major_axis_m": round(float(a_transfer), 1),
        "transfer_time_s": round(float(transfer_time_s), 1),
        "transfer_time_hr": round(float(transfer_time_s) / 3600.0, 4),
        "raising_orbit": radius2_m > radius1_m,
    }


def plane_change_delta_v(velocity_ms: float, inclination_change_deg: float) -> dict:
    """Delta-v for a simple (circular, speed-preserving) plane change.

    delta-v = 2 * v * sin(delta_i / 2). Cheapest where orbital speed is lowest
    (high apoapsis), which is why combined maneuvers are done near apogee.
    """
    if velocity_ms <= 0:
        raise ValueError("velocity_ms must be > 0")
    if not 0.0 <= inclination_change_deg <= 180.0:
        raise ValueError("inclination_change_deg must be in [0, 180]")

    di = np.radians(inclination_change_deg)
    delta_v = 2.0 * velocity_ms * np.sin(di / 2.0)
    return {
        "delta_v_ms": round(float(delta_v), 3),
        "delta_v_kms": round(float(delta_v) / 1000.0, 5),
        "velocity_ms": velocity_ms,
        "inclination_change_deg": inclination_change_deg,
    }


def orbital_period(semi_major_axis_m: float, mu: float = MU_EARTH) -> dict:
    """Keplerian orbital period: T = 2*pi*sqrt(a^3 / mu)."""
    if semi_major_axis_m <= 0:
        raise ValueError("semi_major_axis_m must be > 0")

    period_s = 2.0 * np.pi * np.sqrt(semi_major_axis_m**3 / mu)
    return {
        "period_s": round(float(period_s), 2),
        "period_min": round(float(period_s) / 60.0, 4),
        "period_hr": round(float(period_s) / 3600.0, 5),
        "semi_major_axis_m": semi_major_axis_m,
    }
