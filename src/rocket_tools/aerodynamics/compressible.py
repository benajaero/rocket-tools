"""Compressible flow relations for supersonic aircraft, rockets, and missiles.

Covers:
- Isentropic flow (T/T0, P/P0, rho/rho0, A/A*)
- Normal shock relations
- Oblique shock relations
- Prandtl-Meyer expansion

References:
    - Anderson, "Fundamentals of Aerodynamics", 6th Ed. (Ch. 4)
      Isentropic flow relations (Eq. 4.43-4.50),
      normal shock relations (Eq. 4.58-4.65),
      oblique shock (Eq. 4.85-4.89),
      Prandtl-Meyer function (Eq. 4.104).
    - Hill & Peterson, "Mechanics and Thermodynamics of Propulsion", 2nd Ed.
      Area-Mach relation, choked flow conditions.
"""

import numpy as np
from numba import njit

from rocket_tools.utils.validation import ToolError

GAMMA = 1.4  # Ratio of specific heats for air


@njit(cache=True)
def _mach_from_area_ratio(a_a_star: float, gamma: float = GAMMA):
    """Solve for supersonic Mach number given A/A* using Newton-Raphson."""
    if a_a_star < 1.0:
        raise ValueError("A/A* must be >= 1.0")
    # Initial guess for supersonic branch
    m = 2.0 if a_a_star < 2.0 else a_a_star
    for _ in range(50):
        f = _area_ratio(m, gamma) - a_a_star
        df = _d_area_ratio_dm(m, gamma)
        if abs(df) < 1e-12:
            break
        m_new = m - f / df
        if m_new <= 1.0:
            m_new = 1.01
        if abs(m_new - m) < 1e-8:
            return m_new
        m = m_new
    return m


@njit(cache=True)
def _area_ratio(m: float, gamma: float = GAMMA):
    if m <= 0.0:
        raise ValueError("Mach number must be > 0")
    g1 = (gamma + 1.0) / 2.0
    g2 = (gamma - 1.0) / 2.0
    return (1.0 / m) * ((1.0 + g2 * m**2) / g1) ** (g1 / (gamma - 1.0))


@njit(cache=True)
def _d_area_ratio_dm(m: float, gamma: float = GAMMA):
    g1 = (gamma + 1.0) / 2.0
    g2 = (gamma - 1.0) / 2.0
    term = (1.0 + g2 * m**2) / g1
    return -(1.0 / m**2) * term ** (g1 / (gamma - 1.0)) + (1.0 / m) * term ** (
        g1 / (gamma - 1.0) - 1.0
    ) * (g1 / (gamma - 1.0)) * (2.0 * g2 * m / g1)


@njit(cache=True)
def _isentropic_t_ratio(m: float, gamma: float = GAMMA):
    return 1.0 / (1.0 + (gamma - 1.0) / 2.0 * m**2)


@njit(cache=True)
def _isentropic_p_ratio(m: float, gamma: float = GAMMA):
    return (1.0 / (1.0 + (gamma - 1.0) / 2.0 * m**2)) ** (gamma / (gamma - 1.0))


@njit(cache=True)
def _isentropic_rho_ratio(m: float, gamma: float = GAMMA):
    return (1.0 / (1.0 + (gamma - 1.0) / 2.0 * m**2)) ** (1.0 / (gamma - 1.0))


@njit(cache=True)
def _normal_shock_m2(m1: float, gamma: float = GAMMA):
    m1sq = m1**2
    return np.sqrt((1.0 + (gamma - 1.0) / 2.0 * m1sq) / (gamma * m1sq - (gamma - 1.0) / 2.0))


@njit(cache=True)
def _normal_shock_p2_p1(m1: float, gamma: float = GAMMA):
    return 1.0 + 2.0 * gamma / (gamma + 1.0) * (m1**2 - 1.0)


