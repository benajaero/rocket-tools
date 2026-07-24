"""End-to-end rocket design: ascent trajectory simulation and preliminary sizing.

``simulate_ascent`` numerically integrates a point-mass launch vehicle through the
ISA atmosphere (thrust, drag, altitude-varying gravity) and reports burnout/apogee
events, max-q, peak acceleration, and time-series arrays for plotting.

``size_vehicle`` performs integrated preliminary mass sizing by *chaining the existing
mission-design tools* (``rocket_delta_v``, ``thrust_to_weight``, ``propellant_tank_sizing``)
rather than re-deriving them.

References:
    - Curtis, "Orbital Mechanics for Engineering Students", 3rd Ed. (Ch. 11).
    - Sutton & Biblarz, "Rocket Propulsion Elements", 9th Ed. (Ch. 4).
"""

import math

import numpy as np

from rocket_tools.design.mass import propellant_tank_sizing
from rocket_tools.design.performance import rocket_delta_v, thrust_to_weight
from rocket_tools.trajectory.integrator import G0, _integrate


def _downsample(arr: np.ndarray, n_points: int) -> list[float]:
    """Return at most ``n_points`` evenly-spaced samples (endpoints preserved)."""
    n = len(arr)
    if n <= n_points:
        return [round(float(x), 4) for x in arr]
    idx = np.linspace(0, n - 1, n_points).astype(int)
    return [round(float(arr[i]), 4) for i in idx]


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
    gravity_model: str = "inverse_square",
) -> dict:
    """Simulate a launch vehicle ascent with a fixed-step RK4 integrator.

    A planar point-mass gravity-turn model: thrust ``F = mdot * Isp * g0`` acts along
    the velocity vector while propellant remains, drag is ``0.5*rho*V^2*Cd*A`` with ISA
    density, and gravity is inverse-square (or constant for analytic comparison).
    ``launch_angle_deg = 90`` is a pure vertical launch; smaller angles give a gravity turn.

    Returns a dict with ``events`` (burnout, apogee), summary scalars (apogee_m,
    burnout_velocity_ms, max_q_pa, max_accel_g, ...), and downsampled ``series`` arrays
    (t, altitude, velocity, mass, dynamic pressure, acceleration_g, flight-path angle,
    downrange) suitable for ``plot_trajectory``.
    """
    if initial_mass_kg <= 0 or dry_mass_kg <= 0:
        raise ValueError("masses must be > 0")
    if dry_mass_kg >= initial_mass_kg:
        raise ValueError("dry_mass must be less than initial_mass")
    if specific_impulse_s <= 0:
        raise ValueError("specific_impulse must be > 0")
    if mass_flow_rate_kg_s <= 0:
        raise ValueError("mass_flow_rate must be > 0")
    if reference_area_m2 <= 0:
        raise ValueError("reference_area must be > 0")
    if drag_coefficient < 0:
        raise ValueError("drag_coefficient must be >= 0")
    if not 0.0 < launch_angle_deg <= 90.0:
        raise ValueError("launch_angle_deg must be in (0, 90]")
    if dt <= 0 or max_time <= 0:
        raise ValueError("dt and max_time must be > 0")
    if gravity_model not in ("inverse_square", "constant"):
        raise ValueError("gravity_model must be 'inverse_square' or 'constant'")

    propellant_mass = initial_mass_kg - dry_mass_kg
    burn_time = propellant_mass / mass_flow_rate_kg_s
    thrust = mass_flow_rate_kg_s * specific_impulse_s * G0
    gamma0 = math.radians(launch_angle_deg)

    t, h, v, m, gamma, x, q, a = _integrate(
        float(initial_altitude_m),
        float(initial_velocity_ms),
        float(initial_mass_kg),
        float(gamma0),
        float(dry_mass_kg),
        float(mass_flow_rate_kg_s),
        float(thrust),
        float(burn_time),
        float(drag_coefficient),
        float(reference_area_m2),
        float(dt),
        float(max_time),
        bool(include_drag),
        gravity_model == "inverse_square",
    )

    # --- Burnout: linear interpolation at t = burn_time ---
    if burn_time <= t[-1]:
        j = int(np.searchsorted(t, burn_time))
        if j == 0:
            frac, lo = 0.0, 0
        else:
            lo = j - 1
            span = t[j] - t[lo]
            frac = (burn_time - t[lo]) / span if span > 0 else 0.0
        bo_h = h[lo] + frac * (h[min(lo + 1, len(h) - 1)] - h[lo])
        bo_v = v[lo] + frac * (v[min(lo + 1, len(v) - 1)] - v[lo])
        bo_m = m[lo] + frac * (m[min(lo + 1, len(m) - 1)] - m[lo])
        bo_t = burn_time
    else:  # never reached burnout within max_time
        bo_h, bo_v, bo_m, bo_t = h[-1], v[-1], m[-1], t[-1]

    # --- Apogee: peak altitude ---
    ap_i = int(np.argmax(h))
    ideal_dv = specific_impulse_s * G0 * math.log(initial_mass_kg / dry_mass_kg)
    max_q_i = int(np.argmax(q))
    max_a_i = int(np.argmax(a))

    return {
        "events": {
            "burnout": {
                "time_s": round(float(bo_t), 3),
                "altitude_m": round(float(bo_h), 2),
                "velocity_ms": round(float(bo_v), 2),
                "mass_kg": round(float(bo_m), 2),
            },
            "apogee": {
                "time_s": round(float(t[ap_i]), 3),
                "altitude_m": round(float(h[ap_i]), 2),
                "velocity_ms": round(float(v[ap_i]), 2),
            },
        },
        "apogee_m": round(float(h[ap_i]), 2),
        "apogee_km": round(float(h[ap_i]) / 1000.0, 4),
        "burnout_velocity_ms": round(float(bo_v), 2),
        "burnout_altitude_m": round(float(bo_h), 2),
        "burnout_time_s": round(float(bo_t), 3),
        "max_dynamic_pressure_pa": round(float(q[max_q_i]), 2),
        "max_q_altitude_m": round(float(h[max_q_i]), 2),
        "max_q_velocity_ms": round(float(v[max_q_i]), 2),
        "max_accel_g": round(float(a[max_a_i]) / G0, 3),
        "ideal_delta_v_ms": round(float(ideal_dv), 2),
        "total_losses_ms": round(float(ideal_dv - bo_v), 2),
        "propellant_mass_kg": round(float(propellant_mass), 2),
        "burn_time_s": round(float(burn_time), 3),
        "liftoff_thrust_n": round(float(thrust), 2),
        "liftoff_twr": round(float(thrust / (initial_mass_kg * G0)), 3),
        "flight_time_s": round(float(t[-1]), 2),
        "series": {
            "time_s": _downsample(t, 250),
            "altitude_m": _downsample(h, 250),
            "velocity_ms": _downsample(v, 250),
            "mass_kg": _downsample(m, 250),
            "dynamic_pressure_pa": _downsample(q, 250),
            "acceleration_g": _downsample(a / G0, 250),
            "flight_path_angle_deg": _downsample(np.degrees(gamma), 250),
            "downrange_m": _downsample(x, 250),
        },
    }


