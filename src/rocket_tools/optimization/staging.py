"""Optimal multi-stage rocket staging (restricted problem, Lagrange multiplier).

Given a total delta-v target and per-stage effective exhaust velocity c_i = Isp_i*g0
and structural ratio eps_i = m_structure_i/(m_structure_i + m_propellant_i), find the
stage mass ratios that MAXIMIZE the overall payload fraction. The classic Lagrange
solution reduces the whole problem to a single scalar equation in the multiplier
lambda, solved here by a robust bracketed bisection (no negative-delta-v escape).

References:
    - Curtis, "Orbital Mechanics for Engineering Students", 3rd Ed. (Ch. 11, optimal
      staging / restricted problem).
    - Hill & Peterson, "Mechanics and Thermodynamics of Propulsion", 2nd Ed. (staging).
"""

import math

from rocket_tools.utils.validation import ToolError

G0 = 9.80665


def _delta_v_of_lambda(lam: float, c: list[float], eps: list[float]) -> float:
    """Total delta-v achieved by the optimal ratios at Lagrange multiplier ``lam``."""
    total = 0.0
    for ci, ei in zip(c, eps):
        n_i = (ci * lam - 1.0) / (ci * lam * ei)
        total += ci * math.log(n_i)
    return total


def optimize_staging(
    delta_v_target_ms: float,
    stages: list[dict],
    payload_mass_kg: float = 1.0,
    gravity: float = G0,
) -> dict:
    """Optimal delta-v split across stages that maximizes overall payload fraction.

    Args:
        delta_v_target_ms: Required total mission delta-v (m/s).
        stages: List of dicts, each with ``specific_impulse_s`` and ``structural_ratio``
            (epsilon in (0,1)).
        payload_mass_kg: Payload mass (for absolute stage masses; the payload fraction
            is dimensionless and independent of this).
        gravity: g0 for c = Isp*g0 (m/s^2).

    Returns:
        dict with per-stage optimal delta-v / mass ratio, total delta-v, overall
        ``optimal_payload_fraction``, the Lagrange multiplier, and
        ``max_achievable_delta_v_ms``. Returns ``achievable=False`` with the max
        achievable delta-v when the target exceeds the theoretical ceiling.
    """
    if delta_v_target_ms <= 0:
        raise ValueError("delta_v_target_ms must be > 0")
    if len(stages) < 1:
        raise ValueError("at least one stage is required")

    c: list[float] = []
    eps: list[float] = []
    for i, st in enumerate(stages):
        isp = st.get("specific_impulse_s")
        ep = st.get("structural_ratio")
        if isp is None or ep is None:
            raise ValueError(f"stage {i}: needs specific_impulse_s and structural_ratio")
        if isp <= 0:
            raise ValueError(f"stage {i}: specific_impulse_s must be > 0")
        if not 0.0 < ep < 1.0:
            raise ValueError(f"stage {i}: structural_ratio must be in (0, 1)")
        c.append(isp * gravity)
        eps.append(ep)

    # Theoretical ceiling: every stage mass ratio -> 1/eps_i as lambda -> infinity.
    dv_max = sum(ci * math.log(1.0 / ei) for ci, ei in zip(c, eps))
    if delta_v_target_ms >= dv_max:
        return {
            "achievable": False,
            "reason": "delta-v target exceeds the theoretical maximum for these stages",
            "max_achievable_delta_v_ms": round(dv_max, 2),
            "delta_v_target_ms": round(delta_v_target_ms, 2),
        }

    # lambda must keep every mass ratio > 1: lambda > 1/(c_i*(1-eps_i)).
    lam_min = max(1.0 / (ci * (1.0 - ei)) for ci, ei in zip(c, eps))
    lam_lo = lam_min * (1.0 + 1e-12)

    # delta-v is monotonically increasing in lambda; bracket the target.
    if _delta_v_of_lambda(lam_lo, c, eps) > delta_v_target_ms:
        # Optimum would require a stage to contribute negative delta-v: ill-posed target.
        raise ToolError(
            "delta-v target is below the well-posed optimum for these stages "
            "(a stage would need to do no/negative work)",
            error_code="INFEASIBLE",
            parameter="delta_v_target_ms",
            constraint="target must lie in the interior optimal range",
            suggestion="Increase the target, reduce the number of stages, or relax epsilon.",
        )
    lam_hi = lam_lo
    for _ in range(200):
        lam_hi *= 2.0
        if _delta_v_of_lambda(lam_hi, c, eps) > delta_v_target_ms:
            break

    # Bisection on the monotone delta-v(lambda).
    for _ in range(200):
        lam = 0.5 * (lam_lo + lam_hi)
        if _delta_v_of_lambda(lam, c, eps) < delta_v_target_ms:
            lam_lo = lam
        else:
            lam_hi = lam
    lam = 0.5 * (lam_lo + lam_hi)

    # Recover per-stage ratios and the overall payload fraction.
    stage_out = []
    payload_fraction = 1.0
    total_dv = 0.0
    for i, (ci, ei) in enumerate(zip(c, eps)):
        n_i = (ci * lam - 1.0) / (ci * lam * ei)
        dv_i = ci * math.log(n_i)
        total_dv += dv_i
        pi = (1.0 / n_i - ei) / (1.0 - ei)  # stage payload ratio
        payload_fraction *= pi
        stage_out.append(
            {
                "stage": i + 1,
                "specific_impulse_s": round(ci / gravity, 2),
                "structural_ratio": ei,
                "delta_v_ms": round(dv_i, 2),
                "mass_ratio": round(n_i, 4),
                "stage_payload_ratio": round(pi, 5),
            }
        )

    gross_mass = payload_mass_kg / payload_fraction if payload_fraction > 0 else float("inf")

    return {
        "achievable": True,
        "lagrange_multiplier": lam,
        "total_delta_v_ms": round(total_dv, 2),
        "delta_v_target_ms": round(delta_v_target_ms, 2),
        "optimal_payload_fraction": round(payload_fraction, 6),
        "max_achievable_delta_v_ms": round(dv_max, 2),
        "gross_liftoff_mass_kg": round(gross_mass, 2),
        "payload_mass_kg": payload_mass_kg,
        "stages": stage_out,
    }