@njit(cache=True)
def _normal_shock_rho2_rho1(m1: float, gamma: float = GAMMA):
    return (gamma + 1.0) * m1**2 / (2.0 + (gamma - 1.0) * m1**2)


@njit(cache=True)
def _normal_shock_t2_t1(m1: float, gamma: float = GAMMA):
    return _normal_shock_p2_p1(m1, gamma) / _normal_shock_rho2_rho1(m1, gamma)


@njit(cache=True)
def _normal_shock_p0_ratio(m1: float, gamma: float = GAMMA):
    """Stagnation pressure ratio p02/p01 across a normal shock (NACA 1135 Eq. 100).

    p02/p01 = [ (g+1) M1^2 / ((g-1) M1^2 + 2) ]^(g/(g-1))
              * [ (g+1) / (2 g M1^2 - (g-1)) ]^(1/(g-1))

    Always <= 1: total pressure drops across a shock (entropy rises).
    """
    m1sq = m1 * m1
    term1 = ((gamma + 1.0) * m1sq / ((gamma - 1.0) * m1sq + 2.0)) ** (gamma / (gamma - 1.0))
    term2 = ((gamma + 1.0) / (2.0 * gamma * m1sq - (gamma - 1.0))) ** (1.0 / (gamma - 1.0))
    return term1 * term2


@njit(cache=True)
def _prandtl_meyer_nu(m: float, gamma: float = GAMMA):
    """Prandtl-Meyer function nu(M) in radians."""
    if m <= 1.0:
        return 0.0
    gp1 = gamma + 1.0
    gm1 = gamma - 1.0
    return np.sqrt(gp1 / gm1) * np.arctan(np.sqrt(gm1 / gp1 * (m**2 - 1.0))) - np.arctan(
        np.sqrt(m**2 - 1.0)
    )


@njit(cache=True)
def _prandtl_meyer_mach(nu: float, gamma: float = GAMMA):
    """Solve for Mach number given Prandtl-Meyer angle (radians)."""
    if nu <= 0.0:
        return 1.0
    m = 1.5
    for _ in range(50):
        f = _prandtl_meyer_nu(m, gamma) - nu
        df = np.sqrt(m**2 - 1.0) / (1.0 + (gamma - 1.0) / 2.0 * m**2) / m
        if abs(df) < 1e-12:
            break
        m_new = m - f / df
        if m_new <= 1.0:
            m_new = 1.001
        if abs(m_new - m) < 1e-8:
            return m_new
        m = m_new
    return m


@njit(cache=True)
def _oblique_theta_from_beta(m1: float, beta: float, gamma: float = GAMMA):
    """theta-beta-M relation: deflection theta (rad) for a wave angle beta (rad)."""
    sb = np.sin(beta)
    cb = np.cos(beta)
    num = 2.0 * (cb / sb) * (m1**2 * sb**2 - 1.0)
    den = m1**2 * (gamma + np.cos(2.0 * beta)) + 2.0
    return np.arctan(num / den)


@njit(cache=True)
def _oblique_shock_theta_max(m1: float, gamma: float = GAMMA):
    """Maximum deflection (rad) for an attached shock and the wave angle where it occurs.

    theta(beta) rises from 0 at the Mach angle to a single maximum, then falls to 0
    at beta=90 deg; above theta_max the shock detaches. Coarse-scan then refine.
    """
    beta_min = np.arcsin(1.0 / m1)
    beta_hi = np.pi / 2.0
    best_theta = 0.0
    best_beta = beta_min
    n = 2000
    for i in range(1, n):
        beta = beta_min + (beta_hi - beta_min) * i / n
        t = _oblique_theta_from_beta(m1, beta, gamma)
        if t > best_theta:
            best_theta = t
            best_beta = beta
    # Refine around the peak by climbing the local gradient.
    step = (beta_hi - beta_min) / n
    lo = best_beta - step
    hi = best_beta + step
    for _ in range(100):
        mid = (lo + hi) / 2.0
        d = 1e-8
        if _oblique_theta_from_beta(m1, mid + d, gamma) > _oblique_theta_from_beta(
            m1, mid - d, gamma
        ):
            lo = mid
        else:
            hi = mid
    best_beta = (lo + hi) / 2.0
    return _oblique_theta_from_beta(m1, best_beta, gamma), best_beta


