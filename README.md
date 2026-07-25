# 🚀 rocket-tools

> **Engineering-grade aerospace computation. AI-native interface.**

[![Tests](https://img.shields.io/badge/tests-760%20passing-brightgreen)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-87%25-green)](tests/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml)
[![License](https://img.shields.io/badge/license-Apache--2.0-yellow)](LICENSE)

---

## Install & Run in 30 Seconds

```bash
pip install rocket-tools
```

```python
from rocket_tools.materials import material_lookup
from rocket_tools.aerodynamics import dynamic_pressure

# How much pressure does a rocket face at Mach 2.5, sea level?
mat = material_lookup("Inconel-718")
q = dynamic_pressure(velocity=857, altitude_m=0)  # 857 m/s ≈ Mach 2.5
print(f"Dynamic pressure: {q['dynamic_pressure_pa']/1e3:.0f} kPa")
print(f"Inconel-718 yield strength: {mat['yield_strength_mpa']:.0f} MPa")
```

**[→ Features](FEATURES.md)** · **[→ Roadmap](ROADMAP.md)** · **[→ Skills Library](skills/)** · **[→ Quick Start for AI Agents](#for-ai-agents)** · **[→ Contributing](CONTRIBUTING.md)**

---

## What is This?

**rocket-tools** is a Python library of fast aerospace engineering calculations, covering areas like beam deflection, atmospheric properties, material trade studies, and ascent trajectories. It is built for three kinds of people:

- Hobbyists and students designing rockets, drones, or aircraft in Python
- Propulsion and structures engineers who need reliable numbers without opening a full FEM suite
- AI-agent builders who want engineering tools exposed through the [Model Context Protocol](https://modelcontextprotocol.io/) (MCP)

Each tool is self-contained and validated against a published reference, and fast enough to call thousands of times per second. You can use one function on its own or chain several into a design review.

### How it compares

rocket-tools spans many domains at preliminary-design fidelity rather than going deep in one. Reach for it early, when you want a fast, traceable number in code or from an agent; hand off to the specialist tool for a final design. Roughly where it sits:

- **OpenRocket / RASAero** are dedicated rocket flight simulators with a GUI. rocket-tools gives you scriptable Barrowman stability, a point-mass ascent, and recovery sizing at lower fidelity, as part of a broader library.
- **NASA CEA / RPA** do rocket chemical equilibrium. rocket-tools does the ideal nozzle and Isp relations once you supply the gas properties CEA computes; a CEA front end is on the roadmap.
- **NASTRAN / Ansys** are general FEM suites. rocket-tools covers closed-form beams, columns, trusses, plates, and thermal and pressure-vessel stress, not general FEM.
- **GMAT / STK / poliastro** are astrodynamics tools. rocket-tools covers two-body transfers, Lambert, orbit determination, and propagation, without perturbations or ephemerides.

The full table is in [FEATURES.md](FEATURES.md#how-it-compares). The one thing none of those do is expose validated aerospace calculations as MCP tools an AI agent can call and cite.

---

## What Can It Do?

| Capability | What You Get |
|------------|--------------|
| **80 MCP Tools** | Exposed via [FastMCP](https://github.com/modelcontextprotocol/python-sdk) — AI agents can call aerospace computations with structured inputs and validated outputs |
| **49+ Materials** | Aluminum, titanium, steel, nickel superalloys, composites, refractory metals — with thermal & mechanical properties, filterable by application (rocket, drone, aircraft, spacecraft, engine) |
| **Structural Analysis** | Beam bending/deflection/shear, 7 cross-section types, Euler-Johnson column buckling, plate buckling coefficients, margin of safety (stress/load/deflection), von Mises combined stress, 2D/3D truss analysis |
| **Compressible Flow** | Isentropic relations, normal & oblique shocks, Prandtl-Meyer expansions — all Numba JIT-compiled |
| **Aircraft Performance** | Lift curve slope, drag polar with compressibility, Breguet range & endurance, wing loading & stall speed |
| **Rocket Nozzle Design** | Thrust, Isp, thrust coefficient, expansion ratio optimization with under/over-expansion detection |
| **Mission Design** | Tsiolkovsky ΔV, multi-stage staging, orbital velocity, payload fraction, thrust-to-weight, composite CG, propellant tank sizing |
| **Orbital Mechanics** | Hohmann & bi-elliptic transfers, vis-viva speed, plane-change ΔV, Keplerian period, universal-variable Lambert solver, state-vector ↔ classical-orbital-element conversion, and time-of-flight state propagation — validated vs Curtis/Vallado |
| **Aerothermodynamics** | Stagnation & recovery temperature, Sutton-Graves stagnation heat flux, Allen-Eggers ballistic-entry peak deceleration |
| **Propulsion Thermochemistry** | Characteristic velocity c*, ideal specific impulse from pressure ratio, choked throat mass flux (Sutton & Biblarz Ch. 3) |
| **Ascent & Vehicle Sizing** | `simulate_ascent` — fixed-step RK4 ascent through the ISA atmosphere (thrust/drag/gravity) reporting burnout, apogee, max-q, and g-load with time-series; `size_vehicle` chains the rocket equation, thrust-to-weight, and tank sizing. Pinned to the analytic vacuum trajectory (Curtis Ch. 11) |
| **Optimization** | `optimize_staging` — optimal ΔV split across stages (Lagrange multiplier, robust bisection) validated against an independent brute-force optimum; `optimize_design` golden-section optimizes any output of any tool over one variable |
| **Visualization** | `plot_beam_diagrams` (shear/moment/deflection), `plot_drag_polar`, `plot_nozzle_contour`, `plot_isa_profile`, `plot_trajectory` — return a base64 PNG **and** the underlying data series, or a native MCP image (`render="image"`). Optional `viz` extra |
| **Standards & Reliability** | `design_review_report` rolls up margins of safety into a PASS/FAIL verdict with the governing item; `fmea_report` ranks failure modes by RPN (MIL-STD-1629A); `list_standards` + `rocket-tools://standards` catalog the referenced standards |
| **Research Provenance** | `cite_tool` returns the authoritative reference, formula, assumptions, and validation benchmark behind any tool; `list_references` gives the full bibliography — every number is traceable |
| **Uncertainty & Sensitivity** | `propagate_uncertainty` runs Monte-Carlo over any tool with normal/uniform/lognormal/truncated-normal inputs, reporting mean/std/95% CI and a correlation-based ranking of which inputs drive each output |
| **MCP Resources** | Readable datasets an agent can pull as context — `rocket-tools://references`, `://benchmarks`, `://provenance`, `://standards`, `://materials` (+ `://materials/{name}`) |
| **Research Workflows** | `parameter_sweep` trade studies over any input, `list_validation_benchmarks` + `validate_result` so an agent can self-check its numbers against a cited reference |
| **Natural Language Router** | Ask *"What's the Reynolds number at 250 m/s and 5 km?"* and get a validated tool call — no API memorization needed |
| **ISA Atmosphere** | Full 7-layer U.S. Standard Atmosphere 1976, 0–86 km, with ~54 ns cached lookups |
| **Workflow Engine** | Chain tools into reusable YAML workflows for design reviews |
| **ASGI Server** | Production-ready SSE (Server-Sent Events) endpoint with `/health`, `/ready`, and Prometheus `/metrics` |
| **Unit Conversions** | NIST-traceable SI ↔ imperial (psi, psf, ft, in, lbf, mph, knots, Fahrenheit, Rankine) |

**Performance:** All hot paths are Numba JIT-compiled. Every tool runs in under 1 ms.

---

## How to Use It

### 1. As a Python Library

The simplest way — import and compute.

```python
from rocket_tools.structural import beam_analysis, section_properties, column_buckling
from rocket_tools.materials import material_lookup, compare_materials
from rocket_tools.aerodynamics import (
    aero_analysis, mach_number, isentropic_flow, normal_shock, oblique_shock
)
from rocket_tools.design import (
    rocket_delta_v, multi_stage_delta_v, orbital_velocity,
    payload_fraction, propellant_tank_sizing
)
from rocket_tools.utils.units import unit_convert

# --- Structural: design a beam ---
mat = material_lookup("6061-T6")
beam = beam_analysis(
    load=500.0,
    length=2.0,
    youngs_modulus=mat["youngs_modulus_pa"],
    cross_section={"type": "rectangle", "width": 0.05, "height": 0.02},
    load_type="point_midspan",
    support_type="simply_supported",
)
print(f"Deflection: {beam['max_deflection_m']*1000:.2f} mm")
print(f"Bending stress: {beam['bending_stress_pa']/1e6:.1f} MPa")

# --- Cross-section properties ---
section = section_properties("ibeam", flange_width=0.1, height=0.2, flange_thickness=0.01, web_thickness=0.008)
print(f"Ixx = {section['i_xx_m4']:.2e} m⁴")

# --- Column buckling ---
buckling = column_buckling(
    youngs_modulus=mat["youngs_modulus_pa"],
    area_moment=section["i_xx_m4"],
    area=section["area_m2"],
    length=1.5,
    yield_strength=mat["yield_strength_mpa"] * 1e6,
    end_condition="pinned-pinned",
)
print(f"Critical load: {buckling['critical_load_n']:.0f} N ({buckling['regime']})")

# --- Materials: compare alloys for a rocket tank ---
comparison = compare_materials(["2219-T87", "Ti-6Al-4V", "2195"])
for m in comparison:
    print(f"{m['name']}: specific strength = {m['specific_strength']:.0f} m²/s²")

# --- Aerodynamics: full characterization ---
aero = aero_analysis(
    velocity=250.0,
    altitude_m=5000.0,
    characteristic_length=20.0,
    reference_area=40.0,
    lift=50000.0,
    drag=5000.0,
)
print(f"Re = {aero['reynolds_number']:.2e}")
print(f"Mach = {aero['mach_number']:.3f} ({aero['mach_regime']})")
print(f"L/D = {aero['lift_to_drag_ratio']:.1f}")

# --- Compressible flow ---
iso = isentropic_flow(mach=2.5, gamma=1.4)
print(f"P/P0 = {iso['pressure_ratio']:.4f}, T/T0 = {iso['temperature_ratio']:.4f}")

ns = normal_shock(mach1=2.5, gamma=1.4)
print(f"Downstream Mach = {ns['mach_downstream']:.3f}, P2/P1 = {ns['pressure_ratio']:.3f}")

os = oblique_shock(mach1=2.5, deflection_deg=10, gamma=1.4)
print(f"Weak shock angle = {os['wave_angle_deg']:.1f}°")

# --- Rocket mission design ---
dv = rocket_delta_v(specific_impulse_s=320, initial_mass_kg=10000, final_mass_kg=2000)
print(f"Single-stage ΔV = {dv['delta_v_ms']:.0f} m/s")

orb = orbital_velocity(altitude_m=400e3)  # Earth by default
print(f"Circular orbit at 400 km: {orb['circular_velocity_ms']:.0f} m/s")

tank = propellant_tank_sizing(
    propellant_volume_m3=5.0,
    tank_shape="cylinder",
    material_density_kg_m3=4430.0,  # Ti-6Al-4V
)
print(f"Tank mass: {tank['tank_mass_kg']:.1f} kg")

# --- Units: convert anything (returns a dict; take converted_value) ---
unit_convert(14.7, "psi", "Pa")["converted_value"]    # 101352.9...
unit_convert(68, "F", "C")["converted_value"]         # 20.0
unit_convert(100, "mph", "m/s")["converted_value"]    # 44.704
```

**Key concepts:**
- **`material_lookup(name)`** — Fuzzy-matches material names (`"6061"`, `"ti-6al-4v"`, `"inconel 718"` all work). Returns a dict with `youngs_modulus_pa`, `density_kg_m3`, `yield_strength_mpa`, `thermal_conductivity_w_m_k`, and more.
- **`compare_materials([...])`** — Side-by-side trade study sorted by specific strength (strength-to-weight ratio).
- **`beam_analysis(...)`** — Supports rectangle and circle cross-sections, point/distributed/axial loads, and simply-supported/cantilever/fixed-ends boundary conditions.
- **`section_properties(...)`** — 7 shapes: rectangle, hollow_rectangle, circle, hollow_circle, ibeam, cchannel, tsection.
- **`aero_analysis(...)`** — One call returns Reynolds number, Mach number, dynamic pressure, lift coefficient, drag coefficient, and skin friction coefficient.
- **`isentropic_flow(...)`, `normal_shock(...)`, `oblique_shock(...)`** — Compressible flow relations for supersonic/hypersonic analysis.
- **`rocket_delta_v(...)`, `multi_stage_delta_v(...)`** — Tsiolkovsky rocket equation and serial staging.
- **`propellant_tank_sizing(...)`** — Cylindrical, spherical, or ellipsoidal tanks with wall thickness and mass estimates.

### 2. Natural Language Router

If you do not want to memorize function signatures, ask in plain English:

```python
from rocket_tools.router import route_query

# First question
result = route_query("Mach number at 250 m/s and 10,000 m")
print(result.tool_name)      # 'mach_number'
print(result.params)         # {'velocity': 250.0, 'altitude_m': 10000.0}

# Follow-up with session memory
from rocket_tools.memory import SessionMemory
session = SessionMemory(session_id="design-1")
session.parameters["beam_analysis"] = {"load": 1000.0, "length": 1.5}

result = route_query("What is the deflection?", session=session)
print(result.tool_name)      # 'beam_analysis' — inferred from context
```

The router uses regex-based extractors for parameters (velocity, altitude, load, length, etc.) and a lightweight intent classifier to pick the right tool. It handles imperial units (`"10 inch beam"`, `"500 lbf load"`) automatically.

### 3. Workflow Engine

Chain tools into reusable YAML workflows for design reviews:

```yaml
# my_workflow.yaml
name: aero_characterization
steps:
  - id: re
    tool: reynolds_number
    params:
      velocity: "${inputs.velocity}"
      altitude_m: "${inputs.altitude_m}"
      characteristic_length: "${inputs.characteristic_length}"
    save_as: re

  - id: mach
    tool: mach_number
    params:
      velocity: "${inputs.velocity}"
      altitude_m: "${inputs.altitude_m}"
    save_as: mach

  - id: skin_friction
    tool: skin_friction_coefficient
    params:
      reynolds_number: "${re.reynolds_number}"
      flow_regime: "${inputs.flow_regime}"
    save_as: cf
```

Run it:

```python
from rocket_tools.workflows import load_workflow, run_workflow

wf = load_workflow("my_workflow.yaml")
result = run_workflow(wf, {
    "velocity": 100.0,
    "altitude_m": 5000.0,
    "characteristic_length": 2.0,
    "flow_regime": "laminar",
})

print(result["re"]["reynolds_number"])
print(result["mach"]["mach_number"])
print(result["cf"]["skin_friction_coefficient"])
```

Interpolation supports arithmetic (`${re.reynolds_number / 1000}`) and cross-step references. All expressions are evaluated safely via AST — no `eval()`.

### 4. MCP Server

Expose all tools to AI agents via the [Model Context Protocol](https://modelcontextprotocol.io/):

```bash
# Start the MCP server over stdio (for Claude Desktop, Claude Code, etc.)
rocket-tools serve

# Or serve over SSE for web clients
uvicorn rocket_tools.asgi:app --host 0.0.0.0 --port 8000
```

**Add it to Claude Desktop.** Put this in `claude_desktop_config.json`, then restart Claude:

```json
{
  "mcpServers": {
    "rocket-tools": {
      "command": "rocket-tools",
      "args": ["serve"]
    }
  }
}
```

Prefer a zero-install setup? Use [uv](https://docs.astral.sh/uv/) and skip the `pip install`:

```json
{
  "mcpServers": {
    "rocket-tools": {
      "command": "uvx",
      "args": ["rocket-tools", "serve"]
    }
  }
}
```

The config file lives at `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows).

The ASGI app exposes:
- `GET /sse` — MCP Server-Sent Events endpoint
- `GET /health` — Liveness probe
- `GET /ready` — Readiness probe (checks tool registration)
- `GET /metrics` — Prometheus metrics (`rocket_tools_http_requests_total`, `rocket_tools_tool_calls_total`, etc.)

All tool inputs are validated via Pydantic schemas before execution. Errors are structured with `error_code`, `parameter`, `constraint`, and `suggestion` fields.

### 5. Docker Deployment

```bash
docker build -t rocket-tools .
docker run -p 8000:8000 rocket-tools
```

---

## Architecture

```
rocket_tools/
├── schemas/        # Pydantic models for every tool's inputs/outputs
├── utils/          # Units, validation, caching, safe_eval
├── materials/      # 49+ materials + ISA atmosphere
├── structural/     # Beam mechanics, section properties, buckling (Numba JIT)
├── aerodynamics/   # Re, Mach, q, CL, CD, Cf, compressible flow, aircraft perf, nozzle (Numba JIT)
├── design/         # Rocket ΔV, staging, orbital velocity, payload fraction, tank sizing, CG
├── router/         # Natural language intent + parameter extraction
├── memory/         # Session store for contextual conversations
├── workflows/      # YAML workflow engine + safe interpolation
├── config.py       # pydantic-settings configuration (ROCKET_* env vars)
├── server.py       # FastMCP tool definitions with schema validation
├── asgi.py         # Production SSE + health/metrics endpoints
└── rust_kernels/   # Experimental Rust/PyO3 kernels — compiles; NOT in the wheel (see its README)
```

**Numba JIT** accelerates all hot paths.
**Pydantic schemas** validate every tool input.
**Structured errors** tell you exactly what went wrong and how to fix it.

---

## Skills Library

Human-readable engineering references in `skills/`:

- [`skills/structural-analysis.md`](skills/structural-analysis.md) — Beam theory, Euler buckling, section properties
- [`skills/aerodynamics.md`](skills/aerodynamics.md) — Reynolds, Mach, dynamic pressure, lift/drag, compressible flow
- [`skills/units.md`](skills/units.md) — Supported units, conversion reference, temperature handling
- [`skills/schemas.md`](skills/schemas.md) — Pydantic model reference for all tools
- [`skills/router.md`](skills/router.md) — Intent classification, confidence scoring, session memory

Each skill includes formulas, MCP tool cross-references, worked Python examples, and common pitfalls.

---

## Roadmap

Done through 0.4.0: the core tool set with tests and benchmarks, the natural-language router, YAML workflows, uncertainty propagation, and provenance. Version 0.4.0 added ascent trajectory simulation and vehicle sizing, the visualization tools, optimal staging and a general design optimizer, and the standards and reliability reports (design review, FMEA).

Planned next:

- Native acceleration wheels (Rust/PyO3 via maturin) with a pure-Python fallback, so the fast path installs without a build step.
- Adaptive-step and multi-stage trajectory integration, plus a 3-DOF option.
- Finish the reference re-derivation of the remaining aircraft-aerodynamics tools and tighten the ISA tolerance bands.
- An optional LLM-backed router as an alternative to the current regex intent classifier.

---

## Contributing

We welcome contributions. See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development environment setup
- Running the test suite
- Code style (ruff, mypy)
- Adding new materials
- Adding new tools
- Pull request process

Quick start for contributors:

```bash
git clone https://github.com/benajaero/rocket-tools.git
cd rocket-tools
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -v                    # 240 tests
pytest --benchmark-only -v   # 18 benchmarks
ruff check src/ tests/       # lint
mypy src/rocket_tools/       # type check
```

---

## License and attribution

rocket-tools is released under the [Apache License 2.0](LICENSE).

**Attribution is required.** Any use, modification, or redistribution must credit both
**Chukwudiebube E. Ajaero** and **Human Engine Labs** as the original authors, and must preserve the
[NOTICE](NOTICE) file. This applies to using rocket-tools within, or as a dependency or component
of, any other project, product, service, or published work. Where an "about", "credits",
"acknowledgements", or documentation section exists, put the credit there.

When you use rocket-tools in research or a published work, please also cite it
(see [CITATION.cff](CITATION.cff)).

---

*Built by [Human Engine labs](https://www.humanengine.co/) for the agentic era.*

---

<!-- AGENT-MANIFEST-START -->
<!-- The following section is structured for AI agent discovery. Human readers can safely ignore. -->

## For AI Agents

### MCP Tool Manifest

This repository exposes 80 tools via FastMCP. The key ones by domain are below; for the
complete, always-current list run `rocket-tools tools`.

#### Structural Analysis
| Tool | Schema | Description |
|------|--------|-------------|
| `beam_analysis` | `BeamAnalysisInput` | Structural beam analysis with bending, deflection, shear, buckling |
| `section_properties` | `SectionPropertiesInput` | Cross-section properties for 7 shapes (I-beam, C-channel, T-section, etc.) |
| `column_buckling` | `ColumnBucklingInput` | Euler-Johnson column buckling with effective length factors |
| `plate_buckling_coefficient` | `PlateBucklingInput` | Buckling coefficient k for plates under compression, shear, or bending |
| `margin_of_safety` | `MarginOfSafetyInput` | Aerospace margin of safety: MS = (Allowable / (FOS × Actual)) − 1 |
| `von_mises_stress` | `VonMisesInput` | Von Mises equivalent stress and principal stresses for combined loading |
| `combined_margin_of_safety` | `CombinedMarginInput` | Margin of safety for combined stress states using von Mises |
| `deflection_margin` | `DeflectionMarginInput` | Margin of safety against deflection limits (L/360, L/500, etc.) |
| `truss_analysis` | `TrussAnalysisInput` | 2D/3D pin-jointed truss analysis via direct stiffness method |
| `thermal_stress` | `ThermalStressInput` | Thermal stress and free/restrained expansion of a heated or cooled member |
| `pressure_vessel_stress` | `PressureVesselStressInput` | Thin-wall hoop/longitudinal/von Mises stress and margin for a pressurized cylinder or sphere |

#### Aerodynamics
| Tool | Schema | Description |
|------|--------|-------------|
| `aero_analysis` | `AeroAnalysisInput` | Comprehensive aerodynamic characterization (Re, Mach, q, CL, CD, Cf) |
| `reynolds_number` | `ReynoldsNumberInput` | Reynolds number from velocity, altitude, and characteristic length |
| `mach_number` | `MachNumberInput` | Mach number at altitude |
| `dynamic_pressure` | `DynamicPressureInput` | Dynamic pressure q = ½ρV² |
| `lift_coefficient` | `LiftCoefficientInput` | CL from lift, velocity, altitude, area |
| `drag_coefficient` | `DragCoefficientInput` | CD from drag, velocity, altitude, area |
| `skin_friction_coefficient` | `SkinFrictionInput` | Blasius skin friction (laminar / turbulent) |

#### Compressible Flow
| Tool | Schema | Description |
|------|--------|-------------|
| `isentropic_flow` | `IsentropicFlowInput` | Isentropic relations: T/T0, P/P0, ρ/ρ0, A/A* |
| `normal_shock` | `NormalShockInput` | Normal shock relations: downstream Mach, pressure/temperature/density ratios |
| `oblique_shock` | `ObliqueShockInput` | Oblique shock wave angle for weak/strong solutions |
| `prandtl_meyer` | `PrandtlMeyerInput` | Prandtl-Meyer expansion angle from Mach number |
| `prandtl_meyer_from_angle` | `PrandtlMeyerInverseInput` | Mach number from Prandtl-Meyer expansion angle |

#### Aircraft Performance
| Tool | Schema | Description |
|------|--------|-------------|
| `lift_curve_slope` | `LiftCurveSlopeInput` | Subsonic/supersonic lift curve slope a = dCL/dα |
| `drag_polar` | `DragPolarInput` | Drag coefficient with compressibility and wave drag |
| `breguet_range` | `BreguetRangeInput` | Breguet range equation for jet and propeller aircraft |
| `breguet_endurance` | `BreguetEnduranceInput` | Breguet endurance equation |
| `wing_loading` | `WingLoadingInput` | Wing loading W/S with stall speed estimate |

#### Static Stability
| Tool | Schema | Description |
|------|--------|-------------|
| `center_of_pressure` | `CenterOfPressureInput` | Subsonic center of pressure of a fin-stabilized rocket (Barrowman method) |
| `static_margin` | `StaticMarginInput` | Static margin in calibers from CP, CG, and reference diameter |

#### Rocket Nozzle Design
| Tool | Schema | Description |
|------|--------|-------------|
| `nozzle_performance` | `NozzlePerformanceInput` | Thrust, Isp, thrust coefficient, expansion state |
| `optimal_area_ratio` | `OptimalAreaRatioInput` | Optimal A/A* for matched expansion to ambient pressure |
| `motor_thrust_curve_analysis` | `MotorThrustCurveInput` | Total impulse, burn time, avg/peak thrust, delivered Isp, and NAR class from a thrust-time curve |

#### Mission Design
| Tool | Schema | Description |
|------|--------|-------------|
| `rocket_delta_v` | `RocketDeltaVInput` | Tsiolkovsky rocket equation ΔV |
| `multi_stage_delta_v` | `MultiStageDeltaVInput` | Serial multi-stage rocket ΔV with mass ratios |
| `orbital_velocity` | `OrbitalVelocityInput` | Circular and escape velocity for planets |
| `payload_fraction` | `PayloadFractionInput` | Mission payload fraction from ΔV, Isp, and inert mass fraction |
| `thrust_to_weight` | `ThrustToWeightInput` | Thrust-to-weight ratio with hover/climb capability |
| `composite_cg` | `CompositeCGInput` | Center of gravity and mass moments for composite bodies |
| `propellant_tank_sizing` | `PropellantTankSizingInput` | Tank mass, wall thickness, and dimensions for cylinder/sphere/ellipsoid |
| `bi_elliptic_transfer` | `BiEllipticTransferInput` | Three-impulse bi-elliptic transfer between circular orbits, compared against Hohmann |
| `lambert_solver` | `LambertSolverInput` | Two-body Lambert problem: transfer-orbit velocities from two positions and a time of flight |
| `orbital_elements_from_state` | `OrbitalElementsFromStateInput` | Classical orbital elements (a, e, i, RAAN, ω, θ) from a position/velocity state vector |
| `state_from_orbital_elements` | `StateFromOrbitalElementsInput` | Inertial position/velocity state vector from classical orbital elements (inverse) |
| `kepler_propagate` | `KeplerPropagateInput` | Propagate a state vector forward/backward in time on its two-body orbit (universal variables) |

#### Trajectory & Vehicle Sizing
| Tool | Schema | Description |
|------|--------|-------------|
| `simulate_ascent` | `AscentSimInput` | RK4 ascent through the ISA atmosphere; burnout, apogee, max-q, g-load, time-series |
| `size_vehicle` | `VehicleSizingInput` | Preliminary mass sizing from a ΔV budget (chains rocket equation, T/W, tank sizing) |
| `parachute_descent_rate` | `ParachuteDescentInput` | Terminal descent rate and landing energy under a round parachute |
| `parachute_area_for_descent_rate` | `ParachuteAreaInput` | Canopy area/diameter needed for a target landing speed |

#### Optimization
| Tool | Schema | Description |
|------|--------|-------------|
| `optimize_staging` | `StagingOptimizerInput` | Payload-maximizing ΔV split across stages (Lagrange multiplier) |
| `optimize_design` | `DesignOptimizerInput` | Golden-section optimize any output of any tool over one variable |

#### Visualization (optional `viz` extra)
| Tool | Schema | Description |
|------|--------|-------------|
| `plot_beam_diagrams` | `BeamDiagramInput` | Shear/moment/deflection diagrams (base64 PNG + data, or native MCP image) |
| `plot_drag_polar` | `DragPolarPlotInput` | Drag polar and L/D curve |
| `plot_nozzle_contour` | `NozzleContourInput` | Convergent-divergent nozzle wall contour |
| `plot_isa_profile` | `ISAProfileInput` | Temperature, pressure, and density vs altitude |
| `plot_trajectory` | `TrajectoryPlotInput` | Altitude, velocity, dynamic pressure, and g-load vs time |

#### Standards & Reliability
| Tool | Schema | Description |
|------|--------|-------------|
| `design_review_report` | `DesignReviewInput` | Margin-of-safety rollup with the governing margin and a PASS/FAIL verdict |
| `fmea_report` | `FMEAInput` | Rank failure modes by RPN = Severity × Occurrence × Detection |
| `list_standards` | — | Catalog of referenced aerospace design standards |

#### Materials & Utilities
| Tool | Schema | Description |
|------|--------|-------------|
| `material_lookup` | `MaterialLookupInput` | Look up 49+ aerospace materials by name |
| `isa_atmosphere` | `ISAAtmosphereInput` | Standard atmosphere properties 0–86 km (7-layer US Std Atm 1976) |
| `unit_convert` | `UnitConvertInput` | NIST-traceable unit conversion |

### ASGI Deployment

```bash
uvicorn rocket_tools.asgi:app --host 0.0.0.0 --port 8000
```

Endpoints:
- `GET /sse` — MCP SSE transport
- `GET /health` — `{"status": "ok", "version": "0.3.3"}`
- `GET /ready` — `{"status": "ready", "tools": 35}`
- `GET /metrics` — Prometheus metrics

### Natural Language Routing

```python
from rocket_tools.router import route_query
result = route_query("Calculate Reynolds number at 100 m/s, 5000 m, length 2 m")
# result.tool_name == 'reynolds_number'
# result.params == {'velocity': 100.0, 'altitude_m': 5000.0, 'characteristic_length': 2.0}
```

### Schema Files

- `src/rocket_tools/schemas/structural.py` — Beam, section, and buckling schemas
- `src/rocket_tools/schemas/aerodynamics.py` — Aerodynamics, compressible flow, aircraft, and nozzle schemas
- `src/rocket_tools/schemas/materials.py` — Materials & unit conversion schemas
- `src/rocket_tools/schemas/design.py` — Mission design and performance schemas

<!-- AGENT-MANIFEST-END -->
