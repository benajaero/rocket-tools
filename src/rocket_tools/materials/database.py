"""Aerospace material database with 45+ alloys, composites, and specialty materials.

Covers materials for rockets, aircraft, drones/UAVs, helicopters, spacecraft,
satellites, and propulsion systems.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Material:
    """Physical and mechanical properties of an aerospace material."""

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
    applications: frozenset[str] = field(default_factory=lambda: frozenset({"general"}))


# ---- Aluminum Alloys ----
# Widely used in aircraft skins, drone frames, rocket tanks, helicopter structures

_ALUMINUM: dict[str, Material] = {
    "1100-H14": Material(
        name="1100-H14",
        youngs_modulus_pa=68.9e9,
        density_kg_m3=2710.0,
        yield_strength_pa=110e6,
        ultimate_strength_pa=125e6,
        poisson_ratio=0.33,
        thermal_expansion_1_k=2.36e-5,
        thermal_conductivity_w_m_k=218.0,
        specific_heat_j_kg_k=904.0,
        applications=frozenset({"aircraft", "drone", "general"}),
        source="MIL-HDBK-5J Table 3.2.2.0(b)",
    ),
    "2024-T3": Material(
        name="2024-T3",
        youngs_modulus_pa=73.1e9,
        density_kg_m3=2780.0,
        yield_strength_pa=345e6,
        ultimate_strength_pa=483e6,
        poisson_ratio=0.33,
        thermal_expansion_1_k=2.32e-5,
        thermal_conductivity_w_m_k=151.0,
        specific_heat_j_kg_k=875.0,
        applications=frozenset({"aircraft", "helicopter", "drone"}),
        source="MIL-HDBK-5J Table 3.2.3.0(b)",
    ),
    "2024-T351": Material(
        name="2024-T351",
        youngs_modulus_pa=73.1e9,
        density_kg_m3=2780.0,
        yield_strength_pa=325e6,
        ultimate_strength_pa=470e6,
        poisson_ratio=0.33,
        thermal_expansion_1_k=2.32e-5,
        thermal_conductivity_w_m_k=151.0,
        specific_heat_j_kg_k=875.0,
        applications=frozenset({"aircraft", "helicopter", "drone"}),
        source="MIL-HDBK-5J Table 3.2.3.0(b)",
    ),
    "5052-H32": Material(
        name="5052-H32",
        youngs_modulus_pa=70.3e9,
        density_kg_m3=2680.0,
        yield_strength_pa=193e6,
        ultimate_strength_pa=228e6,
        poisson_ratio=0.33,
        thermal_expansion_1_k=2.38e-5,
        thermal_conductivity_w_m_k=138.0,
        specific_heat_j_kg_k=880.0,
        applications=frozenset({"aircraft", "drone", "rocket"}),
        source="MIL-HDBK-5J Table 3.2.5.0(b)",
    ),
    "5083-H116": Material(
        name="5083-H116",
        youngs_modulus_pa=70.3e9,
        density_kg_m3=2660.0,
        yield_strength_pa=228e6,
        ultimate_strength_pa=317e6,
        poisson_ratio=0.33,
        thermal_expansion_1_k=2.39e-5,
        thermal_conductivity_w_m_k=117.0,
        specific_heat_j_kg_k=900.0,
        applications=frozenset({"aircraft", "helicopter", "rocket", "marine"}),
        source="MIL-HDBK-5J Table 3.2.6.0(b)",
    ),
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
        applications=frozenset({"aircraft", "drone", "rocket", "helicopter", "general"}),
        source="MIL-HDBK-5J Table 3.2.7.0(b)",
    ),
    "6082-T6": Material(
        name="6082-T6",
        youngs_modulus_pa=70.0e9,
        density_kg_m3=2700.0,
        yield_strength_pa=260e6,
        ultimate_strength_pa=310e6,
        poisson_ratio=0.33,
        thermal_expansion_1_k=2.36e-5,
        thermal_conductivity_w_m_k=170.0,
        specific_heat_j_kg_k=890.0,
        applications=frozenset({"aircraft", "drone", "rocket"}),
        source="Typical values",
    ),
    "7050-T7451": Material(
        name="7050-T7451",
        youngs_modulus_pa=71.7e9,
        density_kg_m3=2830.0,
        yield_strength_pa=469e6,
        ultimate_strength_pa=524e6,
        poisson_ratio=0.33,
        thermal_expansion_1_k=2.36e-5,
        thermal_conductivity_w_m_k=154.0,
        specific_heat_j_kg_k=860.0,
        applications=frozenset({"aircraft", "helicopter"}),
        source="MMPDS-15",
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
        applications=frozenset({"aircraft", "drone", "helicopter"}),
        source="MIL-HDBK-5J Section 3.7 (7075 aluminum), representative room-temperature values",
    ),
    "7075-T73": Material(
        name="7075-T73",
        youngs_modulus_pa=71.7e9,
        density_kg_m3=2810.0,
        yield_strength_pa=386e6,
        ultimate_strength_pa=469e6,
        poisson_ratio=0.33,
        thermal_expansion_1_k=2.36e-5,
        thermal_conductivity_w_m_k=130.0,
        specific_heat_j_kg_k=960.0,
        applications=frozenset({"aircraft", "drone"}),
        source="MIL-HDBK-5J Section 3.7 (7075 aluminum), representative room-temperature values",
    ),
    "7475-T761": Material(
        name="7475-T761",
        youngs_modulus_pa=70.3e9,
        density_kg_m3=2810.0,
        yield_strength_pa=462e6,
        ultimate_strength_pa=524e6,
        poisson_ratio=0.33,
        thermal_expansion_1_k=2.36e-5,
        thermal_conductivity_w_m_k=154.0,
        specific_heat_j_kg_k=860.0,
        applications=frozenset({"aircraft", "helicopter"}),
        source="Typical values",
    ),
    "2219-T87": Material(
        name="2219-T87",
        youngs_modulus_pa=73.8e9,
        density_kg_m3=2840.0,
        yield_strength_pa=393e6,
        ultimate_strength_pa=476e6,
        poisson_ratio=0.33,
        thermal_expansion_1_k=2.26e-5,
        thermal_conductivity_w_m_k=154.0,
        specific_heat_j_kg_k=864.0,
        applications=frozenset({"rocket", "spacecraft"}),
        source="MIL-HDBK-5J Table 3.2.9.0(b)",
    ),
    "2195": Material(
        name="2195",
        youngs_modulus_pa=76.0e9,
        density_kg_m3=2700.0,
        yield_strength_pa=448e6,
        ultimate_strength_pa=517e6,
        poisson_ratio=0.33,
        thermal_expansion_1_k=2.26e-5,
        thermal_conductivity_w_m_k=130.0,
        specific_heat_j_kg_k=864.0,
        applications=frozenset({"rocket", "spacecraft", "satellite"}),
        source="MMPDS-15 / NASA MSFC data",
    ),
}

# ---- Titanium Alloys ----
# High strength-to-weight for rocket engines, airframes, helicopter rotors

_TITANIUM: dict[str, Material] = {
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
        applications=frozenset({"aircraft", "rocket", "helicopter", "drone", "spacecraft"}),
        source="MIL-HDBK-5J Table 5.3.1.0(b)",
    ),
    "Ti-6Al-2Sn-4Zr-2Mo": Material(
        name="Ti-6Al-2Sn-4Zr-2Mo",
        youngs_modulus_pa=113.8e9,
        density_kg_m3=4540.0,
        yield_strength_pa=896e6,
        ultimate_strength_pa=965e6,
        poisson_ratio=0.33,
        thermal_expansion_1_k=8.6e-6,
        thermal_conductivity_w_m_k=7.2,
        specific_heat_j_kg_k=520.0,
        applications=frozenset({"aircraft", "rocket", "spacecraft"}),
        source="MIL-HDBK-5J Table 5.3.2.0(b)",
    ),
    "Ti-5Al-2.5Sn": Material(
        name="Ti-5Al-2.5Sn",
        youngs_modulus_pa=110.0e9,
        density_kg_m3=4480.0,
        yield_strength_pa=758e6,
        ultimate_strength_pa=814e6,
        poisson_ratio=0.33,
        thermal_expansion_1_k=8.8e-6,
        thermal_conductivity_w_m_k=7.8,
        specific_heat_j_kg_k=520.0,
        applications=frozenset({"aircraft", "spacecraft"}),
        source="MIL-HDBK-5J Table 5.3.3.0(b)",
    ),
    "Ti-10V-2Fe-3Al": Material(
        name="Ti-10V-2Fe-3Al",
        youngs_modulus_pa=103.4e9,
        density_kg_m3=4650.0,
        yield_strength_pa=1100e6,
        ultimate_strength_pa=1172e6,
        poisson_ratio=0.33,
        thermal_expansion_1_k=8.5e-6,
        thermal_conductivity_w_m_k=7.5,
        specific_heat_j_kg_k=520.0,
        applications=frozenset({"aircraft", "helicopter"}),
        source="Typical values",
    ),
}

# ---- Steels ----
# Landing gear, engine shafts, gears, bearings, rocket structures

_STEELS: dict[str, Material] = {
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
        applications=frozenset({"aircraft", "drone", "rocket", "general"}),
        source="MIL-HDBK-5J Table 2.3.1.0(b)",
    ),
    "4340": Material(
        name="4340",
        youngs_modulus_pa=205e9,
        density_kg_m3=7850.0,
        yield_strength_pa=710e6,
        ultimate_strength_pa=850e6,
        poisson_ratio=0.29,
        thermal_expansion_1_k=1.23e-5,
        thermal_conductivity_w_m_k=44.5,
        specific_heat_j_kg_k=475.0,
        applications=frozenset({"aircraft", "helicopter", "rocket"}),
        source="MIL-HDBK-5J Table 2.3.2.0(b)",
    ),
    "17-4PH": Material(
        name="17-4PH",
        youngs_modulus_pa=196e9,
        density_kg_m3=7800.0,
        yield_strength_pa=1000e6,
        ultimate_strength_pa=1103e6,
        poisson_ratio=0.27,
        thermal_expansion_1_k=1.07e-5,
        thermal_conductivity_w_m_k=17.9,
        specific_heat_j_kg_k=460.0,
        applications=frozenset({"rocket", "spacecraft", "engine"}),
        source="MIL-HDBK-5J Table 2.6.1.0(b)",
    ),
    "15-5PH": Material(
        name="15-5PH",
        youngs_modulus_pa=196e9,
        density_kg_m3=7780.0,
        yield_strength_pa=965e6,
        ultimate_strength_pa=1070e6,
        poisson_ratio=0.27,
        thermal_expansion_1_k=1.07e-5,
        thermal_conductivity_w_m_k=17.9,
        specific_heat_j_kg_k=460.0,
        applications=frozenset({"rocket", "spacecraft", "engine"}),
        source="MIL-HDBK-5J Table 2.6.2.0(b)",
    ),
    "A286": Material(
        name="A286",
        youngs_modulus_pa=201e9,
        density_kg_m3=7920.0,
        yield_strength_pa=621e6,
        ultimate_strength_pa=1034e6,
        poisson_ratio=0.30,
        thermal_expansion_1_k=1.52e-5,
        thermal_conductivity_w_m_k=15.1,
        specific_heat_j_kg_k=450.0,
        applications=frozenset({"rocket", "engine", "spacecraft"}),
        source="Typical values",
    ),
    "300M": Material(
        name="300M",
        youngs_modulus_pa=207e9,
        density_kg_m3=7740.0,
        yield_strength_pa=1586e6,
        ultimate_strength_pa=1931e6,
        poisson_ratio=0.30,
        thermal_expansion_1_k=1.15e-5,
        thermal_conductivity_w_m_k=42.0,
        specific_heat_j_kg_k=460.0,
        applications=frozenset({"aircraft", "helicopter"}),
        source="MIL-HDBK-5J Table 2.3.3.0(b)",
    ),
    "304": Material(
        name="304",
        youngs_modulus_pa=193e9,
        density_kg_m3=8000.0,
        yield_strength_pa=215e6,
        ultimate_strength_pa=505e6,
        poisson_ratio=0.29,
        thermal_expansion_1_k=1.73e-5,
        thermal_conductivity_w_m_k=16.2,
        specific_heat_j_kg_k=500.0,
        applications=frozenset({"rocket", "spacecraft", "engine", "general"}),
        source="Typical values",
    ),
    "316": Material(
        name="316",
        youngs_modulus_pa=193e9,
        density_kg_m3=8000.0,
        yield_strength_pa=170e6,
        ultimate_strength_pa=480e6,
        poisson_ratio=0.30,
        thermal_expansion_1_k=1.60e-5,
        thermal_conductivity_w_m_k=16.2,
        specific_heat_j_kg_k=500.0,
        applications=frozenset({"rocket", "spacecraft", "engine", "marine"}),
        source="Typical values",
    ),
    "M50": Material(
        name="M50",
        youngs_modulus_pa=210e9,
        density_kg_m3=7800.0,
        yield_strength_pa=1724e6,
        ultimate_strength_pa=2069e6,
        poisson_ratio=0.30,
        thermal_expansion_1_k=1.20e-5,
        thermal_conductivity_w_m_k=35.0,
        specific_heat_j_kg_k=460.0,
        applications=frozenset({"aircraft", "helicopter", "engine"}),
        source="MIL-HDBK-5J Table 2.4.1.0(b)",
    ),
    "52100": Material(
        name="52100",
        youngs_modulus_pa=210e9,
        density_kg_m3=7810.0,
        yield_strength_pa=1724e6,
        ultimate_strength_pa=2240e6,
        poisson_ratio=0.30,
        thermal_expansion_1_k=1.17e-5,
        thermal_conductivity_w_m_k=46.6,
        specific_heat_j_kg_k=460.0,
        applications=frozenset({"aircraft", "helicopter", "engine"}),
        source="AISI/SAE handbook",
    ),
}

# ---- Nickel Superalloys ----
# Turbine blades, combustion chambers, rocket engine components

_NICKEL: dict[str, Material] = {
    "Inconel-600": Material(
        name="Inconel-600",
        youngs_modulus_pa=214e9,
        density_kg_m3=8470.0,
        yield_strength_pa=240e6,
        ultimate_strength_pa=550e6,
        poisson_ratio=0.31,
        thermal_expansion_1_k=1.28e-5,
        thermal_conductivity_w_m_k=14.9,
        specific_heat_j_kg_k=444.0,
        applications=frozenset({"rocket", "engine", "spacecraft"}),
        source="Special Metals datasheet",
    ),
    "Inconel-625": Material(
        name="Inconel-625",
        youngs_modulus_pa=207e9,
        density_kg_m3=8440.0,
        yield_strength_pa=517e6,
        ultimate_strength_pa=930e6,
        poisson_ratio=0.31,
        thermal_expansion_1_k=1.28e-5,
        thermal_conductivity_w_m_k=9.8,
        specific_heat_j_kg_k=410.0,
        applications=frozenset({"rocket", "engine", "spacecraft", "marine"}),
        source="Special Metals datasheet",
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
        applications=frozenset({"rocket", "engine", "aircraft", "spacecraft"}),
        source="MIL-HDBK-5J Table 6.3.1.0(b)",
    ),
    "Inconel-X750": Material(
        name="Inconel-X750",
        youngs_modulus_pa=214e9,
        density_kg_m3=8280.0,
        yield_strength_pa=725e6,
        ultimate_strength_pa=1138e6,
        poisson_ratio=0.30,
        thermal_expansion_1_k=1.24e-5,
        thermal_conductivity_w_m_k=11.7,
        specific_heat_j_kg_k=430.0,
        applications=frozenset({"rocket", "engine", "aircraft"}),
        source="Special Metals datasheet",
    ),
    "Hastelloy-X": Material(
        name="Hastelloy-X",
        youngs_modulus_pa=205e9,
        density_kg_m3=8220.0,
        yield_strength_pa=345e6,
        ultimate_strength_pa=755e6,
        poisson_ratio=0.32,
        thermal_expansion_1_k=1.29e-5,
        thermal_conductivity_w_m_k=13.4,
        specific_heat_j_kg_k=440.0,
        applications=frozenset({"rocket", "engine", "spacecraft"}),
        source="Haynes International datasheet",
    ),
    "Waspaloy": Material(
        name="Waspaloy",
        youngs_modulus_pa=211e9,
        density_kg_m3=8190.0,
        yield_strength_pa=793e6,
        ultimate_strength_pa=1241e6,
        poisson_ratio=0.30,
        thermal_expansion_1_k=1.27e-5,
        thermal_conductivity_w_m_k=11.3,
        specific_heat_j_kg_k=420.0,
        applications=frozenset({"aircraft", "engine"}),
        source="Special Metals datasheet",
    ),
    "Rene-41": Material(
        name="Rene-41",
        youngs_modulus_pa=218e9,
        density_kg_m3=8240.0,
        yield_strength_pa=758e6,
        ultimate_strength_pa=1241e6,
        poisson_ratio=0.30,
        thermal_expansion_1_k=1.24e-5,
        thermal_conductivity_w_m_k=11.3,
        specific_heat_j_kg_k=420.0,
        applications=frozenset({"aircraft", "engine", "rocket"}),
        source="Haynes International datasheet",
    ),
    "Haynes-230": Material(
        name="Haynes-230",
        youngs_modulus_pa=211e9,
        density_kg_m3=8390.0,
        yield_strength_pa=420e6,
        ultimate_strength_pa=880e6,
        poisson_ratio=0.34,
        thermal_expansion_1_k=1.31e-5,
        thermal_conductivity_w_m_k=11.5,
        specific_heat_j_kg_k=420.0,
        applications=frozenset({"rocket", "engine", "spacecraft"}),
        source="Haynes International datasheet",
    ),
}

# ---- Composites ----
# Drone frames, aircraft structures, rocket fairings, helicopter blades

_COMPOSITES: dict[str, Material] = {
    "Carbon-Epoxy-T300": Material(
        name="Carbon-Epoxy-T300",
        youngs_modulus_pa=150e9,
        density_kg_m3=1600.0,
        yield_strength_pa=1500e6,
        ultimate_strength_pa=1800e6,
        poisson_ratio=0.30,
        thermal_expansion_1_k=2.0e-6,
        thermal_conductivity_w_m_k=1.5,
        specific_heat_j_kg_k=900.0,
        applications=frozenset({"aircraft", "drone", "rocket", "spacecraft"}),
        source="MIL-HDBK-17-2F Table 4.4.1",
    ),
    "Carbon-Epoxy-T700": Material(
        name="Carbon-Epoxy-T700",
        youngs_modulus_pa=165e9,
        density_kg_m3=1600.0,
        yield_strength_pa=2550e6,
        ultimate_strength_pa=2737e6,
        poisson_ratio=0.30,
        thermal_expansion_1_k=1.5e-6,
        thermal_conductivity_w_m_k=1.8,
        specific_heat_j_kg_k=900.0,
        applications=frozenset({"aircraft", "drone", "rocket", "spacecraft"}),
        source="Hexcel datasheet / MMPDS",
    ),
    "Glass-Epoxy": Material(
        name="Glass-Epoxy",
        youngs_modulus_pa=45e9,
        density_kg_m3=1850.0,
        yield_strength_pa=600e6,
        ultimate_strength_pa=620e6,
        poisson_ratio=0.25,
        thermal_expansion_1_k=1.2e-5,
        thermal_conductivity_w_m_k=0.3,
        specific_heat_j_kg_k=900.0,
        applications=frozenset({"drone", "aircraft", "general"}),
        source="MIL-HDBK-17-2F Table 5.4.1",
    ),
    "Kevlar-49": Material(
        name="Kevlar-49",
        youngs_modulus_pa=112e9,
        density_kg_m3=1440.0,
        yield_strength_pa=2800e6,
        ultimate_strength_pa=3000e6,
        poisson_ratio=0.36,
        thermal_expansion_1_k=-2.0e-6,
        thermal_conductivity_w_m_k=0.04,
        specific_heat_j_kg_k=1420.0,
        applications=frozenset({"aircraft", "drone", "spacecraft"}),
        source="DuPont / MIL-HDBK-17-2F",
    ),
    "Carbon-Carbon": Material(
        name="Carbon-Carbon",
        youngs_modulus_pa=60e9,
        density_kg_m3=1600.0,
        yield_strength_pa=200e6,
        ultimate_strength_pa=400e6,
        poisson_ratio=0.30,
        thermal_expansion_1_k=1.0e-6,
        thermal_conductivity_w_m_k=20.0,
        specific_heat_j_kg_k=710.0,
        applications=frozenset({"rocket", "spacecraft", "engine"}),
        source="MIL-HDBK-17-5",
    ),
    "Silica-Phenolic": Material(
        name="Silica-Phenolic",
        youngs_modulus_pa=20e9,
        density_kg_m3=1650.0,
        yield_strength_pa=30e6,
        ultimate_strength_pa=50e6,
        poisson_ratio=0.25,
        thermal_expansion_1_k=1.5e-6,
        thermal_conductivity_w_m_k=0.5,
        specific_heat_j_kg_k=1000.0,
        applications=frozenset({"rocket", "spacecraft"}),
        source="Avcoat / NASA data",
    ),
}

# ---- Refractory / High-Temperature ----
# Rocket nozzles, combustion chambers, re-entry heat shields

_REFRACTORY: dict[str, Material] = {
    "Tungsten": Material(
        name="Tungsten",
        youngs_modulus_pa=400e9,
        density_kg_m3=19300.0,
        yield_strength_pa=550e6,
        ultimate_strength_pa=1500e6,
        poisson_ratio=0.28,
        thermal_expansion_1_k=4.5e-6,
        thermal_conductivity_w_m_k=173.0,
        specific_heat_j_kg_k=134.0,
        applications=frozenset({"rocket", "engine", "spacecraft"}),
        source="Plansee / Goodfellow datasheet",
    ),
    "Molybdenum": Material(
        name="Molybdenum",
        youngs_modulus_pa=329e9,
        density_kg_m3=10280.0,
        yield_strength_pa=400e6,
        ultimate_strength_pa=700e6,
        poisson_ratio=0.31,
        thermal_expansion_1_k=5.35e-6,
        thermal_conductivity_w_m_k=138.0,
        specific_heat_j_kg_k=251.0,
        applications=frozenset({"rocket", "engine", "spacecraft"}),
        source="Plansee datasheet",
    ),
    "C18150": Material(
        name="C18150",
        youngs_modulus_pa=117e9,
        density_kg_m3=8920.0,
        yield_strength_pa=400e6,
        ultimate_strength_pa=500e6,
        poisson_ratio=0.33,
        thermal_expansion_1_k=1.75e-5,
        thermal_conductivity_w_m_k=310.0,
        specific_heat_j_kg_k=385.0,
        applications=frozenset({"rocket", "engine"}),
        source="NGK / Materion datasheet",
    ),
    "GlidCop-Al-25": Material(
        name="GlidCop-Al-25",
        youngs_modulus_pa=130e9,
        density_kg_m3=8930.0,
        yield_strength_pa=380e6,
        ultimate_strength_pa=450e6,
        poisson_ratio=0.33,
        thermal_expansion_1_k=1.68e-5,
        thermal_conductivity_w_m_k=365.0,
        specific_heat_j_kg_k=385.0,
        applications=frozenset({"rocket", "engine"}),
        source="SCM Metal Products datasheet",
    ),
    "Rhenium": Material(  # NOTE: poisson corrected 0.49 -> 0.30 (near-incompressible was wrong)
        name="Rhenium",
        youngs_modulus_pa=463e9,
        density_kg_m3=21020.0,
        yield_strength_pa=300e6,
        ultimate_strength_pa=1070e6,
        poisson_ratio=0.30,
        thermal_expansion_1_k=6.2e-6,
        thermal_conductivity_w_m_k=48.0,
        specific_heat_j_kg_k=137.0,
        applications=frozenset({"rocket", "engine", "spacecraft"}),
        source="Goodfellow datasheet",
    ),
}

# ---- Other Materials ----
# Copper, magnesium, beryllium, specialty alloys

_OTHER: dict[str, Material] = {
    "Beryllium-Copper": Material(
        name="Beryllium-Copper",
        youngs_modulus_pa=128e9,
        density_kg_m3=8250.0,
        yield_strength_pa=965e6,
        ultimate_strength_pa=1103e6,
        poisson_ratio=0.30,
        thermal_expansion_1_k=1.68e-5,
        thermal_conductivity_w_m_k=105.0,
        specific_heat_j_kg_k=420.0,
        applications=frozenset({"aircraft", "spacecraft", "general"}),
        source="Materion datasheet",
    ),
    "Magnesium-AZ31B": Material(
        name="Magnesium-AZ31B",
        youngs_modulus_pa=45e9,
        density_kg_m3=1770.0,
        yield_strength_pa=200e6,
        ultimate_strength_pa=260e6,
        poisson_ratio=0.35,
        thermal_expansion_1_k=2.61e-5,
        thermal_conductivity_w_m_k=96.0,
        specific_heat_j_kg_k=1020.0,
        applications=frozenset({"aircraft", "drone", "spacecraft"}),
        source="MIL-HDBK-5J Table 4.3.1.0(b)",
    ),
    "Copper-C11000": Material(
        name="Copper-C11000",
        youngs_modulus_pa=115e9,
        density_kg_m3=8940.0,
        yield_strength_pa=69e6,
        ultimate_strength_pa=220e6,
        poisson_ratio=0.33,
        thermal_expansion_1_k=1.65e-5,
        thermal_conductivity_w_m_k=388.0,
        specific_heat_j_kg_k=385.0,
        applications=frozenset({"general", "engine", "rocket"}),
        source="ASTM B152",
    ),
}

# ---- Merge all categories ----

_MATERIALS: dict[str, Material] = {
    **_ALUMINUM,
    **_TITANIUM,
    **_STEELS,
    **_NICKEL,
    **_COMPOSITES,
    **_REFRACTORY,
    **_OTHER,
}

# Category mappings for filtering by material family
_CATEGORIES: dict[str, set[str]] = {
    "aluminum": set(_ALUMINUM.keys()),
    "titanium": set(_TITANIUM.keys()),
    "steel": set(_STEELS.keys()),
    "stainless": {"304", "316"},
    "nickel": set(_NICKEL.keys()),
    "superalloy": set(_NICKEL.keys()),
    "composite": set(_COMPOSITES.keys()),
    "refractory": set(_REFRACTORY.keys()),
    "copper": {"Beryllium-Copper", "Copper-C11000", "C18150", "GlidCop-Al-25"},
    "magnesium": {"Magnesium-AZ31B"},
}

# Application mappings for filtering by vehicle / system type
_APPLICATIONS: dict[str, set[str]] = {
    "aircraft": {k for k, m in _MATERIALS.items() if "aircraft" in m.applications},
    "rocket": {k for k, m in _MATERIALS.items() if "rocket" in m.applications},
    "drone": {k for k, m in _MATERIALS.items() if "drone" in m.applications},
    "uav": {k for k, m in _MATERIALS.items() if "drone" in m.applications},
    "helicopter": {k for k, m in _MATERIALS.items() if "helicopter" in m.applications},
    "spacecraft": {k for k, m in _MATERIALS.items() if "spacecraft" in m.applications},
    "satellite": {k for k, m in _MATERIALS.items() if "satellite" in m.applications},
    "engine": {k for k, m in _MATERIALS.items() if "engine" in m.applications},
    "propulsion": {k for k, m in _MATERIALS.items() if "engine" in m.applications},
    "general": {k for k, m in _MATERIALS.items() if "general" in m.applications},
}


def _fuzzy_match(name: str) -> str | None:
    """Try to match a material name with fuzzy logic."""
    name_normalized = name.strip().upper().replace(" ", "-")

    # Direct match
    if name_normalized in _MATERIALS:
        return name_normalized

    # Case-insensitive direct match
    for key in _MATERIALS:
        if key.upper() == name_normalized:
            return key

    # Remove dashes match
    name_no_dash = name_normalized.replace("-", "")
    for key in _MATERIALS:
        if key.upper().replace("-", "") == name_no_dash:
            return key

    # Substring match (e.g. "6061" matches "6061-T6")
    for key in _MATERIALS:
        if name_normalized in key.upper() or key.upper() in name_normalized:
            return key

    return None


def material_lookup(name: str, property_filter: str | None = None) -> dict:
    """Look up aerospace material properties by name.

    Supports 45+ materials across aluminum, titanium, steel, nickel superalloys,
    composites, refractory metals, and specialty alloys. Covers rockets, aircraft,
    drones/UAVs, helicopters, spacecraft, satellites, and propulsion systems.

    Args:
        name: Material name (e.g. "6061-T6", "Ti-6Al-4V", "Inconel-718",
              "Carbon-Carbon", "GlidCop-Al-25")
        property_filter: Optional filter — "youngs_modulus", "density",
            "yield_strength", "ultimate_strength", "poisson_ratio",
            or "all" (default)

    Returns:
        dict with material properties and application tags
    """
    if not name.strip():
        raise ValueError("Material name must not be empty")

    matched = _fuzzy_match(name)
    if matched is None:
        available = sorted(_MATERIALS.keys())
        raise ValueError(f"Material '{name}' not found. Available: {', '.join(available)}")

    mat = _MATERIALS[matched]
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
        "specific_strength": round(mat.yield_strength_pa / mat.density_kg_m3, 1),
        "applications": sorted(mat.applications),
        "warning": "These are representative values, not for certification.",
    }

    if property_filter:
        key = property_filter.strip().lower()
        if key == "all":
            return result
        mapping = {
            "youngs_modulus": "youngs_modulus_pa",
            "density": "density_kg_m3",
            "yield_strength": "yield_strength_pa",
            "ultimate_strength": "ultimate_strength_pa",
            "poisson_ratio": "poisson_ratio",
            "thermal_expansion": "thermal_expansion_1_k",
            "thermal_conductivity": "thermal_conductivity_w_m_k",
            "specific_heat": "specific_heat_j_kg_k",
            "specific_strength": "specific_strength",
        }
        if key in mapping:
            return {"material_name": mat.name, key: result[mapping[key]]}
        raise ValueError(
            f"Unknown material property '{property_filter}'. Available: {list(mapping.keys())}"
        )

    return result


def list_materials(category: str | None = None) -> list[str]:
    """List available materials, optionally filtered by category.

    Material family categories: aluminum, titanium, steel, stainless, nickel,
    superalloy, composite, refractory, copper, magnesium.

    Application categories: aircraft, rocket, drone, uav, helicopter,
    spacecraft, satellite, engine, propulsion, general.
    """
    if category is None:
        return sorted(_MATERIALS.keys())
    cat = category.lower()
    if cat in _CATEGORIES:
        return sorted(_CATEGORIES[cat])
    if cat in _APPLICATIONS:
        return sorted(_APPLICATIONS[cat])
    return []


def search_materials(query: str) -> list[dict]:
    """Search materials by partial name match.

    Returns a list of material summary dicts including application tags.
    """
    query_upper = query.upper()
    results = []
    for key, mat in _MATERIALS.items():
        if query_upper in key.upper():
            results.append(
                {
                    "name": mat.name,
                    "youngs_modulus_gpa": round(mat.youngs_modulus_pa / 1e9, 1),
                    "density_kg_m3": mat.density_kg_m3,
                    "yield_strength_mpa": round(mat.yield_strength_pa / 1e6, 1),
                    "specific_strength": round(mat.yield_strength_pa / mat.density_kg_m3, 1),
                    "applications": sorted(mat.applications),
                }
            )
    return results


def compare_materials(names: list[str]) -> list[dict[str, float | int | str | list[str]]]:
    """Compare multiple materials side-by-side.

    Returns a list of material dicts with key properties for comparison.
    Useful for trade studies (e.g. rocket tank material selection).
    """
    results: list[dict[str, float | int | str | list[str]]] = []
    for name in names:
        matched = _fuzzy_match(name)
        if matched is None:
            continue
        mat = _MATERIALS[matched]
        results.append(
            {
                "name": mat.name,
                "youngs_modulus_gpa": round(mat.youngs_modulus_pa / 1e9, 1),
                "density_kg_m3": mat.density_kg_m3,
                "yield_strength_mpa": round(mat.yield_strength_pa / 1e6, 1),
                "ultimate_strength_mpa": round(mat.ultimate_strength_pa / 1e6, 1),
                "specific_strength": round(mat.yield_strength_pa / mat.density_kg_m3, 1),
                "thermal_conductivity_w_m_k": mat.thermal_conductivity_w_m_k,
                "applications": sorted(mat.applications),
            }
        )
    # Sort by specific_strength descending (best strength-to-weight first)
    results.sort(key=lambda x: x["specific_strength"], reverse=True)
    return results
