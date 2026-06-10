"""Unit conversion engine with NIST-traceable constants and aerospace units."""

from decimal import Decimal

# NIST SP 811 defined constants (exact)
_INCH_TO_METER = Decimal("0.0254")
_FOOT_TO_METER = Decimal("0.3048")
_YARD_TO_METER = Decimal("0.9144")
_MILE_TO_METER = Decimal("1609.344")
_NAUTICAL_MILE_TO_METER = Decimal("1852")

_POUND_FORCE_TO_NEWTON = Decimal("4.4482216152605")
_KIP_TO_NEWTON = Decimal("4448.2216152605")
_TON_FORCE_TO_NEWTON = Decimal("8896.443230521")

_PSI_TO_PASCAL = Decimal("6894.757293168361")
_PSF_TO_PASCAL = _PSI_TO_PASCAL / Decimal("144")
_KSI_TO_PASCAL = _PSI_TO_PASCAL * Decimal("1000")
_ATM_TO_PASCAL = Decimal("101325")
_BAR_TO_PASCAL = Decimal("100000")
_TORR_TO_PASCAL = Decimal("133.32236842105263")

_STD_GRAVITY = Decimal("9.80665")

_LBM_TO_KG = Decimal("0.45359237")
_SLUG_TO_KG = Decimal("14.59390")

# Speed
_MPH_TO_MPS = Decimal("0.44704")
_FPS_TO_MPS = _FOOT_TO_METER
_KNOT_TO_MPS = Decimal("0.514444")

# Area
_SQFT_TO_SQM = _FOOT_TO_METER**2
_SQIN_TO_SQM = _INCH_TO_METER**2

# Density
_SLUG_PER_CUBIC_FOOT_TO_KG_M3 = Decimal("515.378818")
_LB_PER_CUBIC_FOOT_TO_KG_M3 = Decimal("16.018463")

# Energy
_FTLBF_TO_JOULE = Decimal("1.3558179483314")
_BTU_TO_JOULE = Decimal("1055.05585262")

