"""Beam mechanics with Numba JIT fallback.

References:
    - Roark's Formulas for Stress and Strain, 8th Ed. (Young & Budynas)
      Table 8.1: Beam deflections and stresses for common load cases.
    - Euler-Bernoulli beam theory for small deflections.
"""

from collections.abc import Mapping
from typing import Literal

import numpy as np
from numba import njit


@njit(cache=True)
def _bending_stress(m: float, s: float) -> float:
    if s <= 0.0:
        raise ValueError("Section modulus must be > 0")
    return m / s


@njit(cache=True)
def _deflection_point_load(p: float, beam_length: float, e: float, i_val: float) -> float:
    if e <= 0.0 or i_val <= 0.0:
        raise ValueError("E and I must be > 0")
    return (p * beam_length**3) / (48.0 * e * i_val)


@njit(cache=True)
def _section_modulus_rectangle(b: float, h: float) -> float:
    if b <= 0.0 or h <= 0.0:
        raise ValueError("Dimensions must be > 0")
    return (b * h**2) / 6.0


@njit(cache=True)
def _area_moment_rectangle(b: float, h: float) -> float:
    if b <= 0.0 or h <= 0.0:
        raise ValueError("Dimensions must be > 0")
    return (b * h**3) / 12.0


@njit(cache=True)
def _shear_stress_average(v: float, a: float) -> float:
    if a <= 0.0:
        raise ValueError("Area must be > 0")
    return v / a


@njit(cache=True)
def _critical_buckling_load(e: float, i_val: float, beam_length: float, k_factor: float) -> float:
    if e <= 0.0 or i_val <= 0.0 or beam_length <= 0.0:
        raise ValueError("E, I, and L must be > 0")
    if k_factor <= 0.0:
        raise ValueError("Effective length factor must be > 0")
    effective_length = k_factor * beam_length
    return (np.pi**2 * e * i_val) / (effective_length**2)


def _effective_length_factor(support_type: str) -> float:
    if support_type == "simply_supported":
        return 1.0
    if support_type == "fixed_ends":
        return 0.5
    if support_type == "cantilever":
        return 2.0
    raise ValueError(f"Unsupported support type: {support_type}")


def _require_finite(value: float, name: str) -> None:
    if not np.isfinite(value):
        raise ValueError(f"{name} must be finite")


def _positive_section_value(cross_section: Mapping[str, object], key: str) -> float:
    value = cross_section.get(key, 0.0)
    if not isinstance(value, int | float) or not np.isfinite(value) or value <= 0.0:
        raise ValueError(f"{key.replace('_', ' ').capitalize()} must be > 0")
    return float(value)


