---
title: Structural Analysis
skill_type: engineering
layer: structural
tools:
  - beam_analysis
  - material_lookup
  - unit_convert
version: 0.1.0
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

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `load` | float | Applied load (N for point, N/m for distributed) |
| `length` | float | Span length (m) |
| `youngs_modulus` | float | E in Pa |
| `cross_section` | dict | `{type: "rectangle", width: m, height: m}` or `{type: "circle", diameter: m}` |
| `load_type` | str | `"point_midspan"`, `"distributed"`, `"axial"` |
| `support_type` | str | `"simply_supported"`, `"cantilever"`, `"fixed_ends"` |

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

Convert between engineering units.

**Supported units:**
- Length: m, mm, inch, ft
- Pressure: Pa, kPa, MPa, psi
- Force: N, kN, lbf
- Temperature: C, K, F

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

## Common Pitfalls

1. **Unit consistency** — Always use SI units (m, Pa, N) in the tools
2. **Small deflection assumption** — Euler-Bernoulli theory breaks down for large deflections (> L/10)
3. **Buckling mode** — Euler formula assumes the weakest axis; check $I_{min}$
4. **Dynamic loads** — Static analysis only; apply safety factors for dynamic cases
