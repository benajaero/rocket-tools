"""Mass properties and center of gravity calculations.

Supports composite bodies made of simple shapes — useful for
preliminary aircraft, rocket, drone, and spacecraft mass estimation.

References:
    - Raymer, "Aircraft Design: A Conceptual Approach", 5th Ed. (Ch. 11)
      CG estimation methods, component mass fractions.
    - Sutton & Biblarz, "Rocket Propulsion Elements", 9th Ed. (Ch. 7)
      Propellant tank sizing and mass estimation.
"""

import numpy as np


def composite_cg(masses: list[float], positions: list[list[float]]) -> dict:
    """Compute center of gravity for a composite body.

    Args:
        masses: List of component masses in kg
        positions: List of [x, y, z] positions in meters for each component

    Returns:
        dict with total_mass, cg position, and moments of inertia about CG
    """
    if len(masses) != len(positions):
        raise ValueError("masses and positions must have the same length")
    if not masses:
        raise ValueError("At least one component required")
    if any(m <= 0 for m in masses):
        raise ValueError("All masses must be > 0")

    total_mass = sum(masses)

    # CG position
    cg_x = sum(m * p[0] for m, p in zip(masses, positions)) / total_mass
    cg_y = sum(m * p[1] for m, p in zip(masses, positions)) / total_mass
    cg_z = sum(m * p[2] for m, p in zip(masses, positions)) / total_mass

    # Moments of inertia about CG (parallel axis theorem)
    i_xx = sum(m * ((p[1] - cg_y) ** 2 + (p[2] - cg_z) ** 2) for m, p in zip(masses, positions))
    i_yy = sum(m * ((p[0] - cg_x) ** 2 + (p[2] - cg_z) ** 2) for m, p in zip(masses, positions))
    i_zz = sum(m * ((p[0] - cg_x) ** 2 + (p[1] - cg_y) ** 2) for m, p in zip(masses, positions))
    i_xy = sum(m * (p[0] - cg_x) * (p[1] - cg_y) for m, p in zip(masses, positions))
    i_xz = sum(m * (p[0] - cg_x) * (p[2] - cg_z) for m, p in zip(masses, positions))
    i_yz = sum(m * (p[1] - cg_y) * (p[2] - cg_z) for m, p in zip(masses, positions))

    return {
        "total_mass_kg": round(total_mass, 4),
        "cg_x_m": round(cg_x, 6),
        "cg_y_m": round(cg_y, 6),
        "cg_z_m": round(cg_z, 6),
        "i_xx_kg_m2": round(i_xx, 4),
        "i_yy_kg_m2": round(i_yy, 4),
        "i_zz_kg_m2": round(i_zz, 4),
        "i_xy_kg_m2": round(i_xy, 4),
        "i_xz_kg_m2": round(i_xz, 4),
        "i_yz_kg_m2": round(i_yz, 4),
        "components": len(masses),
    }


def propellant_tank_sizing(
    propellant_volume_m3: float,
    ullage_fraction: float = 0.1,
    tank_shape: str = "cylinder",
    aspect_ratio: float = 2.0,
    wall_thickness_m: float = 0.003,
    material_density_kg_m3: float = 2700.0,
) -> dict:
    """Size a propellant tank and estimate its mass.

    Used for: rocket stage design, aircraft fuel tank sizing,
    and spacecraft propulsion system layout.

    Args:
        propellant_volume_m3: Required propellant volume
        ullage_fraction: Extra volume for ullage/expansion (default 10%)
        tank_shape: "cylinder", "sphere", or "ellipsoid"
        aspect_ratio: For cylinder: length/diameter (default 2.0)
        wall_thickness_m: Tank wall thickness
        material_density_kg_m3: Tank material density (default 2700 for aluminum)
    """
    if propellant_volume_m3 <= 0:
        raise ValueError("propellant_volume must be > 0")

    total_volume = propellant_volume_m3 * (1.0 + ullage_fraction)

    if tank_shape == "cylinder":
        # V = pi * r^2 * L = pi * r^2 * (aspect_ratio * 2r) = 2 * pi * aspect_ratio * r^3
        r = (total_volume / (2.0 * np.pi * aspect_ratio)) ** (1.0 / 3.0)
        diameter = 2.0 * r
        length = aspect_ratio * diameter
        surface_area = 2.0 * np.pi * r * length + 2.0 * np.pi * r**2

    elif tank_shape == "sphere":
        r = ((3.0 * total_volume) / (4.0 * np.pi)) ** (1.0 / 3.0)
        diameter = 2.0 * r
        length = diameter
        surface_area = 4.0 * np.pi * r**2
        aspect_ratio = 1.0

    elif tank_shape == "ellipsoid":
        # Approximate as oblate spheroid with aspect_ratio = major/minor
        # V = 4/3 * pi * a^2 * c where a = b = r, c = r / aspect_ratio
        # This is a simplified approximation
        r = ((3.0 * total_volume * aspect_ratio) / (4.0 * np.pi)) ** (1.0 / 3.0)
        diameter = 2.0 * r
        length = diameter / aspect_ratio
        # Approximate surface area
        surface_area = 4.0 * np.pi * r**2  # Simplified

    else:
        raise ValueError(f"Unknown tank_shape: {tank_shape}")

    tank_mass = surface_area * wall_thickness_m * material_density_kg_m3

    return {
        "tank_shape": tank_shape,
        "propellant_volume_m3": round(propellant_volume_m3, 4),
        "total_volume_m3": round(total_volume, 4),
        "ullage_fraction": ullage_fraction,
        "diameter_m": round(diameter, 4),
        "length_m": round(length, 4),
        "aspect_ratio": round(aspect_ratio, 2),
        "wall_thickness_m": wall_thickness_m,
        "surface_area_m2": round(surface_area, 4),
        "tank_mass_kg": round(tank_mass, 4),
        "material_density_kg_m3": material_density_kg_m3,
    }
