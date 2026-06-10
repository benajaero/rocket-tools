---
title: Rocket Nozzle Design
skill_type: engineering
layer: aerodynamics
tools:
  - nozzle_performance
  - optimal_area_ratio
  - isentropic_flow
  - unit_convert
version: 0.3.2
---

# Rocket Nozzle Design

Engineering skill for convergent-divergent (De Laval) rocket nozzle analysis.

## When to Use

- Sizing rocket nozzle throat and exit areas
- Computing thrust, Isp, and thrust coefficient
- Checking expansion state (optimal / underexpanded / overexpanded)
- Designing for specific altitude (sea level vs vacuum)
- Comparing propellant performance

## Key Concepts

### Nozzle Flow Basics

Rocket nozzles accelerate hot gas from chamber conditions to supersonic exit velocities. The flow is assumed:
- Steady, one-dimensional
- Isentropic (except across shocks)
- Calorically perfect gas

### Critical (Throat) Conditions

At the throat (M = 1):

$$ \frac{P^*}{P_0} = \left(\frac{2}{\gamma + 1}\right)^{\frac{\gamma}{\gamma - 1}} $$

$$ \frac{T^*}{T_0} = \frac{2}{\gamma + 1} $$

### Thrust Equation

$$ F = \dot{m} V_e + (P_e - P_a) A_e $$

Where:
- $\dot{m}$ = mass flow rate (kg/s)
- $V_e$ = exit velocity (m/s)
- $P_e$ = exit pressure (Pa)
- $P_a$ = ambient pressure (Pa)
- $A_e$ = exit area (m²)

### Thrust Coefficient

$$ C_F = \frac{F}{P_0 A^*} $$

Where $P_0$ = chamber pressure and $A^*$ = throat area.

### Specific Impulse

$$ I_{sp} = \frac{F}{\dot{m} g_0} = \frac{V_{eq}}{g_0} $$

Where $V_{eq} = V_e + \frac{(P_e - P_a)A_e}{\dot{m}}$ is the equivalent exhaust velocity.

### Characteristic Velocity

$$ c^* = \frac{P_0 A^*}{\dot{m}} = \frac{\sqrt{\gamma R T_0}}{\gamma \sqrt{\left(\frac{2}{\gamma + 1}\right)^{\frac{\gamma + 1}{\gamma - 1}}}} $$

A figure of merit for propellant combustion efficiency, independent of nozzle geometry.

### Expansion State

| Condition | Definition | Effect |
|-----------|------------|--------|
| **Optimal** | $P_e \approx P_a$ | Maximum thrust, no divergence loss |
| **Underexpanded** | $P_e > P_a$ | Thrust loss from unexpanded gas |
| **Overexpanded** | $P_e < P_a$ | Flow separation, side loads, thrust loss |

### Optimal Area Ratio

For matched expansion ($P_e = P_a$), solve for exit Mach from:

$$ \frac{P_0}{P_a} = \left(1 + \frac{\gamma - 1}{2} M_e^2\right)^{\frac{\gamma}{\gamma - 1}} $$

Then compute $A_e/A^*$ from the area-Mach relation.

## MCP Tool Reference

### `nozzle_performance`

Analyze full nozzle performance from chamber to exit.

**Parameters (schema: `NozzlePerformanceInput`):**
- `chamber_pressure_pa` — Chamber total pressure (`> 0`)
- `chamber_temperature_k` — Chamber total temperature (`> 0`)
- `ambient_pressure_pa` — Back pressure (`> 0`)
- `throat_area_m2` — Throat area (`> 0`)
- `exit_area_m2` — Exit area (`≥ throat_area`)
- `gamma` — Ratio of specific heats (default 1.4)
- `molecular_weight` — Exhaust gas molecular weight in kg/kmol (default 28.97)

**Returns:**
- `thrust_n`, `thrust_kn`
- `thrust_coefficient_cf`
- `specific_impulse_s`, `specific_impulse_ms`
- `characteristic_velocity_ms`
- `mass_flow_rate_kg_s`
- `exit_mach`, `exit_pressure_pa`, `exit_temperature_k`, `exit_velocity_ms`
- `area_ratio`, `expansion_state` (`"optimal"`, `"underexpanded"`, `"overexpanded"`)

