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


def _beam_stations(
    load: float,
    length: float,
    youngs_modulus: float,
    area_moment_m4: float,
    load_type: str,
    support_type: str,
    n: int = 101,
) -> dict:
    """Along-span shear V(x), moment M(x), and deflection d(x) arrays (Roark Table 8.1).

    Returns numpy arrays for the load/support combinations that ``beam_analysis``
    supports for bending (point_midspan: simply_supported / cantilever / fixed_ends;
    distributed: simply_supported / cantilever). ``cantilever`` uses a tip point load,
    matching ``beam_analysis``. Used by ``viz.plot_beam_diagrams``; not an MCP tool.
    """
    x = np.linspace(0.0, length, n)
    e_i = youngs_modulus * area_moment_m4
    w = load
    p = load
    ll = length

    if load_type == "point_midspan" and support_type == "simply_supported":
        v = np.where(x < ll / 2.0, p / 2.0, -p / 2.0)
        m = np.where(x <= ll / 2.0, p * x / 2.0, p * (ll - x) / 2.0)
        d = np.where(
            x <= ll / 2.0,
            p * x * (3.0 * ll**2 - 4.0 * x**2) / (48.0 * e_i),
            p * (ll - x) * (3.0 * ll**2 - 4.0 * (ll - x) ** 2) / (48.0 * e_i),
        )
    elif load_type == "point_tip" and support_type == "cantilever":
        # Point load P at the free tip, fixed at x=0.
        v = np.full_like(x, p)
        m = -p * (ll - x)
        d = p * x**2 * (3.0 * ll - x) / (6.0 * e_i)
    elif load_type == "point_midspan" and support_type == "cantilever":
        # Point load P at mid-span (a = L/2) of a cantilever fixed at x=0.
        a = ll / 2.0
        v = np.where(x < a, p, 0.0)
        m = np.where(x <= a, -p * (a - x), 0.0)
        d = np.where(
            x <= a,
            p * x**2 * (3.0 * a - x) / (6.0 * e_i),
            p * a**2 * (3.0 * x - a) / (6.0 * e_i),
        )
    elif load_type == "point_midspan" and support_type == "fixed_ends":
        v = np.where(x < ll / 2.0, p / 2.0, -p / 2.0)
        m = np.where(
            x <= ll / 2.0,
            p * x / 2.0 - p * ll / 8.0,
            p * (ll - x) / 2.0 - p * ll / 8.0,
        )
        d = np.where(
            x <= ll / 2.0,
            p * x**2 * (3.0 * ll - 4.0 * x) / (48.0 * e_i),
            p * (ll - x) ** 2 * (3.0 * ll - 4.0 * (ll - x)) / (48.0 * e_i),
        )
    elif load_type == "distributed" and support_type == "simply_supported":
        v = w * (ll / 2.0 - x)
        m = w * x * (ll - x) / 2.0
        d = w * x * (ll**3 - 2.0 * ll * x**2 + x**3) / (24.0 * e_i)
    elif load_type == "distributed" and support_type == "cantilever":
        v = w * (ll - x)
        m = -w * (ll - x) ** 2 / 2.0
        d = w * x**2 * (6.0 * ll**2 - 4.0 * ll * x + x**2) / (24.0 * e_i)
    else:
        raise ValueError(
            f"No station diagram for load_type={load_type!r}, support_type={support_type!r}"
        )

    return {
        "x_m": x,
        "shear_n": v,
        "moment_n_m": m,
        "deflection_m": d,
    }


def beam_analysis(
    load: float,
    length: float,
    youngs_modulus: float,
    cross_section: dict,
    load_type: Literal["point_midspan", "point_tip", "distributed", "axial"] = "point_midspan",
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

    # Compute max moment, max deflection, and max shear force V_max by load/support.
    # v_max is the true peak transverse shear force (needed for a correct shear stress);
    # the previous code used `load` directly, which was dimensionally wrong for
    # distributed loads and 2x too large for a simply-supported point load.
    if load_type in ("point_midspan", "point_tip"):
        if load_type == "point_tip" and support_type != "cantilever":
            raise ValueError("point_tip load is only defined for a cantilever (fixed-free) beam")
        if support_type == "simply_supported":
            max_moment = load * length / 4.0
            max_deflection = _deflection_point_load(load, length, youngs_modulus, i_val)
            v_max = load / 2.0
        elif support_type == "cantilever":
            if load_type == "point_tip":
                # Load P at the free tip: M_root = P*L, tip deflection = P*L^3/(3EI).
                max_moment = load * length
                max_deflection = (load * length**3) / (3.0 * youngs_modulus * i_val)
            else:
                # point_midspan: load P at mid-span (a = L/2), not the tip.
                # M_root = P*a; tip deflection = P*a^2*(3L - a)/(6EI) = 5PL^3/(48EI).
                a = length / 2.0
                max_moment = load * a
                max_deflection = load * a**2 * (3.0 * length - a) / (6.0 * youngs_modulus * i_val)
            v_max = load
        elif support_type == "fixed_ends":
            max_moment = load * length / 8.0
            max_deflection = (load * length**3) / (192.0 * youngs_modulus * i_val)
            v_max = load / 2.0
        else:
            raise ValueError(f"Unsupported support type: {support_type}")
    elif load_type == "distributed":
        if support_type == "simply_supported":
            max_moment = load * length**2 / 8.0
            max_deflection = (5 * load * length**4) / (384.0 * youngs_modulus * i_val)
            v_max = load * length / 2.0
        elif support_type == "cantilever":
            max_moment = load * length**2 / 2.0
            max_deflection = (load * length**4) / (8.0 * youngs_modulus * i_val)
            v_max = load * length
        else:
            raise ValueError(f"Unsupported support type for distributed load: {support_type}")
    elif load_type == "axial":
        # Buckling / compression
        max_moment = 0.0
        max_deflection = load * length / (youngs_modulus * area)
        sigma = load / area
        tau = 0.0
        v_max = 0.0
    else:
        raise ValueError(f"Unsupported load type: {load_type}")

    if load_type != "axial":
        sigma = _bending_stress(max_moment, s)
        # Peak transverse shear stress tau_max = k * V_max / A, with the section shape
        # factor k (1.5 for a rectangle, 4/3 for a solid circle).
        shear_factor = 1.5 if cs_type == "rectangle" else 4.0 / 3.0 if cs_type == "circle" else 1.5
        tau = shear_factor * v_max / area

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
        "max_shear_force_n": round(float(v_max), 4),
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
