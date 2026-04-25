"""Beam mechanics with Numba JIT fallback."""

import numpy as np
from numba import njit
from typing import Literal


@njit(cache=True)
def _bending_stress(m: float, s: float) -> float:
    if s <= 0.0:
        raise ValueError("Section modulus must be > 0")
    return m / s


@njit(cache=True)
def _deflection_point_load(p: float, l: float, e: float, i_val: float) -> float:
    if e <= 0.0 or i_val <= 0.0:
        raise ValueError("E and I must be > 0")
    return (p * l ** 3) / (48.0 * e * i_val)


@njit(cache=True)
def _section_modulus_rectangle(b: float, h: float) -> float:
    if b <= 0.0 or h <= 0.0:
        raise ValueError("Dimensions must be > 0")
    return (b * h ** 2) / 6.0


@njit(cache=True)
def _area_moment_rectangle(b: float, h: float) -> float:
    return (b * h ** 3) / 12.0


@njit(cache=True)
def _shear_stress_average(v: float, a: float) -> float:
    if a <= 0.0:
        raise ValueError("Area must be > 0")
    return v / a


@njit(cache=True)
def _critical_buckling_load(e: float, i_val: float, l: float) -> float:
    if e <= 0.0 or i_val <= 0.0 or l <= 0.0:
        raise ValueError("E, I, and L must be > 0")
    return (np.pi ** 2 * e * i_val) / (l ** 2)


def beam_analysis(
    load: float,
    length: float,
    youngs_modulus: float,
    cross_section: dict,
    load_type: Literal["point_midspan", "distributed", "axial"] = "point_midspan",
    support_type: Literal["simply_supported", "cantilever", "fixed_ends"] = "simply_supported",
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
        {"type": "rectangle", "width": float, "height": float} or {"type": "circle", "diameter": float}
    load_type : str
        "point_midspan", "distributed", "axial"
    support_type : str
        "simply_supported", "cantilever", "fixed_ends"
    
    Returns
    -------
    dict
        Complete structural analysis result
    """
    if length <= 0:
        raise ValueError("Length must be > 0")
    if youngs_modulus <= 0:
        raise ValueError("Young's modulus must be > 0")

    # Cross-section properties
    cs_type = cross_section.get("type", "rectangle")
    if cs_type == "rectangle":
        b = cross_section.get("width", 0.0)
        h = cross_section.get("height", 0.0)
        if b <= 0 or h <= 0:
            raise ValueError("Width and height must be > 0")
        i_val = _area_moment_rectangle(b, h)
        s = _section_modulus_rectangle(b, h)
        area = b * h
    elif cs_type == "circle":
        d = cross_section.get("diameter", 0.0)
        if d <= 0:
            raise ValueError("Diameter must be > 0")
        r = d / 2.0
        i_val = np.pi * r ** 4 / 4.0
        s = np.pi * r ** 3 / 4.0
        area = np.pi * r ** 2
    else:
        raise ValueError(f"Unsupported cross-section type: {cs_type}")

    # Compute based on load type and support
    if load_type == "point_midspan":
        if support_type == "simply_supported":
            max_moment = load * length / 4.0
            max_deflection = _deflection_point_load(load, length, youngs_modulus, i_val)
        elif support_type == "cantilever":
            max_moment = load * length
            max_deflection = (load * length ** 3) / (3.0 * youngs_modulus * i_val)
        elif support_type == "fixed_ends":
            max_moment = load * length / 8.0
            max_deflection = (load * length ** 3) / (192.0 * youngs_modulus * i_val)
        else:
            raise ValueError(f"Unsupported support type: {support_type}")
    elif load_type == "distributed":
        if support_type == "simply_supported":
            max_moment = load * length ** 2 / 8.0
            max_deflection = (5 * load * length ** 4) / (384.0 * youngs_modulus * i_val)
        elif support_type == "cantilever":
            max_moment = load * length ** 2 / 2.0
            max_deflection = (load * length ** 4) / (8.0 * youngs_modulus * i_val)
        else:
            raise ValueError(f"Unsupported support type for distributed load: {support_type}")
    elif load_type == "axial":
        # Buckling / compression
        max_moment = 0.0
        max_deflection = load * length / (youngs_modulus * area)
    else:
        raise ValueError(f"Unsupported load type: {load_type}")

    sigma = _bending_stress(max_moment, s)
    tau = _shear_stress_average(load, area)
    
    # Critical buckling load (Euler)
    p_cr = _critical_buckling_load(youngs_modulus, i_val, length)

    # Safety factor against Euler buckling
    sf_buckling = float("inf")
    if load_type == "axial" and load > 0:
        sf_buckling = p_cr / load

    # Section efficiency (I/A - higher is better for bending stiffness per weight)
    efficiency = i_val / area

    return {
        "max_bending_moment_n_m": round(float(max_moment), 4),
        "max_deflection_m": round(float(max_deflection), 8),
        "bending_stress_pa": round(float(sigma), 2),
        "shear_stress_pa": round(float(tau), 2),
        "max_normal_stress_pa": round(float(sigma), 2),  # for uniaxial bending
        "section_modulus_m3": round(float(s), 8),
        "area_moment_m4": round(float(i_val), 8),
        "cross_sectional_area_m2": round(float(area), 8),
        "critical_buckling_load_n": round(float(p_cr), 2),
        "safety_factor_euler_buckling": round(float(sf_buckling), 2) if sf_buckling != float("inf") else None,
        "section_efficiency_m2": round(float(efficiency), 8),
        "load_type": load_type,
        "support_type": support_type,
    }
