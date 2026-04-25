"""Intent pattern registry for aerospace queries."""

from dataclasses import dataclass, field
from typing import Callable

from .extractors import (
    extract_load,
    extract_length,
    extract_velocity,
    extract_altitude,
    extract_material,
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
}
