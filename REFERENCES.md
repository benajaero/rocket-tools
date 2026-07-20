# References & Data Sources

This document catalogs the primary references and data sources used throughout rocket-tools.

---

## Standards & Handbooks

| Reference | Used In | Description |
|-----------|---------|-------------|
| **MIL-HDBK-5J** | `materials/database.py` | Metallic Materials and Elements for Aerospace Vehicle Structures. Primary source for aluminum, titanium, steel, and nickel alloy mechanical properties at room temperature. |
| **MMPDS-15** | `materials/database.py` | Metallic Materials Properties Development and Standardization (successor to MIL-HDBK-5). Updated allowables for modern alloys. |
| **MIL-HDBK-17** | `materials/database.py` | Composite Materials Handbook. Source for carbon/epoxy, glass/epoxy, and Kevlar properties. |
| **ISO 2533:1975** | `materials/isa.py` | Standard Atmosphere. Defines the International Standard Atmosphere (ISA) temperature, pressure, and density profiles. |
| **NASA-TM-X-74335** | `materials/isa.py` | U.S. Standard Atmosphere, 1976. Implementation reference for atmosphere tables 0–25 km. |
| **FAA AC 25.571-1D** | `structural/margin.py` | Damage Tolerance and Fatigue Evaluation of Structure. Defines margin of safety methodology and factors of safety for aircraft. |
| **ASME Y14.5** | `utils/units.py` | Dimensioning and Tolerancing. Basis for SI/imperial unit conversion constants. |

---

## Textbooks & Monographs

### Structural Analysis

| Reference | Used In | Key Formulas |
|-----------|---------|--------------|
| **Roark's Formulas for Stress and Strain** (Young & Budynas, 8th Ed.) | `structural/beams.py`, `structural/sections.py` | Beam deflections (Table 8.1), section properties, bending stress formulas for rectangular and circular sections. |
| **Bruhn: Analysis and Design of Flight Vehicle Structures** | `structural/buckling.py` | Plate buckling coefficients (Fig. C5.2, C5.3), column effective length factors (Table C2.1). |
| **Shigley's Mechanical Engineering Design** (Budynas & Nisbett, 11th Ed.) | `structural/margin.py` | Margin of safety definitions, factor of safety selection guidelines, von Mises stress formulation. |
| **Timoshenko & Gere: Theory of Elastic Stability** (2nd Ed.) | `structural/buckling.py` | Euler buckling load, Johnson parabola transition slenderness ratio. |
| **Megson: Aircraft Structures for Engineering Students** (6th Ed.) | `structural/truss.py` | Direct stiffness method for pin-jointed trusses. |

### Aerodynamics

| Reference | Used In | Key Formulas |
|-----------|---------|--------------|
| **Anderson: Fundamentals of Aerodynamics** (6th Ed.) | `aerodynamics/fundamentals.py`, `aerodynamics/compressible.py` | Reynolds number, Mach number, dynamic pressure, isentropic flow relations (Ch. 4), normal shock (Ch. 4), oblique shock (Ch. 4), Prandtl-Meyer expansion (Ch. 4). |
| **Anderson: Aircraft Performance and Design** | `aerodynamics/aircraft.py` | Lift curve slope (lifting line theory), drag polar, Breguet range and endurance equations (Ch. 6). |
| **Blasius (1908)** | `aerodynamics/fundamentals.py` | Skin friction coefficients: $c_f = 1.328 / \sqrt{Re}$ (laminar), $c_f = 0.0592 / Re^{0.2}$ (turbulent). |
| **Anderson: Hypersonic and High-Temperature Gas Dynamics** (2nd Ed.) | `aerodynamics/aerothermo.py` | Stagnation and recovery (adiabatic-wall) temperature; recovery factor $r = Pr^{0.5}$ (laminar), $Pr^{1/3}$ (turbulent). |
| **Sutton, K. & Graves, R. A., NASA TR R-376 (1971)** | `aerodynamics/aerothermo.py` | Stagnation-point convective heating $q = C\sqrt{\rho/R_n}\,V^3$, $C = 1.7415\times10^{-4}$ for Earth air (W/m²). |
| **Allen, H. J. & Eggers, A. J., NACA TR 1381 (1958)** | `aerodynamics/aerothermo.py` | Ballistic entry: peak deceleration $a_{max} = V_e^2\sin\gamma/(2eH)$ and velocity at peak $V_e/\sqrt{e}$. |

### Propulsion & Nozzle Design

