"""Margin of safety calculations for aerospace structural analysis.

Covers stress-based, load-based, and combined loading margin of safety
computations per aerospace industry standards.

References:
    - FAA AC 25.571-1D: Damage Tolerance and Fatigue Evaluation of Structure.
      Defines margin of safety methodology and factors of safety.
    - MIL-HDBK-5J / MMPDS-15: Metallic Materials and Elements for
      Aerospace Vehicle Structures. Source for material allowables.
    - Shigley's Mechanical Engineering Design, 11th Ed. (Budynas & Nisbett)
      Margin of safety definitions, factor of safety selection,
      von Mises stress formulation (Section 5-3).
"""

from typing import Literal

import numpy as np

FAILURE_MODES = {
    "yield": "Yield strength",
    "ultimate": "Ultimate strength",
    "buckling": "Critical buckling load",
    "fatigue": "Fatigue endurance limit",
    "custom": "Custom allowable",
}


def margin_of_safety(
    allowable_stress_pa: float | None = None,
    actual_stress_pa: float | None = None,
    allowable_load_n: float | None = None,
    actual_load_n: float | None = None,
    factor_of_safety: float = 1.5,
    failure_mode: Literal[
        "yield", "ultimate", "buckling", "fatigue", "custom"
    ] = "yield",
) -> dict:
    """Compute margin of safety for aerospace structural analysis.

    Margin of Safety (MS) is defined as:
        MS = (Allowable / (FOS × Actual)) − 1

    A positive MS indicates the design is safe. Negative MS means failure.
    MS = 0 means the design is exactly at the limit.

    Common aerospace factors of safety:
    - Yield: 1.15–1.5 (typical 1.5 for metallic structures)
    - Ultimate: 1.5 (FAR 25)
    - Buckling: 1.5–2.0
    - Fatigue: 4.0 (for infinite life)

    Args:
        allowable_stress_pa: Material allowable stress (Pa). Required for stress-based MS.
        actual_stress_pa: Computed/actual stress (Pa). Required for stress-based MS.
        allowable_load_n: Allowable load (N). Required for load-based MS.
        actual_load_n: Applied load (N). Required for load-based MS.
        factor_of_safety: Design factor of safety (default 1.5).
        failure_mode: Type of failure being checked.

    Returns:
        dict with margin_of_safety, utilization_ratio, pass_fail, and metadata.
    """
    if factor_of_safety <= 0:
        raise ValueError("factor_of_safety must be > 0")

    # Determine if stress-based or load-based
    _stress = allowable_stress_pa is not None and actual_stress_pa is not None
    _load = allowable_load_n is not None and actual_load_n is not None

    if not _stress and not _load:
        raise ValueError(
            "Must provide either (allowable_stress_pa + actual_stress_pa) "
            "or (allowable_load_n + actual_load_n)"
        )

    if _stress and _load:
        raise ValueError(
            "Cannot mix stress-based and load-based inputs. "
            "Provide either stress OR load pairs, not both."
        )

    if _stress:
        assert allowable_stress_pa is not None and actual_stress_pa is not None
        if allowable_stress_pa <= 0 or actual_stress_pa <= 0:
            raise ValueError("Stresses must be > 0")
        allowable: float = allowable_stress_pa
        actual: float = actual_stress_pa
        unit = "Pa"
    else:
        assert allowable_load_n is not None and actual_load_n is not None
        if allowable_load_n <= 0 or actual_load_n <= 0:
            raise ValueError("Loads must be > 0")
        allowable = allowable_load_n
        actual = actual_load_n
        unit = "N"

    design_allowable = allowable / factor_of_safety
    utilization_ratio = actual / allowable
    design_utilization = actual / design_allowable

    ms = (design_allowable / actual) - 1.0 if actual > 0 else float("inf")

    if ms > 0:
        status = "PASS"
    elif abs(ms) < 1e-9:
        status = "MARGINAL"
    else:
        status = "FAIL"

    return {
        "margin_of_safety": round(ms, 4),
        "utilization_ratio": round(utilization_ratio, 6),
        "design_utilization": round(design_utilization, 6),
        "factor_of_safety": factor_of_safety,
        "allowable": round(allowable, 2),
        "actual": round(actual, 2),
        "design_allowable": round(design_allowable, 2),
        "unit": unit,
        "failure_mode": failure_mode,
        "status": status,
        "pass": status == "PASS",
    }


