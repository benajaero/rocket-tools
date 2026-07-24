"""Column buckling and plate crippling analysis.

Supports aircraft struts, rocket interstage cylinders, drone booms,
helicopter rotor masts, and spacecraft truss members.

References:
    - Timoshenko & Gere, "Theory of Elastic Stability", 2nd Ed.
      Euler buckling load and Johnson parabola for inelastic buckling.
    - Bruhn, "Analysis and Design of Flight Vehicle Structures"
      Plate buckling coefficients (Fig. C5.2, C5.3) and effective
      length factors (Table C2.1).
"""

from typing import Literal

import numpy as np
from numba import njit


@njit(cache=True)
def _euler_buckling_load(e: float, i_val: float, effective_length: float):
    if e <= 0.0 or i_val <= 0.0 or effective_length <= 0.0:
        raise ValueError("E, I, and effective_length must be > 0")
    return (np.pi**2 * e * i_val) / (effective_length**2)


@njit(cache=True)
def _johnson_buckling_load(
    yield_strength: float, area: float, e: float, i_val: float, effective_length: float
):
    """Johnson parabola for short columns (inelastic buckling)."""
    if yield_strength <= 0.0 or area <= 0.0 or e <= 0.0 or i_val <= 0.0 or effective_length <= 0.0:
        raise ValueError("All inputs must be > 0")
    slenderness = effective_length / np.sqrt(i_val / area)
    cc = np.sqrt(2.0 * np.pi**2 * e / yield_strength)
    if slenderness < cc:
        # Johnson parabola
        sigma_cr = yield_strength - (yield_strength**2 / (4.0 * np.pi**2 * e)) * slenderness**2
        return sigma_cr * area
    else:
        # Euler
        return _euler_buckling_load(e, i_val, effective_length)


# Effective length factors for common end conditions
_EFFECTIVE_LENGTH_FACTORS: dict[str, float] = {
    "pinned_pinned": 1.0,
    "fixed_free": 2.0,
    "fixed_pinned": 0.699,
    "fixed_fixed": 0.5,
}


def column_buckling(
    youngs_modulus: float,
    area_moment: float,
    area: float,
    length: float,
    yield_strength: float,
    end_condition: Literal[
        "pinned_pinned", "fixed_free", "fixed_pinned", "fixed_fixed"
    ] = "pinned_pinned",
) -> dict:
    """Compute column buckling load using Euler-Johnson transition.

    Args:
        youngs_modulus: Young's modulus in Pa
        area_moment: I (area moment of inertia) in m^4
        area: Cross-sectional area in m^2
        length: Column length in m
        yield_strength: Material yield strength in Pa
        end_condition: Support condition affecting effective length

    Returns:
        dict with euler_load_n, johnson_load_n, critical_load_n,
        slenderness_ratio, critical_stress_pa, regime
    """
    if youngs_modulus <= 0 or area_moment <= 0 or area <= 0 or length <= 0 or yield_strength <= 0:
        raise ValueError("All material and geometric inputs must be > 0")

    k = _EFFECTIVE_LENGTH_FACTORS.get(end_condition, 1.0)
    effective_length = k * length
    radius_of_gyration = np.sqrt(area_moment / area)
    slenderness = effective_length / radius_of_gyration

    cc = np.sqrt(2.0 * np.pi**2 * youngs_modulus / yield_strength)

    euler_load = _euler_buckling_load(youngs_modulus, area_moment, effective_length)
    johnson_load = _johnson_buckling_load(
        yield_strength, area, youngs_modulus, area_moment, effective_length
    )

    if slenderness < cc:
        critical_load = johnson_load
        regime = "inelastic"
        critical_stress = critical_load / area
    else:
        critical_load = euler_load
        regime = "elastic"
        critical_stress = critical_load / area

    return {
        "euler_load_n": euler_load,
        "johnson_load_n": johnson_load,
        "critical_load_n": critical_load,
        "critical_stress_pa": critical_stress,
        "critical_stress_mpa": critical_stress / 1e6,
        "slenderness_ratio": slenderness,
        "transition_slenderness": cc,
        "effective_length_m": effective_length,
        "end_condition": end_condition,
        "regime": regime,
    }


def plate_buckling_coefficient(
    aspect_ratio: float,
    boundary_condition: Literal["simply_supported", "clamped", "free_edge"] = "simply_supported",
    load_type: Literal["compression", "shear", "bending"] = "compression",
):
    """Return approximate buckling coefficient k for flat rectangular plates.

    Used for aircraft wing skins, rocket propellant tank walls,
    helicopter rotor blade spars, and spacecraft pressure vessels.

    Args:
        aspect_ratio: Plate length / width (a/b)
        boundary_condition: Edge support condition
        load_type: Type of applied load

    Returns:
        Buckling coefficient k (dimensionless)
    """
    if aspect_ratio <= 0:
        raise ValueError("aspect_ratio must be > 0")

    # Approximate coefficients from plate-buckling theory (Timoshenko & Gere;
    # Bruhn, "Analysis and Design of Flight Vehicle Structures").
    r = aspect_ratio
    if load_type == "compression":
        # Simply-supported uniaxial compression: exact minimum over the integer number
        # of buckle half-waves m, k = min_m (m/r + r/m)^2. This is 4.0 at a/b = 1, 2, 3,...
        # and rises toward (1/r + r)^2 (e.g. 6.25 at a/b = 0.5) for short plates. The old
        # min(4*r^2, 4) branch was ~6x unconservative for a/b < 1.
        m_hi = int(r) + 2
        k_ss = min((m / r + r / m) ** 2 for m in range(1, m_hi + 1))
        if boundary_condition == "simply_supported":
            k = k_ss
        elif boundary_condition == "clamped":
            # Clamped unloaded edges: about 1.745x the SS value (long-plate 6.98 vs 4.0).
            k = 1.745 * k_ss
        elif boundary_condition == "free_edge":
            # One unloaded edge free (outstanding flange); long-plate asymptotic value.
            k = 0.425
        else:
            k = k_ss

    elif load_type == "shear":
        # Simply-supported shear buckling.
        if r >= 1.0:
            k = 5.34 + 4.0 / r**2
        else:
            k = 4.0 + 5.34 / r**2

    elif load_type == "bending":
        # Governing (minimum) in-plane-bending buckling coefficient; conservative across
        # aspect ratios (the true k is >= this for short plates).
        k = 41.8 if boundary_condition == "clamped" else 23.9

    else:
        raise ValueError(f"Unknown load_type: {load_type}")

    return round(k, 2)
