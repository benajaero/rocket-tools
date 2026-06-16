"""Aerodynamics fundamentals with Numba JIT.

References:
    - Anderson, "Fundamentals of Aerodynamics", 6th Ed.
      Reynolds number (Eq. 1.36), Mach number (Eq. 1.37),
      dynamic pressure (Eq. 1.39), lift/drag coefficients (Eq. 1.40-1.41).
    - Blasius (1908), ZAMM: Skin friction correlations.
      Laminar: cf = 1.328 / sqrt(Re); Turbulent: cf = 0.0592 / Re^0.2
"""

import numpy as np
from numba import njit


@njit(cache=True)
def _reynolds_number(rho: float, v: float, char_length: float, mu: float) -> float:
    if mu <= 0.0 or char_length <= 0.0 or rho < 0.0 or v < 0.0:
        raise ValueError("Invalid physical parameters for Re")
    return rho * v * char_length / mu


@njit(cache=True)
def _mach_number(v: float, a: float) -> float:
    if a <= 0.0:
        raise ValueError("Speed of sound must be > 0")
    return v / a


@njit(cache=True)
def _dynamic_pressure(rho: float, v: float) -> float:
    if rho < 0.0 or v < 0.0:
        raise ValueError("Density and velocity must be >= 0")
    return 0.5 * rho * v**2


@njit(cache=True)
def _lift_coefficient(lift: float, rho: float, v: float, s: float) -> float:
    q = _dynamic_pressure(rho, v)
    if q <= 0.0 or s <= 0.0:
        raise ValueError("Dynamic pressure and area must be > 0")
    return lift / (q * s)  # type: ignore[no-any-return]


@njit(cache=True)
def _drag_coefficient(drag: float, rho: float, v: float, s: float) -> float:
    q = _dynamic_pressure(rho, v)
    if q <= 0.0 or s <= 0.0:
        raise ValueError("Dynamic pressure and area must be > 0")
    return drag / (q * s)  # type: ignore[no-any-return]


@njit(cache=True)
def _skin_friction_coefficient(re: float, laminar: bool = True) -> float:
    if re <= 0.0:
        raise ValueError("Re must be > 0")
    if laminar:
        return 1.328 / np.sqrt(re)  # type: ignore[no-any-return]
    else:
        # Blasius turbulent: cf = 0.0592 * Re^(-0.2)
        return 0.0592 * re ** (-0.2)  # type: ignore[no-any-return]


# ---- Public API ----


def reynolds_number(
    velocity: float,
    characteristic_length: float,
    density: float | None = None,
    dynamic_viscosity: float | None = None,
    altitude_m: float | None = None,
    temperature_k: float | None = None,
) -> dict:
    """
    Compute Reynolds number.

    Either provide density and viscosity directly, or altitude_m for ISA lookup,
    or temperature_k for standard density with given temperature.
    """
    if density is not None and dynamic_viscosity is not None:
        rho = density
        mu = dynamic_viscosity
    elif altitude_m is not None:
        from rocket_tools.materials import isa_atmosphere

        isa = isa_atmosphere(altitude_m)
        rho = isa["density_kg_m3"]
        # Sutherland's law for dynamic viscosity of air
        t = isa["temperature_k"]
        mu_ref = 1.789e-5  # at 288.15 K
        t_ref = 288.15
        s_const = 110.4
        mu = mu_ref * (t / t_ref) ** 1.5 * (t_ref + s_const) / (t + s_const)
    elif temperature_k is not None:
        # Standard sea-level density, given temperature
        rho = 1.225 * (288.15 / temperature_k)  # ideal gas approx
        mu_ref = 1.789e-5
        t_ref = 288.15
        s_const = 110.4
        mu = mu_ref * (temperature_k / t_ref) ** 1.5 * (t_ref + s_const) / (temperature_k + s_const)
    else:
        raise ValueError("Must provide (density + viscosity) or altitude_m or temperature_k")

    re = _reynolds_number(rho, velocity, characteristic_length, mu)

    flow_regime = "laminar" if re < 5e5 else "transitional" if re < 1e6 else "turbulent"

    return {
        "reynolds_number": round(float(re), 2),
        "density_kg_m3": round(float(rho), 4),
        "dynamic_viscosity_pa_s": round(float(mu), 8),
        "velocity_m_s": velocity,
        "characteristic_length_m": characteristic_length,
        "flow_regime": flow_regime,
    }


