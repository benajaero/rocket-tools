"""Rocket nozzle and supersonic inlet performance analysis.

Covers: convergent-divergent nozzle design, thrust coefficient,
area ratio, and supersonic inlet performance.

References:
    - Sutton & Biblarz, "Rocket Propulsion Elements", 9th Ed. (Ch. 3)
      Thrust equation, thrust coefficient, specific impulse,
      characteristic velocity c*, optimal expansion ratio.
    - Hill & Peterson, "Mechanics and Thermodynamics of Propulsion", 2nd Ed.
      Isentropic nozzle flow, choked flow, area-Mach relation.
"""

import numpy as np
from numba import njit

GAMMA = 1.4


@njit(cache=True)
def _isentropic_p_ratio(m: float, gamma: float = GAMMA):
    return (1.0 / (1.0 + (gamma - 1.0) / 2.0 * m**2)) ** (gamma / (gamma - 1.0))


@njit(cache=True)
def _isentropic_t_ratio(m: float, gamma: float = GAMMA):
    return 1.0 / (1.0 + (gamma - 1.0) / 2.0 * m**2)


@njit(cache=True)
def _area_ratio(m: float, gamma: float = GAMMA):
    g1 = (gamma + 1.0) / 2.0
    g2 = (gamma - 1.0) / 2.0
    return (1.0 / m) * ((1.0 + g2 * m**2) / g1) ** (g1 / (gamma - 1.0))


@njit(cache=True)
def _mach_from_area_ratio(a_a_star: float, gamma: float = GAMMA):
    if a_a_star < 1.0:
        raise ValueError("A/A* must be >= 1.0")
    m = 2.0 if a_a_star < 2.0 else a_a_star
    for _ in range(50):
        g1 = (gamma + 1.0) / 2.0
        g2 = (gamma - 1.0) / 2.0
        term = (1.0 + g2 * m**2) / g1
        f = (1.0 / m) * term ** (g1 / (gamma - 1.0)) - a_a_star
        # Derivative
        df = -1.0 / m**2 * term ** (g1 / (gamma - 1.0)) + (1.0 / m) * (
            g1 / (gamma - 1.0)
        ) * term ** (g1 / (gamma - 1.0) - 1.0) * (2.0 * g2 * m / g1)
        if abs(df) < 1e-12:
            break
        m_new = m - f / df
        if m_new <= 1.0:
            m_new = 1.01
        if abs(m_new - m) < 1e-8:
            return m_new
        m = m_new
    return m


