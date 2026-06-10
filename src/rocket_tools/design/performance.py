"""Vehicle performance analysis for rockets, aircraft, and drones.

Covers:
- Rocket delta-v (Tsiolkovsky equation)
- Multi-stage rocket performance
- Aircraft range and endurance (Breguet)
- Fuel/payload fraction estimation

References:
    - Sutton & Biblarz, "Rocket Propulsion Elements", 9th Ed. (Ch. 2, 4)
      Tsiolkovsky rocket equation, multi-stage performance,
      payload fraction analysis.
    - Vallado, "Fundamentals of Astrodynamics and Applications", 4th Ed. (Ch. 1)
      Circular orbital velocity, escape velocity, orbital period.
    - Anderson, "Aircraft Performance and Design" (Ch. 6)
      Breguet range and endurance equations.
"""

import numpy as np

G_STD = 9.80665


def rocket_delta_v(
    specific_impulse_s: float,
    initial_mass_kg: float,
    final_mass_kg: float,
    gravity: float = G_STD,
) -> dict:
    """Compute rocket delta-v using the Tsiolkovsky rocket equation.

    delta-v = Isp * g0 * ln(m0 / mf)

    Used for: mission design, stage sizing, and orbit transfer calculations.
    """
    if specific_impulse_s <= 0:
        raise ValueError("specific_impulse must be > 0")
    if initial_mass_kg <= 0 or final_mass_kg <= 0:
        raise ValueError("masses must be > 0")
    if final_mass_kg >= initial_mass_kg:
        raise ValueError("final_mass must be less than initial_mass")

    delta_v = specific_impulse_s * gravity * np.log(initial_mass_kg / final_mass_kg)
    mass_ratio = initial_mass_kg / final_mass_kg
    propellant_fraction = 1.0 - final_mass_kg / initial_mass_kg

    return {
        "delta_v_ms": round(delta_v, 2),
        "delta_v_kms": round(delta_v / 1000.0, 4),
        "specific_impulse_s": specific_impulse_s,
        "mass_ratio": round(mass_ratio, 4),
        "propellant_fraction": round(propellant_fraction, 4),
        "structure_plus_payload_kg": round(final_mass_kg, 2),
        "propellant_mass_kg": round(initial_mass_kg - final_mass_kg, 2),
    }


def multi_stage_delta_v(
    stages: list[dict],
    gravity: float = G_STD,
) -> dict:
    """Compute total delta-v for a multi-stage rocket.

    Args:
        stages: List of dicts, each with:
            - specific_impulse_s: Isp in seconds
            - dry_mass_kg: Stage dry mass (without propellant)
            - propellant_mass_kg: Stage propellant mass
            - payload_mass_kg: Mass above this stage (upper stages + payload)

    Returns:
        dict with total_delta_v and per-stage breakdown
    """
    if not stages:
        raise ValueError("At least one stage required")

    total_delta_v = 0.0
    stage_results = []

    for i, stage in enumerate(stages):
        isp = stage["specific_impulse_s"]
        dry = stage["dry_mass_kg"]
        prop = stage["propellant_mass_kg"]
        payload = stage.get("payload_mass_kg", 0.0)

        if isp <= 0 or dry <= 0 or prop <= 0:
            raise ValueError(f"Stage {i}: isp, dry_mass, and propellant_mass must be > 0")

        m0 = dry + prop + payload
        mf = dry + payload

        dv = isp * gravity * np.log(m0 / mf)
        total_delta_v += dv

        stage_results.append(
            {
                "stage": i + 1,
                "delta_v_ms": round(dv, 2),
                "delta_v_kms": round(dv / 1000.0, 4),
                "mass_ratio": round(m0 / mf, 4),
                "propellant_fraction": round(prop / m0, 4),
            }
        )

    return {
        "total_delta_v_ms": round(total_delta_v, 2),
        "total_delta_v_kms": round(total_delta_v / 1000.0, 4),
        "stages": stage_results,
    }


