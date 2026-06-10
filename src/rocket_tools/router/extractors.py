"""Regex-based parameter extraction from natural language."""

import re

_UNIT_RE = r"m|mm|cm|km|inch|inches|ft|feet|pa|kpa|mpa|psi|n|kn|lbf|c|k|f"
_CONVERSION_RE = re.compile(
    rf"(\d+\.?\d*)\s*({_UNIT_RE})\s+(?:to|into|in)\s+({_UNIT_RE})",
    re.IGNORECASE,
)


def _normalize_unit(unit: str) -> str:
    mapping = {
        "inches": "inch",
        "feet": "ft",
        "meter": "m",
        "meters": "m",
        "metre": "m",
        "metres": "m",
        "pascal": "pa",
        "pascals": "pa",
        "kilopascal": "kpa",
        "kilopascals": "kpa",
        "megapascal": "mpa",
        "megapascals": "mpa",
        "newton": "n",
        "newtons": "n",
        "kilonewton": "kn",
        "kilonewtons": "kn",
        "pound": "lbf",
        "pounds": "lbf",
        "celsius": "c",
        "kelvin": "k",
        "fahrenheit": "f",
    }
    u = unit.lower()
    return mapping.get(u, u)


def extract_conversion_value(text: str) -> float | None:
    m = _CONVERSION_RE.search(text)
    if m:
        return float(m.group(1))
    return None


def extract_from_unit(text: str) -> str | None:
    m = _CONVERSION_RE.search(text)
    if m:
        return _normalize_unit(m.group(2))
    return None


def extract_to_unit(text: str) -> str | None:
    m = _CONVERSION_RE.search(text)
    if m:
        return _normalize_unit(m.group(3))
    return None


def extract_number_with_unit(
    text: str, unit_pattern: str, negative_lookahead: str = ""
) -> tuple[float, str] | None:
    if negative_lookahead:
        pattern = rf"(\d+\.?\d*)\s*({unit_pattern})(?!{negative_lookahead})"
    else:
        pattern = rf"(\d+\.?\d*)\s*({unit_pattern})"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return float(match.group(1)), match.group(2).lower()
    return None


def extract_load(text: str) -> float | None:
    result = extract_number_with_unit(text, r"N|n|Newtons?|newtons?|kN|kn")
    if result:
        val, unit = result
        if unit in ("kn", "kN"):
            return val * 1000
        return val
    return None


def extract_length(text: str) -> float | None:
    result = extract_number_with_unit(text, r"m|mm|cm|km|meters?|metres?")
    if result:
        val, unit = result
        if unit in ("mm",):
            return val / 1000
        if unit in ("cm",):
            return val / 100
        if unit in ("km",):
            return val * 1000
        return val
    return None


def extract_velocity(text: str) -> float | None:
    result = extract_number_with_unit(text, r"m/s|mps|km/h|kmh|mph")
    if result:
        val, unit = result
        if unit in ("km/h", "kmh"):
            return val / 3.6
        if unit in ("mph",):
            return val * 0.44704
        return val
    return None


def extract_altitude(text: str) -> float | None:
    result = extract_number_with_unit(text, r"m|km|ft|feet|kft", negative_lookahead=r"\s*/")
    if result:
        val, unit = result
        if unit in ("km",):
            return val * 1000
        if unit in ("ft", "feet"):
            return val * 0.3048
        if unit in ("kft",):
            return val * 304.8
        return val
    return None


def extract_material(text: str) -> str | None:
    from rocket_tools.materials.database import _MATERIALS

    for key in _MATERIALS:
        if key.lower() in text.lower():
            return key
    return None