@njit(cache=True)
def _oblique_shock_beta(m1: float, theta: float, beta_star: float, gamma: float = GAMMA):
    """Weak-shock wave angle beta (rad) for deflection theta (rad).

    The weak (physically-realized, attached) solution lies on the rising branch
    below beta_star, where theta(beta) is monotonic. Callers must reject
    theta > theta_max first (detached shock — no attached solution exists).
    """
    if theta <= 0.0 or m1 <= 1.0:
        raise ValueError("theta must be > 0 and M1 > 1 for oblique shocks")

    beta_lo = np.arcsin(1.0 / m1) + 1e-9
    beta_hi = beta_star
    for _ in range(100):
        beta = (beta_lo + beta_hi) / 2.0
        t = _oblique_theta_from_beta(m1, beta, gamma)
        if t < theta:
            beta_lo = beta
        else:
            beta_hi = beta
        if abs(t - theta) < 1e-10:
            return beta

    return (beta_lo + beta_hi) / 2.0


def isentropic_flow(mach: float, gamma: float = GAMMA) -> dict:
    """Compute isentropic flow ratios for given Mach number.

    Used for: rocket nozzle design, supersonic aircraft intake analysis,
    wind tunnel calibration, and spacecraft re-entry aerothermodynamics.
    """
    if mach <= 0.0:
        raise ValueError("Mach number must be > 0")

    t_t0 = _isentropic_t_ratio(mach, gamma)
    p_p0 = _isentropic_p_ratio(mach, gamma)
    rho_rho0 = _isentropic_rho_ratio(mach, gamma)
    a_a_star = _area_ratio(mach, gamma)

    # Mach angle for supersonic
    mach_angle = np.degrees(np.arcsin(1.0 / mach)) if mach > 1.0 else None

    # Dynamic pressure ratio q/q0
    q_q0 = mach**2 * rho_rho0

    return {
        "mach": mach,
        "gamma": gamma,
        "temperature_ratio": round(t_t0, 6),
        "pressure_ratio": round(p_p0, 6),
        "density_ratio": round(rho_rho0, 6),
        "area_ratio": round(a_a_star, 6),
        "dynamic_pressure_ratio": round(q_q0, 6),
        "mach_angle_deg": round(mach_angle, 2) if mach_angle is not None else None,
    }


def normal_shock(mach1: float, gamma: float = GAMMA) -> dict:
    """Compute normal shock relations for given upstream Mach number.

    Used for: supersonic intake design, shock tube analysis,
    rocket nozzle overexpanded flow, and re-entry capsule bow shocks.
    """
    if mach1 <= 1.0:
        raise ValueError("Upstream Mach number must be > 1.0 for normal shock")

    m2 = _normal_shock_m2(mach1, gamma)
    p2_p1 = _normal_shock_p2_p1(mach1, gamma)
    rho2_rho1 = _normal_shock_rho2_rho1(mach1, gamma)
    t2_t1 = _normal_shock_t2_t1(mach1, gamma)
    p0_ratio = _normal_shock_p0_ratio(mach1, gamma)

    return {
        "mach_upstream": mach1,
        "mach_downstream": round(m2, 6),
        "pressure_ratio": round(p2_p1, 6),
        "density_ratio": round(rho2_rho1, 6),
        "temperature_ratio": round(t2_t1, 6),
        "stagnation_pressure_ratio": round(p0_ratio, 6),
        "gamma": gamma,
    }