def orbital_velocity(
    altitude_m: float,
    body_radius_m: float = 6_371_000.0,
    body_mass_kg: float = 5.972e24,
    gravity_constant: float = 6.67430e-11,
) -> dict:
    """Compute circular orbital velocity at given altitude.

    Default values are for Earth.
    """
    if altitude_m < 0:
        raise ValueError("altitude must be >= 0")

    r = body_radius_m + altitude_m
    v_circular = np.sqrt(gravity_constant * body_mass_kg / r)
    v_escape = np.sqrt(2.0) * v_circular
    period_s = 2.0 * np.pi * r / v_circular

    return {
        "altitude_m": altitude_m,
        "altitude_km": round(altitude_m / 1000.0, 2),
        "orbital_radius_m": round(r, 1),
        "circular_velocity_ms": round(v_circular, 2),
        "circular_velocity_kms": round(v_circular / 1000.0, 4),
        "escape_velocity_ms": round(v_escape, 2),
        "escape_velocity_kms": round(v_escape / 1000.0, 4),
        "orbital_period_s": round(period_s, 1),
        "orbital_period_min": round(period_s / 60.0, 2),
        "orbital_period_hr": round(period_s / 3600.0, 3),
    }


def payload_fraction(
    delta_v_required_ms: float,
    specific_impulse_s: float,
    inert_mass_fraction: float,
    gravity: float = G_STD,
) -> dict:
    """Estimate payload mass fraction for a rocket given mission requirements.

    payload_fraction = 1 - inert_fraction - propellant_fraction

    Where propellant_fraction comes from the rocket equation rearranged.
    """
    if delta_v_required_ms <= 0:
        raise ValueError("delta_v must be > 0")
    if specific_impulse_s <= 0:
        raise ValueError("specific_impulse must be > 0")
    if inert_mass_fraction < 0 or inert_mass_fraction >= 1.0:
        raise ValueError("inert_mass_fraction must be in [0, 1)")

    # From rocket equation: mf/m0 = exp(-delta_v / (Isp * g0))
    # mf = inert + payload, m0 = inert + payload + propellant
    # Let inert = sigma * m0, payload = epsilon * m0
    # mf/m0 = sigma + epsilon = exp(-delta_v / (Isp * g0))
    # epsilon = exp(-delta_v / (Isp * g0)) - sigma

    mass_ratio_term = np.exp(-delta_v_required_ms / (specific_impulse_s * gravity))
    payload_frac = mass_ratio_term - inert_mass_fraction

    if payload_frac <= 0:
        return {
            "payload_fraction": 0.0,
            "achievable": False,
            "reason": "Mission delta-v exceeds capability with given Isp and inert fraction",
            "required_mass_ratio": round(1.0 / mass_ratio_term, 4),
            "inert_mass_fraction": inert_mass_fraction,
        }

    propellant_frac = 1.0 - inert_mass_fraction - payload_frac

    return {
        "payload_fraction": round(payload_frac, 4),
        "propellant_fraction": round(propellant_frac, 4),
        "inert_mass_fraction": inert_mass_fraction,
        "achievable": True,
        "required_mass_ratio": round(1.0 / mass_ratio_term, 4),
        "delta_v_required_ms": round(delta_v_required_ms, 2),
        "specific_impulse_s": specific_impulse_s,
    }


def thrust_to_weight(
    thrust_n: float,
    mass_kg: float,
    gravity: float = G_STD,
) -> dict:
    """Compute thrust-to-weight ratio.

    Used for: launch vehicle performance, drone agility assessment,
    and aircraft climb capability.
    """
    if thrust_n <= 0 or mass_kg <= 0:
        raise ValueError("thrust and mass must be > 0")

    weight_n = mass_kg * gravity
    tw = thrust_n / weight_n

    return {
        "thrust_n": thrust_n,
        "weight_n": round(weight_n, 2),
        "mass_kg": mass_kg,
        "thrust_to_weight_ratio": round(tw, 3),
        "can_hover": tw > 1.0,
        "can_climb_vertical": tw > 1.0,
        "max_vertical_climb_acceleration_ms2": round((tw - 1.0) * gravity, 2) if tw > 1.0 else 0.0,
    }
