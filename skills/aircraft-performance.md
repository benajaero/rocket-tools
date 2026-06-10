---
title: Aircraft Performance
skill_type: engineering
layer: aerodynamics
tools:
  - lift_curve_slope
  - drag_polar
  - breguet_range
  - breguet_endurance
  - wing_loading
version: 0.3.2
---

# Aircraft Performance

Engineering skill for fixed-wing aircraft aerodynamics and mission analysis.

## When to Use

- Preliminary wing design and lift curve estimation
- Drag polar construction for performance analysis
- Mission range and endurance calculations
- Wing loading and stall speed estimation
- UAV and drone performance sizing

## Key Concepts

### Lift Curve Slope

The 3D wing lift curve slope $C_{L_\alpha}$ relates lift coefficient to angle of attack:

**Subsonic (Prandtl-Glauert + Helmbold):**
$$ a_0 = \frac{2\pi}{\sqrt{1 - M^2}} \quad \text{(2D, per radian)} $$

$$ C_{L_\alpha} = \frac{a_0 \cos\Lambda}{1 + \frac{a_0 \cos\Lambda}{\pi A R \cdot e}} \quad \text{(3D, per radian)} $$

**Supersonic (linear theory):**
$$ C_{L_\alpha} = \frac{4}{\sqrt{M^2 - 1}} \left(1 - \frac{1}{2 A R \sqrt{M^2 - 1}}\right) $$

Where $A R$ = aspect ratio, $e$ = Oswald efficiency, $\Lambda$ = sweep angle.

### Drag Polar

$$ C_D = C_{D_0} + K \cdot C_L^2 + C_{D_{comp}} $$

Where:
- $C_{D_0}$ = zero-lift drag coefficient
- $K = \frac{1}{\pi A R \cdot e}$ = induced drag factor
- $C_{D_{comp}}$ = compressibility drag rise (approximated for M > 0.7)

Lift-to-drag ratio:
$$ \frac{L}{D} = \frac{C_L}{C_D} $$

### Breguet Range Equation

For jet aircraft:
$$ R = \frac{V}{SFC} \cdot \frac{L}{D} \cdot \ln\left(\frac{W_i}{W_f}\right) $$

For propeller aircraft (endurance focus):
$$ E = \frac{1}{SFC} \cdot \frac{L}{D} \cdot \ln\left(\frac{W_i}{W_f}\right) \cdot \frac{1}{g} $$

Where:
- $V$ = true airspeed (m/s)
- $SFC$ = specific fuel consumption (kg/(N·s))
- $W_i/W_f$ = initial/final mass ratio

### Wing Loading & Stall Speed

$$ \frac{W}{S} = \frac{\text{weight}}{\text{wing area}} $$

Stall speed at sea level:
$$ V_{stall} = \sqrt{\frac{2 (W/S)}{\rho_{SL} C_{L_{max}}}} $$

Typical $C_{L_{max}}$: 1.5 (clean), 2.0 (with flaps).

## MCP Tool Reference

### `lift_curve_slope`

Compute 3D wing lift curve slope $C_{L_\alpha}$.

**Parameters (schema: `LiftCurveSlopeInput`):**
- `mach` — Freestream Mach number
- `aspect_ratio` — $b^2/S$ (`> 0`)
- `taper_ratio` — Tip chord / root chord (default 1.0)
- `sweep_deg` — Quarter-chord sweep in degrees (default 0)
- `oswald_efficiency` — Oswald span efficiency (default 0.85)

**Returns:** `cl_alpha_2d_per_rad`, `cl_alpha_3d_per_rad`, `cl_alpha_3d_per_deg`, `induced_drag_factor_k`

### `drag_polar`

Compute drag coefficient from drag polar equation.

**Parameters (schema: `DragPolarInput`):**
- `cl` — Lift coefficient
- `cd0` — Zero-lift drag coefficient
- `aspect_ratio` — (`> 0`)
- `oswald_efficiency` — (default 0.85)
- `mach` — For compressibility drag (default 0)

**Returns:** `drag_coefficient`, `cd_induced`, `cd_compressibility`, `lift_to_drag_ratio`

### `breguet_range`

Compute aircraft range using Breguet equation.

**Parameters (schema: `BreguetRangeInput`):**
- `lift_to_drag_ratio` — L/D (`> 0`)
- `specific_fuel_consumption` — SFC in kg/(N·s) or lb/(lbf·hr)
- `velocity` — True airspeed in m/s (`> 0`)
- `initial_mass_kg` — Initial mass including fuel (`> 0`)
- `final_mass_kg` — Final mass after fuel burn (`> 0`, `< initial`)

