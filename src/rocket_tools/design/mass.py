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


def composite_cg(
    masses: list[float],
    positions: list[list[float]],
    inertias: list[list[float]] | None = None,
) -> dict:
    """Compute center of gravity and mass moments of inertia for a composite body.

    Args:
        masses: List of component masses in kg
        positions: List of [x, y, z] CG positions in meters for each component
        inertias: Optional list of each component's OWN inertia tensor about its own CG,
            as [Ixx, Iyy, Izz, Ixy, Ixz, Iyz] (kg.m^2). Defaults to zeros (point masses).
            Include these for slender bodies (a rocket's roll inertia is dominated by the
            components' own inertia, not just the parallel-axis m*d^2 term).

    Returns:
        dict with total_mass, cg position, and moments of inertia about the composite CG
    """
    if len(masses) != len(positions):
        raise ValueError("masses and positions must have the same length")
    if not masses:
        raise ValueError("At least one component required")
    if any(m <= 0 for m in masses):
        raise ValueError("All masses must be > 0")
    if inertias is None:
        inertias = [[0.0] * 6 for _ in masses]
    if len(inertias) != len(masses):
        raise ValueError("inertias must have the same length as masses")
    if any(len(io) != 6 for io in inertias):
        raise ValueError("each inertia must be [Ixx, Iyy, Izz, Ixy, Ixz, Iyz]")

    total_mass = sum(masses)

    # CG position
    cg_x = sum(m * p[0] for m, p in zip(masses, positions)) / total_mass
    cg_y = sum(m * p[1] for m, p in zip(masses, positions)) / total_mass
    cg_z = sum(m * p[2] for m, p in zip(masses, positions)) / total_mass

    # Inertia about the composite CG: each component's own inertia plus its parallel-axis
    # (m*d^2) contribution.
    zipped = list(zip(masses, positions, inertias))
    i_xx = sum(io[0] + m * ((p[1] - cg_y) ** 2 + (p[2] - cg_z) ** 2) for m, p, io in zipped)
    i_yy = sum(io[1] + m * ((p[0] - cg_x) ** 2 + (p[2] - cg_z) ** 2) for m, p, io in zipped)
    i_zz = sum(io[2] + m * ((p[0] - cg_x) ** 2 + (p[1] - cg_y) ** 2) for m, p, io in zipped)
    i_xy = sum(io[3] + m * (p[0] - cg_x) * (p[1] - cg_y) for m, p, io in zipped)
    i_xz = sum(io[4] + m * (p[0] - cg_x) * (p[2] - cg_z) for m, p, io in zipped)
    i_yz = sum(io[5] + m * (p[1] - cg_y) * (p[2] - cg_z) for m, p, io in zipped)

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
    design_pressure_pa: float | None = None,
    material_yield_pa: float | None = None,
    safety_factor: float = 1.5,
) -> dict:
    """Size a propellant tank and estimate its mass.

    Used for: rocket stage design, aircraft fuel tank sizing, and spacecraft propulsion
    layout. The cylinder is modeled with hemispherical domes (not flat discs), and when a
    design pressure and material yield are supplied the wall thickness is sized from hoop
    stress (t = P*r*SF/sigma_y) rather than taken as an input.

    Args:
        propellant_volume_m3: Required propellant volume
        ullage_fraction: Extra volume for ullage/expansion (default 10%)
        tank_shape: "cylinder", "sphere", or "ellipsoid"
        aspect_ratio: cylinder overall length/diameter (incl. domes; must be > 1)
        wall_thickness_m: Wall thickness used only if design_pressure/material_yield are omitted
        material_density_kg_m3: Tank material density (default 2700 for aluminum)
        design_pressure_pa: Max expected operating pressure (MEOP); enables hoop-stress sizing
        material_yield_pa: Material yield strength for hoop-stress sizing
        safety_factor: Design factor of safety on pressure (default 1.5)
    """
    if propellant_volume_m3 <= 0:
        raise ValueError("propellant_volume must be > 0")
    if ullage_fraction < 0:
        raise ValueError("ullage_fraction must be >= 0")
    if safety_factor <= 0:
        raise ValueError("safety_factor must be > 0")

    total_volume = propellant_volume_m3 * (1.0 + ullage_fraction)

    if tank_shape == "cylinder":
        if aspect_ratio <= 1.0:
            raise ValueError("cylinder aspect_ratio (overall L/D, incl. domes) must be > 1.0")
        # Cylindrical barrel closed by two hemispherical domes (not flat discs):
        #   V = pi*r^2*Lc + 4/3*pi*r^3, overall L = Lc + 2r, AR = L/(2r) -> Lc = 2r(AR-1).
        r = (total_volume / (np.pi * (2.0 * (aspect_ratio - 1.0) + 4.0 / 3.0))) ** (1.0 / 3.0)
        l_cyl = 2.0 * r * (aspect_ratio - 1.0)
        diameter = 2.0 * r
        length = l_cyl + 2.0 * r
        surface_area = 2.0 * np.pi * r * l_cyl + 4.0 * np.pi * r**2  # barrel + 2 hemispheres

    elif tank_shape == "sphere":
        r = ((3.0 * total_volume) / (4.0 * np.pi)) ** (1.0 / 3.0)
        diameter = 2.0 * r
        length = diameter
        surface_area = 4.0 * np.pi * r**2
        aspect_ratio = 1.0

    elif tank_shape == "ellipsoid":
        # Oblate spheroid: equatorial radius a=b=r, polar c=r/aspect_ratio.
        #   V = 4/3*pi*r^2*c = 4/3*pi*r^3/aspect_ratio.
        r = ((3.0 * total_volume * aspect_ratio) / (4.0 * np.pi)) ** (1.0 / 3.0)
        c = r / aspect_ratio
        diameter = 2.0 * r
        length = 2.0 * c
        # Knud Thomsen surface-area approximation (p = 1.6075), not the sphere formula.
        p = 1.6075
        surface_area = 4.0 * np.pi * ((r ** (2 * p) + 2.0 * (r**p * c**p)) / 3.0) ** (1.0 / p)

    else:
        raise ValueError(f"Unknown tank_shape: {tank_shape}")

    # Wall thickness: size it from thin-wall cylinder hoop stress when a design (max
    # expected operating) pressure and a material yield are given: t = P*r*SF/sigma_y.
    # Otherwise fall back to the supplied wall_thickness_m.
    sizing_method = "input_thickness"
    hoop_stress_pa = None
    if design_pressure_pa is not None and material_yield_pa is not None:
        if design_pressure_pa <= 0 or material_yield_pa <= 0:
            raise ValueError("design_pressure_pa and material_yield_pa must be > 0")
        wall_thickness_m = design_pressure_pa * r * safety_factor / material_yield_pa
        hoop_stress_pa = design_pressure_pa * r / wall_thickness_m
        sizing_method = "hoop_stress"

    tank_mass = surface_area * wall_thickness_m * material_density_kg_m3

    return {
        "tank_shape": tank_shape,
        "propellant_volume_m3": round(propellant_volume_m3, 4),
        "total_volume_m3": round(total_volume, 4),
        "ullage_fraction": ullage_fraction,
        "diameter_m": round(diameter, 4),
        "length_m": round(length, 4),
        "aspect_ratio": round(aspect_ratio, 2),
        "wall_thickness_m": round(wall_thickness_m, 6),
        "wall_thickness_sizing": sizing_method,
        "hoop_stress_pa": round(hoop_stress_pa, 2) if hoop_stress_pa is not None else None,
        "design_pressure_pa": design_pressure_pa,
        "safety_factor": safety_factor,
        "surface_area_m2": round(surface_area, 4),
        "tank_mass_kg": round(tank_mass, 4),
        "material_density_kg_m3": material_density_kg_m3,
    }