def mach_number(velocity: float, altitude_m: float) -> dict:
    from rocket_tools.materials import isa_atmosphere

    isa = isa_atmosphere(altitude_m)
    a = isa["speed_of_sound_m_s"]
    m = _mach_number(velocity, a)

    regime = (
        "subsonic"
        if m < 0.8
        else "transonic"
        if m < 1.2
        else "supersonic"
        if m < 5.0
        else "hypersonic"
    )

    return {
        "mach_number": round(float(m), 4),
        "velocity_m_s": velocity,
        "speed_of_sound_m_s": round(a, 1),
        "altitude_m": altitude_m,
        "regime": regime,
    }


def dynamic_pressure(velocity: float, altitude_m: float) -> dict:
    from rocket_tools.materials import isa_atmosphere

    isa = isa_atmosphere(altitude_m)
    rho = isa["density_kg_m3"]
    q = _dynamic_pressure(rho, velocity)
    return {
        "dynamic_pressure_pa": round(float(q), 2),
        "dynamic_pressure_kpa": round(float(q) / 1000, 4),
        "velocity_m_s": velocity,
        "altitude_m": altitude_m,
        "density_kg_m3": rho,
    }


def lift_coefficient(
    lift: float, velocity: float, altitude_m: float, reference_area: float
) -> dict:
    from rocket_tools.materials import isa_atmosphere

    isa = isa_atmosphere(altitude_m)
    rho = isa["density_kg_m3"]
    cl = _lift_coefficient(lift, rho, velocity, reference_area)
    q = _dynamic_pressure(rho, velocity)
    return {
        "lift_coefficient": round(float(cl), 4),
        "lift_n": lift,
        "dynamic_pressure_pa": round(float(q), 2),
        "reference_area_m2": reference_area,
    }


def drag_coefficient(
    drag: float, velocity: float, altitude_m: float, reference_area: float
) -> dict:
    from rocket_tools.materials import isa_atmosphere

    isa = isa_atmosphere(altitude_m)
    rho = isa["density_kg_m3"]
    cd = _drag_coefficient(drag, rho, velocity, reference_area)
    q = _dynamic_pressure(rho, velocity)
    return {
        "drag_coefficient": round(float(cd), 4),
        "drag_n": drag,
        "dynamic_pressure_pa": round(float(q), 2),
        "reference_area_m2": reference_area,
    }


def skin_friction_coefficient(reynolds_number: float, flow_regime: str = "laminar") -> dict:
    laminar = flow_regime.lower() == "laminar"
    cf = _skin_friction_coefficient(reynolds_number, laminar)
    return {
        "skin_friction_coefficient": round(float(cf), 6),
        "reynolds_number": reynolds_number,
        "flow_regime": flow_regime,
        "correlation": "blasius_laminar" if laminar else "blasius_turbulent",
    }


def aero_analysis(
    velocity: float,
    altitude_m: float,
    characteristic_length: float,
    reference_area: float,
    lift: float = 0.0,
    drag: float = 0.0,
) -> dict:
    """
    Comprehensive aerodynamic analysis in a single call.
    """
    re_result = reynolds_number(
        velocity=velocity, characteristic_length=characteristic_length, altitude_m=altitude_m
    )
    mach_result = mach_number(velocity=velocity, altitude_m=altitude_m)
    q_result = dynamic_pressure(velocity=velocity, altitude_m=altitude_m)

    cl = None
    cd = None
    if reference_area > 0:
        if lift != 0.0:
            cl = lift_coefficient(lift, velocity, altitude_m, reference_area)["lift_coefficient"]
        if drag != 0.0:
            cd = drag_coefficient(drag, velocity, altitude_m, reference_area)["drag_coefficient"]

    re_val = re_result["reynolds_number"]
    cf = skin_friction_coefficient(re_val, re_result["flow_regime"])["skin_friction_coefficient"]

    if cl is not None and cd is not None and cd != 0.0:
        lift_to_drag = round(cl / cd, 3)
    elif cl is not None and cd == 0.0:
        lift_to_drag = float("inf")
    else:
        lift_to_drag = None

    return {
        "reynolds_number": re_val,
        "mach_number": mach_result["mach_number"],
        "dynamic_pressure_pa": q_result["dynamic_pressure_pa"],
        "dynamic_pressure_kpa": q_result["dynamic_pressure_kpa"],
        "flow_regime": re_result["flow_regime"],
        "mach_regime": mach_result["regime"],
        "lift_coefficient": cl,
        "drag_coefficient": cd,
        "lift_to_drag_ratio": lift_to_drag,
        "skin_friction_coefficient": cf,
        "altitude_m": altitude_m,
        "velocity_m_s": velocity,
        "characteristic_length_m": characteristic_length,
        "reference_area_m2": reference_area,
    }