| Reference | Used In | Key Formulas |
|-----------|---------|--------------|
| **Sutton & Biblarz: Rocket Propulsion Elements** (9th Ed.) | `aerodynamics/nozzle.py`, `design/performance.py` | Tsiolkovsky rocket equation, thrust coefficient, specific impulse, characteristic velocity $c^*$, optimal expansion ratio (Ch. 3). |
| **Hill & Peterson: Mechanics and Thermodynamics of Propulsion** (2nd Ed.) | `aerodynamics/nozzle.py` | Isentropic nozzle flow relations, choked flow conditions, area-Mach relation. |

### Orbital Mechanics

| Reference | Used In | Key Formulas |
|-----------|---------|--------------|
| **Vallado: Fundamentals of Astrodynamics and Applications** (4th Ed.) | `design/performance.py`, `design/orbital.py` | Circular orbital velocity, escape velocity, orbital period (Ch. 1); vis-viva equation (Eq. 2-70), simple plane change (Eq. 6-19), Earth mu=3.986004418e14 m³/s² (App. D). |
| **Curtis: Orbital Mechanics for Engineering Students** (3rd Ed.) | `design/orbital.py` | Hohmann transfer delta-v and transfer time (Ch. 6, Example 6.1). |
| **Bate, Mueller & White: Fundamentals of Astrodynamics** | `design/orbital.py` | Two-body energy and the vis-viva relation (Ch. 3). |

---

## Material Properties — Specific Sources

### Aluminum Alloys

| Alloy | Primary Source | Notes |
|-------|---------------|-------|
| 1100-H14 | MIL-HDBK-5J, Table 3.2.2.0(b) | Pure aluminum, general purpose |
| 2024-T3/T351 | MIL-HDBK-5J, Table 3.2.3.0(b) | Aircraft skin and wing structures |
| 5052-H32 | MIL-HDBK-5J, Table 3.2.5.0(b) | Marine and cryogenic applications |
| 5083-H116 | MIL-HDBK-5J, Table 3.2.6.0(b) | Weldable structural alloy |
| 6061-T6 | MIL-HDBK-5J, Table 3.2.7.0(b) | Most widely used general-purpose alloy |
| 6061-T651 | MIL-HDBK-5J, Table 3.2.7.0(b) | Stress-relieved plate |
| 7075-T6/T651 | MIL-HDBK-5J, Table 3.2.8.0(b) | High-strength aircraft alloy |
| 7075-T73 | MIL-HDBK-5J, Table 3.2.8.0(c) | Stress-corrosion resistant temper |
| 2219-T87 | MIL-HDBK-5J, Table 3.2.9.0(b) | High-temperature aerospace |
| 2195 | NASA/MSFC data, MMPDS-15 | Al-Li alloy for cryogenic tanks |
| 7050-T7451 | MMPDS-15 | Thick-section aircraft forgings |
| 7085-T7651 | MMPDS-15 | Landing gear and bulkheads |

### Titanium Alloys

| Alloy | Primary Source | Notes |
|-------|---------------|-------|
| Ti-6Al-4V (Grade 5) | MIL-HDBK-5J, Table 5.3.1.0(b) | Workhorse aerospace titanium |
| Ti-6Al-2Sn-4Zr-2Mo | MIL-HDBK-5J, Table 5.3.2.0(b) | High-temperature applications |
| Ti-5Al-2.5Sn (Grade 6) | MIL-HDBK-5J, Table 5.3.3.0(b) | Cryogenic applications |
| Ti-15V-3Cr-3Al-3Sn | MIL-HDBK-5J, Table 5.3.4.0(b) | High-strength sheet alloy |

### Steels

| Alloy | Primary Source | Notes |
|-------|---------------|-------|
| 4130 (normalized) | MIL-HDBK-5J, Table 2.3.1.0(b) | Chrome-moly tube and sheet |
| 4340 | MIL-HDBK-5J, Table 2.3.2.0(b) | High-strength landing gear steel |
| 17-4PH (H900) | MIL-HDBK-5J, Table 2.6.1.0(b) | Precipitation hardening stainless |
| 300M (4340M) | MIL-HDBK-5J, Table 2.3.3.0(b) | Ultra-high-strength landing gear |
| M50 | MIL-HDBK-5J, Table 2.4.1.0(b) | Bearing steel |
| 52100 | AISI/SAE handbook | Bearing steel |
| A-286 | MIL-HDBK-5J, Table 2.7.1.0(b) | High-temperature fastener alloy |
| 15-5PH | MIL-HDBK-5J, Table 2.6.2.0(b) | Stainless precipitation hardening |
| Maraging 250 | MIL-HDBK-5J, Table 2.8.1.0(b) | Ultra-high-strength tool steel |
| 440C | MIL-HDBK-5J, Table 2.6.3.0(b) | Corrosion-resistant bearing steel |

