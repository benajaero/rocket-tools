"""Intent pattern registry for aerospace queries."""

from collections.abc import Callable
from dataclasses import dataclass, field

from .extractors import (
    extract_altitude,
    extract_conversion_value,
    extract_drag,
    extract_flow_regime,
    extract_from_unit,
    extract_length,
    extract_lift,
    extract_load,
    extract_material,
    extract_reference_area,
    extract_reynolds_number,
    extract_to_unit,
    extract_velocity,
)


@dataclass
class IntentConfig:
    patterns: list[str]
    param_extractors: dict[str, Callable]
    defaults: dict = field(default_factory=dict)
    required_params: list[str] = field(default_factory=list)


INTENT_REGISTRY = {
    "beam_analysis": IntentConfig(
        patterns=[
            r"beam",
            r"(load|force|weight|carry|support|handle|design|calculate|find).*beam",
            r"beam.*(load|force|weight|carry|support|handle|design|calculate|find)",
            r"(deflection|bending stress|bending moment|section modulus)",
        ],
        param_extractors={
            "load": extract_load,
            "length": extract_length,
            "material": extract_material,
        },
        defaults={
            "cross_section": {"type": "rectangle", "width": 0.05, "height": 0.01},
            "support_type": "simply_supported",
            "load_type": "point_midspan",
        },
        required_params=["load", "length"],
    ),
    "aero_analysis": IntentConfig(
        patterns=[
            r"(aerodynamic|flow|Reynolds|Mach|dynamic pressure|lift|drag)",
            r"(subsonic|transonic|supersonic|hypersonic)",
            r"(velocity|speed|altitude|height).*analysis",
        ],
        param_extractors={
            "velocity": extract_velocity,
            "altitude_m": extract_altitude,
            "characteristic_length": extract_length,
        },
        defaults={
            "reference_area": 1.0,
            "lift": 0.0,
            "drag": 0.0,
        },
        required_params=["velocity", "altitude_m"],
    ),
    "reynolds_number": IntentConfig(
        patterns=[
            r"Reynolds\s*number",
            r"\bRe\s*\d",
            r"Re\s*=",
        ],
        param_extractors={
            "velocity": extract_velocity,
            "characteristic_length": extract_length,
            "altitude_m": extract_altitude,
        },
        defaults={},
        required_params=["velocity", "characteristic_length"],
    ),
    "mach_number": IntentConfig(
        patterns=[
            r"Mach\s*number",
            r"Mach\s*\d",
        ],
        param_extractors={
            "velocity": extract_velocity,
            "altitude_m": extract_altitude,
        },
        defaults={},
        required_params=["velocity", "altitude_m"],
    ),
    "dynamic_pressure": IntentConfig(
        patterns=[
            r"dynamic\s*pressure",
            r"q\s*=",
        ],
        param_extractors={
            "velocity": extract_velocity,
            "altitude_m": extract_altitude,
        },
        defaults={},
        required_params=["velocity", "altitude_m"],
    ),
    "lift_coefficient": IntentConfig(
        patterns=[
            r"lift\s*coefficient",
            r"CL\s*=",
            r"CL\s*\d",
        ],
        param_extractors={
            "lift": extract_lift,
            "velocity": extract_velocity,
            "altitude_m": extract_altitude,
            "reference_area": extract_reference_area,
        },
        defaults={},
        required_params=["lift", "velocity", "altitude_m", "reference_area"],
    ),
    "drag_coefficient": IntentConfig(
        patterns=[
            r"drag\s*coefficient",
            r"CD\s*=",
            r"CD\s*\d",
        ],
        param_extractors={
            "drag": extract_drag,
            "velocity": extract_velocity,
            "altitude_m": extract_altitude,
            "reference_area": extract_reference_area,
        },
        defaults={},
        required_params=["drag", "velocity", "altitude_m", "reference_area"],
    ),
    "skin_friction_coefficient": IntentConfig(
        patterns=[
            r"skin\s*friction",
            r"friction\s*coefficient",
            r"Cf\s*=",
            r"Cf\s*\d",
        ],
        param_extractors={
            "reynolds_number": extract_reynolds_number,
            "flow_regime": extract_flow_regime,
        },
        defaults={"flow_regime": "laminar"},
        required_params=["reynolds_number"],
    ),
    "material_lookup": IntentConfig(
        patterns=[
            r"(properties|property|specs|material data)",
            r"look up.*material",
            r"what is.*(6061|7075|titanium|inconel|steel|aluminum|aluminium)",
            r"(6061|7075|ti-6al-4v|inconel|4130)",
        ],
        param_extractors={
            "name": extract_material,
        },
        defaults={},
        required_params=["name"],
    ),
    "isa_atmosphere": IntentConfig(
        patterns=[
            r"(ISA|atmosphere|atmospheric)",
            r"(density|pressure|temperature).*at.*(altitude|height)",
            r"at\s+(\d+).*m.*(altitude|height)",
        ],
        param_extractors={
            "altitude_m": extract_altitude,
        },
        defaults={},
        required_params=["altitude_m"],
    ),
    "unit_convert": IntentConfig(
        patterns=[
            r"convert",
            r"(\d+\.?\d*)\s*\w+\s+(to|into|in)\s+\w+",
        ],
        param_extractors={
            "value": extract_conversion_value,
            "from_unit": extract_from_unit,
            "to_unit": extract_to_unit,
        },
        defaults={},
        required_params=["value", "from_unit", "to_unit"],
    ),
}