**Returns:** `range_m`, `range_km`, `range_nm`, `endurance_s`, `endurance_hr`, `fuel_fraction`

### `breguet_endurance`

Compute aircraft endurance (jet aircraft version).

**Parameters:** Same as `breguet_range` except `velocity` is not required.

**Returns:** `endurance_s`, `endurance_hr`, `fuel_fraction`

### `wing_loading`

Compute wing loading and stall speeds.

**Parameters (schema: `WingLoadingInput`):**
- `weight_n` — Aircraft weight in N (`> 0`)
- `wing_area_m2` — Wing area in m² (`> 0`)

**Returns:** `wing_loading_pa`, `wing_loading_psf`, `stall_speed_clean_ms`, `stall_speed_clean_knots`, `stall_speed_flaps_ms`, `stall_speed_flaps_knots`

## Worked Example: Wing Lift Curve

**Problem:** A wing with AR = 8, sweep = 25°, flying at Mach 0.75. Find $C_{L_\alpha}$.

**Solution:**
```python
from rocket_tools.aerodynamics import lift_curve_slope

result = lift_curve_slope(
    mach=0.75,
    aspect_ratio=8.0,
    sweep_deg=25.0,
    oswald_efficiency=0.85,
)
print(f"CL_alpha = {result['cl_alpha_3d_per_deg']:.4f} /deg")
print(f"Induced drag factor K = {result['induced_drag_factor_k']:.4f}")
```

## Worked Example: Drag Polar

**Problem:** An aircraft with $C_{D_0}$ = 0.025, AR = 9, at Mach 0.8. Find drag at $C_L$ = 0.5.

**Solution:**
```python
from rocket_tools.aerodynamics import drag_polar

result = drag_polar(
    cl=0.5,
    cd0=0.025,
    aspect_ratio=9.0,
    oswald_efficiency=0.85,
    mach=0.8,
)
print(f"CD = {result['drag_coefficient']:.4f}")
print(f"L/D = {result['lift_to_drag_ratio']:.1f}")
print(f"Compressibility drag = {result['cd_compressibility']:.4f}")
```

## Worked Example: Mission Range

**Problem:** A business jet with L/D = 15, SFC = 0.00002 kg/(N·s), cruises at 250 m/s. Takeoff mass = 10,000 kg, landing mass = 8,500 kg. Find range and endurance.

**Solution:**
```python
from rocket_tools.aerodynamics import breguet_range, breguet_endurance

range_result = breguet_range(
    lift_to_drag_ratio=15.0,
    specific_fuel_consumption=0.00002,
    velocity=250.0,
    initial_mass_kg=10000.0,
    final_mass_kg=8500.0,
)
print(f"Range = {range_result['range_km']:.0f} km")
print(f"Fuel fraction = {range_result['fuel_fraction']*100:.1f}%")

endurance = breguet_endurance(
    lift_to_drag_ratio=15.0,
    specific_fuel_consumption=0.00002,
    initial_mass_kg=10000.0,
    final_mass_kg=8500.0,
)
print(f"Endurance = {endurance['endurance_hr']:.1f} hr")
```

## Worked Example: Wing Loading

**Problem:** A 2,000 kg aircraft with 15 m² wing area. Find wing loading and stall speeds.

**Solution:**
```python
from rocket_tools.aerodynamics import wing_loading

result = wing_loading(
    weight_n=2000 * 9.80665,
    wing_area_m2=15.0,
)
print(f"W/S = {result['wing_loading_pa']:.0f} N/m²")
print(f"Stall speed (clean) = {result['stall_speed_clean_knots']:.1f} kt")
print(f"Stall speed (flaps) = {result['stall_speed_flaps_knots']:.1f} kt")
```

## Common Pitfalls

1. **SFC units** — The tool auto-converts if SFC > 1e-3 (assumes imperial lb/(lbf·hr)). Typical jet SFC ≈ 0.00002 kg/(N·s).
2. **Compressibility drag** — The built-in model is a rough approximation. Use CFD or wind tunnel data for accurate transonic drag.
3. **Oswald efficiency** — Typical values: 0.75–0.85 for straight wings, 0.65–0.75 for swept wings.
4. **Breguet assumptions** — Constant L/D and SFC during cruise. Real missions have climb, descent, and loiter phases.
5. **Stall speed** — Computed at sea level standard day. Adjust for altitude and non-standard temperature.
