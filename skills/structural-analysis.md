---
title: Structural Analysis
skill_type: engineering
layer: structural
tools:
  - beam_analysis
  - section_properties
  - column_buckling
  - plate_buckling_coefficient
  - margin_of_safety
  - von_mises_stress
  - combined_margin_of_safety
  - deflection_margin
  - truss_analysis
  - material_lookup
  - unit_convert
version: 0.3.3
---

# Structural Analysis

Engineering skill for analyzing beams, columns, plates, and structural members.

## When to Use

- Computing bending stress and deflection in beams
- Determining cross-section properties for custom shapes
- Checking Euler-Johnson column buckling loads
- Estimating plate buckling coefficients for skins and tanks
- Computing margin of safety for yield, ultimate, buckling, and fatigue
- Analyzing combined stress states with von Mises equivalent stress
- Checking deflection limits (L/360, L/500, custom ratios)
- Analyzing 2D/3D pin-jointed truss structures
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

$$ P_{cr} = \frac{\pi^2 E I}{L_e^2} $$

Where $L_e = K \cdot L$ is the effective length. End condition factors:
| Condition | K |
|-----------|---|
| Pinned-pinned | 1.0 |
| Fixed-free | 2.0 |
| Fixed-pinned | 0.699 |
| Fixed-fixed | 0.5 |

### Johnson Parabola (Inelastic Buckling)

For short columns where slenderness $L_e/r < C_c$:

$$ \sigma_{cr} = \sigma_y - \frac{\sigma_y^2}{4\pi^2 E} \left(\frac{L_e}{r}\right)^2 $$

### Section Properties

Key properties for any cross-section:
- **Area** $A$ — m²
- **Area moment of inertia** $I_{xx}$ — m⁴ (resistance to bending)
- **Section modulus** $S_{xx}$ — m³ ($\sigma_{max} = M/S$)
- **Radius of gyration** $r$ — m ($r = \sqrt{I/A}$, used in buckling)

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

### `section_properties`

Compute properties for 7 structural shapes.

**Shapes and required parameters:**
| Shape | Parameters |
|-------|------------|
| `rectangle` | `width`, `height` |
| `hollow_rectangle` | `width`, `height`, `wall_thickness` |
| `circle` | `diameter` |
| `hollow_circle` | `outer_diameter`, `inner_diameter` |
| `ibeam` | `flange_width`, `height`, `flange_thickness`, `web_thickness` |
| `cchannel` | `flange_width`, `height`, `flange_thickness`, `web_thickness` |
| `tsection` | `flange_width`, `height`, `flange_thickness`, `web_thickness` |

**Returns:** `area_m2`, `i_xx_m4`, `s_xx_m3`, `r_xx_m`

### `column_buckling`

Compute critical buckling load using Euler-Johnson transition.

**Parameters:**
- `youngs_modulus` (Pa)
- `area_moment` (m⁴)
- `area` (m²)
- `length` (m)
- `yield_strength` (Pa)
- `end_condition` — `"pinned_pinned"`, `"fixed_free"`, `"fixed_pinned"`, `"fixed_fixed"`

**Returns:** `critical_load_n`, `critical_stress_pa`, `slenderness_ratio`, `regime` (`"elastic"` or `"inelastic"`)

### `plate_buckling_coefficient`

Approximate buckling coefficient $k$ for flat rectangular plates.

**Parameters:**
- `aspect_ratio` — plate length / width
- `boundary_condition` — `"simply_supported"`, `"clamped"`, `"free_edge"`
- `load_type` — `"compression"`, `"shear"`, `"bending"`

### `margin_of_safety`

Compute aerospace margin of safety.

$$ MS = \frac{Allowable}{FOS \times Actual} - 1 $$

**Parameters:**
- `allowable_stress_pa` + `actual_stress_pa` — for stress-based MS
- `allowable_load_n` + `actual_load_n` — for load-based MS
- `factor_of_safety` — default 1.5 (yield), 1.5 (ultimate), 2.0 (buckling)
- `failure_mode` — `"yield"`, `"ultimate"`, `"buckling"`, `"fatigue"`, `"custom"`

**Returns:** `margin_of_safety`, `utilization_ratio`, `status` (PASS/MARGINAL/FAIL)

### `von_mises_stress`

Compute von Mises equivalent stress for combined loading.

$$ \sigma_{vm} = \sqrt{ \frac{(\sigma_x - \sigma_y)^2 + (\sigma_y - \sigma_z)^2 + (\sigma_z - \sigma_x)^2 + 6(\tau_{xy}^2 + \tau_{yz}^2 + \tau_{xz}^2)}{2} } $$

**Returns:** `von_mises_stress_pa`, `sigma_1_pa`, `sigma_2_pa`, `sigma_3_pa`, `max_shear_stress_pa`

