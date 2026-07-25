"""Rocket static stability: Barrowman center of pressure and static margin.

Subsonic center-of-pressure estimation for fin-stabilized rockets using the Barrowman
method (Barrowman & Barrowman, 1966; the same method used by OpenRocket and RockSim),
plus the static margin in calibers. This closes the stability gap that a trajectory or
vehicle-sizing study needs before it means anything: a rocket with the CP ahead of the CG
is unflyable regardless of its delta-v.

References:
    - Barrowman, J. S., "The Practical Calculation of the Aerodynamic Characteristics of
      Slender Finned Vehicles", NASA TN (1966).
    - Box, Bishop & Hunt, "Estimating the dynamic and aerodynamic parameters of passively
      controlled high power rockets" (Barrowman summary).
"""

import math

__all__ = ["center_of_pressure", "static_margin"]


def center_of_pressure(
    nose_shape: str,
    nose_length_m: float,
    body_diameter_m: float,
    fin_count: int,
    fin_root_chord_m: float,
    fin_tip_chord_m: float,
    fin_semi_span_m: float,
    fin_sweep_length_m: float,
    fin_position_from_nose_m: float,
    reference_diameter_m: float | None = None,
) -> dict:
    """Subsonic center of pressure of a fin-stabilized rocket (Barrowman method).

    Models a nose cone plus a set of trapezoidal fins on a straight body tube (the body
    contributes negligible normal force in the Barrowman method). Returns the CP location
    measured from the nose tip and the total normal-force-coefficient slope.

    Args:
        nose_shape: "cone", "ogive", or "parabolic".
        nose_length_m: Nose cone length.
        body_diameter_m: Body tube diameter at the fins.
        fin_count: Number of fins (>= 1).
        fin_root_chord_m: Fin root chord Cr.
        fin_tip_chord_m: Fin tip chord Ct (0 for a delta/triangular fin).
        fin_semi_span_m: Fin semi-span s (tip-to-root, perpendicular to the body).
        fin_sweep_length_m: Axial distance from the root leading edge to the tip leading edge.
        fin_position_from_nose_m: Fin root leading-edge position from the nose tip.
        reference_diameter_m: Reference diameter for the coefficients (defaults to body diameter).
    """
    if nose_length_m <= 0:
        raise ValueError("nose_length_m must be > 0")
    if body_diameter_m <= 0:
        raise ValueError("body_diameter_m must be > 0")
    if fin_count < 1:
        raise ValueError("fin_count must be >= 1")
    if fin_root_chord_m <= 0 or fin_semi_span_m <= 0:
        raise ValueError("fin_root_chord_m and fin_semi_span_m must be > 0")
    if fin_tip_chord_m < 0:
        raise ValueError("fin_tip_chord_m must be >= 0")
    if fin_position_from_nose_m < 0:
        raise ValueError("fin_position_from_nose_m must be >= 0")

    d_ref = reference_diameter_m if reference_diameter_m is not None else body_diameter_m
    if d_ref <= 0:
        raise ValueError("reference_diameter_m must be > 0")

    # --- Nose cone ---
    cn_nose = 2.0  # referenced to the reference area
    shape = nose_shape.lower()
    if shape == "cone":
        x_nose = 0.666 * nose_length_m
    elif shape == "ogive":
        x_nose = 0.466 * nose_length_m
    elif shape == "parabolic":
        x_nose = 0.5 * nose_length_m
    else:
        raise ValueError("nose_shape must be one of: cone, ogive, parabolic")

    # --- Fins (Barrowman) ---
    cr = fin_root_chord_m
    ct = fin_tip_chord_m
    s = fin_semi_span_m
    xt = fin_sweep_length_m
    r = body_diameter_m / 2.0
    # Mid-chord line length.
    l_mid = math.sqrt(s**2 + (xt + (ct - cr) / 2.0) ** 2)
    # Body-to-fin interference factor.
    k_fb = 1.0 + r / (s + r)
    cn_fins = (
        k_fb
        * (4.0 * fin_count * (s / d_ref) ** 2)
        / (1.0 + math.sqrt(1.0 + (2.0 * l_mid / (cr + ct)) ** 2))
    )
    # Fin CP from the fin root leading edge.
    x_f = (xt / 3.0) * (cr + 2.0 * ct) / (cr + ct) + (1.0 / 6.0) * (
        (cr + ct) - (cr * ct) / (cr + ct)
    )
    x_fins = fin_position_from_nose_m + x_f

    # --- Combine ---
    cn_total = cn_nose + cn_fins
    x_cp = (cn_nose * x_nose + cn_fins * x_fins) / cn_total

    return {
        "cp_from_nose_m": round(x_cp, 5),
        "cn_alpha_total_per_rad": round(cn_total, 4),
        "cn_alpha_nose": round(cn_nose, 4),
        "cp_nose_from_nose_m": round(x_nose, 5),
        "cn_alpha_fins": round(cn_fins, 4),
        "cp_fins_from_nose_m": round(x_fins, 5),
        "reference_diameter_m": d_ref,
    }


def static_margin(
    cp_from_nose_m: float,
    cg_from_nose_m: float,
    reference_diameter_m: float,
) -> dict:
    """Static margin in calibers from the CP, CG, and reference diameter.

    Static margin = (X_cp - X_cg) / d. Positive (CP aft of CG) is statically stable; a
    common rule of thumb for fin-stabilized rockets is 1-2 calibers.
    """
    if reference_diameter_m <= 0:
        raise ValueError("reference_diameter_m must be > 0")
    if cp_from_nose_m < 0 or cg_from_nose_m < 0:
        raise ValueError("cp and cg positions must be >= 0")

    margin_m = cp_from_nose_m - cg_from_nose_m
    calibers = margin_m / reference_diameter_m
    return {
        "static_margin_calibers": round(calibers, 3),
        "static_margin_m": round(margin_m, 5),
        "cp_from_nose_m": round(cp_from_nose_m, 5),
        "cg_from_nose_m": round(cg_from_nose_m, 5),
        "stable": calibers > 0.0,
        "adequately_stable": 1.0 <= calibers <= 2.0,
    }
