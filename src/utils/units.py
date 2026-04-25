"""Unit conversion engine with NIST-traceable constants."""

from decimal import Decimal

# NIST SP 811 defined constants (exact)
_INCH_TO_METER = Decimal("0.0254")
_POUND_FORCE_TO_NEWTON = Decimal("4.4482216152605")
_PSI_TO_PASCAL = Decimal("6894.757293168361")
_STD_GRAVITY = Decimal("9.80665")

# Conversion factors: (from_unit, to_unit) -> factor
_CONVERSIONS = {
    # Length
    ("m", "mm"): Decimal("1000"),
    ("mm", "m"): Decimal("0.001"),
    ("m", "inch"): Decimal("1") / _INCH_TO_METER,
    ("inch", "m"): _INCH_TO_METER,
    ("m", "ft"): Decimal("1") / _INCH_TO_METER / Decimal("12"),
    ("ft", "m"): _INCH_TO_METER * Decimal("12"),
    # Pressure
    ("pa", "kpa"): Decimal("0.001"),
    ("kpa", "pa"): Decimal("1000"),
    ("pa", "mpa"): Decimal("0.000001"),
    ("mpa", "pa"): Decimal("1000000"),
    ("pa", "psi"): Decimal("1") / _PSI_TO_PASCAL,
    ("psi", "pa"): _PSI_TO_PASCAL,
    ("psi", "kpa"): _PSI_TO_PASCAL * Decimal("0.001"),
    # Force
    ("n", "kn"): Decimal("0.001"),
    ("kn", "n"): Decimal("1000"),
    ("n", "lbf"): Decimal("1") / _POUND_FORCE_TO_NEWTON,
    ("lbf", "n"): _POUND_FORCE_TO_NEWTON,
}


def unit_convert(value: float, from_unit: str, to_unit: str) -> dict:
    from_u = from_unit.lower()
    to_u = to_unit.lower()

    if from_u == to_u:
        return {
            "original_value": value,
            "original_unit": from_unit,
            "converted_value": value,
            "converted_unit": to_unit,
            "conversion_factor": 1.0,
        }

    # Temperature requires special handling
    if from_u in ("c", "celsius") and to_u in ("k", "kelvin"):
        return _make_result(value, from_unit, to_unit, value + 273.15, 1.0)
    if from_u in ("k", "kelvin") and to_u in ("c", "celsius"):
        return _make_result(value, from_unit, to_unit, value - 273.15, 1.0)
    if from_u in ("f", "fahrenheit") and to_u in ("c", "celsius"):
        return _make_result(value, from_unit, to_unit, (value - 32) * 5 / 9, 5 / 9)

    key = (from_u, to_u)
    if key not in _CONVERSIONS:
        raise ValueError(f"Unsupported conversion: {from_unit} -> {to_unit}")

    factor = float(_CONVERSIONS[key])
    return _make_result(value, from_unit, to_unit, value * factor, factor)


def _make_result(ov, ou, cu, cv, cf) -> dict:
    return {
        "original_value": ov,
        "original_unit": ou,
        "converted_value": cv,
        "converted_unit": cu,
        "conversion_factor": cf,
    }