def nozzle_performance(
    chamber_pressure_pa: float,
    chamber_temperature_k: float,
    ambient_pressure_pa: float,
    throat_area_m2: float,
    exit_area_m2: float,
    gamma: float = 1.2,
    molecular_weight: float = 22.0,
) -> dict:
    """Analyze rocket nozzle performance.

    Computes thrust, thrust coefficient, specific impulse, and exit conditions
    for a convergent-divergent (De Laval) nozzle. Overexpanded flow separation is
    modeled with the Summerfield criterion so sea-level firing of a vacuum-optimized
    nozzle no longer reports unphysical attached supersonic flow.

    Args:
        chamber_pressure_pa: Combustion chamber total pressure (Pa)
        chamber_temperature_k: Combustion chamber total temperature (K)
        ambient_pressure_pa: Ambient/back pressure (Pa)
        throat_area_m2: Nozzle throat area (m²)
        exit_area_m2: Nozzle exit area (m²)
        gamma: Ratio of specific heats (default 1.2, typical combustion gas; use 1.4 for air)
        molecular_weight: Exhaust gas molecular weight (kg/kmol, default 22 for rocket
            exhaust; use 28.97 for air)

    Returns:
        dict with thrust_n, thrust_coefficient, specific_impulse_s,
        exit_mach, exit_pressure_pa, mass_flow_rate_kg_s, etc.
    """
    if chamber_pressure_pa <= 0 or chamber_temperature_k <= 0:
        raise ValueError("Chamber pressure and temperature must be > 0")
    if throat_area_m2 <= 0 or exit_area_m2 <= 0:
        raise ValueError("Areas must be > 0")
    if exit_area_m2 < throat_area_m2:
        raise ValueError("exit_area must be >= throat_area")

    r_specific = 8314.462 / molecular_weight  # J/(kg.K), universal R unified across modules
    g1 = (gamma + 1.0) / 2.0

    # Throat conditions (sonic)
    p_star = chamber_pressure_pa * (1.0 / g1) ** (gamma / (gamma - 1.0))
    t_star = chamber_temperature_k / g1
    rho_star = p_star / (r_specific * t_star)
    v_star = np.sqrt(gamma * r_specific * t_star)

    # Mass flow rate (choked)
    mass_flow = rho_star * v_star * throat_area_m2

    # Exit Mach from area ratio
    area_ratio = exit_area_m2 / throat_area_m2
    exit_mach = _mach_from_area_ratio(area_ratio, gamma)

    # Exit conditions
    exit_pressure = chamber_pressure_pa * _isentropic_p_ratio(exit_mach, gamma)
    exit_temperature = chamber_temperature_k * _isentropic_t_ratio(exit_mach, gamma)
    exit_velocity = exit_mach * np.sqrt(gamma * r_specific * exit_temperature)

    # Thrust
    momentum_thrust = mass_flow * exit_velocity
    pressure_thrust = (exit_pressure - ambient_pressure_pa) * exit_area_m2
    total_thrust = momentum_thrust + pressure_thrust

    # Thrust coefficient
    cf = total_thrust / (chamber_pressure_pa * throat_area_m2)

    # Specific impulse
    isp = total_thrust / (mass_flow * 9.80665) if mass_flow > 0.0 else 0.0

    # Characteristic velocity c*
    c_star = chamber_pressure_pa * throat_area_m2 / mass_flow if mass_flow > 0.0 else 0.0

    # Pressure ratio
    pressure_ratio = (
        chamber_pressure_pa / ambient_pressure_pa if ambient_pressure_pa > 0.0 else np.inf
    )

    # Choked-flow check: the sonic-throat analysis requires choked flow, i.e. the
    # chamber/ambient pressure ratio above the critical ratio.
    critical_pr = g1 ** (gamma / (gamma - 1.0))
    choked = ambient_pressure_pa <= 0.0 or pressure_ratio >= critical_pr

    # Over/under-expanded state (guards the vacuum case, which previously divided by zero).
    if ambient_pressure_pa <= 0.0:
        expansion_state = "vacuum"
    elif abs(exit_pressure - ambient_pressure_pa) / ambient_pressure_pa < 0.05:
        expansion_state = "optimal"
    elif exit_pressure > ambient_pressure_pa:
        expansion_state = "underexpanded"
    else:
        expansion_state = "overexpanded"

    # Overexpansion separation (Summerfield criterion): if the ideal exit pressure drops
    # below ~40% of ambient, the flow separates in the divergent section and the nozzle
    # effectively exits at the separation point (p ~ p_sep, smaller area). Reporting the
    # attached-flow result would give a large, wrong negative pressure thrust, so recompute
    # exit conditions and thrust at the separation point.
    flow_separated = False
    separation_ratio = 0.4
    if ambient_pressure_pa > 0.0 and exit_pressure < separation_ratio * ambient_pressure_pa:
        p_sep = separation_ratio * ambient_pressure_pa
        m_sep = np.sqrt(
            (2.0 / (gamma - 1.0)) * ((chamber_pressure_pa / p_sep) ** ((gamma - 1.0) / gamma) - 1.0)
        )
        a_sep_ratio = (1.0 / m_sep) * (
            (2.0 / (gamma + 1.0)) * (1.0 + (gamma - 1.0) / 2.0 * m_sep**2)
        ) ** ((gamma + 1.0) / (2.0 * (gamma - 1.0)))
        a_eff = a_sep_ratio * throat_area_m2
        if a_eff < exit_area_m2:
            flow_separated = True
            expansion_state = "overexpanded_separated"
            exit_mach = m_sep
            exit_pressure = p_sep
            exit_temperature = chamber_temperature_k * _isentropic_t_ratio(m_sep, gamma)
            exit_velocity = m_sep * np.sqrt(gamma * r_specific * exit_temperature)
            momentum_thrust = mass_flow * exit_velocity
            pressure_thrust = (p_sep - ambient_pressure_pa) * a_eff
            total_thrust = momentum_thrust + pressure_thrust
            cf = total_thrust / (chamber_pressure_pa * throat_area_m2)
            isp = total_thrust / (mass_flow * 9.80665) if mass_flow > 0.0 else 0.0

    return {
        "thrust_n": round(total_thrust, 2),
        "thrust_kn": round(total_thrust / 1000.0, 4),
        "thrust_coefficient_cf": round(cf, 4),
        "specific_impulse_s": round(isp, 2),
        "specific_impulse_ms": round(isp * 9.80665, 2),
        "characteristic_velocity_ms": round(c_star, 2),
        "mass_flow_rate_kg_s": round(mass_flow, 6),
        "exit_mach": round(exit_mach, 4),
        "exit_pressure_pa": round(exit_pressure, 2),
        "exit_pressure_bar": round(exit_pressure / 1e5, 4),
        "exit_temperature_k": round(exit_temperature, 2),
        "exit_velocity_ms": round(exit_velocity, 2),
        "throat_pressure_pa": round(p_star, 2),
        "throat_temperature_k": round(t_star, 2),
        "throat_velocity_ms": round(v_star, 2),
        "area_ratio": round(area_ratio, 4),
        "pressure_ratio": round(pressure_ratio, 2) if pressure_ratio != np.inf else None,
        "expansion_state": expansion_state,
        "flow_separated": flow_separated,
        "choked": choked,
        "gamma": gamma,
        "molecular_weight": molecular_weight,
    }


