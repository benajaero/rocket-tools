"""Pressure-vessel stresses.

Stresses in a pressurized cylinder or sphere, thin-wall (membrane) or thick-wall (Lame),
plus the von Mises equivalent and, optionally, the margin of safety against a material
yield. This is the stress-analysis complement to ``propellant_tank_sizing`` (which sizes
the wall): here the geometry is given and the stresses are reported.

References:
    - Boresi & Schmidt, "Advanced Mechanics of Materials", 6th Ed. (thin- and thick-wall vessels).
    - Roark's Formulas for Stress and Strain (membrane theory and Lame thick-wall equations).
"""

import math

__all__ = ["pressure_vessel_stress", "thick_wall_pressure_vessel_stress"]


def _von_mises(s1: float, s2: float, s3: float) -> float:
    """Von Mises equivalent stress from three principal stresses."""
    return math.sqrt(0.5 * ((s1 - s2) ** 2 + (s2 - s3) ** 2 + (s3 - s1) ** 2))


def pressure_vessel_stress(
    internal_pressure_pa: float,
    inner_radius_m: float,
    wall_thickness_m: float,
    geometry: str = "cylinder",
    material_yield_pa: float | None = None,
) -> dict:
    """Membrane stresses in a thin-walled pressurized vessel.

    For a cylinder: hoop sigma_h = p*r/t, longitudinal sigma_l = p*r/(2t). For a sphere
    both membrane stresses equal p*r/(2t). The von Mises equivalent uses the two membrane
    stresses with the radial stress taken as ~0 (thin-wall assumption). Thin-wall theory
    applies for r/t >= 10; below that, treat the result as approximate and use a thick-wall
    (Lame) analysis.

    Args:
        internal_pressure_pa: Gauge internal pressure in Pa.
        inner_radius_m: Inner radius in m.
        wall_thickness_m: Wall thickness in m.
        geometry: "cylinder" or "sphere".
        material_yield_pa: Yield strength in Pa (optional; enables margin of safety).
    """
    if internal_pressure_pa <= 0:
        raise ValueError("internal_pressure_pa must be > 0")
    if inner_radius_m <= 0:
        raise ValueError("inner_radius_m must be > 0")
    if wall_thickness_m <= 0:
        raise ValueError("wall_thickness_m must be > 0")
    if material_yield_pa is not None and material_yield_pa <= 0:
        raise ValueError("material_yield_pa must be > 0 when provided")

    shape = geometry.lower()
    if shape not in ("cylinder", "sphere"):
        raise ValueError("geometry must be 'cylinder' or 'sphere'")

    p = internal_pressure_pa
    r = inner_radius_m
    t = wall_thickness_m
    r_over_t = r / t

    if shape == "cylinder":
        hoop = p * r / t
        longitudinal = p * r / (2.0 * t)
    else:  # sphere
        hoop = p * r / (2.0 * t)
        longitudinal = hoop

    # von Mises with the third (radial) principal stress ~ 0 for a thin wall.
    von_mises = math.sqrt(hoop**2 - hoop * longitudinal + longitudinal**2)

    result: dict = {
        "hoop_stress_pa": round(hoop, 3),
        "hoop_stress_mpa": round(hoop / 1.0e6, 5),
        "longitudinal_stress_pa": round(longitudinal, 3),
        "longitudinal_stress_mpa": round(longitudinal / 1.0e6, 5),
        "von_mises_stress_pa": round(von_mises, 3),
        "von_mises_stress_mpa": round(von_mises / 1.0e6, 5),
        "radius_to_thickness_ratio": round(r_over_t, 3),
        "thin_wall_valid": r_over_t >= 10.0,
        "geometry": shape,
    }
    if not result["thin_wall_valid"]:
        result["note"] = (
            "r/t < 10: thin-wall membrane theory is approximate here; use a thick-wall "
            "(Lame) analysis for an accurate result."
        )
    if material_yield_pa is not None:
        # Margin of safety on the von Mises stress against yield.
        result["margin_of_safety"] = round(material_yield_pa / von_mises - 1.0, 4)
        result["yields"] = von_mises >= material_yield_pa
    return result


def thick_wall_pressure_vessel_stress(
    internal_pressure_pa: float,
    inner_radius_m: float,
    outer_radius_m: float,
    geometry: str = "cylinder",
    material_yield_pa: float | None = None,
) -> dict:
    """Thick-wall (Lame) stresses in a pressurized cylinder or sphere.

    Exact elasticity solution for a thick wall under internal pressure, valid at any
    radius ratio (use this when r/t < 10, where thin-wall membrane theory is inaccurate).
    Stresses are largest at the inner surface, which is what this reports along with the
    outer hoop stress. For a closed-ended cylinder the axial stress is the constant Lame
    longitudinal term; for a sphere the two tangential stresses are equal.

    Args:
        internal_pressure_pa: Gauge internal pressure in Pa.
        inner_radius_m: Inner radius a in m.
        outer_radius_m: Outer radius b in m (must exceed the inner radius).
        geometry: "cylinder" or "sphere".
        material_yield_pa: Yield strength in Pa (optional; enables the margin of safety).
    """
    if internal_pressure_pa <= 0:
        raise ValueError("internal_pressure_pa must be > 0")
    if inner_radius_m <= 0:
        raise ValueError("inner_radius_m must be > 0")
    if outer_radius_m <= inner_radius_m:
        raise ValueError("outer_radius_m must be > inner_radius_m")
    if material_yield_pa is not None and material_yield_pa <= 0:
        raise ValueError("material_yield_pa must be > 0 when provided")

    shape = geometry.lower()
    if shape not in ("cylinder", "sphere"):
        raise ValueError("geometry must be 'cylinder' or 'sphere'")

    p = internal_pressure_pa
    a = inner_radius_m
    b = outer_radius_m

    if shape == "cylinder":
        denom = b**2 - a**2
        hoop_inner = p * (b**2 + a**2) / denom
        hoop_outer = p * (2.0 * a**2) / denom
        radial_inner = -p
        longitudinal = p * a**2 / denom  # closed-ended axial stress
        # Principal stresses at the inner surface.
        von_mises = _von_mises(hoop_inner, longitudinal, radial_inner)
    else:  # sphere
        denom = b**3 - a**3
        hoop_inner = p * (2.0 * a**3 + b**3) / (2.0 * denom)
        hoop_outer = p * (3.0 * a**3) / (2.0 * denom)
        radial_inner = -p
        longitudinal = hoop_inner  # two equal tangential stresses
        von_mises = _von_mises(hoop_inner, hoop_inner, radial_inner)

    max_shear_inner = 0.5 * (hoop_inner - radial_inner)

    result: dict = {
        "hoop_stress_inner_pa": round(hoop_inner, 3),
        "hoop_stress_inner_mpa": round(hoop_inner / 1.0e6, 5),
        "hoop_stress_outer_pa": round(hoop_outer, 3),
        "hoop_stress_outer_mpa": round(hoop_outer / 1.0e6, 5),
        "radial_stress_inner_pa": round(radial_inner, 3),
        "longitudinal_stress_pa": round(longitudinal, 3),
        "von_mises_stress_inner_pa": round(von_mises, 3),
        "von_mises_stress_inner_mpa": round(von_mises / 1.0e6, 5),
        "max_shear_stress_inner_pa": round(max_shear_inner, 3),
        "radius_ratio_b_over_a": round(b / a, 4),
        "geometry": shape,
    }
    if material_yield_pa is not None:
        result["margin_of_safety"] = round(material_yield_pa / von_mises - 1.0, 4)
        result["yields"] = von_mises >= material_yield_pa
    return result
