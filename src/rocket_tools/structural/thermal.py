"""Thermal stress and expansion of a restrained member.

A member that is heated or cooled wants to change length by the free thermal strain
alpha*dT. When that motion is restrained, the restraint induces a thermal stress
sigma = -constraint * E * alpha * dT (compressive when heated and held). This is the
first-order thermal-stress check that structural sizing needs but a pure mechanical-load
tool omits.

References:
    - Boresi & Schmidt, "Advanced Mechanics of Materials", 6th Ed. (thermal stress).
    - Roark's Formulas for Stress and Strain (restrained thermal expansion).
"""

__all__ = ["thermal_stress"]


def thermal_stress(
    youngs_modulus_pa: float,
    cte_per_k: float,
    delta_temperature_k: float,
    constraint_factor: float = 1.0,
    length_m: float | None = None,
    area_m2: float | None = None,
) -> dict:
    """Thermal stress and free expansion of a heated/cooled member.

    Args:
        youngs_modulus_pa: Young's modulus E in Pa.
        cte_per_k: Coefficient of thermal expansion alpha in 1/K.
        delta_temperature_k: Temperature change dT in K (positive = heating).
        constraint_factor: Axial restraint fraction, 0 (free) to 1 (fully restrained).
        length_m: Member length in m (optional; enables free-elongation output).
        area_m2: Cross-sectional area in m^2 (optional; enables restraint-force output).

    Sign convention: heating a restrained member (dT > 0) produces compressive stress
    (negative thermal_stress_pa).
    """
    if youngs_modulus_pa <= 0:
        raise ValueError("youngs_modulus_pa must be > 0")
    if not 0.0 <= constraint_factor <= 1.0:
        raise ValueError("constraint_factor must be in [0, 1]")
    if length_m is not None and length_m <= 0:
        raise ValueError("length_m must be > 0 when provided")
    if area_m2 is not None and area_m2 <= 0:
        raise ValueError("area_m2 must be > 0 when provided")

    free_strain = cte_per_k * delta_temperature_k
    # Restraint opposes the free strain: heating (dT>0) held in place -> compression.
    stress = -constraint_factor * youngs_modulus_pa * free_strain

    result: dict = {
        "thermal_stress_pa": round(stress, 3),
        "thermal_stress_mpa": round(stress / 1.0e6, 5),
        "free_thermal_strain": round(free_strain, 9),
        "stress_type": (
            "none" if stress == 0.0 else ("compressive" if stress < 0.0 else "tensile")
        ),
        "constraint_factor": constraint_factor,
        "delta_temperature_k": delta_temperature_k,
    }
    if length_m is not None:
        # Elongation actually realized: the unrestrained fraction of the free expansion.
        free_elongation = free_strain * length_m
        result["free_elongation_m"] = round(free_elongation, 9)
        result["restrained_elongation_m"] = round((1.0 - constraint_factor) * free_elongation, 9)
    if area_m2 is not None:
        result["restraint_force_n"] = round(stress * area_m2, 3)
    return result