def optimal_area_ratio(
    chamber_pressure_pa: float,
    ambient_pressure_pa: float,
    gamma: float = GAMMA,
) -> dict:
    """Compute optimal nozzle area ratio for given pressure ratio.

    Finds the exit Mach number where exit pressure equals ambient pressure,
    then returns the corresponding A/A*.
    """
    if chamber_pressure_pa <= 0 or ambient_pressure_pa <= 0:
        raise ValueError("Pressures must be > 0")
    if ambient_pressure_pa >= chamber_pressure_pa:
        raise ValueError("ambient_pressure must be less than chamber_pressure")

    p_ratio = chamber_pressure_pa / ambient_pressure_pa

    # Solve for Mach from isentropic pressure ratio
    m = 2.0
    for _ in range(50):
        f = (1.0 / (1.0 + (gamma - 1.0) / 2.0 * m**2)) ** (-gamma / (gamma - 1.0)) - p_ratio
        df = (
            gamma
            * m
            / (1.0 + (gamma - 1.0) / 2.0 * m**2)
            * (1.0 / (1.0 + (gamma - 1.0) / 2.0 * m**2)) ** (-gamma / (gamma - 1.0) - 1.0)
        )
        if abs(df) < 1e-12:
            break
        m_new = m - f / df
        if m_new <= 1.0:
            m_new = 1.01
        if abs(m_new - m) < 1e-8:
            m = m_new
            break
        m = m_new

    a_ratio = _area_ratio(m, gamma)

    return {
        "optimal_exit_mach": round(m, 4),
        "optimal_area_ratio": round(a_ratio, 4),
        "pressure_ratio": round(p_ratio, 2),
        "gamma": gamma,
    }
