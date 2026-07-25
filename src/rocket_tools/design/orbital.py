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


def bi_elliptic_transfer(
    radius1_m: float,
    radius2_m: float,
    intermediate_radius_m: float,
    mu: float = MU_EARTH,
) -> dict:
    """Three-impulse bi-elliptic transfer between coplanar circular orbits.

    A bi-elliptic transfer raises apoapsis to an intermediate radius rb (beyond the
    target), coasts to rb, raises periapsis to the target radius, then circularizes. For
    large radius ratios (r2/r1 > ~11.94) with a sufficiently high rb it needs less total
    delta-v than a Hohmann transfer, at the cost of a much longer flight time. Returns the
    three burns, total delta-v and time, and a comparison against the Hohmann transfer.

    Args:
        radius1_m: Initial circular-orbit radius in m.
        radius2_m: Final circular-orbit radius in m.
        intermediate_radius_m: Apoapsis radius rb of the first transfer ellipse in m.
        mu: Gravitational parameter in m^3/s^2 (default Earth).
    """
    if radius1_m <= 0 or radius2_m <= 0:
        raise ValueError("orbital radii must be > 0")
    if radius1_m == radius2_m:
        raise ValueError("radius1_m and radius2_m must differ (no transfer needed)")
    if intermediate_radius_m < radius1_m or intermediate_radius_m < radius2_m:
        raise ValueError(
            "intermediate_radius_m must be >= both orbit radii (the apoapsis is beyond both)"
        )

    v_c1 = np.sqrt(mu / radius1_m)
    v_c2 = np.sqrt(mu / radius2_m)
    rb = intermediate_radius_m

    # Ellipse 1: periapsis r1, apoapsis rb.
    a1 = 0.5 * (radius1_m + rb)
    v_p1 = np.sqrt(mu * (2.0 / radius1_m - 1.0 / a1))
    v_a1 = np.sqrt(mu * (2.0 / rb - 1.0 / a1))
    # Ellipse 2: apoapsis rb, periapsis r2.
    a2 = 0.5 * (radius2_m + rb)
    v_a2 = np.sqrt(mu * (2.0 / rb - 1.0 / a2))
    v_p2 = np.sqrt(mu * (2.0 / radius2_m - 1.0 / a2))

    delta_v1 = abs(v_p1 - v_c1)  # raise apoapsis to rb
    delta_v2 = abs(v_a2 - v_a1)  # raise periapsis to r2
    delta_v3 = abs(v_c2 - v_p2)  # circularize at r2
    total_delta_v = delta_v1 + delta_v2 + delta_v3
    transfer_time_s = np.pi * np.sqrt(a1**3 / mu) + np.pi * np.sqrt(a2**3 / mu)

    hohmann = hohmann_transfer(radius1_m, radius2_m, mu)
    hohmann_dv = hohmann["total_delta_v_ms"]

    return {
        "delta_v1_ms": round(float(delta_v1), 3),
        "delta_v2_ms": round(float(delta_v2), 3),
        "delta_v3_ms": round(float(delta_v3), 3),
        "total_delta_v_ms": round(float(total_delta_v), 3),
        "total_delta_v_kms": round(float(total_delta_v) / 1000.0, 5),
        "transfer_time_s": round(float(transfer_time_s), 1),
        "transfer_time_hr": round(float(transfer_time_s) / 3600.0, 4),
        "hohmann_total_delta_v_ms": hohmann_dv,
        "delta_v_saving_vs_hohmann_ms": round(float(hohmann_dv - total_delta_v), 3),
        "cheaper_than_hohmann": bool(total_delta_v < hohmann_dv),
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


def orbital_elements_from_state(
    position_m: list[float],
    velocity_ms: list[float],
    mu: float = MU_EARTH,
) -> dict:
    """Classical orbital elements from a state vector (position + velocity).

    Converts an inertial position/velocity pair to the six classical (Keplerian)
    orbital elements, following Curtis, Orbital Mechanics for Engineering Students,
    3rd Ed., Algorithm 4.2. Complements lambert_solver: solve for the transfer
    velocity, then read off the resulting orbit's elements.

    Args:
        position_m: Inertial position vector [x, y, z] in m.
        velocity_ms: Inertial velocity vector [vx, vy, vz] in m/s.
        mu: Gravitational parameter of the central body in m^3/s^2 (default Earth).

    Returns eccentricity, inclination, RAAN, argument of perigee, and true anomaly
    (degrees), specific angular momentum, semi-major axis, and apoapsis/periapsis radii.
    Circular and equatorial special cases collapse the undefined angles to 0.
    """
    if len(position_m) != 3 or len(velocity_ms) != 3:
        raise ValueError("position_m and velocity_ms must each be 3-component vectors")
    if mu <= 0:
        raise ValueError("mu must be > 0")

    r_vec = np.asarray(position_m, dtype=float)
    v_vec = np.asarray(velocity_ms, dtype=float)
    r = float(np.linalg.norm(r_vec))
    v = float(np.linalg.norm(v_vec))
    if r == 0.0:
        raise ValueError("position vector must be non-zero")

    vr = float(np.dot(r_vec, v_vec) / r)
    h_vec = np.cross(r_vec, v_vec)
    h = float(np.linalg.norm(h_vec))
    if h == 0.0:
        raise ValueError("angular momentum is zero (rectilinear trajectory); elements undefined")

    inclination = float(np.arccos(np.clip(h_vec[2] / h, -1.0, 1.0)))

    n_vec = np.cross([0.0, 0.0, 1.0], h_vec)
    n = float(np.linalg.norm(n_vec))

    e_vec = (1.0 / mu) * ((v**2 - mu / r) * r_vec - r * vr * v_vec)
    e = float(np.linalg.norm(e_vec))

    tol = 1e-10
    # Right ascension of the ascending node.
    if n > tol:
        raan = float(np.arccos(np.clip(n_vec[0] / n, -1.0, 1.0)))
        if n_vec[1] < 0.0:
            raan = 2.0 * np.pi - raan
    else:
        raan = 0.0

    # Argument of perigee.
    if n > tol and e > tol:
        argp = float(np.arccos(np.clip(np.dot(n_vec, e_vec) / (n * e), -1.0, 1.0)))
        if e_vec[2] < 0.0:
            argp = 2.0 * np.pi - argp
    else:
        argp = 0.0

    # True anomaly.
    if e > tol:
        true_anomaly = float(np.arccos(np.clip(np.dot(e_vec, r_vec) / (e * r), -1.0, 1.0)))
        if vr < 0.0:
            true_anomaly = 2.0 * np.pi - true_anomaly
    elif n > tol:
        # Circular, inclined: measure from the node line.
        true_anomaly = float(np.arccos(np.clip(np.dot(n_vec, r_vec) / (n * r), -1.0, 1.0)))
        if r_vec[2] < 0.0:
            true_anomaly = 2.0 * np.pi - true_anomaly
    else:
        # Circular, equatorial: measure from the x-axis.
        true_anomaly = float(np.arccos(np.clip(r_vec[0] / r, -1.0, 1.0)))
        if r_vec[1] < 0.0:
            true_anomaly = 2.0 * np.pi - true_anomaly

    # Semi-major axis from the vis-viva energy (a < 0 for hyperbolic orbits).
    energy = 0.5 * v**2 - mu / r
    semi_major_axis = -mu / (2.0 * energy) if abs(energy) > 0.0 else float("inf")
    periapsis = h**2 / mu / (1.0 + e)
    apoapsis = h**2 / mu / (1.0 - e) if e < 1.0 else float("inf")

    return {
        "semi_major_axis_m": round(semi_major_axis, 3) if np.isfinite(semi_major_axis) else None,
        "eccentricity": round(e, 6),
        "inclination_deg": round(float(np.degrees(inclination)), 4),
        "raan_deg": round(float(np.degrees(raan)), 4),
        "argument_of_perigee_deg": round(float(np.degrees(argp)), 4),
        "true_anomaly_deg": round(float(np.degrees(true_anomaly)), 4),
        "specific_angular_momentum_m2_s": round(h, 3),
        "periapsis_radius_m": round(float(periapsis), 3),
        "apoapsis_radius_m": round(float(apoapsis), 3) if np.isfinite(apoapsis) else None,
        "orbit_type": "closed" if e < 1.0 else ("parabolic" if e == 1.0 else "hyperbolic"),
    }


def state_from_orbital_elements(
    semi_major_axis_m: float,
    eccentricity: float,
    inclination_deg: float,
    raan_deg: float,
    argument_of_perigee_deg: float,
    true_anomaly_deg: float,
    mu: float = MU_EARTH,
) -> dict:
    """Inertial state vector (position + velocity) from classical orbital elements.

    The inverse of orbital_elements_from_state: builds the perifocal state from the
    orbit shape and true anomaly, then rotates into the geocentric-equatorial frame
    (Curtis, Orbital Mechanics for Engineering Students, 3rd Ed., Algorithm 4.5).

    Args:
        semi_major_axis_m: Semi-major axis in m (negative for hyperbolic orbits).
        eccentricity: Orbit eccentricity (>= 0; parabolic e == 1 is not supported here).
        inclination_deg: Inclination in degrees [0, 180].
        raan_deg: Right ascension of the ascending node in degrees.
        argument_of_perigee_deg: Argument of perigee in degrees.
        true_anomaly_deg: True anomaly in degrees.
        mu: Gravitational parameter of the central body in m^3/s^2 (default Earth).
    """
    if eccentricity < 0:
        raise ValueError("eccentricity must be >= 0")
    if eccentricity == 1.0:
        raise ValueError(
            "parabolic orbit (e == 1) is not supported via (a, e); the semi-latus "
            "rectum is required instead"
        )
    if mu <= 0:
        raise ValueError("mu must be > 0")
    if not 0.0 <= inclination_deg <= 180.0:
        raise ValueError("inclination_deg must be in [0, 180]")

    # Semi-latus rectum p = a(1 - e^2) is positive for every real conic.
    p = semi_major_axis_m * (1.0 - eccentricity**2)
    if p <= 0.0:
        raise ValueError(
            "inconsistent semi_major_axis and eccentricity (a(1-e^2) must be > 0): "
            "use a > 0 with e < 1, or a < 0 with e > 1"
        )
    h = np.sqrt(mu * p)

    theta = np.radians(true_anomaly_deg)
    incl = np.radians(inclination_deg)
    raan = np.radians(raan_deg)
    argp = np.radians(argument_of_perigee_deg)

    # Perifocal (PQW) position and velocity.
    r_scalar = (h**2 / mu) / (1.0 + eccentricity * np.cos(theta))
    r_pf = r_scalar * np.array([np.cos(theta), np.sin(theta), 0.0])
    v_pf = (mu / h) * np.array([-np.sin(theta), eccentricity + np.cos(theta), 0.0])

    # Perifocal -> geocentric-equatorial rotation (Curtis Eq. 4.49).
    c_o, s_o = np.cos(raan), np.sin(raan)
    c_i, s_i = np.cos(incl), np.sin(incl)
    c_w, s_w = np.cos(argp), np.sin(argp)
    q_mat = np.array(
        [
            [-s_o * c_i * s_w + c_o * c_w, -s_o * c_i * c_w - c_o * s_w, s_o * s_i],
            [c_o * c_i * s_w + s_o * c_w, c_o * c_i * c_w - s_o * s_w, -c_o * s_i],
            [s_i * s_w, s_i * c_w, c_i],
        ]
    )

    r_vec = q_mat @ r_pf
    v_vec = q_mat @ v_pf
    return {
        "position_x_m": round(float(r_vec[0]), 3),
        "position_y_m": round(float(r_vec[1]), 3),
        "position_z_m": round(float(r_vec[2]), 3),
        "velocity_x_ms": round(float(v_vec[0]), 5),
        "velocity_y_ms": round(float(v_vec[1]), 5),
        "velocity_z_ms": round(float(v_vec[2]), 5),
        "radius_m": round(float(np.linalg.norm(r_vec)), 3),
        "speed_ms": round(float(np.linalg.norm(v_vec)), 5),
        "specific_angular_momentum_m2_s": round(float(h), 3),
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


def kepler_propagate(
    position_m: list[float],
    velocity_ms: list[float],
    time_of_flight_s: float,
    mu: float = MU_EARTH,
) -> dict:
    """Propagate a state vector forward in time on its two-body orbit.

    Given an initial position/velocity and an elapsed time, returns the position and
    velocity at that later time, via the universal-variable formulation and Lagrange
    coefficients (Curtis, Orbital Mechanics for Engineering Students, 3rd Ed.,
    Algorithm 3.4). Works for elliptical and hyperbolic orbits alike; time_of_flight_s
    may be negative to propagate backward.

    Args:
        position_m: Initial inertial position vector [x, y, z] in m.
        velocity_ms: Initial inertial velocity vector [vx, vy, vz] in m/s.
        time_of_flight_s: Elapsed time in seconds (may be negative).
        mu: Gravitational parameter of the central body in m^3/s^2 (default Earth).
    """
    if len(position_m) != 3 or len(velocity_ms) != 3:
        raise ValueError("position_m and velocity_ms must each be 3-component vectors")
    if mu <= 0:
        raise ValueError("mu must be > 0")

    r0_vec = np.asarray(position_m, dtype=float)
    v0_vec = np.asarray(velocity_ms, dtype=float)
    r0 = float(np.linalg.norm(r0_vec))
    v0 = float(np.linalg.norm(v0_vec))
    if r0 == 0.0:
        raise ValueError("position vector must be non-zero")

    dt = time_of_flight_s
    vr0 = float(np.dot(r0_vec, v0_vec) / r0)
    # Reciprocal of the semi-major axis (alpha > 0 ellipse, < 0 hyperbola, 0 parabola).
    alpha = 2.0 / r0 - v0**2 / mu
    root_mu = np.sqrt(mu)

    # Solve the universal Kepler equation for the universal anomaly chi (Newton).
    chi = root_mu * abs(alpha) * dt
    tol = 1e-8
    max_iter = 200
    converged = False
    for _ in range(max_iter):
        z = alpha * chi**2
        cz = _stumpff_c(z)
        sz = _stumpff_s(z)
        f_chi = (
            r0 * vr0 / root_mu * chi**2 * cz
            + (1.0 - alpha * r0) * chi**3 * sz
            + r0 * chi
            - root_mu * dt
        )
        dfdchi = (
            r0 * vr0 / root_mu * chi * (1.0 - alpha * chi**2 * sz)
            + (1.0 - alpha * r0) * chi**2 * cz
            + r0
        )
        ratio = f_chi / dfdchi
        chi -= ratio
        if abs(ratio) < tol:
            converged = True
            break
    if not converged:
        raise ValueError("Kepler propagation did not converge; check inputs / time of flight")

    z = alpha * chi**2
    cz = _stumpff_c(z)
    sz = _stumpff_s(z)
    # Lagrange coefficients for the new position.
    f = 1.0 - chi**2 / r0 * cz
    g = dt - 1.0 / root_mu * chi**3 * sz
    r_vec = f * r0_vec + g * v0_vec
    r = float(np.linalg.norm(r_vec))
    # Lagrange coefficients for the new velocity.
    fdot = root_mu / (r * r0) * (alpha * chi**3 * sz - chi)
    gdot = 1.0 - chi**2 / r * cz
    v_vec = fdot * r0_vec + gdot * v0_vec

    return {
        "position_x_m": round(float(r_vec[0]), 3),
        "position_y_m": round(float(r_vec[1]), 3),
        "position_z_m": round(float(r_vec[2]), 3),
        "velocity_x_ms": round(float(v_vec[0]), 5),
        "velocity_y_ms": round(float(v_vec[1]), 5),
        "velocity_z_ms": round(float(v_vec[2]), 5),
        "radius_m": round(r, 3),
        "speed_ms": round(float(np.linalg.norm(v_vec)), 5),
        "universal_anomaly": round(float(chi), 6),
    }
