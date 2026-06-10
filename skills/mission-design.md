---
title: Mission Design
skill_type: engineering
layer: design
tools:
  - rocket_delta_v
  - multi_stage_delta_v
  - orbital_velocity
  - payload_fraction
  - thrust_to_weight
  - composite_cg
  - propellant_tank_sizing
version: 0.3.2
---

# Mission Design

Engineering skill for rocket mission planning, orbital mechanics, and vehicle sizing.

## When to Use

- Computing rocket ΔV budgets for orbital insertion
- Sizing multi-stage rockets
- Estimating payload fractions for mission feasibility
- Checking thrust-to-weight ratios for launch capability
- Computing center of gravity for composite vehicles
- Sizing propellant tanks for rockets and spacecraft

## Key Concepts

### Tsiolkovsky Rocket Equation

$$ \Delta v = I_{sp} \cdot g_0 \cdot \ln\left(\frac{m_0}{m_f}\right) $$

Where:
- $I_{sp}$ = specific impulse (s)
- $g_0$ = standard gravity (9.80665 m/s²)
- $m_0$ = initial mass (propellant + structure + payload)
- $m_f$ = final mass (structure + payload)

Mass ratio: $\frac{m_0}{m_f} = e^{\Delta v / (I_{sp} \cdot g_0)}$

### Multi-Stage Rocket

For serial staging, total ΔV is the sum of individual stage ΔVs:

$$ \Delta v_{total} = \sum_{i} I_{sp,i} \cdot g_0 \cdot \ln\left(\frac{m_{0,i}}{m_{f,i}}\right) $$

Where $m_{0,i}$ includes the stage's own propellant, dry mass, and all upper stages + payload.

### Orbital Velocity

Circular orbit velocity:
$$ v_c = \sqrt{\frac{GM}{r}} = \sqrt{\frac{\mu}{R + h}} $$

Escape velocity:
$$ v_e = \sqrt{2} \cdot v_c $$

Where $r = R + h$ is the orbital radius (planet radius + altitude).

### Payload Fraction

From the rocket equation rearranged:

$$ \epsilon = e^{-\Delta v / (I_{sp} \cdot g_0)} - \sigma $$

Where:
- $\epsilon$ = payload fraction
- $\sigma$ = inert (structural) mass fraction

If $\epsilon \leq 0$, the mission is **not achievable** with the given $I_{sp}$ and $\sigma$.

### Thrust-to-Weight

$$ T/W = \frac{F_{thrust}}{m \cdot g} $$

| T/W | Capability |
|-----|------------|
| < 1.0 | Cannot hover; needs runway or aerodynamic lift |
| = 1.0 | Can hover, no climb |
| > 1.0 | Can climb vertically |
| > 1.3 | Comfortable launch margin |
| > 2.0 | High-g launch (common for solid boosters) |

### Center of Gravity

For a composite body with $n$ components:

$$ \vec{r}_{CG} = \frac{\sum_{i} m_i \vec{r}_i}{\sum_{i} m_i} $$

Moments of inertia about CG (parallel axis theorem):

$$ I_{xx} = \sum_i m_i \left[(y_i - y_{CG})^2 + (z_i - z_{CG})^2\right] $$

### Propellant Tank Sizing

Tank volume includes ullage (typically 5–10% extra for cryogenic boil-off and expansion):

$$ V_{total} = V_{propellant} \cdot (1 + f_{ullage}) $$

**Cylinder:** $V = \frac{\pi}{4} d^2 L$, where $L/d$ = aspect ratio

**Sphere:** $V = \frac{\pi}{6} d^3$ (most mass-efficient shape)

Tank mass ≈ surface area × wall thickness × material density

## MCP Tool Reference

### `rocket_delta_v`

Compute single-stage ΔV using Tsiolkovsky equation.

**Parameters (schema: `RocketDeltaVInput`):**
- `specific_impulse_s` — Isp in seconds (`> 0`)
- `initial_mass_kg` — Initial mass (`> 0`)
- `final_mass_kg` — Final mass (`> 0`, `< initial`)
- `gravity` — Standard gravity (default 9.80665)

