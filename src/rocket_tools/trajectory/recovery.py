"""Recovery-system sizing: parachute descent rate and canopy area.

Closes the recovery gap for preliminary rocketry: given a recovered mass and a
parachute, what descent rate does it settle to (terminal velocity), and inversely,
what canopy area meets a target landing speed. Terminal velocity comes from a drag
balance mg = 0.5*rho*V^2*Cd*S at steady descent.

References:
    - Knacke, T. W., "Parachute Recovery Systems Design Manual", NWC TP 6575 (1992).
    - Sutton & Biblarz / standard rocketry recovery practice for the drag balance.
"""

import math

from rocket_tools.materials import isa_atmosphere

__all__ = ["parachute_descent_rate", "parachute_area_for_descent_rate"]

G_STD = 9.80665


def _air_density(altitude_m: float, air_density_kg_m3: float | None) -> float:
    """Air density: explicit value if given, else ISA at the altitude."""
    if air_density_kg_m3 is not None:
        if air_density_kg_m3 <= 0:
            raise ValueError("air_density_kg_m3 must be > 0")
        return air_density_kg_m3
    return float(isa_atmosphere(altitude_m)["density_kg_m3"])


def parachute_descent_rate(
    mass_kg: float,
    canopy_diameter_m: float,
    drag_coefficient: float = 0.75,
    altitude_m: float = 0.0,
    air_density_kg_m3: float | None = None,
) -> dict:
    """Terminal descent rate of a mass under a round parachute.

    Steady descent balances weight against drag: mg = 0.5*rho*V^2*Cd*S, so
    V = sqrt(2*m*g / (rho*Cd*S)) with S the canopy area (pi*D^2/4). The drag
    coefficient is referenced to the canopy's flat (constructed) area; typical
    round-parachute values are Cd ~ 0.7-0.85 (Knacke).

    Args:
        mass_kg: Recovered mass under the canopy.
        canopy_diameter_m: Nominal (flat) canopy diameter.
        drag_coefficient: Parachute drag coefficient referenced to canopy area.
        altitude_m: Landing-site altitude for the ISA density lookup (ignored if
            air_density_kg_m3 is given).
        air_density_kg_m3: Explicit air density override in kg/m^3.
    """
    if mass_kg <= 0:
        raise ValueError("mass_kg must be > 0")
    if canopy_diameter_m <= 0:
        raise ValueError("canopy_diameter_m must be > 0")
    if drag_coefficient <= 0:
        raise ValueError("drag_coefficient must be > 0")

    rho = _air_density(altitude_m, air_density_kg_m3)
    area = math.pi * (canopy_diameter_m / 2.0) ** 2
    v = math.sqrt(2.0 * mass_kg * G_STD / (rho * drag_coefficient * area))
    # Kinetic energy at landing is the usual recovery acceptance metric.
    ke = 0.5 * mass_kg * v**2
    return {
        "descent_rate_ms": round(v, 4),
        "canopy_area_m2": round(area, 5),
        "landing_kinetic_energy_j": round(ke, 3),
        "air_density_kg_m3": round(rho, 6),
        "drag_coefficient": drag_coefficient,
        "mass_kg": mass_kg,
    }


def parachute_area_for_descent_rate(
    mass_kg: float,
    target_descent_rate_ms: float,
    drag_coefficient: float = 0.75,
    altitude_m: float = 0.0,
    air_density_kg_m3: float | None = None,
) -> dict:
    """Canopy area and diameter needed to hit a target descent rate.

    Inverts the drag balance: S = 2*m*g / (rho*Cd*V_target^2). A common recovery
    target for hobby rockets is a landing speed of roughly 3-6 m/s.
    """
    if mass_kg <= 0:
        raise ValueError("mass_kg must be > 0")
    if target_descent_rate_ms <= 0:
        raise ValueError("target_descent_rate_ms must be > 0")
    if drag_coefficient <= 0:
        raise ValueError("drag_coefficient must be > 0")

    rho = _air_density(altitude_m, air_density_kg_m3)
    area = 2.0 * mass_kg * G_STD / (rho * drag_coefficient * target_descent_rate_ms**2)
    diameter = math.sqrt(4.0 * area / math.pi)
    return {
        "canopy_area_m2": round(area, 5),
        "canopy_diameter_m": round(diameter, 4),
        "target_descent_rate_ms": target_descent_rate_ms,
        "air_density_kg_m3": round(rho, 6),
        "drag_coefficient": drag_coefficient,
        "mass_kg": mass_kg,
    }
