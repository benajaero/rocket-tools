# 🚀 rocket-tools

Fast, reference-validated aerospace engineering calculations, from beam deflection to
atmospheric properties to a full ascent simulation. One shared core, reachable three ways:

- a plain Python library,
- a `rocket-tools` command line, and
- an MCP server, so an AI agent can call the same validated calculations with structured
  inputs and outputs.

Every tool is checked against a published reference (NACA 1135, Anderson, Sutton & Biblarz,
Curtis, Vallado, Roark), carries provenance you can query with `cite_tool`, and rejects
non-finite inputs at the schema boundary.

## Install

```bash
pip install rocket-tools          # core (pure Python + Numba)
pip install "rocket-tools[viz]"   # adds matplotlib for the plotting tools
```

## A 30-second example

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

| Domain | What you get |
|--------|--------------|
| Structures | Beam bending, shear, and deflection; 7 section types; Euler-Johnson buckling; plate buckling; margins of safety; von Mises; 2D and 3D truss; thermal and pressure-vessel stress |
| Aerodynamics | Reynolds, Mach, dynamic pressure; isentropic, normal and oblique shock, Prandtl-Meyer; aircraft performance; nozzle design |
| Propulsion and mission | Rocket equation and staging; c* and specific impulse; motor thrust-curve analysis; orbital mechanics; aerothermodynamics |
| Ascent and sizing | `simulate_ascent` (RK4 through the ISA atmosphere), `size_vehicle`, parachute recovery sizing |
| Orbital mechanics | Hohmann and bi-elliptic transfers, Lambert solver, state-vector and orbital-element conversion, Kepler propagation |
| Optimization | `optimize_staging` for the optimal delta-v split, `optimize_design` over any tool and variable |
| Visualization | Beam, drag-polar, nozzle, ISA, and trajectory plots, as data or a native MCP image |
| Standards and reliability | Design-review margin rollups, FMEA by risk priority number, a standards catalog |
| Research support | Provenance and citations, Monte-Carlo uncertainty and sensitivity, curated benchmarks, parameter sweeps |

For the full tool reference see the [README on GitHub](https://github.com/benajaero/rocket-tools)
and the [feature list](https://github.com/benajaero/rocket-tools/blob/main/FEATURES.md). The
[roadmap](https://github.com/benajaero/rocket-tools/blob/main/ROADMAP.md) covers what is
coming next, and [scientific validity](scientific-validity.md) is honest about the
validation scope and the known limits.

!!! warning "Not certification software"
    These are preliminary engineering calculations for design exploration, education, and
    agent integration. They are not certification artifacts, and a qualified engineer should
    check any result before it informs a real design or flight.