### Nickel Superalloys

| Alloy | Primary Source | Notes |
|-------|---------------|-------|
| Inconel-600 | Special Metals / Haynes Int'l datasheet | General high-temperature |
| Inconel-625 | Special Metals datasheet | High-strength, corrosion resistant |
| Inconel-718 | MIL-HDBK-5J, Table 6.3.1.0(b) | Most common Ni superalloy |
| Inconel-X750 | Special Metals datasheet | Spring and fastener applications |
| Hastelloy-X | Haynes International datasheet | Oxidation-resistant sheet |
| Waspaloy | Special Metals datasheet | Turbine disks and rings |
| Rene-41 | Haynes International datasheet | Turbine blades and vanes |
| Haynes-230 | Haynes International datasheet | Combustor components |

### Composites

| Material | Primary Source | Notes |
|----------|---------------|-------|
| Carbon-Epoxy T300/5208 | MIL-HDBK-17-2F, Table 4.4.1 | Baseline aerospace composite |
| Carbon-Epoxy T700/M21 | Hexcel datasheet / MMPDS | Intermediate modulus |
| Carbon-Epoxy IM7/8552 | MIL-HDBK-17-2F, Table 4.6.1 | High modulus |
| Glass-Epoxy E-Glass/7781 | MIL-HDBK-17-2F, Table 5.4.1 | General purpose fiberglass |
| Kevlar-49/Epoxy | DuPont / MIL-HDBK-17-2F | Ballistic and tension applications |
| Carbon-Carbon | MIL-HDBK-17-5 | Re-entry thermal protection |
| Silica-Phenolic | Avcoat / NASA data | Ablative heat shield material |

### Refractory & Specialty Metals

| Material | Primary Source | Notes |
|----------|---------------|-------|
| Tungsten | Plansee / Goodfellow datasheet | Highest melting point metal |
| Molybdenum | Plansee datasheet | High-temperature structural |
| Rhenium | Goodfellow datasheet | Rocket engine coatings |
| C18150 (CuCrZr) | NGK / Materion datasheet | High-conductivity, high-strength copper |
| GlidCop-Al-25 | SCM Metal Products datasheet | Dispersion-strengthened copper |
| Beryllium-Copper C17200 | Materion datasheet | Spring and explosive-forming dies |
| Magnesium AZ31B | MIL-HDBK-5J, Table 4.3.1.0(b) | Lightweight castings |
| Copper C11000 | ASTM B152 | Electrical bus bars |

---

## Validation & Benchmark Data

| Benchmark | Source | Used For |
|-----------|--------|----------|
| NACA 0012 drag polar at Re = 3×10⁶ | Abbott & von Doenhoff, "Theory of Wing Sections" | Validation of drag polar and skin friction tools |
| Blasius boundary layer solution | Blasius (1908), ZAMM | Validation of skin friction coefficient |
| Roark Table 8.1 Case 1 | Roark's Formulas (8th Ed.) | Validation of simply supported beam deflection |
| Standard Atmosphere 1976 | NASA-TM-X-74335 | Validation of ISA atmosphere model |
| Rocket equation standard cases | Sutton & Biblarz, Table 3-2 | Validation of delta-v calculations |

---

## Unit Conversion Constants

| Quantity | Reference | Notes |
|----------|-----------|-------|
| Standard gravity $g_0$ | ISO 80000-4 | 9.80665 m/s² (exact) |
| Standard atmosphere | ISO 2533:1975 | Sea level: 101325 Pa, 288.15 K, 1.225 kg/m³ |
| Universal gas constant | CODATA 2018 | 8.314462618 J/(mol·K) (exact) |
| Inch-to-meter | NIST SP 330 | 0.0254 m (exact) |
| Pound-force | NIST SP 330 | 4.4482216152605 N (exact) |
| PSI to Pascal | Derived | 6894.757293168 Pa |

---

## How to Cite rocket-tools

If you use rocket-tools in published work:

```bibtex
@software{rocket_tools,
  title = {rocket-tools: Engineering-grade aerospace computation for AI agents},
  author = {Human Engine labs},
  url = {https://github.com/benajaero/rocket-tools},
  year = {2025},
}
```

**Important:** Always verify critical design values against primary sources (MIL-HDBK-5, MMPDS, manufacturer datasheets) before use in flight hardware. The values in this database are for preliminary design and educational purposes.
