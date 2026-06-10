---
title: Structural Analysis
skill_type: engineering
layer: structural
tools:
  - beam_analysis
  - material_lookup
  - unit_convert
version: 0.3.0
---

# Structural Analysis

Engineering skill for analyzing beams, columns, and structural members.

## When to Use

- Computing bending stress and deflection
- Checking Euler buckling loads
- Comparing material properties for structural applications
- Converting between SI and imperial units

## Key Concepts

### Euler-Bernoulli Beam Theory

For small deflections, the beam equation is:

$$ EI \frac{d^4 w}{dx^4} = q(x) $$

### Bending Stress

$$ \sigma = \frac{M}{S} $$

Where $M$ = bending moment (N·m) and $S$ = section modulus (m³).

### Euler Buckling Load

$$ P_{cr} = \frac{\pi^2 E I}{L^2} $$

For simply supported columns. Use $L_e = K \cdot L$ for other end conditions.

## MCP Tool Reference

### `beam_analysis`

Analyze a beam under various load and support conditions.

**Parameters (Pydantic schema: `BeamAnalysisInput`):**
| Parameter | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `load` | float | `> 0` | Applied load (N for point, N/m for distributed) |
| `length` | float | `> 0` | Span length (m) |
| `youngs_modulus` | float | `> 0` | E in Pa |
| `cross_section` | dict | required | `RectangleSection` or `CircleSection` |
| `load_type` | str | enum | `"point_midspan"`, `"distributed"`, `"axial"` |
| `support_type` | str | enum | `"simply_supported"`, `"cantilever"`, `"fixed_ends"` |

**Returns:**
- `max_bending_moment_n_m`
- `max_deflection_m`
- `bending_stress_pa`
- `critical_buckling_load_n`
- `safety_factor_euler_buckling`
- `section_efficiency_m2`

### `material_lookup`

Look up material properties by name.

**Available materials:**
- `6061-T6` — General purpose aluminum
- `7075-T6` — High-strength aluminum
- `Ti-6Al-4V` — Aerospace titanium
- `4130` — Chrome-moly steel
- `Inconel-718` — High-temperature superalloy

### `unit_convert`

Convert between engineering units. See [Unit Conversion skill](./units.md) for full reference.

**Quick reference:**
```python
from rocket_tools.utils import unit_convert
unit_convert(10, "ft", "m")      # -> 3.048 m
unit_convert(1000, "lbf", "n")   # -> 4448.22 N
unit_convert(14.7, "psi", "kpa") # -> 101.35 kPa
```

## Worked Example

**Problem:** A 6061-T6 aluminum beam, 1.0 m long, 50mm wide × 10mm deep, carries a 100N point load at midspan. Simply supported. Find the maximum deflection and bending stress.

**Solution:**
```python
from rocket_tools.structural import beam_analysis

result = beam_analysis(
    load=100.0,
    length=1.0,
    youngs_modulus=68.9e9,
    cross_section={"type": "rectangle", "width": 0.05, "height": 0.01},
)
print(f"Deflection: {result['max_deflection_m']*1000:.3f} mm")
print(f"Bending stress: {result['bending_stress_pa']/1e6:.2f} MPa")
```

## Worked Example: Imperial Units

**Problem:** A steel beam (E = 30 Msi), 10 ft long, 2 in × 4 in rectangular section, carries 500 lbf at midspan. Simply supported. Find deflection in inches and bending stress in psi.

**Solution:**
```python
from rocket_tools.utils.units import ft_to_m, lbf_to_n, psi_to_pa, in_to_m
from rocket_tools.structural import beam_analysis

result = beam_analysis(
    load=lbf_to_n(500),
    length=ft_to_m(10),
    youngs_modulus=psi_to_pa(30e6),
    cross_section={"type": "rectangle", "width": in_to_m(2), "height": in_to_m(4)},
)

deflection_in = result["max_deflection_m"] / 0.0254
stress_psi = result["bending_stress_pa"] / 6894.757
print(f"Deflection: {deflection_in:.4f} in")
print(f"Bending stress: {stress_psi:.1f} psi")
```

## Common Pitfalls

1. **Unit consistency** — Tools expect SI inputs (m, Pa, N). Use `convert_to_si()` or helpers like `ft_to_m()`, `lbf_to_n()` for imperial inputs.
2. **Small deflection assumption** — Euler-Bernoulli theory breaks down for large deflections (> L/10)
3. **Buckling mode** — Euler formula assumes the weakest axis; check $I_{min}$
4. **Dynamic loads** — Static analysis only; apply safety factors for dynamic cases
