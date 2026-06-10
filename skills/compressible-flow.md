---
title: Compressible Flow
skill_type: engineering
layer: aerodynamics
tools:
  - isentropic_flow
  - normal_shock
  - oblique_shock
  - prandtl_meyer
  - prandtl_meyer_from_angle
version: 0.3.2
---

# Compressible Flow

Engineering skill for supersonic and hypersonic flow analysis. All relations assume a calorically perfect gas with constant specific heat ratio $\gamma$.

## When to Use

- Rocket nozzle design (convergent-divergent flow)
- Supersonic aircraft intake analysis
- Wind tunnel calibration
- Spacecraft re-entry aerothermodynamics
- Missile aerodynamics

## Key Concepts

### Isentropic Flow Relations

For isentropic flow of a perfect gas:

$$ \frac{T}{T_0} = \left(1 + \frac{\gamma - 1}{2} M^2\right)^{-1} $$

$$ \frac{P}{P_0} = \left(1 + \frac{\gamma - 1}{2} M^2\right)^{-\frac{\gamma}{\gamma - 1}} $$

$$ \frac{\rho}{\rho_0} = \left(1 + \frac{\gamma - 1}{2} M^2\right)^{-\frac{1}{\gamma - 1}} $$

$$ \frac{A}{A^*} = \frac{1}{M} \left(\frac{2}{\gamma + 1} \left(1 + \frac{\gamma - 1}{2} M^2\right)\right)^{\frac{\gamma + 1}{2(\gamma - 1)}} $$

Where $T_0$, $P_0$, $\rho_0$ are stagnation conditions and $A^*$ is the sonic throat area.

### Normal Shock Relations

Across a normal shock ($M_1 > 1$):

$$ M_2 = \sqrt{\frac{1 + \frac{\gamma - 1}{2} M_1^2}{\gamma M_1^2 - \frac{\gamma - 1}{2}}} $$

$$ \frac{P_2}{P_1} = 1 + \frac{2\gamma}{\gamma + 1}(M_1^2 - 1) $$

$$ \frac{\rho_2}{\rho_1} = \frac{(\gamma + 1) M_1^2}{2 + (\gamma - 1) M_1^2} $$

### Oblique Shock Relations

For a weak oblique shock with deflection angle $\theta$:

$$ \tan\theta = 2\cot\beta \frac{M_1^2 \sin^2\beta - 1}{M_1^2(\gamma + \cos 2\beta) + 2} $$

Where $\beta$ is the shock wave angle. The downstream Mach number is:

$$ M_2 = \frac{M_{n2}}{\sin(\beta - \theta)} $$

Where $M_{n1} = M_1 \sin\beta$ and $M_{n2}$ is computed from normal shock relations.

### Prandtl-Meyer Expansion

The Prandtl-Meyer function gives the total turning angle through an expansion fan:

$$ \nu(M) = \sqrt{\frac{\gamma + 1}{\gamma - 1}} \arctan\sqrt{\frac{\gamma - 1}{\gamma + 1}(M^2 - 1)} - \arctan\sqrt{M^2 - 1} $$

For $M \geq 1$. The turning angle from $M_1$ to $M_2$ is $\Delta\theta = \nu(M_2) - \nu(M_1)$.

## MCP Tool Reference

### `isentropic_flow`

Compute isentropic ratios for a given Mach number.

**Parameters (schema: `IsentropicFlowInput`):**
- `mach` — Mach number (`> 0`)
- `gamma` — Ratio of specific heats (default 1.4)

**Returns:** `temperature_ratio` (T/T₀), `pressure_ratio` (P/P₀), `density_ratio` (ρ/ρ₀), `area_ratio` (A/A*), `dynamic_pressure_ratio`, `mach_angle_deg` (if supersonic)

### `normal_shock`

Compute normal shock relations.

**Parameters (schema: `NormalShockInput`):**
- `mach1` — Upstream Mach number (`> 1`)
- `gamma` — Default 1.4

**Returns:** `mach_downstream`, `pressure_ratio`, `density_ratio`, `temperature_ratio`, `stagnation_pressure_ratio`

### `oblique_shock`

Compute weak oblique shock relations.

