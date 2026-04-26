"""Regex-based parameter extraction from natural language."""

import re


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