# Conversion factors: (from_unit, to_unit) -> factor
_CONVERSIONS: dict[tuple[str, str], Decimal] = {
    # Length
    ("m", "mm"): Decimal("1000"),
    ("mm", "m"): Decimal("0.001"),
    ("m", "cm"): Decimal("100"),
    ("cm", "m"): Decimal("0.01"),
    ("m", "km"): Decimal("0.001"),
    ("km", "m"): Decimal("1000"),
    ("m", "inch"): Decimal("1") / _INCH_TO_METER,
    ("inch", "m"): _INCH_TO_METER,
    ("m", "in"): Decimal("1") / _INCH_TO_METER,
    ("in", "m"): _INCH_TO_METER,
    ("m", "ft"): Decimal("1") / _FOOT_TO_METER,
    ("ft", "m"): _FOOT_TO_METER,
    ("m", "yd"): Decimal("1") / _YARD_TO_METER,
    ("yd", "m"): _YARD_TO_METER,
    ("m", "mi"): Decimal("1") / _MILE_TO_METER,
    ("mi", "m"): _MILE_TO_METER,
    ("m", "nm"): Decimal("1") / _NAUTICAL_MILE_TO_METER,
    ("nm", "m"): _NAUTICAL_MILE_TO_METER,
    # Length imperial-internal
    ("ft", "inch"): Decimal("12"),
    ("inch", "ft"): Decimal("1") / Decimal("12"),
    ("mi", "ft"): Decimal("5280"),
    ("ft", "mi"): Decimal("1") / Decimal("5280"),
    ("nm", "ft"): Decimal("6076.11549"),
    # Pressure
    ("pa", "kpa"): Decimal("0.001"),
    ("kpa", "pa"): Decimal("1000"),
    ("pa", "mpa"): Decimal("0.000001"),
    ("mpa", "pa"): Decimal("1000000"),
    ("pa", "gpa"): Decimal("0.000000001"),
    ("gpa", "pa"): Decimal("1000000000"),
    ("pa", "psi"): Decimal("1") / _PSI_TO_PASCAL,
    ("psi", "pa"): _PSI_TO_PASCAL,
    ("psi", "kpa"): _PSI_TO_PASCAL * Decimal("0.001"),
    ("pa", "psf"): Decimal("1") / _PSF_TO_PASCAL,
    ("psf", "pa"): _PSF_TO_PASCAL,
    ("pa", "ksi"): Decimal("1") / _KSI_TO_PASCAL,
    ("ksi", "pa"): _KSI_TO_PASCAL,
    ("pa", "atm"): Decimal("1") / _ATM_TO_PASCAL,
    ("atm", "pa"): _ATM_TO_PASCAL,
    ("pa", "bar"): Decimal("1") / _BAR_TO_PASCAL,
    ("bar", "pa"): _BAR_TO_PASCAL,
    ("bar", "kpa"): Decimal("100"),
    ("kpa", "bar"): Decimal("0.01"),
    ("pa", "torr"): Decimal("1") / _TORR_TO_PASCAL,
    ("torr", "pa"): _TORR_TO_PASCAL,
    # Force
    ("n", "kn"): Decimal("0.001"),
    ("kn", "n"): Decimal("1000"),
    ("n", "lbf"): Decimal("1") / _POUND_FORCE_TO_NEWTON,
    ("lbf", "n"): _POUND_FORCE_TO_NEWTON,
    ("n", "kip"): Decimal("1") / _KIP_TO_NEWTON,
    ("kip", "n"): _KIP_TO_NEWTON,
    ("n", "tonf"): Decimal("1") / _TON_FORCE_TO_NEWTON,
    ("tonf", "n"): _TON_FORCE_TO_NEWTON,
    ("lbf", "kip"): Decimal("0.001"),
    ("kip", "lbf"): Decimal("1000"),
    # Mass
    ("kg", "lbm"): Decimal("1") / _LBM_TO_KG,
    ("lbm", "kg"): _LBM_TO_KG,
    ("kg", "slug"): Decimal("1") / _SLUG_TO_KG,
    ("slug", "kg"): _SLUG_TO_KG,
    # Speed
    ("m/s", "mph"): Decimal("1") / _MPH_TO_MPS,
    ("mph", "m/s"): _MPH_TO_MPS,
    ("m/s", "fps"): Decimal("1") / _FPS_TO_MPS,
    ("fps", "m/s"): _FPS_TO_MPS,
    ("m/s", "knot"): Decimal("1") / _KNOT_TO_MPS,
    ("knot", "m/s"): _KNOT_TO_MPS,
    ("km/h", "m/s"): Decimal("1") / Decimal("3.6"),
    ("m/s", "km/h"): Decimal("3.6"),
    # Area
    ("m2", "sqft"): Decimal("1") / _SQFT_TO_SQM,
    ("sqft", "m2"): _SQFT_TO_SQM,
    ("m2", "sqin"): Decimal("1") / _SQIN_TO_SQM,
    ("sqin", "m2"): _SQIN_TO_SQM,
    ("sqft", "sqin"): Decimal("144"),
    ("sqin", "sqft"): Decimal("1") / Decimal("144"),
    # Density
    ("kg/m3", "slug/ft3"): Decimal("1") / _SLUG_PER_CUBIC_FOOT_TO_KG_M3,
    ("slug/ft3", "kg/m3"): _SLUG_PER_CUBIC_FOOT_TO_KG_M3,
    ("kg/m3", "lb/ft3"): Decimal("1") / _LB_PER_CUBIC_FOOT_TO_KG_M3,
    ("lb/ft3", "kg/m3"): _LB_PER_CUBIC_FOOT_TO_KG_M3,
    # Energy
    ("j", "ftlbf"): Decimal("1") / _FTLBF_TO_JOULE,
    ("ftlbf", "j"): _FTLBF_TO_JOULE,
    ("j", "btu"): Decimal("1") / _BTU_TO_JOULE,
    ("btu", "j"): _BTU_TO_JOULE,
}


