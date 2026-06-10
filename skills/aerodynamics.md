---
title: Aerodynamics
skill_type: engineering
layer: aerodynamics
tools:
  - reynolds_number
  - mach_number
  - dynamic_pressure
  - lift_coefficient
  - drag_coefficient
  - skin_friction_coefficient
  - aero_analysis
  - isa_atmosphere
  - unit_convert
version: 0.3.0
---

# Aerodynamics

Engineering skill for aerodynamic analysis using the International Standard Atmosphere (ISA).

## When to Use

- Computing Reynolds number for flow regime determination
- Determining Mach number and flow regime classification
- Calculating dynamic pressure for structural loads
- Estimating lift and drag coefficients
- Computing skin friction for boundary layer analysis

## Key Concepts

### Reynolds Number

$$ Re = \frac{\rho V L}{\mu} $$

Flow regimes:
| Range | Regime |
|-------|--------|
| Re < 5×10⁵ | Laminar |
| 5×10⁵ ≤ Re < 10⁶ | Transitional |
| Re ≥ 10⁶ | Turbulent |

### Mach Number

$$ M = \frac{V}{a} = \frac{V}{\sqrt{\gamma R T}} $$

Where $a$ is the speed of sound. Regime classification:
| Range | Regime |
|-------|--------|
| M < 0.8 | Subsonic |
| 0.8 ≤ M < 1.2 | Transonic |
| 1.2 ≤ M < 5.0 | Supersonic |
| M ≥ 5.0 | Hypersonic |

### Dynamic Pressure

$$ q = \frac{1}{2} \rho V^2 $$

Used extensively in aerodynamic force calculations.

### Skin Friction Coefficient

Blasius correlations:
- Laminar: $c_f = \frac{1.328}{\sqrt{Re}}$
- Turbulent: $c_f = \frac{0.0592}{Re^{0.2}}$

## MCP Tool Reference

### `reynolds_number`

Compute Reynolds number using direct properties or ISA lookup.

**Parameters (schema: `ReynoldsNumberInput`):**
- `velocity` (m/s) — `> 0`
- `characteristic_length` (m) — `> 0`
- `density` + `dynamic_viscosity` (Pa·s) — OR —
- `altitude_m` (ISA lookup, 0–25,000) — OR —
- `temperature_k` (standard density)

### `mach_number`

Compute Mach number at altitude.

**Parameters (schema: `MachNumberInput`):**
- `velocity` (m/s) — `> 0`
- `altitude_m` — `0 ≤ altitude_m ≤ 25000`

### `dynamic_pressure`

Compute $q$ at altitude.

### `aero_analysis`

Comprehensive analysis: Re, Mach, q, CL, CD, Cf in one call.

**Parameters (schema: `AeroAnalysisInput`):**
- `velocity`, `altitude_m`, `characteristic_length`, `reference_area`
- Optional: `lift`, `drag`

### `isa_atmosphere`

Get ISA properties at altitude (0–25,000 m).

Returns: temperature (K, °C), pressure (Pa, kPa), density (kg/m³), speed of sound (m/s).

## Worked Example

**Problem:** An aircraft flies at 250 m/s at 5,000 m altitude. Wingspan = 20m, reference area = 40 m². Lift = 50,000 N, Drag = 5,000 N. Characterize the flow.

**Solution:**
```python
from rocket_tools.aerodynamics import aero_analysis

result = aero_analysis(
    velocity=250.0,
    altitude_m=5000.0,
    characteristic_length=20.0,
    reference_area=40.0,
    lift=50000.0,
    drag=5000.0,
)
print(f"Re = {result['reynolds_number']:.1e}")
print(f"Mach = {result['mach_number']:.3f} ({result['mach_regime']})")
print(f"L/D = {result['lift_to_drag_ratio']:.1f}")
```

## Worked Example: Imperial Inputs

**Problem:** An aircraft at 15,000 ft, 500 mph, wing chord 8 ft, wing area 350 sq ft, lift 11,000 lbf, drag 1,200 lbf.

**Solution:**
```python
from rocket_tools.utils.units import ft_to_m, mph_to_mps, lbf_to_n, sqft_to_sqm
from rocket_tools.aerodynamics import aero_analysis

result = aero_analysis(
    velocity=mph_to_mps(500),
    altitude_m=ft_to_m(15000),
    characteristic_length=ft_to_m(8),
    reference_area=sqft_to_sqm(350),
    lift=lbf_to_n(11000),
    drag=lbf_to_n(1200),
)
print(f"Re = {result['reynolds_number']:.1e}")
print(f"Mach = {result['mach_number']:.3f}")
```

## Common Pitfalls

1. **Characteristic length** — Use chord for wings, diameter for bodies, not span
2. **Reference area** — Must be consistent between CL and CD calculations
3. **Compressibility** — CL and CD formulas assume incompressible; corrections needed for M > 0.3
4. **Temperature effects** — ISA assumes standard day; adjust for non-standard conditions
5. **Altitude units** — `isa_atmosphere` expects meters. Convert from feet: `altitude_m = ft * 0.3048`
