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


def _stumpff_c(z: float) -> float:
    """Stumpff function C(z)."""
    if z > 0:
        return float((1.0 - np.cos(np.sqrt(z))) / z)
    if z < 0:
        return float((np.cosh(np.sqrt(-z)) - 1.0) / (-z))
    return 0.5


def _stumpff_s(z: float) -> float:
    """Stumpff function S(z)."""
    if z > 0:
        sz = np.sqrt(z)
        return float((sz - np.sin(sz)) / sz**3)
    if z < 0:
        sz = np.sqrt(-z)
        return float((np.sinh(sz) - sz) / sz**3)
    return 1.0 / 6.0


def lambert_solver(
    r1_m: list[float],
    r2_m: list[float],
    time_of_flight_s: float,
    mu: float = MU_EARTH,
    prograde: bool = True,
) -> dict:
    """Solve Lambert's problem: the transfer orbit connecting two position vectors.

    Given start and end position vectors and a time of flight, returns the required
    departure and arrival velocity vectors of the connecting two-body (Keplerian) orbit,
    via the universal-variable formulation with Stumpff functions and Newton iteration
    (Curtis, Orbital Mechanics for Engineering Students, 3rd Ed., Algorithm 5.2).

    Args:
        r1_m: Initial position vector [x, y, z] in m (from the central body's center).
        r2_m: Final position vector [x, y, z] in m.
        time_of_flight_s: Transfer time in seconds.
        mu: Gravitational parameter of the central body in m^3/s^2 (default Earth).
        prograde: True for a prograde transfer (0 <= i < 90 deg), False for retrograde.
    """
    if len(r1_m) != 3 or len(r2_m) != 3:
        raise ValueError("r1_m and r2_m must each be 3-component vectors")
    if time_of_flight_s <= 0:
        raise ValueError("time_of_flight_s must be > 0")
    if mu <= 0:
        raise ValueError("mu must be > 0")

    r1 = np.asarray(r1_m, dtype=float)
    r2 = np.asarray(r2_m, dtype=float)
    norm1 = float(np.linalg.norm(r1))
    norm2 = float(np.linalg.norm(r2))
    if norm1 == 0.0 or norm2 == 0.0:
        raise ValueError("position vectors must be non-zero")

    c12 = np.cross(r1, r2)
    theta = float(np.arccos(np.clip(np.dot(r1, r2) / (norm1 * norm2), -1.0, 1.0)))
    if prograde:
        if c12[2] < 0.0:
            theta = 2.0 * np.pi - theta
    else:
        if c12[2] >= 0.0:
            theta = 2.0 * np.pi - theta

    sin_theta = np.sin(theta)
    if abs(sin_theta) < 1e-12:
        raise ValueError(
            "transfer angle is 0 or 180 deg (collinear vectors); the orbital plane is "
            "undefined and the universal-variable solver does not apply"
        )
    a_coeff = sin_theta * np.sqrt(norm1 * norm2 / (1.0 - np.cos(theta)))

    def _y(z: float) -> float:
        cz = _stumpff_c(z)
        sz = _stumpff_s(z)
        return float(norm1 + norm2 + a_coeff * (z * sz - 1.0) / np.sqrt(cz))

    # Ratchet the starting z up until y > 0 so the sqrt(y) terms are real.
    z = 0.0
    while _y(z) < 0.0:
        z += 0.1

    root_mu_t = np.sqrt(mu) * time_of_flight_s
    tol = 1e-8
    max_iter = 200
    converged = False
    iterations = 0
    for iterations in range(1, max_iter + 1):
        cz = _stumpff_c(z)
        sz = _stumpff_s(z)
        y = _y(z)
        f_z = (y / cz) ** 1.5 * sz + a_coeff * np.sqrt(y) - root_mu_t
        if abs(z) < 1e-12:
            # At z=0, C(0)=1/2 so y here is y(0); use it directly (Curtis Eq. 5.43 limit).
            dfdz = (np.sqrt(2.0) / 40.0) * y**1.5 + (a_coeff / 8.0) * (
                np.sqrt(y) + a_coeff * np.sqrt(1.0 / (2.0 * y))
            )
        else:
            dfdz = (y / cz) ** 1.5 * (
                (1.0 / (2.0 * z)) * (cz - 3.0 * sz / (2.0 * cz)) + 3.0 * sz**2 / (4.0 * cz)
            ) + (a_coeff / 8.0) * (3.0 * sz / cz * np.sqrt(y) + a_coeff * np.sqrt(cz / y))
        ratio = f_z / dfdz
        z -= ratio
        if abs(ratio) < tol:
            converged = True
            break

    if not converged:
        raise ValueError("Lambert solver did not converge; check inputs / time of flight")

    cz = _stumpff_c(z)
    y = _y(z)
    # Lagrange coefficients.
    f = 1.0 - y / norm1
    g = a_coeff * np.sqrt(y / mu)
    gdot = 1.0 - y / norm2
    v1 = (r2 - f * r1) / g
    v2 = (gdot * r2 - r1) / g

    speed1 = float(np.linalg.norm(v1))
    speed2 = float(np.linalg.norm(v2))
    return {
        "v1_x_ms": round(float(v1[0]), 4),
        "v1_y_ms": round(float(v1[1]), 4),
        "v1_z_ms": round(float(v1[2]), 4),
        "v2_x_ms": round(float(v2[0]), 4),
        "v2_y_ms": round(float(v2[1]), 4),
        "v2_z_ms": round(float(v2[2]), 4),
        "v1_speed_ms": round(speed1, 4),
        "v2_speed_ms": round(speed2, 4),
        "transfer_angle_deg": round(float(np.degrees(theta)), 4),
        "z": round(float(z), 6),
        "iterations": iterations,
    }
