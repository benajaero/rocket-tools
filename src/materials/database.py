"""Aerospace material database with O(1) hash map lookup."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class Material:
    name: str
    youngs_modulus_pa: float
    density_kg_m3: float
    yield_strength_pa: float
    ultimate_strength_pa: float
    poisson_ratio: float
    thermal_expansion_1_k: float
    thermal_conductivity_w_m_k: float
    specific_heat_j_kg_k: float
    source: str = "typical_values"


_MATERIALS: dict[str, Material] = {
    "6061-T6": Material(
        name="6061-T6",
        youngs_modulus_pa=68.9e9,
        density_kg_m3=2700.0,
        yield_strength_pa=276e6,
        ultimate_strength_pa=310e6,
        poisson_ratio=0.33,
        thermal_expansion_1_k=2.36e-5,
        thermal_conductivity_w_m_k=167.0,
        specific_heat_j_kg_k=896.0,
    ),
    "7075-T6": Material(
        name="7075-T6",
        youngs_modulus_pa=71.7e9,
        density_kg_m3=2810.0,
        yield_strength_pa=503e6,
        ultimate_strength_pa=572e6,
        poisson_ratio=0.33,
        thermal_expansion_1_k=2.36e-5,
        thermal_conductivity_w_m_k=130.0,
        specific_heat_j_kg_k=960.0,
    ),
    "Ti-6Al-4V": Material(
        name="Ti-6Al-4V",
        youngs_modulus_pa=113.8e9,
        density_kg_m3=4430.0,
        yield_strength_pa=880e6,
        ultimate_strength_pa=950e6,
        poisson_ratio=0.342,
        thermal_expansion_1_k=8.6e-6,
        thermal_conductivity_w_m_k=6.7,
        specific_heat_j_kg_k=526.3,
    ),
    "4130": Material(
        name="4130",
        youngs_modulus_pa=205e9,
        density_kg_m3=7850.0,
        yield_strength_pa=460e6,
        ultimate_strength_pa=560e6,
        poisson_ratio=0.29,
        thermal_expansion_1_k=1.2e-5,
        thermal_conductivity_w_m_k=42.7,
        specific_heat_j_kg_k=477.0,
    ),
    "Inconel-718": Material(
        name="Inconel-718",
        youngs_modulus_pa=200e9,
        density_kg_m3=8190.0,
        yield_strength_pa=1100e6,
        ultimate_strength_pa=1240e6,
        poisson_ratio=0.294,
        thermal_expansion_1_k=1.3e-5,
        thermal_conductivity_w_m_k=11.4,
        specific_heat_j_kg_k=435.0,
    ),
}


def material_lookup(name: str, property_filter: Optional[str] = None) -> dict:
    name_normalized = name.strip().upper()
    if name_normalized not in _MATERIALS:
        # Simple fuzzy match
        for key in _MATERIALS:
            if name_normalized.replace("-", "") == key.replace("-", ""):
                name_normalized = key
                break
        else:
            raise ValueError(f"Material '{name}' not found. Available: {list(_MATERIALS.keys())}")

    mat = _MATERIALS[name_normalized]
    result = {
        "material_name": mat.name,
        "youngs_modulus_gpa": mat.youngs_modulus_pa / 1e9,
        "youngs_modulus_pa": mat.youngs_modulus_pa,
        "density_kg_m3": mat.density_kg_m3,
        "yield_strength_mpa": mat.yield_strength_pa / 1e6,
        "yield_strength_pa": mat.yield_strength_pa,
        "ultimate_strength_mpa": mat.ultimate_strength_pa / 1e6,
        "ultimate_strength_pa": mat.ultimate_strength_pa,
        "poisson_ratio": mat.poisson_ratio,
        "thermal_expansion_1_k": mat.thermal_expansion_1_k,
        "thermal_conductivity_w_m_k": mat.thermal_conductivity_w_m_k,
        "specific_heat_j_kg_k": mat.specific_heat_j_kg_k,
        "source": mat.source,
        "warning": "These are representative values, not for certification.",
    }

    if property_filter and property_filter != "all":
        key = property_filter.lower()
        mapping = {
            "youngs_modulus": "youngs_modulus_pa",
            "density": "density_kg_m3",
            "yield_strength": "yield_strength_pa",
            "ultimate_strength": "ultimate_strength_pa",
            "poisson_ratio": "poisson_ratio",
        }
        if key in mapping:
            return {"material_name": mat.name, property_filter: result[mapping[key]]}

    return result