# SI base units for each dimension
_SI_BASE: dict[str, str] = {
    # Length
    "m": "m",
    "mm": "m",
    "cm": "m",
    "km": "m",
    "inch": "m",
    "in": "m",
    "ft": "m",
    "yd": "m",
    "mi": "m",
    "nm": "m",
    # Pressure
    "pa": "pa",
    "kpa": "pa",
    "mpa": "pa",
    "gpa": "pa",
    "psi": "pa",
    "psf": "pa",
    "ksi": "pa",
    "atm": "pa",
    "bar": "pa",
    "torr": "pa",
    # Force
    "n": "n",
    "kn": "n",
    "lbf": "n",
    "kip": "n",
    "tonf": "n",
    # Mass
    "kg": "kg",
    "lbm": "kg",
    "slug": "kg",
    # Speed
    "m/s": "m/s",
    "mph": "m/s",
    "fps": "m/s",
    "knot": "m/s",
    "km/h": "m/s",
    # Area
    "m2": "m2",
    "sqft": "m2",
    "sqin": "m2",
    # Density
    "kg/m3": "kg/m3",
    "slug/ft3": "kg/m3",
    "lb/ft3": "kg/m3",
    # Energy
    "j": "j",
    "ftlbf": "j",
    "btu": "j",
}


def _normalize_unit(unit: str) -> str:
    """Normalize unit string to canonical form."""
    mapping = {
        # Length
        "inches": "inch",
        "feet": "ft",
        "foot": "ft",
        "yard": "yd",
        "yards": "yd",
        "mile": "mi",
        "miles": "mi",
        "nautical mile": "nm",
        "nautical miles": "nm",
        "nmi": "nm",
        "meter": "m",
        "meters": "m",
        "metre": "m",
        "metres": "m",
        "millimeter": "mm",
        "millimeters": "mm",
        "centimeter": "cm",
        "centimeters": "cm",
        "kilometer": "km",
        "kilometers": "km",
        # Pressure
        "pascal": "pa",
        "pascals": "pa",
        "kilopascal": "kpa",
        "kilopascals": "kpa",
        "megapascal": "mpa",
        "megapascals": "mpa",
        "gigapascal": "gpa",
        "gigapascals": "gpa",
        "pound per square inch": "psi",
        "pounds per square inch": "psi",
        "pound per square foot": "psf",
        "pounds per square foot": "psf",
        "ksi": "ksi",
        "atmosphere": "atm",
        "atmospheres": "atm",
        "torr": "torr",
        "bar": "bar",
        # Force
        "newton": "n",
        "newtons": "n",
        "kilonewton": "kn",
        "kilonewtons": "kn",
        "pound force": "lbf",
        "pounds force": "lbf",
        "pound": "lbf",
        "pounds": "lbf",
        "kip": "kip",
        "kips": "kip",
        "ton force": "tonf",
        "tons force": "tonf",
        # Mass
        "pound mass": "lbm",
        "pounds mass": "lbm",
        "lb": "lbm",
        "lbs": "lbm",
        "slug": "slug",
        "slugs": "slug",
        # Speed
        "miles per hour": "mph",
        "mile per hour": "mph",
        "feet per second": "fps",
        "foot per second": "fps",
        "ft/s": "fps",
        "knot": "knot",
        "knots": "knot",
        "kt": "knot",
        "kts": "knot",
        "kmh": "km/h",
        # Area
        "square foot": "sqft",
        "square feet": "sqft",
        "square inch": "sqin",
        "square inches": "sqin",
        "sq ft": "sqft",
        "sq in": "sqin",
        # Density
        "slug per cubic foot": "slug/ft3",
        "slugs per cubic foot": "slug/ft3",
        "pound per cubic foot": "lb/ft3",
        "pounds per cubic foot": "lb/ft3",
        "lb/ft³": "lb/ft3",
        "slug/ft³": "slug/ft3",
        # Energy
        "foot pound": "ftlbf",
        "foot pounds": "ftlbf",
        "ft-lbf": "ftlbf",
        "ft lb": "ftlbf",
        "british thermal unit": "btu",
        "british thermal units": "btu",
        "btus": "btu",
        # Temperature
        "celsius": "c",
        "kelvin": "k",
        "fahrenheit": "f",
        "rankine": "r",
    }
    u = unit.lower().strip()
    return mapping.get(u, u)