**Returns:** `delta_v_ms`, `delta_v_kms`, `mass_ratio`, `propellant_fraction`

### `multi_stage_delta_v`

Compute total ΔV for serial multi-stage rocket with per-stage breakdown.

**Parameters (schema: `MultiStageDeltaVInput`):**
- `stages` — List of dicts, each with:
  - `specific_impulse_s`
  - `dry_mass_kg`
  - `propellant_mass_kg`
  - `payload_mass_kg` (mass above this stage)
- `gravity` — Default 9.80665

**Returns:** `total_delta_v_ms`, `total_delta_v_kms`, `stages` (list with per-stage ΔV, mass ratio, propellant fraction)

### `orbital_velocity`

Compute circular and escape velocity.

**Parameters (schema: `OrbitalVelocityInput`):**
- `altitude_m` — Altitude above surface (`≥ 0`)
- `body_radius_m` — Planet radius (default 6,371,000 for Earth)
- `body_mass_kg` — Planet mass (default 5.972e24 for Earth)
- `gravity_constant` — G (default 6.67430e-11)

**Returns:** `circular_velocity_ms`, `escape_velocity_ms`, `orbital_period_s`, `orbital_period_min`, `orbital_period_hr`

### `payload_fraction`

Estimate mission payload fraction.

**Parameters (schema: `PayloadFractionInput`):**
- `delta_v_required_ms` — Mission ΔV budget (`> 0`)
- `specific_impulse_s` — (`> 0`)
- `inert_mass_fraction` — Structure fraction `[0, 1)`
- `gravity` — Default 9.80665

**Returns:** `payload_fraction`, `propellant_fraction`, `achievable` (bool), `required_mass_ratio`

### `thrust_to_weight`

Compute thrust-to-weight ratio.

**Parameters (schema: `ThrustToWeightInput`):**
- `thrust_n` — Total thrust (`> 0`)
- `mass_kg` — Vehicle mass (`> 0`)
- `gravity` — Default 9.80665

**Returns:** `thrust_to_weight_ratio`, `can_hover`, `max_vertical_climb_acceleration_ms2`

### `composite_cg`

Compute center of gravity and mass moments.

**Parameters (schema: `CompositeCGInput`):**
- `masses` — List of component masses in kg (all `> 0`)
- `positions` — List of `[x, y, z]` positions in meters

**Returns:** `total_mass_kg`, `cg_x_m`, `cg_y_m`, `cg_z_m`, `i_xx_kg_m2`, `i_yy_kg_m2`, `i_zz_kg_m2`, plus product of inertia terms

### `propellant_tank_sizing`

Size a tank and estimate mass.

**Parameters (schema: `PropellantTankSizingInput`):**
- `propellant_volume_m3` — Required propellant volume (`> 0`)
- `ullage_fraction` — Extra volume fraction (default 0.1)
- `tank_shape` — `"cylinder"`, `"sphere"`, or `"ellipsoid"`
- `aspect_ratio` — Length/diameter for cylinder (default 2.0)
- `wall_thickness_m` — Tank wall thickness (default 0.003)
- `material_density_kg_m3` — Tank material density (default 2700 for aluminum)

**Returns:** `diameter_m`, `length_m`, `surface_area_m2`, `tank_mass_kg`, `total_volume_m3`

## Worked Example: Single-Stage to Orbit?

**Problem:** Can a single stage with Isp = 350 s deliver 9.4 km/s ΔV? Initial mass = 100,000 kg, structural fraction = 8%.

**Solution:**
```python
from rocket_tools.design import rocket_delta_v, payload_fraction

# ΔV capability
dv = rocket_delta_v(
    specific_impulse_s=350,
    initial_mass_kg=100000,
    final_mass_kg=100000 * 0.08,  # Just structure, no payload
)
print(f"Max ΔV = {dv['delta_v_kms']:.2f} km/s")

# With 9.4 km/s required
pf = payload_fraction(
    delta_v_required_ms=9400,
    specific_impulse_s=350,
    inert_mass_fraction=0.08,
)
print(f"Achievable: {pf['achievable']}")
if pf['achievable']:
    print(f"Payload fraction = {pf['payload_fraction']*100:.2f}%")
else:
    print(f"Reason: {pf['reason']}")
```

