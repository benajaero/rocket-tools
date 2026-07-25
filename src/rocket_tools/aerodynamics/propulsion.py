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


# NAR/TRA total-impulse classes: letter -> inclusive upper bound in N*s.
# Each letter doubles the previous ceiling (A: 2.5, B: 5, C: 10, ...).
_NAR_LETTERS = "ABCDEFGHIJKLMNOPQRSTUV"


def _nar_motor_class(total_impulse_ns: float) -> str:
    """NAR/TRA motor class letter for a total impulse in N*s.

    A = 1.26-2.5 N*s, and each subsequent letter doubles the upper bound. Impulses at
    or below 1.25 N*s fall into the fractional-A classes.
    """
    if total_impulse_ns <= 0.3125:
        return "sub-1/4A"
    if total_impulse_ns <= 0.625:
        return "1/4A"
    if total_impulse_ns <= 1.25:
        return "1/2A"
    # Letter n (A = 0) has inclusive upper bound 2.5 * 2^n.
    idx = int(np.ceil(np.log2(total_impulse_ns / 2.5)))
    idx = max(idx, 0)
    if idx >= len(_NAR_LETTERS):
        idx = len(_NAR_LETTERS) - 1
    return _NAR_LETTERS[idx]


def motor_thrust_curve_analysis(
    times_s: list[float],
    thrusts_n: list[float],
    propellant_mass_kg: float,
) -> dict:
    """Motor performance figures of merit from a measured thrust-time curve.

    Integrates the thrust curve (trapezoidal rule) to the total impulse, then reports
    burn time, average and peak thrust, delivered specific impulse, effective exhaust
    velocity, and the NAR/TRA motor class and designation (e.g. "C6").

    Args:
        times_s: Strictly increasing sample times in seconds.
        thrusts_n: Thrust at each sample in Newtons (>= 0), same length as times_s.
        propellant_mass_kg: Total propellant (grain) mass consumed, in kg.

    References:
        - NAR/TRA motor certification: total-impulse letter classes.
        - Sutton & Biblarz, Rocket Propulsion Elements, 9th Ed. (total impulse, Isp).
    """
    if len(times_s) != len(thrusts_n):
        raise ValueError("times_s and thrusts_n must have the same length")
    if len(times_s) < 2:
        raise ValueError("need at least two samples to integrate a thrust curve")
    if propellant_mass_kg <= 0:
        raise ValueError("propellant_mass_kg must be > 0")

    t = np.asarray(times_s, dtype=float)
    f = np.asarray(thrusts_n, dtype=float)
    if np.any(np.diff(t) <= 0):
        raise ValueError("times_s must be strictly increasing")
    if np.any(f < 0):
        raise ValueError("thrusts_n must be >= 0")

    total_impulse = float(np.trapezoid(f, t))
    burn_time = float(t[-1] - t[0])
    if total_impulse <= 0:
        raise ValueError("total impulse is zero (thrust curve is all zeros)")

    average_thrust = total_impulse / burn_time
    peak_thrust = float(np.max(f))
    # Delivered specific impulse and effective exhaust velocity from the propellant mass.
    specific_impulse = total_impulse / (propellant_mass_kg * G_STD)
    exhaust_velocity = total_impulse / propellant_mass_kg
    motor_class = _nar_motor_class(total_impulse)
    designation = f"{motor_class}{int(round(average_thrust))}" if motor_class.isalpha() else None

    return {
        "total_impulse_ns": round(total_impulse, 4),
        "burn_time_s": round(burn_time, 4),
        "average_thrust_n": round(average_thrust, 4),
        "peak_thrust_n": round(peak_thrust, 4),
        "specific_impulse_s": round(specific_impulse, 3),
        "effective_exhaust_velocity_ms": round(exhaust_velocity, 3),
        "motor_class": motor_class,
        "motor_designation": designation,
        "propellant_mass_kg": propellant_mass_kg,
    }
