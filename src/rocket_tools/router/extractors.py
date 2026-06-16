"""Regex-based parameter extraction from natural language."""

import re

_UNIT_RE = (
    r"meters?|metres?|m|millimeters?|millimetres?|mm|centimeters?|centimetres?|cm|"
    r"kilometers?|kilometres?|km|inch|inches|ft|feet|"
    r"pascals?|pa|kilopascals?|kpa|megapascals?|mpa|psi|"
    r"newtons?|n|kilonewtons?|kn|lbf|pounds?|"
    r"celsius|c|kelvin|k|fahrenheit|f"
)
_CONVERSION_RE = re.compile(
    rf"(\d+\.?\d*)\s*({_UNIT_RE})\s+(?:to|into|in)\s+({_UNIT_RE})",
    re.IGNORECASE,
)


def extract_number(text: str) -> float | None:
    m = re.search(r"(\d+\.?\d*(?:[eE][+-]?\d+)?)", text)
    if m:
        return float(m.group(1))
    return None


def _normalize_unit(unit: str) -> str:
    mapping = {
        "inches": "inch",
        "feet": "ft",
        "meter": "m",
        "meters": "m",
        "metre": "m",
        "metres": "m",
        "millimeter": "mm",
        "millimeters": "mm",
        "millimetre": "mm",
        "millimetres": "mm",
        "centimeter": "cm",
        "centimeters": "cm",
        "centimetre": "cm",
        "centimetres": "cm",
        "kilometer": "km",
        "kilometers": "km",
        "kilometre": "km",
        "kilometres": "km",
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
    result = extract_number_with_unit(text, r"N|n|Newtons?|newtons?|kN|kn|lbf|kip")
    if result:
        val, unit = result
        if unit in ("kn", "kN"):
            return val * 1000
        if unit == "lbf":
            return val * 4.4482216152605
        if unit == "kip":
            return val * 4448.2216152605
        return val
    return None


_LENGTH_UNIT_RE = r"m|mm|cm|km|meters?|metres?|inch|in|ft|feet|yd|yard"


def _convert_length(val: float, unit: str) -> float:
    if unit in ("mm", "millimeter", "millimeters", "millimetre", "millimetres"):
        return val / 1000
    if unit in ("cm", "centimeter", "centimeters", "centimetre", "centimetres"):
        return val / 100
    if unit in ("km", "kilometer", "kilometers", "kilometre", "kilometres"):
        return val * 1000
    if unit in ("inch", "in"):
        return val * 0.0254
    if unit in ("ft", "feet"):
        return val * 0.3048
    if unit in ("yd", "yard"):
        return val * 0.9144
    return val


def extract_length(text: str) -> float | None:
    unit_pattern = (
        r"millimeters?|millimetres?|centimeters?|centimetres?|kilometers?|kilometres?|"
        r"meters?|metres?|mm|cm|km|inch|in|ft|feet|yd|yard|m"
    )
    label_pattern = r"length|chord|span|diameter|width|height"

    labeled_patterns = [
        rf"(?:{label_pattern})\s*(?:of|is|=|:)?\s*(\d+\.?\d*)\s*({unit_pattern})(?!\s*/)",
        rf"(\d+\.?\d*)\s*({unit_pattern})(?!\s*/)\s*(?:{label_pattern}|long|wide|tall)",
        rf"(?:over|across)\s+(\d+\.?\d*)\s*({unit_pattern})(?!\s*/)",
    ]
    for pattern in labeled_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return _convert_length(float(match.group(1)), match.group(2).lower())

    result = extract_number_with_unit(text, unit_pattern, negative_lookahead=r"\s*/")
    if result:
        val, unit = result
        return _convert_length(val, unit)
    return None


def extract_velocity(text: str) -> float | None:
    result = extract_number_with_unit(text, r"m/s|mps|km/h|kmh|mph|fps|knot|kt")
    if result:
        val, unit = result
        if unit in ("km/h", "kmh"):
            return val / 3.6
        if unit in ("mph",):
            return val * 0.44704
        if unit in ("fps",):
            return val * 0.3048
        if unit in ("knot", "kt"):
            return val * 0.514444
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


_LIFT_RE = re.compile(r"lift\s*(?:of|is|=|:)?\s*(\d+\.?\d*)\s*(N|kN|lbf|kip)", re.IGNORECASE)
_DRAG_RE = re.compile(r"drag\s*(?:of|is|=|:)?\s*(\d+\.?\d*)\s*(N|kN|lbf|kip)", re.IGNORECASE)
_AREA_RE = re.compile(
    r"(?:area|reference\s*area|S)\s*(?:of|is|=|:)?\s*(\d+\.?\d*)\s*(m2|m\^2|sq\s*m|m²|sqft|sq\s*ft|ft2|ft\^2|sqin|sq\s*in|in2|in\^2)",
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
        if unit == "lbf":
            return val * 4.4482216152605
        if unit == "kip":
            return val * 4448.2216152605
        return val
    return None


def extract_drag(text: str) -> float | None:
    m = _DRAG_RE.search(text)
    if m:
        val = float(m.group(1))
        unit = m.group(2).lower()
        if unit == "kn":
            return val * 1000
        if unit == "lbf":
            return val * 4.4482216152605
        if unit == "kip":
            return val * 4448.2216152605
        return val
    return None


def extract_reference_area(text: str) -> float | None:
    m = _AREA_RE.search(text)
    if m:
        val = float(m.group(1))
        unit = m.group(2).lower()
        if unit in ("sqft", "sq ft", "ft2", "ft^2"):
            return val * 0.092903
        if unit in ("sqin", "sq in", "in2", "in^2"):
            return val * 0.00064516
        return val
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


def extract_stress(text: str) -> float | None:
    result = extract_number_with_unit(text, r"MPa|mpa|GPa|gpa|Pa|pa|psi|ksi|kPa|kpa")
    if result:
        val, unit = result
        if unit.lower() in ("gpa",):
            return val * 1e9
        if unit.lower() in ("mpa",):
            return val * 1e6
        if unit.lower() in ("kpa",):
            return val * 1e3
        if unit.lower() in ("psi",):
            return val * 6894.757
        if unit.lower() in ("ksi",):
            return val * 6.894757e6
        return val
    return None


def extract_pressure(text: str) -> float | None:
    result = extract_number_with_unit(text, r"MPa|mpa|bar|kPa|kpa|Pa|pa|psi|atm")
    if result:
        val, unit = result
        if unit.lower() in ("bar",):
            return val * 1e5
        if unit.lower() in ("mpa",):
            return val * 1e6
        if unit.lower() in ("kpa",):
            return val * 1e3
        if unit.lower() in ("psi",):
            return val * 6894.757
        if unit.lower() in ("atm",):
            return val * 101325.0
        return val
    return None


def extract_temperature(text: str) -> float | None:
    result = extract_number_with_unit(text, r"K|k|°C|C|°F|F")
    if result:
        val, unit = result
        if unit.lower() in ("°f", "f"):
            return (val - 32) * 5 / 9 + 273.15
        if unit.lower() in ("°c", "c"):
            return val + 273.15
        return val
    return None


def extract_gamma(text: str) -> float | None:
    m = re.search(r"gamma\s*(?:of|is|=|:)?\s*(\d+\.?\d*)", text, re.IGNORECASE)
    if m:
        return float(m.group(1))
    return None


def extract_mach(text: str) -> float | None:
    m = re.search(r"Mach\s*(?:number\s*)?(?:of|is|=|:)?\s*(\d+\.?\d*)", text, re.IGNORECASE)
    if m:
        return float(m.group(1))
    return None


def extract_angle(text: str) -> float | None:
    result = extract_number_with_unit(text, r"deg|degrees?|°|rad|radians?")
    if result:
        val, unit = result
        if unit.lower() in ("rad", "radians"):
            return val * 57.2958
        return val
    return None


def extract_aspect_ratio(text: str) -> float | None:
    m = re.search(r"aspect\s*ratio\s*(?:of|is|=|:)?\s*(\d+\.?\d*)", text, re.IGNORECASE)
    if m:
        return float(m.group(1))
    return None


def extract_sweep(text: str) -> float | None:
    result = extract_number_with_unit(text, r"deg|degrees?|°", negative_lookahead=r"\s*from")
    if result:
        return result[0]
    return None


def extract_mass(text: str) -> float | None:
    result = extract_number_with_unit(text, r"kg|g|lbm|lb|slug")
    if result:
        val, unit = result
        if unit.lower() in ("g",):
            return val / 1000
        if unit.lower() in ("lbm", "lb"):
            return val * 0.453592
        if unit.lower() in ("slug",):
            return val * 14.5939
        return val
    return None


def extract_thrust(text: str) -> float | None:
    result = extract_number_with_unit(text, r"N|n|kN|kn|lbf|kip")
    if result:
        val, unit = result
        if unit.lower() in ("kn",):
            return val * 1000
        if unit.lower() in ("lbf",):
            return val * 4.4482216152605
        if unit.lower() in ("kip",):
            return val * 4448.2216152605
        return val
    return None


def extract_youngs_modulus(text: str) -> float | None:
    result = extract_number_with_unit(text, r"GPa|gpa|MPa|mpa|Pa|pa|psi|ksi|kPa|kpa")
    if result:
        val, unit = result
        if unit.lower() in ("gpa",):
            return val * 1e9
        if unit.lower() in ("mpa",):
            return val * 1e6
        if unit.lower() in ("kpa",):
            return val * 1e3
        if unit.lower() in ("psi",):
            return val * 6894.757
        if unit.lower() in ("ksi",):
            return val * 6.894757e6
        return val
    return None


def extract_deflection(text: str) -> float | None:
    result = extract_number_with_unit(text, r"mm|cm|m|inch|in|ft|feet")
    if result:
        val, unit = result
        if unit in ("mm",):
            return val / 1000
        if unit in ("cm",):
            return val / 100
        if unit in ("inch", "in"):
            return val * 0.0254
        if unit in ("ft", "feet"):
            return val * 0.3048
        return val
    return None
