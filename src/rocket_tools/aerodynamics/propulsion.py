"""Rocket propulsion thermochemistry: propellant figures of merit.

Geometry-free performance parameters derived from combustion-gas properties,
complementing the geometry-based ``nozzle_performance``. Use these to compare
propellants and chamber conditions before a nozzle is sized.

References:
    - Sutton & Biblarz, "Rocket Propulsion Elements", 9th Ed. (Ch. 3)
      Characteristic velocity c* (Eq. 3-32), effective/ideal exhaust velocity
      (Eq. 3-16), choked mass flow (Eq. 3-24), Vandenkerckhove function.
    - Hill & Peterson, "Mechanics and Thermodynamics of Propulsion", 2nd Ed.
      Ideal rocket relations and the area-Mach / choked-flow derivation.
"""

import numpy as np

# Universal gas constant, J/(kmol*K) (CODATA). Molecular weights are in kg/kmol.
R_UNIVERSAL = 8314.462
G_STD = 9.80665


def _vandenkerckhove(gamma: float) -> float:
    """Vandenkerckhove function Gamma = sqrt(g)*(2/(g+1))^((g+1)/(2(g-1)))."""
    return float(np.sqrt(gamma) * (2.0 / (gamma + 1.0)) ** ((gamma + 1.0) / (2.0 * (gamma - 1.0))))


def characteristic_velocity(
    chamber_temperature_k: float, gamma: float = 1.2, molecular_weight: float = 22.0
) -> dict:
    """Characteristic velocity c* = sqrt(R*Tc) / Gamma (m/s).

    A propellant/combustion figure of merit independent of nozzle geometry:
    it measures how effectively the chamber converts propellant into throat
    mass flux. c* = p_c * A_t / mdot for an ideal choked throat.
    """
    if chamber_temperature_k <= 0:
        raise ValueError("chamber_temperature_k must be > 0")
    if gamma <= 1.0:
        raise ValueError("gamma must be > 1")
    if molecular_weight <= 0:
        raise ValueError("molecular_weight must be > 0")

    r_specific = R_UNIVERSAL / molecular_weight
    gamma_vdk = _vandenkerckhove(gamma)
    c_star = np.sqrt(r_specific * chamber_temperature_k) / gamma_vdk
    return {
        "characteristic_velocity_ms": round(float(c_star), 3),
        "vandenkerckhove_gamma": round(gamma_vdk, 5),
        "specific_gas_constant_j_kg_k": round(r_specific, 4),
        "chamber_temperature_k": chamber_temperature_k,
    }


def ideal_specific_impulse(
    chamber_temperature_k: float,
    pressure_ratio: float,
    gamma: float = 1.2,
    molecular_weight: float = 22.0,
) -> dict:
    """Ideal exhaust velocity and specific impulse from the pressure ratio.

    v_e = sqrt( 2*g/(g-1) * R*Tc * (1 - (pe/pc)^((g-1)/g)) ), Isp = v_e / g0.
    pressure_ratio is the exit/chamber pressure ratio pe/pc, in (0, 1). Also
    reports the theoretical limit (pe/pc -> 0, i.e. expansion to vacuum).
    """
    if chamber_temperature_k <= 0:
        raise ValueError("chamber_temperature_k must be > 0")
    if not 0.0 < pressure_ratio < 1.0:
        raise ValueError("pressure_ratio (pe/pc) must be in (0, 1)")
    if gamma <= 1.0:
        raise ValueError("gamma must be > 1")
    if molecular_weight <= 0:
        raise ValueError("molecular_weight must be > 0")

    r_specific = R_UNIVERSAL / molecular_weight
    coeff = 2.0 * gamma / (gamma - 1.0) * r_specific * chamber_temperature_k
    v_e = np.sqrt(coeff * (1.0 - pressure_ratio ** ((gamma - 1.0) / gamma)))
    v_e_max = np.sqrt(coeff)
    return {
        "exhaust_velocity_ms": round(float(v_e), 3),
        "specific_impulse_s": round(float(v_e) / G_STD, 3),
        "max_exhaust_velocity_ms": round(float(v_e_max), 3),
        "max_specific_impulse_s": round(float(v_e_max) / G_STD, 3),
        "pressure_ratio": pressure_ratio,
    }


def throat_mass_flux(
    chamber_pressure_pa: float,
    chamber_temperature_k: float,
    gamma: float = 1.2,
    molecular_weight: float = 22.0,
) -> dict:
    """Choked mass flux through the throat: mdot/At = pc*Gamma / sqrt(R*Tc).

    Multiply by throat area to get the mass flow rate of an ideal choked nozzle.
    Units: kg/(s*m^2).
    """
    if chamber_pressure_pa <= 0:
        raise ValueError("chamber_pressure_pa must be > 0")
    if chamber_temperature_k <= 0:
        raise ValueError("chamber_temperature_k must be > 0")
    if gamma <= 1.0:
        raise ValueError("gamma must be > 1")
    if molecular_weight <= 0:
        raise ValueError("molecular_weight must be > 0")

    r_specific = R_UNIVERSAL / molecular_weight
    gamma_vdk = _vandenkerckhove(gamma)
    flux = chamber_pressure_pa * gamma_vdk / np.sqrt(r_specific * chamber_temperature_k)
    return {
        "mass_flux_kg_s_m2": round(float(flux), 4),
        "vandenkerckhove_gamma": round(gamma_vdk, 5),
        "chamber_pressure_pa": chamber_pressure_pa,
        "chamber_temperature_k": chamber_temperature_k,
    }