def beam_analysis(
    load: float,
    length: float,
    youngs_modulus: float,
    cross_section: dict,
    load_type: Literal["point_midspan", "distributed", "axial"] = "point_midspan",
    support_type: Literal["simply_supported", "cantilever", "fixed_ends"] = "simply_supported",
    yield_strength: float | None = None,
) -> dict:
    """
    Unified beam analysis entry point.

    Parameters
    ----------
    load : float
        Applied load (N for force, N/m for distributed)
    length : float
        Beam span length (m)
    youngs_modulus : float
        E in Pa
    cross_section : dict
        {"type": "rectangle", "width": float, "height": float}
        or {"type": "circle", "diameter": float}
    load_type : str
        "point_midspan", "distributed", "axial"
    support_type : str
        "simply_supported", "cantilever", "fixed_ends"
    yield_strength : float, optional
        Material yield strength in Pa. When provided, result includes safety factor to yield.

    Returns
    -------
    dict
        Complete structural analysis result
    """
    _require_finite(load, "Load")
    _require_finite(length, "Length")
    _require_finite(youngs_modulus, "Young's modulus")
    if length <= 0:
        raise ValueError("Length must be > 0")
    if youngs_modulus <= 0:
        raise ValueError("Young's modulus must be > 0")
    if yield_strength is not None:
        _require_finite(yield_strength, "Yield strength")
        if yield_strength <= 0:
            raise ValueError("Yield strength must be > 0")
    if not isinstance(cross_section, Mapping):
        raise ValueError("Cross-section must be a mapping")

    # Cross-section properties
    cs_type = cross_section.get("type", "rectangle")
    if cs_type == "rectangle":
        b = _positive_section_value(cross_section, "width")
        h = _positive_section_value(cross_section, "height")
        i_val = _area_moment_rectangle(b, h)
        s = _section_modulus_rectangle(b, h)
        area = b * h
    elif cs_type == "circle":
        d = _positive_section_value(cross_section, "diameter")
        r = d / 2.0
        i_val = np.pi * r**4 / 4.0
        s = np.pi * r**3 / 4.0
        area = np.pi * r**2
    else:
        raise ValueError(f"Unsupported cross-section type: {cs_type}")

    # Compute based on load type and support
    if load_type == "point_midspan":
        if support_type == "simply_supported":
            max_moment = load * length / 4.0
            max_deflection = _deflection_point_load(load, length, youngs_modulus, i_val)
        elif support_type == "cantilever":
            max_moment = load * length
            max_deflection = (load * length**3) / (3.0 * youngs_modulus * i_val)
        elif support_type == "fixed_ends":
            max_moment = load * length / 8.0
            max_deflection = (load * length**3) / (192.0 * youngs_modulus * i_val)
        else:
            raise ValueError(f"Unsupported support type: {support_type}")
    elif load_type == "distributed":
        if support_type == "simply_supported":
            max_moment = load * length**2 / 8.0
            max_deflection = (5 * load * length**4) / (384.0 * youngs_modulus * i_val)
        elif support_type == "cantilever":
            max_moment = load * length**2 / 2.0
            max_deflection = (load * length**4) / (8.0 * youngs_modulus * i_val)
        else:
            raise ValueError(f"Unsupported support type for distributed load: {support_type}")
    elif load_type == "axial":
        # Buckling / compression
        max_moment = 0.0
        max_deflection = load * length / (youngs_modulus * area)
        sigma = load / area
        tau = 0.0
    else:
        raise ValueError(f"Unsupported load type: {load_type}")

    if load_type != "axial":
        sigma = _bending_stress(max_moment, s)
        tau = _shear_stress_average(abs(load), area)

    k_factor = _effective_length_factor(support_type)

    # Critical buckling load (Euler) using an effective column length K*L.
    p_cr = _critical_buckling_load(youngs_modulus, i_val, length, k_factor)

    # Safety factor against Euler buckling
    sf_buckling = float("inf")
    if load_type == "axial" and load > 0:
        sf_buckling = p_cr / load

    # Section efficiency (I/A - higher is better for bending stiffness per weight)
    efficiency = i_val / area
    safety_factor_yield = None
    if yield_strength is not None:
        stress = abs(float(sigma))
        safety_factor_yield = None if stress == 0.0 else yield_strength / stress

    return {
        "max_bending_moment_n_m": round(float(max_moment), 4),
        "max_deflection_m": round(float(max_deflection), 8),
        "bending_stress_pa": round(float(sigma), 2),
        "shear_stress_pa": round(float(tau), 2),
        "max_normal_stress_pa": round(float(sigma), 2),  # for uniaxial bending
        "section_modulus_m3": float(s),
        "area_moment_m4": float(i_val),
        "cross_sectional_area_m2": round(float(area), 8),
        "critical_buckling_load_n": round(float(p_cr), 2),
        "effective_length_factor": k_factor,
        "yield_strength_pa": yield_strength,
        "safety_factor_yield": round(float(safety_factor_yield), 2)
        if safety_factor_yield is not None
        else None,
        "safety_factor_euler_buckling": round(float(sf_buckling), 2)
        if sf_buckling != float("inf")
        else None,
        "section_efficiency_m2": round(float(efficiency), 8),
        "load_type": load_type,
        "support_type": support_type,
    }