def oblique_shock(mach1: float, deflection_deg: float, gamma: float = GAMMA) -> dict:
    """Compute oblique shock relations for given upstream Mach and deflection angle.

    Returns the **weak** (physically-realized, attached) shock solution. If the
    deflection exceeds the maximum for an attached shock at this Mach the shock
    detaches (a curved bow shock forms) and no oblique-shock solution exists —
    a ValueError is raised naming the maximum deflection.

    Used for: supersonic wing design, inlet geometry, and missile aerodynamics.
    """
    if mach1 <= 1.0:
        raise ValueError("Upstream Mach number must be > 1.0")
    if deflection_deg <= 0.0 or deflection_deg >= 90.0:
        raise ValueError("deflection_deg must be between 0 and 90")

    theta = np.radians(deflection_deg)
    theta_max, beta_star = _oblique_shock_theta_max(mach1, gamma)
    theta_max_deg = float(np.degrees(theta_max))
    if theta > theta_max:
        raise ToolError(
            f"deflection_deg={deflection_deg:g} exceeds the maximum "
            f"{theta_max_deg:.2f} deg for an attached oblique shock at M1={mach1:g}; "
            "the shock detaches into a curved bow shock",
            error_code="INVALID_PARAMETER",
            parameter="deflection_deg",
            constraint=f"deflection_deg <= {theta_max_deg:.2f} (theta_max at M1={mach1:g})",
            suggestion=(
                f"Reduce deflection_deg to <= {theta_max_deg:.2f} deg, or increase mach1. "
                "Above theta_max the shock detaches and no attached oblique-shock solution exists."
            ),
        )

    beta = _oblique_shock_beta(mach1, theta, beta_star, gamma)
    beta_deg = np.degrees(beta)

    mn1 = mach1 * np.sin(beta)
    mn2 = _normal_shock_m2(mn1, gamma)
    m2 = mn2 / np.sin(beta - theta)

    p2_p1 = _normal_shock_p2_p1(mn1, gamma)
    rho2_rho1 = _normal_shock_rho2_rho1(mn1, gamma)
    t2_t1 = _normal_shock_t2_t1(mn1, gamma)

    return {
        "mach_upstream": mach1,
        "mach_downstream": round(m2, 6),
        "wave_angle_deg": round(beta_deg, 2),
        "deflection_angle_deg": round(deflection_deg, 2),
        "solution": "weak",
        "max_deflection_deg": round(theta_max_deg, 2),
        "normal_mach_upstream": round(float(mn1), 6),
        "pressure_ratio": round(p2_p1, 6),
        "density_ratio": round(rho2_rho1, 6),
        "temperature_ratio": round(t2_t1, 6),
        "gamma": gamma,
    }


def prandtl_meyer(mach: float, gamma: float = GAMMA) -> dict:
    """Compute Prandtl-Meyer expansion angle for given Mach number.

    Used for: supersonic nozzle design, expansion fan analysis on wing leading edges,
    and rocket exhaust plume boundary calculations.
    """
    if mach < 1.0:
        raise ValueError("Mach number must be >= 1.0 for Prandtl-Meyer function")

    nu_rad = _prandtl_meyer_nu(mach, gamma)
    nu_deg = np.degrees(nu_rad)

    return {
        "mach": mach,
        "prandtl_meyer_angle_deg": round(nu_deg, 4),
        "prandtl_meyer_angle_rad": round(nu_rad, 6),
        "gamma": gamma,
    }


def prandtl_meyer_from_angle(angle_deg: float, gamma: float = GAMMA) -> dict:
    """Compute Mach number from Prandtl-Meyer expansion angle.

    Used for: determining Mach number at nozzle exit given expansion angle,
    or analyzing flow around a corner.
    """
    if angle_deg < 0.0:
        raise ValueError("angle_deg must be >= 0")

    nu_rad = np.radians(angle_deg)
    mach = _prandtl_meyer_mach(nu_rad, gamma)

    return {
        "mach": round(mach, 6),
        "prandtl_meyer_angle_deg": round(angle_deg, 4),
        "prandtl_meyer_angle_rad": round(nu_rad, 6),
        "gamma": gamma,
    }
