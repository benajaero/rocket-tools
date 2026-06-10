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


_LENGTH_UNIT_RE = r"m|mm|cm|km|meters?|metres?"


def extract_length(text: str) -> float | None:
    result = extract_number_with_unit(text, _LENGTH_UNIT_RE, negative_lookahead=r"\s*/")
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
    if re.search(r"sea\s*level", text, re.IGNORECASE):
        return 0.0
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


_LIFT_RE = re.compile(r"lift\s*(?:of|is|=|:)?\s*(\d+\.?\d*)\s*(N|kN|lbf)", re.IGNORECASE)
_DRAG_RE = re.compile(r"drag\s*(?:of|is|=|:)?\s*(\d+\.?\d*)\s*(N|kN|lbf)", re.IGNORECASE)
_AREA_RE = re.compile(
    r"(?:area|reference\s*area|S)\s*(?:of|is|=|:)?\s*(\d+\.?\d*)\s*(m2|m\^2|sq\s*m|m²)",
    re.IGNORECASE,
)
_REYNOLDS_RE = re.compile(
    r"(?:Reynolds\s*number|Re\s*=?)\s*(\d+\.?\d*(?:[eE][+-]?\d+)?)", re.IGNORECASE
)


def extract_lift(text: str) -> float | None:
    m = _LIFT_RE.search(text)
    if m:
        val = float(m.group(1))
        unit = m.group(2).lower()
        if unit == "kn":
            return val * 1000
        return val
    return None


def extract_drag(text: str) -> float | None:
    m = _DRAG_RE.search(text)
    if m:
        val = float(m.group(1))
        unit = m.group(2).lower()
        if unit == "kn":
            return val * 1000
        return val
    return None


def extract_reference_area(text: str) -> float | None:
    m = _AREA_RE.search(text)
    if m:
        return float(m.group(1))
    return None


def extract_reynolds_number(text: str) -> float | None:
    m = _REYNOLDS_RE.search(text)
    if m:
        return float(m.group(1))
    return None


def extract_flow_regime(text: str) -> str | None:
    if re.search(r"\blaminar\b", text, re.IGNORECASE):
        return "laminar"
    if re.search(r"\bturbulent\b", text, re.IGNORECASE):
        return "turbulent"
    return None
