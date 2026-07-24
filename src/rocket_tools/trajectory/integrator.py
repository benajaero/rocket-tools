"""Numerical ascent integrator (fixed-step RK4) with a self-contained ISA density kernel.

The hot loop is Numba-JIT compiled and deterministic (fixed step), so results pin
cleanly to closed-form and published references. The atmospheric density used inside
the loop is a standalone 7-layer U.S. Standard Atmosphere 1976 kernel (``_isa_rho``)
that reproduces :func:`rocket_tools.materials.isa.isa_atmosphere` to <1e-5 relative
(rounding-limited by that model's 6-significant-figure output; guarded by
``tests/test_trajectory.py``) so the integrator needs no Python callbacks.

References:
    - Curtis, "Orbital Mechanics for Engineering Students", 3rd Ed. (Ch. 11) — powered
      ascent / gravity-turn equations of motion for a point-mass launch vehicle.
    - Sutton & Biblarz, "Rocket Propulsion Elements", 9th Ed. (Ch. 4) — vertical-flight
      gravity loss and burnout/coast relations.
    - NASA-TM-X-74335: U.S. Standard Atmosphere 1976 (density model).
"""

import math

import numpy as np
from numba import njit

G0 = 9.80665  # standard gravity, m/s^2
MU_EARTH = 3.986004418e14  # Earth gravitational parameter, m^3/s^2
R_EARTH = 6.371e6  # mean Earth radius, m (consistent with orbital_velocity)
# Below this speed the flight-path angle is held fixed (initial vertical boost). The
# gravity-turn term dgamma/dt ~ (g/v)cos(gamma) is singular as v->0, so applying it from
# rest would slam a non-vertical vehicle into the ground; a real gravity turn is initiated
# only after the vehicle has built up speed.
V_TURN_MIN = 30.0  # m/s

# ---- U.S. Standard Atmosphere 1976 base layers (must match materials/isa.py) ----
_R_AIR = 287.05
_G_ISA = 9.80665
_P0 = 101_325.0
_ISA_CEIL = 84_852.0  # geopotential model ceiling (86 km geometric)

_H_B = np.array([0.0, 11000.0, 20000.0, 32000.0, 47000.0, 51000.0, 71000.0])
_T_B = np.array([288.15, 216.65, 216.65, 228.65, 270.65, 270.65, 214.65])
_L_B = np.array([-0.0065, 0.0, 0.001, 0.0028, 0.0, -0.0028, -0.002])


def _compute_p_base() -> np.ndarray:
    """Base pressure at the bottom of each layer, chained up from sea level (Pa)."""
    p = [_P0]
    for i in range(1, len(_H_B)):
        h_b, t_b, lapse = _H_B[i - 1], _T_B[i - 1], _L_B[i - 1]
        h_top = _H_B[i]
        if lapse == 0.0:
            p.append(p[i - 1] * math.exp(-_G_ISA * (h_top - h_b) / (_R_AIR * t_b)))
        else:
            t_top = t_b + lapse * (h_top - h_b)
            p.append(p[i - 1] * (t_top / t_b) ** (-_G_ISA / (lapse * _R_AIR)))
    return np.array(p)


_P_B = _compute_p_base()


@njit(cache=True)
def _isa_rho(h: float) -> float:
    """Air density (kg/m^3) at geopotential altitude ``h`` (m), 7-layer US Std Atm 1976.

    Below 0 m clamps to sea level; at/above the 84 852 m model ceiling returns 0
    (treated as vacuum for ascent drag).
    """
    if h <= 0.0:
        h = 0.0
    if h >= _ISA_CEIL:
        return 0.0
    layer = 0
    for i in range(7):
        if h >= _H_B[i]:
            layer = i
        else:
            break
    h_b = _H_B[layer]
    t_b = _T_B[layer]
    lapse = _L_B[layer]
    p_b = _P_B[layer]
    t = t_b + lapse * (h - h_b)
    if lapse == 0.0:
        p = p_b * math.exp(-_G_ISA * (h - h_b) / (_R_AIR * t_b))
    else:
        p = p_b * (t / t_b) ** (-_G_ISA / (lapse * _R_AIR))
    return float(p / (_R_AIR * t))