**Parameters (schema: `ObliqueShockInput`):**
- `mach1` — Upstream Mach (`> 1`)
- `deflection_deg` — Flow deflection angle in degrees (`0 < θ < 90`)
- `gamma` — Default 1.4

**Returns:** `mach_downstream`, `wave_angle_deg`, `pressure_ratio`, `density_ratio`, `temperature_ratio`

### `prandtl_meyer`

Compute Prandtl-Meyer expansion angle from Mach number.

**Parameters:** `mach` (`≥ 1`), `gamma`

**Returns:** `prandtl_meyer_angle_deg`, `prandtl_meyer_angle_rad`

### `prandtl_meyer_from_angle`

Inverse: compute Mach number from Prandtl-Meyer angle.

**Parameters:** `angle_deg` (`≥ 0`), `gamma`

**Returns:** `mach`, `prandtl_meyer_angle_deg`

## Worked Example: Rocket Nozzle Flow

**Problem:** A rocket nozzle expands exhaust from Mach 1 (throat) to Mach 3.5. Chamber pressure = 5 MPa, γ = 1.2 (combustion products). Find exit pressure and area ratio.

**Solution:**
```python
from rocket_tools.aerodynamics import isentropic_flow

result = isentropic_flow(mach=3.5, gamma=1.2)
print(f"P/P0 = {result['pressure_ratio']:.4f}")
print(f"A/A* = {result['area_ratio']:.4f}")

p_exit = 5e6 * result['pressure_ratio']
print(f"Exit pressure = {p_exit/1e3:.1f} kPa")
```

## Worked Example: Normal Shock in Intake

**Problem:** A supersonic intake encounters a normal shock at Mach 2.2. Find downstream Mach and stagnation pressure loss.

**Solution:**
```python
from rocket_tools.aerodynamics import normal_shock

result = normal_shock(mach1=2.2, gamma=1.4)
print(f"Downstream Mach = {result['mach_downstream']:.3f}")
print(f"P2/P1 = {result['pressure_ratio']:.3f}")
print(f"P02/P01 = {result['stagnation_pressure_ratio']:.4f}")
print(f"Stagnation pressure loss = {(1 - result['stagnation_pressure_ratio'])*100:.1f}%")
```

## Worked Example: Oblique Shock on Wedge

**Problem:** A 15° wedge at Mach 2.5. Find shock angle and downstream Mach.

**Solution:**
```python
from rocket_tools.aerodynamics import oblique_shock

result = oblique_shock(mach1=2.5, deflection_deg=15, gamma=1.4)
print(f"Shock angle = {result['wave_angle_deg']:.1f}°")
print(f"Downstream Mach = {result['mach_downstream']:.3f}")
print(f"P2/P1 = {result['pressure_ratio']:.3f}")
```

## Worked Example: Expansion Fan

**Problem:** Flow at Mach 2.0 turns around a 10° corner. Find the final Mach number.

**Solution:**
```python
from rocket_tools.aerodynamics import prandtl_meyer, prandtl_meyer_from_angle

# Initial expansion angle
nu1 = prandtl_meyer(mach=2.0, gamma=1.4)
print(f"nu(M=2.0) = {nu1['prandtl_meyer_angle_deg']:.2f}°")

# After 10° turn
nu2 = nu1['prandtl_meyer_angle_deg'] + 10
result = prandtl_meyer_from_angle(angle_deg=nu2, gamma=1.4)
print(f"Final Mach = {result['mach']:.3f}")
```

## Common Pitfalls

1. **Gamma selection** — Air: γ = 1.4. Combustion products: γ ≈ 1.2–1.3. Hot gas: γ decreases with temperature.
2. **Normal shock limitation** — `mach1` must be > 1. Subsonic shocks are not physically meaningful.
3. **Oblique shock strong solution** — The tool returns the weak shock solution only. Strong solutions (β > 45°) are rarely relevant for external aerodynamics.
4. **Area ratio ambiguity** — A/A* has two solutions (subsonic and supersonic) for a given ratio. The tool returns the supersonic branch.
5. **Prandtl-Meyer range** — Valid only for M ≥ 1. Subsonic flow cannot sustain expansion fans.