def unit_convert(value: float, from_unit: str, to_unit: str) -> dict:
    """Convert engineering units with comprehensive aerospace support.

    Supports SI, US customary, and specialized aerospace units.

    Length: m, mm, cm, km, inch, ft, yd, mi, nm
    Pressure: pa, kpa, mpa, gpa, psi, psf, ksi, atm, bar, torr
    Force: n, kn, lbf, kip, tonf
    Mass: kg, lbm, slug
    Speed: m/s, mph, fps, knot, km/h
    Area: m2, sqft, sqin
    Density: kg/m3, slug/ft3, lb/ft3
    Energy: j, ftlbf, btu
    Temperature: c, k, f, r
    """
    from_u = _normalize_unit(from_unit)
    to_u = _normalize_unit(to_unit)

    if from_u == to_u:
        return _make_result(value, from_unit, to_unit, value, 1.0)

    # Temperature requires special handling
    temp_result = _convert_temperature(value, from_u, to_u)
    if temp_result is not None:
        return _make_result(value, from_unit, to_unit, temp_result["value"], temp_result["factor"])

    key = (from_u, to_u)
    if key not in _CONVERSIONS:
        raise ValueError(f"Unsupported conversion: {from_unit} -> {to_unit}")

    factor = float(_CONVERSIONS[key])
    return _make_result(value, from_unit, to_unit, value * factor, factor)


def _convert_temperature(value: float, from_u: str, to_u: str) -> dict[str, float] | None:
    """Handle temperature conversions. Returns None if not a temperature conversion."""
    temps = {"c", "k", "f", "r"}
    if from_u not in temps or to_u not in temps:
        return None

    # Convert to Kelvin first
    if from_u == "c":
        kelvin = value + 273.15
    elif from_u == "k":
        kelvin = value
    elif from_u == "f":
        kelvin = (value - 32) * 5 / 9 + 273.15
    elif from_u == "r":
        kelvin = value * 5 / 9
    else:
        return None

    # Convert from Kelvin to target
    if to_u == "c":
        return {"value": kelvin - 273.15, "factor": 1.0}
    elif to_u == "k":
        return {"value": kelvin, "factor": 1.0}
    elif to_u == "f":
        return {"value": (kelvin - 273.15) * 9 / 5 + 32, "factor": 1.0}
    elif to_u == "r":
        return {"value": kelvin * 9 / 5, "factor": 1.0}

    return None


def convert_to_si(value: float, unit: str) -> tuple[float, str]:
    """Convert a value from any supported unit to its SI base unit.

    Returns (converted_value, si_unit_string).

    Examples:
        >>> convert_to_si(10, "ft")
        (3.048, "m")
        >>> convert_to_si(1000, "lbf")
        (4448.2216152605, "n")
        >>> convert_to_si(14.7, "psi")
        (101352.931994, "pa")
    """
    normalized = _normalize_unit(unit)
    if normalized not in _SI_BASE:
        raise ValueError(f"Unknown unit: {unit}. Cannot convert to SI.")

    si_unit = _SI_BASE[normalized]
    if normalized == si_unit:
        return value, si_unit

    result = unit_convert(value, normalized, si_unit)
    return result["converted_value"], si_unit


def _make_result(ov, ou, cu, cv, cf) -> dict:
    return {
        "original_value": ov,
        "original_unit": ou,
        "converted_value": cv,
        "converted_unit": cu,
        "conversion_factor": cf,
    }


# Convenience helpers for common aerospace conversions


def ft_to_m(value: float) -> float:
    """Convert feet to meters."""
    return float(_FOOT_TO_METER) * value


def m_to_ft(value: float) -> float:
    """Convert meters to feet."""
    return value / float(_FOOT_TO_METER)


def lbf_to_n(value: float) -> float:
    """Convert pound-force to Newtons."""
    return float(_POUND_FORCE_TO_NEWTON) * value


def n_to_lbf(value: float) -> float:
    """Convert Newtons to pound-force."""
    return value / float(_POUND_FORCE_TO_NEWTON)


def psi_to_pa(value: float) -> float:
    """Convert psi to Pascals."""
    return float(_PSI_TO_PASCAL) * value


def pa_to_psi(value: float) -> float:
    """Convert Pascals to psi."""
    return value / float(_PSI_TO_PASCAL)


def mph_to_mps(value: float) -> float:
    """Convert mph to m/s."""
    return float(_MPH_TO_MPS) * value


def mps_to_mph(value: float) -> float:
    """Convert m/s to mph."""
    return value / float(_MPH_TO_MPS)


def knots_to_mps(value: float) -> float:
    """Convert knots to m/s."""
    return float(_KNOT_TO_MPS) * value


def mps_to_knots(value: float) -> float:
    """Convert m/s to knots."""
    return value / float(_KNOT_TO_MPS)