@njit(cache=True)
def _deriv(
    state: np.ndarray,
    thrust: float,
    mdot: float,
    cd: float,
    area: float,
    include_drag: bool,
    inverse_square_gravity: bool,
) -> np.ndarray:
    """Planar point-mass gravity-turn derivatives for state [h, v, m, gamma, x].

    dh/dt = v sin g ; dx/dt = v cos g ; dv/dt = (T - D)/m - g sin g ;
    dg/dt = -(g/v - v/(R+h)) cos g ; dm/dt = -mdot (while thrusting).
    Vertical flight (gamma=pi/2) is the special case cos(gamma)=0.
    """
    h = state[0]
    v = state[1]
    m = state[2]
    gamma = state[3]

    if inverse_square_gravity:
        g = MU_EARTH / (R_EARTH + h) ** 2
    else:
        g = G0

    drag = 0.0
    if include_drag and v > 0.0:
        rho = _isa_rho(h)
        drag = 0.5 * rho * v * v * cd * area

    dh = v * math.sin(gamma)
    dx = v * math.cos(gamma)
    dv = (thrust - drag) / m - g * math.sin(gamma)
    # Hold the flight-path angle during the low-speed boost (avoids the g/v singularity),
    # then let the gravity turn proceed once the vehicle has built up speed.
    if v > V_TURN_MIN:
        dgamma = -(g / v - v / (R_EARTH + h)) * math.cos(gamma)
    else:
        dgamma = 0.0
    dm = -mdot

    out = np.empty(5)
    out[0] = dh
    out[1] = dv
    out[2] = dm
    out[3] = dgamma
    out[4] = dx
    return out


@njit(cache=True)
def _integrate(
    h0: float,
    v0: float,
    m0: float,
    gamma0: float,
    dry_mass: float,
    mdot: float,
    thrust: float,
    burn_time: float,
    cd: float,
    area: float,
    dt: float,
    max_time: float,
    include_drag: bool,
    inverse_square_gravity: bool,
):
    """Fixed-step RK4 integration of the ascent. Returns filled arrays + count.

    Stops at ground impact (descent through h=0) or ``max_time``. Thrust is active
    while ``t < burn_time``; mass is floored at ``dry_mass``.
    """
    n_max = int(max_time / dt) + 2
    t_arr = np.empty(n_max)
    h_arr = np.empty(n_max)
    v_arr = np.empty(n_max)
    m_arr = np.empty(n_max)
    g_arr = np.empty(n_max)
    x_arr = np.empty(n_max)
    q_arr = np.empty(n_max)
    a_arr = np.empty(n_max)

    state = np.empty(5)
    state[0] = h0
    state[1] = v0
    state[2] = m0
    state[3] = gamma0
    state[4] = 0.0

    t = 0.0
    n = 0
    while n < n_max:
        h = state[0]
        v = state[1]
        m = state[2]

        # Record diagnostics at the current state.
        rho = _isa_rho(h) if include_drag else 0.0
        q = 0.5 * rho * v * v
        thr_now = thrust if t < burn_time else 0.0
        drag_now = 0.5 * rho * v * v * cd * area if (include_drag and v > 0.0) else 0.0
        a_felt = (thr_now - drag_now) / m  # non-gravitational specific force (m/s^2)

        t_arr[n] = t
        h_arr[n] = h
        v_arr[n] = v
        m_arr[n] = m
        g_arr[n] = state[3]
        x_arr[n] = state[4]
        q_arr[n] = q
        a_arr[n] = a_felt
        n += 1

        # Stop once we descend back through the ground (after liftoff).
        if h < 0.0 and t > 0.0:
            break
        if t >= max_time:
            break

        # RK4 step with time-dependent thrust and a mass floor at dry mass.
        thr1 = thrust if t < burn_time else 0.0
        md1 = mdot if t < burn_time else 0.0
        thr_mid = thrust if (t + 0.5 * dt) < burn_time else 0.0
        md_mid = mdot if (t + 0.5 * dt) < burn_time else 0.0
        thr_end = thrust if (t + dt) < burn_time else 0.0
        md_end = mdot if (t + dt) < burn_time else 0.0

        k1 = _deriv(state, thr1, md1, cd, area, include_drag, inverse_square_gravity)
        s2 = state + 0.5 * dt * k1
        if s2[2] < dry_mass:
            s2[2] = dry_mass
        k2 = _deriv(s2, thr_mid, md_mid, cd, area, include_drag, inverse_square_gravity)
        s3 = state + 0.5 * dt * k2
        if s3[2] < dry_mass:
            s3[2] = dry_mass
        k3 = _deriv(s3, thr_mid, md_mid, cd, area, include_drag, inverse_square_gravity)
        s4 = state + dt * k3
        if s4[2] < dry_mass:
            s4[2] = dry_mass
        k4 = _deriv(s4, thr_end, md_end, cd, area, include_drag, inverse_square_gravity)

        state = state + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        if state[2] < dry_mass:
            state[2] = dry_mass
        t += dt

    return (t_arr[:n], h_arr[:n], v_arr[:n], m_arr[:n], g_arr[:n], x_arr[:n], q_arr[:n], a_arr[:n])