def von_mises_stress(
    sigma_x: float,
    sigma_y: float = 0.0,
    tau_xy: float = 0.0,
    sigma_z: float = 0.0,
    tau_yz: float = 0.0,
    tau_xz: float = 0.0,
) -> dict:
    """Compute von Mises equivalent stress for combined loading.

    For plane stress (σz = τyz = τxz = 0):
        σ_vm = sqrt(σx² − σx·σy + σy² + 3·τxy²)

    For full 3D:
        σ_vm = sqrt( (σx−σy)² + (σy−σz)² + (σz−σx)² + 6·(τxy²+τyz²+τxz²) ) / sqrt(2)

    Args:
        sigma_x: Normal stress in x direction (Pa)
        sigma_y: Normal stress in y direction (Pa), default 0
        tau_xy: Shear stress in xy plane (Pa), default 0
        sigma_z: Normal stress in z direction (Pa), default 0
        tau_yz: Shear stress in yz plane (Pa), default 0
        tau_xz: Shear stress in xz plane (Pa), default 0

    Returns:
        dict with von_mises_stress_pa, principal_stresses, and max_shear_stress_pa.
    """
    # Von Mises stress
    term1 = (sigma_x - sigma_y) ** 2
    term2 = (sigma_y - sigma_z) ** 2
    term3 = (sigma_z - sigma_x) ** 2
    term4 = 6.0 * (tau_xy**2 + tau_yz**2 + tau_xz**2)
    sigma_vm = np.sqrt((term1 + term2 + term3 + term4) / 2.0)

    # Principal stresses (eigenvalues of stress tensor)
    stress_tensor = np.array([
        [sigma_x, tau_xy, tau_xz],
        [tau_xy, sigma_y, tau_yz],
        [tau_xz, tau_yz, sigma_z],
    ])
    eigenvalues = np.linalg.eigvalsh(stress_tensor)
    eigenvalues.sort()
    sigma_1, sigma_2, sigma_3 = eigenvalues[2], eigenvalues[1], eigenvalues[0]

    # Maximum shear stress
    tau_max = (sigma_1 - sigma_3) / 2.0

    return {
        "von_mises_stress_pa": round(sigma_vm, 2),
        "von_mises_stress_mpa": round(sigma_vm / 1e6, 4),
        "sigma_1_pa": round(sigma_1, 2),
        "sigma_2_pa": round(sigma_2, 2),
        "sigma_3_pa": round(sigma_3, 2),
        "sigma_1_mpa": round(sigma_1 / 1e6, 4),
        "sigma_2_mpa": round(sigma_2 / 1e6, 4),
        "sigma_3_mpa": round(sigma_3 / 1e6, 4),
        "max_shear_stress_pa": round(tau_max, 2),
        "max_shear_stress_mpa": round(tau_max / 1e6, 4),
    }


def combined_margin_of_safety(
    sigma_x: float,
    sigma_y: float = 0.0,
    tau_xy: float = 0.0,
    yield_strength_pa: float | None = None,
    ultimate_strength_pa: float | None = None,
    factor_of_safety_yield: float = 1.5,
    factor_of_safety_ultimate: float = 1.5,
) -> dict:
    """Compute margin of safety for combined stress state using von Mises.

    This is the standard aerospace approach for checking multi-axial stress states.

    Args:
        sigma_x: Normal stress in x (Pa)
        sigma_y: Normal stress in y (Pa)
        tau_xy: Shear stress in xy (Pa)
        yield_strength_pa: Material yield strength (Pa). Optional.
        ultimate_strength_pa: Material ultimate strength (Pa). Optional.
        factor_of_safety_yield: FOS for yield check (default 1.5)
        factor_of_safety_ultimate: FOS for ultimate check (default 1.5)

    Returns:
        dict with von Mises stress, yield MS, ultimate MS, and pass/fail status.
    """
    vm = von_mises_stress(sigma_x, sigma_y, tau_xy)
    sigma_vm = vm["von_mises_stress_pa"]

    results = {
        "von_mises_stress_pa": vm["von_mises_stress_pa"],
        "von_mises_stress_mpa": vm["von_mises_stress_mpa"],
        "principal_stresses_pa": [
            vm["sigma_1_pa"],
            vm["sigma_2_pa"],
            vm["sigma_3_pa"],
        ],
        "max_shear_stress_pa": vm["max_shear_stress_pa"],
    }

    if yield_strength_pa is not None:
        ms_yield = margin_of_safety(
            allowable_stress_pa=yield_strength_pa,
            actual_stress_pa=sigma_vm,
            factor_of_safety=factor_of_safety_yield,
            failure_mode="yield",
        )
        results["margin_of_safety_yield"] = ms_yield

    if ultimate_strength_pa is not None:
        ms_ultimate = margin_of_safety(
            allowable_stress_pa=ultimate_strength_pa,
            actual_stress_pa=sigma_vm,
            factor_of_safety=factor_of_safety_ultimate,
            failure_mode="ultimate",
        )
        results["margin_of_safety_ultimate"] = ms_ultimate

    return results


def deflection_margin(
    actual_deflection_m: float,
    allowable_deflection_m: float | None = None,
    span_length_m: float | None = None,
    deflection_limit_ratio: float = 360.0,
) -> dict:
    """Compute margin of safety against deflection limits.

    Common aerospace deflection limits:
    - Wing spars: L/360
    - Fuselage frames: L/200
    - Control surfaces: L/500
    - General structures: L/250

    Args:
        actual_deflection_m: Computed deflection (m)
        allowable_deflection_m: Explicit deflection limit (m). Optional.
        span_length_m: Beam span (m). Used with deflection_limit_ratio if allowable not given.
        deflection_limit_ratio: L/deflection ratio (default 360).

    Returns:
        dict with MS, deflection ratio, and status.
    """
    if actual_deflection_m < 0:
        raise ValueError("actual_deflection must be >= 0")

    if allowable_deflection_m is not None:
        allowable = allowable_deflection_m
    elif span_length_m is not None and span_length_m > 0:
        allowable = span_length_m / deflection_limit_ratio
    else:
        raise ValueError(
            "Must provide either allowable_deflection_m or span_length_m"
        )

    if allowable <= 0:
        raise ValueError("allowable deflection must be > 0")

    ratio = (
        span_length_m / actual_deflection_m
        if span_length_m is not None and actual_deflection_m > 0
        else None
    )
    ms = (allowable / actual_deflection_m) - 1.0 if actual_deflection_m > 0 else float("inf")

    if ms > 0:
        status = "PASS"
    elif abs(ms) < 1e-9:
        status = "MARGINAL"
    else:
        status = "FAIL"

    return {
        "margin_of_safety": round(ms, 4),
        "actual_deflection_m": round(actual_deflection_m, 6),
        "allowable_deflection_m": round(allowable, 6),
        "deflection_ratio_l_over_d": (
            round(ratio, 1) if ratio is not None and ratio != float("inf") else None
        ),
        "status": status,
        "pass": status == "PASS",
    }
