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

# Angle (pi to 36 digits; the engine casts to float at the boundary, so this is
# far more than float-exact for deg/rad and the arc subdivisions)
_PI = Decimal("3.14159265358979323846264338327950288")
_DEG_TO_RAD = _PI / Decimal("180")

# Factor to convert one unit of the key into its SI base unit (see _SI_BASE):
# value_in_base = value * _TO_BASE[unit]. Any two units sharing a base convert
# through it, so every intra-dimension pair works without an O(n^2) table.
_TO_BASE: dict[str, Decimal] = {
    # Length -> m
    "m": Decimal("1"),
    "mm": Decimal("0.001"),
    "cm": Decimal("0.01"),
    "km": Decimal("1000"),
    "inch": _INCH_TO_METER,
    "in": _INCH_TO_METER,
    "ft": _FOOT_TO_METER,
    "yd": _YARD_TO_METER,
    "mi": _MILE_TO_METER,
    "nm": _NAUTICAL_MILE_TO_METER,
    # Pressure -> pa
    "pa": Decimal("1"),
    "kpa": Decimal("1000"),
    "mpa": Decimal("1000000"),
    "gpa": Decimal("1000000000"),
    "psi": _PSI_TO_PASCAL,
    "psf": _PSF_TO_PASCAL,
    "ksi": _KSI_TO_PASCAL,
    "atm": _ATM_TO_PASCAL,
    "bar": _BAR_TO_PASCAL,
    "torr": _TORR_TO_PASCAL,
    # Force -> n
    "n": Decimal("1"),
    "kn": Decimal("1000"),
    "lbf": _POUND_FORCE_TO_NEWTON,
    "kip": _KIP_TO_NEWTON,
    "tonf": _TON_FORCE_TO_NEWTON,
    # Mass -> kg
    "kg": Decimal("1"),
    "lbm": _LBM_TO_KG,
    "slug": _SLUG_TO_KG,
    # Speed -> m/s
    "m/s": Decimal("1"),
    "mph": _MPH_TO_MPS,
    "fps": _FPS_TO_MPS,
    "knot": _KNOT_TO_MPS,
    "km/h": Decimal("1") / Decimal("3.6"),
    # Area -> m2
    "m2": Decimal("1"),
    "sqft": _SQFT_TO_SQM,
    "sqin": _SQIN_TO_SQM,
    # Density -> kg/m3
    "kg/m3": Decimal("1"),
    "slug/ft3": _SLUG_PER_CUBIC_FOOT_TO_KG_M3,
    "lb/ft3": _LB_PER_CUBIC_FOOT_TO_KG_M3,
    # Energy -> j
    "j": Decimal("1"),
    "ftlbf": _FTLBF_TO_JOULE,
    "btu": _BTU_TO_JOULE,
    # Angle -> rad
    "rad": Decimal("1"),
    "deg": _DEG_TO_RAD,
    "arcmin": _DEG_TO_RAD / Decimal("60"),
    "arcsec": _DEG_TO_RAD / Decimal("3600"),
    "rev": Decimal("2") * _PI,
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
    # Angle
    "rad": "rad",
    "deg": "rad",
    "arcmin": "rad",
    "arcsec": "rad",
    "rev": "rad",
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
        # Angle
        "radian": "rad",
        "radians": "rad",
        "degree": "deg",
        "degrees": "deg",
        "arcminute": "arcmin",
        "arcminutes": "arcmin",
        "arcsecond": "arcsec",
        "arcseconds": "arcsec",
        "revolution": "rev",
        "revolutions": "rev",
        "turn": "rev",
        "turns": "rev",
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
    Angle: rad, deg, arcmin, arcsec, rev
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

    if from_u not in _TO_BASE:
        raise ValueError(f"Unknown unit: {from_unit}")
    if to_u not in _TO_BASE:
        raise ValueError(f"Unknown unit: {to_unit}")
    if _SI_BASE[from_u] != _SI_BASE[to_u]:
        raise ValueError(
            f"Incompatible units: {from_unit} ({_SI_BASE[from_u]}) -> {to_unit} ({_SI_BASE[to_u]})"
        )

    # Convert through the shared SI base: value * (from->base) / (to->base).
    # Decimal keeps the factor exact; cast to float only at the boundary.
    factor = float(_TO_BASE[from_u] / _TO_BASE[to_u])
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