### `combined_margin_of_safety`

Compute MS for combined stress states using von Mises. Checks both yield and ultimate if strengths are provided.

### `deflection_margin`

Check margin of safety against deflection limits.

Common limits: L/360 (general), L/500 (control surfaces), L/200 (frames).

### `truss_analysis`

Analyze 2D/3D pin-jointed trusses using the direct stiffness method.

**Parameters:**
- `nodes` — List of [x, y] or [x, y, z] coordinates
- `elements` — List of [node_i, node_j] connectivity
- `element_properties` — List of {`youngs_modulus_pa`, `area_m2`}
- `constraints` — List of {`node`, `fixed_dof`}
- `loads` — List of {`node`, `force`}

**Returns:** `member_forces` (tension/compression), `node_displacements`, `reactions`

### `material_lookup`

Look up material properties by name. See [materials database](../src/rocket_tools/materials/database.py) for full list.

**Quick reference:**
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

## Worked Example: Beam Design

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

## Worked Example: Column Buckling

**Problem:** A 6061-T6 aluminum tube (OD = 50mm, ID = 40mm), 1.5m long, pinned-pinned ends. Check buckling.

**Solution:**
```python
from rocket_tools.structural import section_properties, column_buckling
from rocket_tools.materials import material_lookup

mat = material_lookup("6061-T6")
section = section_properties("hollow_circle", outer_diameter=0.05, inner_diameter=0.04)

buckling = column_buckling(
    youngs_modulus=mat["youngs_modulus_pa"],
    area_moment=section["i_xx_m4"],
    area=section["area_m2"],
    length=1.5,
    yield_strength=mat["yield_strength_mpa"] * 1e6,
    end_condition="pinned_pinned",
)
print(f"Critical load: {buckling['critical_load_n']:.0f} N")
print(f"Regime: {buckling['regime']}")
print(f"Slenderness: {buckling['slenderness_ratio']:.1f}")
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

## Worked Example: Margin of Safety

**Problem:** A 6061-T6 beam has bending stress of 120 MPa. Check MS for yield and ultimate.

**Solution:**
```python
from rocket_tools.structural import combined_margin_of_safety

result = combined_margin_of_safety(
    sigma_x=120e6,
    yield_strength_pa=276e6,
    ultimate_strength_pa=310e6,
    factor_of_safety_yield=1.5,
)
print(f"von Mises = {result['von_mises_stress_mpa']:.1f} MPa")
print(f"MS_yield = {result['margin_of_safety_yield']['margin_of_safety']:.3f}")
print(f"Status: {result['margin_of_safety_yield']['status']}")
```

## Worked Example: Truss Analysis

**Problem:** A 2D Warren truss with 3m span carries 10 kN at the center node.

**Solution:**
```python
from rocket_tools.structural import truss_analysis

result = truss_analysis(
    nodes=[[0, 0], [3, 0], [1.5, 1.5]],
    elements=[[0, 2], [1, 2]],
    element_properties=[
        {"youngs_modulus_pa": 200e9, "area_m2": 0.001},
        {"youngs_modulus_pa": 200e9, "area_m2": 0.001},
    ],
    constraints=[
        {"node": 0, "fixed_dof": [0, 1]},
        {"node": 1, "fixed_dof": [1]},
    ],
    loads=[{"node": 2, "force": [0, -10000]}],
)
for mf in result["member_forces"]:
    print(f"Member {mf['element']}: {mf['state']} {abs(mf['force_n']):.0f} N")
```

## References

- Roark's Formulas for Stress and Strain, 8th Ed. (Young & Budynas)
- Bruhn, "Analysis and Design of Flight Vehicle Structures"
- Timoshenko & Gere, "Theory of Elastic Stability", 2nd Ed.
- Megson, "Aircraft Structures for Engineering Students", 6th Ed.
- MIL-HDBK-5J / MMPDS-15: Material allowables
- FAA AC 25.571-1D: Margin of safety methodology

## Common Pitfalls

1. **Unit consistency** — Tools expect SI inputs (m, Pa, N). Use `convert_to_si()` or helpers like `ft_to_m()`, `lbf_to_n()` for imperial inputs.
2. **Small deflection assumption** — Euler-Bernoulli theory breaks down for large deflections (> L/10)
3. **Buckling mode** — Euler formula assumes the weakest axis; check $I_{min}$
4. **Dynamic loads** — Static analysis only; apply safety factors for dynamic cases
5. **Plate buckling** — The `k` coefficient is for ideal boundary conditions; real structures need knock-down factors
6. **MS sign convention** — Positive MS = safe, MS = 0 = exactly at limit, negative MS = failure
7. **Truss assumptions** — All joints are pinned, loads applied at nodes only. Continuous members or distributed loads violate this assumption.
