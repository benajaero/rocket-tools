# 🚀 rocket-tools

> **Engineering-grade aerospace computation. AI-native interface.**

**rocket-tools** gives you fast, precise, *reference-validated* aerospace engineering
calculations — from beam deflection to atmospheric properties to full ascent
simulation — through three surfaces from one shared core:

- a plain **Python library**,
- a **`rocket-tools` CLI**, and
- an **MCP server** so AI agents can call validated aerospace computations with
  structured inputs and outputs.

Every tool is validated against published references (NACA 1135, Anderson, Sutton &
Biblarz, Curtis/Vallado, Roark), carries provenance you can query with `cite_tool`,
and rejects unsafe/non-finite inputs at the schema boundary.

## Install

```bash
pip install rocket-tools          # core (pure Python + Numba)
pip install "rocket-tools[viz]"   # + matplotlib for the plotting tools
```

## 30-second example

```python
from rocket_tools.trajectory import simulate_ascent

sim = simulate_ascent(
    initial_mass_kg=1000.0, dry_mass_kg=400.0,
    specific_impulse_s=250.0, mass_flow_rate_kg_s=20.0,
    reference_area_m2=0.2,
)
print(f"Apogee: {sim['apogee_km']:.1f} km, max-q {sim['max_dynamic_pressure_pa']/1e3:.0f} kPa")
```

## What's inside

| Domain | Highlights |
|--------|-----------|
| **Structures** | Beam bending/shear/deflection, 7 section types, Euler-Johnson buckling, plate buckling, margins, von Mises, 2D/3D truss |
| **Aerodynamics** | Reynolds/Mach/q, isentropic + normal/oblique shock + Prandtl-Meyer, aircraft performance, nozzle design (Numba-JIT) |
| **Propulsion & mission** | Tsiolkovsky ΔV, multi-stage, c*/Isp, orbital mechanics, aerothermodynamics |
| **Ascent & sizing** | `simulate_ascent` (RK4 through the ISA atmosphere), `size_vehicle` |
| **Optimization** | `optimize_staging` (optimal ΔV split), `optimize_design` (any tool, any variable) |
| **Visualization** | Beam/drag-polar/nozzle/ISA/trajectory plots — data **or** native MCP image |
| **Standards & reliability** | Design-review margin rollups, FMEA (RPN), standards catalog |
| **Research** | Provenance/citations, Monte-Carlo uncertainty + sensitivity, curated benchmarks, parameter sweeps |

See the [README on GitHub](https://github.com/benajaero/rocket-tools) for the full tool
reference and the [Skills library](https://github.com/benajaero/rocket-tools/tree/main/skills)
for worked examples, and [Scientific Validity](scientific-validity.md) for the validation
scope and known limitations.

!!! warning "Not certification software"
    Results are preliminary engineering calculations for design exploration, education,
    and agent/tool integration — **not** certification artifacts. Independent verification
    by a qualified engineer is required.