def size_vehicle(
    payload_mass_kg: float,
    delta_v_target_ms: float,
    specific_impulse_s: float,
    inert_mass_fraction: float,
    thrust_to_weight_liftoff: float = 1.3,
    propellant_density_kg_m3: float = 1000.0,
) -> dict:
    """Preliminary single-stage vehicle sizing from a delta-v budget.

    Given a payload, a delta-v target, engine Isp, and a structural (inert) mass
    fraction epsilon = inert/(inert+propellant), solve the rocket equation for the
    gross liftoff mass and propellant/inert breakdown, then chain the existing
    ``rocket_delta_v``, ``thrust_to_weight``, and ``propellant_tank_sizing`` tools to
    report achieved delta-v, liftoff thrust/TWR, and a cylindrical propellant tank.

    Returns ``achievable=False`` (with the max achievable delta-v) when the required
    mass ratio exceeds what the structural fraction allows.
    """
    if payload_mass_kg <= 0:
        raise ValueError("payload_mass must be > 0")
    if delta_v_target_ms <= 0:
        raise ValueError("delta_v_target must be > 0")
    if specific_impulse_s <= 0:
        raise ValueError("specific_impulse must be > 0")
    if not 0.0 < inert_mass_fraction < 1.0:
        raise ValueError("inert_mass_fraction must be in (0, 1)")
    if thrust_to_weight_liftoff <= 0:
        raise ValueError("thrust_to_weight_liftoff must be > 0")
    if propellant_density_kg_m3 <= 0:
        raise ValueError("propellant_density must be > 0")

    eps = inert_mass_fraction
    mass_ratio = math.exp(delta_v_target_ms / (specific_impulse_s * G0))
    inv_mr = 1.0 / mass_ratio

    # Feasibility: gross mass m0 = ml*(eps-1)/(eps - 1/MR) is positive iff eps < 1/MR.
    if eps >= inv_mr:
        max_dv = specific_impulse_s * G0 * math.log(1.0 / eps)
        return {
            "achievable": False,
            "reason": "Structural fraction too high for the delta-v target with this Isp",
            "required_mass_ratio": round(mass_ratio, 4),
            "max_achievable_delta_v_ms": round(max_dv, 2),
            "inert_mass_fraction": eps,
        }

    gross_mass = payload_mass_kg * (eps - 1.0) / (eps - inv_mr)
    final_mass = gross_mass * inv_mr
    inert_mass = eps * (gross_mass - payload_mass_kg)
    propellant_mass = gross_mass - final_mass

    # Chain existing tools for the achieved figures.
    dv = rocket_delta_v(specific_impulse_s, gross_mass, final_mass)
    thrust_n = thrust_to_weight_liftoff * gross_mass * G0
    tw = thrust_to_weight(thrust_n, gross_mass)
    tank = propellant_tank_sizing(
        propellant_volume_m3=propellant_mass / propellant_density_kg_m3,
        tank_shape="cylinder",
    )

    return {
        "achievable": True,
        "gross_liftoff_mass_kg": round(gross_mass, 2),
        "propellant_mass_kg": round(propellant_mass, 2),
        "inert_mass_kg": round(inert_mass, 2),
        "payload_mass_kg": round(payload_mass_kg, 2),
        "final_mass_kg": round(final_mass, 2),
        "payload_fraction": round(payload_mass_kg / gross_mass, 4),
        "propellant_mass_fraction": round(propellant_mass / gross_mass, 4),
        "mass_ratio": round(mass_ratio, 4),
        "achieved_delta_v_ms": dv["delta_v_ms"],
        "liftoff_thrust_n": round(thrust_n, 2),
        "liftoff_twr": tw["thrust_to_weight_ratio"],
        "tank_mass_kg": tank.get("tank_mass_kg"),
        "tank_length_m": tank.get("length_m"),
        "tank_diameter_m": tank.get("diameter_m"),
    }