### `optimal_area_ratio`

Compute the optimal A/A* for matched expansion.

**Parameters (schema: `OptimalAreaRatioInput`):**
- `chamber_pressure_pa` — (`> 0`)
- `ambient_pressure_pa` — (`> 0`, `< chamber_pressure`)
- `gamma` — Default 1.4

**Returns:** `optimal_exit_mach`, `optimal_area_ratio`, `pressure_ratio`

## Worked Example: Sea-Level Nozzle

**Problem:** A rocket engine with $P_0$ = 7 MPa, $T_0$ = 3300 K, throat area = 0.05 m², exit area = 0.5 m², γ = 1.2, MW = 22 kg/kmol. Operating at sea level ($P_a$ = 101.3 kPa). Find thrust, Isp, and expansion state.

**Solution:**
```python
from rocket_tools.aerodynamics import nozzle_performance

result = nozzle_performance(
    chamber_pressure_pa=7e6,
    chamber_temperature_k=3300,
    ambient_pressure_pa=101325,
    throat_area_m2=0.05,
    exit_area_m2=0.5,
    gamma=1.2,
    molecular_weight=22.0,
)
print(f"Thrust = {result['thrust_kn']:.1f} kN")
print(f"Isp = {result['specific_impulse_s']:.1f} s")
print(f"Cf = {result['thrust_coefficient_cf']:.3f}")
print(f"Expansion state: {result['expansion_state']}")
print(f"Exit Mach = {result['exit_mach']:.2f}")
```

## Worked Example: Vacuum-Optimized Nozzle

**Problem:** Same engine, but operating in vacuum ($P_a$ ≈ 0). What is the optimal area ratio for matched expansion?

**Solution:**
```python
from rocket_tools.aerodynamics import optimal_area_ratio

# Use a very low ambient pressure for vacuum
result = optimal_area_ratio(
    chamber_pressure_pa=7e6,
    ambient_pressure_pa=100,  # Near-vacuum
    gamma=1.2,
)
print(f"Optimal A/A* = {result['optimal_area_ratio']:.1f}")
print(f"Exit Mach = {result['optimal_exit_mach']:.2f}")
```

## Worked Example: Compare Expansion States

**Problem:** Compare the same nozzle at sea level, 10 km, and 20 km altitude.

**Solution:**
```python
from rocket_tools.aerodynamics import nozzle_performance
from rocket_tools.materials import isa_atmosphere

altitudes = [0, 10000, 20000]
for alt in altitudes:
    isa = isa_atmosphere(alt)
    result = nozzle_performance(
        chamber_pressure_pa=7e6,
        chamber_temperature_k=3300,
        ambient_pressure_pa=isa['pressure_pa'],
        throat_area_m2=0.05,
        exit_area_m2=0.5,
        gamma=1.2,
        molecular_weight=22.0,
    )
    print(f"Alt {alt/1000:.0f} km: {result['expansion_state']}, "
          f"Thrust = {result['thrust_kn']:.1f} kN, "
          f"Isp = {result['specific_impulse_s']:.1f} s")
```

## Common Pitfalls

1. **Molecular weight units** — kg/kmol (same as g/mol). Air = 28.97, LOX/LH2 exhaust ≈ 10–16, LOX/RP-1 ≈ 20–24.
2. **Gamma for hot gas** — γ decreases with temperature. Typical: 1.2–1.3 for combustion products, 1.4 for cold air.
3. **Overexpansion at sea level** — Large area ratios designed for vacuum will separate at sea level, causing dangerous side loads.
4. **Altitude compensation** — Nozzle with fixed geometry is a compromise. Aerospikes and dual-bell nozzles attempt altitude compensation.
5. **c* independence** — $c^*$ depends only on chamber conditions and propellant chemistry, not on nozzle geometry. It measures combustion efficiency.