## Worked Example: Two-Stage Rocket

**Problem:** A Falcon 9-like two-stage rocket. Stage 1: Isp = 282 s, dry = 25,000 kg, prop = 395,000 kg. Stage 2: Isp = 348 s, dry = 4,000 kg, prop = 92,000 kg. Payload = 5,000 kg. Find total ΔV.

**Solution:**
```python
from rocket_tools.design import multi_stage_delta_v

stages = [
    {
        "specific_impulse_s": 282,
        "dry_mass_kg": 25000,
        "propellant_mass_kg": 395000,
        "payload_mass_kg": 4000 + 92000 + 5000,  # Stage 2 dry + prop + payload
    },
    {
        "specific_impulse_s": 348,
        "dry_mass_kg": 4000,
        "propellant_mass_kg": 92000,
        "payload_mass_kg": 5000,
    },
]

result = multi_stage_delta_v(stages)
print(f"Total ΔV = {result['total_delta_v_kms']:.2f} km/s")
for s in result['stages']:
    print(f"  Stage {s['stage']}: {s['delta_v_kms']:.2f} km/s")
```

## Worked Example: LEO Orbit

**Problem:** Find circular velocity and period for a 400 km altitude Earth orbit.

**Solution:**
```python
from rocket_tools.design import orbital_velocity

result = orbital_velocity(altitude_m=400e3)
print(f"Circular velocity = {result['circular_velocity_kms']:.2f} km/s")
print(f"Escape velocity = {result['escape_velocity_kms']:.2f} km/s")
print(f"Orbital period = {result['orbital_period_min']:.1f} min")
```

## Worked Example: Vehicle CG

**Problem:** A rocket has: engine (500 kg at [0, 0, -5]), tanks (1000 kg at [0, 0, 0]), payload (200 kg at [0, 0, 5]). Find CG.

**Solution:**
```python
from rocket_tools.design import composite_cg

result = composite_cg(
    masses=[500, 1000, 200],
    positions=[[0, 0, -5], [0, 0, 0], [0, 0, 5]],
)
print(f"CG = [{result['cg_x_m']:.3f}, {result['cg_y_m']:.3f}, {result['cg_z_m']:.3f}] m")
print(f"Total mass = {result['total_mass_kg']:.1f} kg")
```

## Worked Example: Tank Sizing

**Problem:** Size a cylindrical LOX tank for 50 m³ propellant, using Ti-6Al-4V (ρ = 4430 kg/m³), wall thickness 5 mm, 10% ullage.

**Solution:**
```python
from rocket_tools.design import propellant_tank_sizing

result = propellant_tank_sizing(
    propellant_volume_m3=50.0,
    ullage_fraction=0.10,
    tank_shape="cylinder",
    aspect_ratio=2.0,
    wall_thickness_m=0.005,
    material_density_kg_m3=4430,
)
print(f"Tank diameter = {result['diameter_m']:.2f} m")
print(f"Tank length = {result['length_m']:.2f} m")
print(f"Tank mass = {result['tank_mass_kg']:.1f} kg")
```

## Common Pitfalls

1. **ΔV budget** — LEO requires ~9.3–9.7 km/s from the surface (including gravity and drag losses). The orbital velocity alone is only ~7.8 km/s at 400 km.
2. **Inert mass fraction** — Modern launch vehicles: ~4–8% for stages, ~10–15% for small rockets. Be realistic.
3. **Payload fraction negative** — If `payload_fraction` returns `achievable=False`, the mission is impossible with that Isp and structural fraction. You need better propellant, lighter structure, or staging.
4. **CG shifts during flight** — `composite_cg` is for a snapshot. Propellant depletion shifts CG significantly; compute at multiple time points.
5. **Tank pressure** — `propellant_tank_sizing` estimates structural mass from surface area only. Pressurized tanks need thicker walls; add a safety factor for pressure vessels.
