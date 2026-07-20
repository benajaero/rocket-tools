# 🚀 rocket-tools

> **Engineering-grade aerospace computation. AI-native interface.**

[![Tests](https://img.shields.io/badge/tests-343%20passing-brightgreen)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-77%25-green)](tests/)
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

**[→ Skills Library](skills/)** · **[→ Quick Start for AI Agents](#for-ai-agents)** · **[→ Contributing](CONTRIBUTING.md)**

---

## What is This?

**rocket-tools** is a Python library that gives you fast, precise aerospace engineering calculations — from beam deflection to atmospheric properties to material trade studies. It is built for three kinds of people:

- **Hobbyists & students** designing rockets, drones, or aircraft in Python
- **Propulsion & structures engineers** who need reliable numbers without opening a full FEM suite
- **AI-agent builders** who want engineering tools exposed through the [Model Context Protocol](https://modelcontextprotocol.io/) (MCP)

Unlike monolithic engineering suites, rocket-tools is **composable**: each tool is self-contained, validated, and fast enough to call thousands of times per second. Use one function or chain them into full design reviews.

---

## What Can It Do?

| Capability | What You Get |
|------------|--------------|
| **47 MCP Tools** | Exposed via [FastMCP](https://github.com/modelcontextprotocol/python-sdk) — AI agents can call aerospace computations with structured inputs and validated outputs |
| **49+ Materials** | Aluminum, titanium, steel, nickel superalloys, composites, refractory metals — with thermal & mechanical properties, filterable by application (rocket, drone, aircraft, spacecraft, engine) |
| **Structural Analysis** | Beam bending/deflection/shear, 7 cross-section types, Euler-Johnson column buckling, plate buckling coefficients, margin of safety (stress/load/deflection), von Mises combined stress, 2D/3D truss analysis |
| **Compressible Flow** | Isentropic relations, normal & oblique shocks, Prandtl-Meyer expansions — all Numba JIT-compiled |
| **Aircraft Performance** | Lift curve slope, drag polar with compressibility, Breguet range & endurance, wing loading & stall speed |
| **Rocket Nozzle Design** | Thrust, Isp, thrust coefficient, expansion ratio optimization with under/over-expansion detection |
| **Mission Design** | Tsiolkovsky ΔV, multi-stage staging, orbital velocity, payload fraction, thrust-to-weight, composite CG, propellant tank sizing |
| **Orbital Mechanics** | Hohmann transfers, vis-viva speed, plane-change ΔV, Keplerian period — validated vs Curtis/Vallado |
| **Aerothermodynamics** | Stagnation & recovery temperature, Sutton-Graves stagnation heat flux, Allen-Eggers ballistic-entry peak deceleration |
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
from rocket_tools.utils.units import convert

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
section = section_properties("ibeam", width=0.1, height=0.2, flange_thickness=0.01, web_thickness=0.008)
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
print(f"Critical load: {buckling['critical_load_n']:.0f} N ({buckling['failure_mode']})")

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
print(f"Downstream Mach = {ns['mach2']:.3f}, P2/P1 = {ns['pressure_ratio']:.3f}")

os = oblique_shock(mach1=2.5, deflection_deg=10, gamma=1.4)
print(f"Weak shock angle = {os['weak_shock_wave_angle_deg']:.1f}°")

# --- Rocket mission design ---
dv = rocket_delta_v(isp_s=320, mass_fraction=0.85)
print(f"Single-stage ΔV = {dv:.0f} m/s")

orb = orbital_velocity(altitude_m=400e3, planet="earth")
print(f"Circular orbit at 400 km: {orb['circular_velocity_m_s']:.0f} m/s")

tank = propellant_tank_sizing(
    propellant_volume_m3=5.0,
    tank_shape="cylinder",
    material="Ti-6Al-4V",
    safety_factor=1.5,
)
print(f"Tank mass: {tank['tank_mass_kg']:.1f} kg")

# --- Units: convert anything ---
convert(14.7, "psi", "Pa")      # 101352.9...
convert(68, "F", "C")           # 20.0
convert(100, "mph", "m_s")      # 44.704
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
# Stdio transport (for Claude Desktop, etc.)
rocket-tools

# SSE transport (for web clients)
uvicorn rocket_tools.asgi:app --host 0.0.0.0 --port 8000
```

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
├── schemas/        # Pydantic models for all 30 tool inputs/outputs
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
└── rust_kernels/   # Rust PyO3 extension (scaffolded, deferred)
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

| Phase | Status | Features |
|-------|--------|----------|
| **Phase 1** | ✅ Complete | Core tools, tests, benchmarks, skills |
| **Phase 2** | ✅ Mostly Complete | Router (11 intents), workflows, session memory, uncertainty propagation, structural & aerodynamic expansion |
| **Phase 3** | 📋 Planned | Visual intelligence (plots/diagrams), design optimization, standards compliance |
| **Phase 4** | 📋 Planned | Knowledge graph, FMEA, multi-agent sessions, plugin architecture |

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

## License

Apache-2.0 — See [LICENSE](LICENSE)

---

*Built by [Human Engine labs](https://www.humanengine.co/) for the agentic era.*

---

<!-- AGENT-MANIFEST-START -->
<!-- The following section is structured for AI agent discovery. Human readers can safely ignore. -->

## For AI Agents

### MCP Tool Manifest

This repository exposes 35 tools via FastMCP:

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

#### Rocket Nozzle Design
| Tool | Schema | Description |
|------|--------|-------------|
| `nozzle_performance` | `NozzlePerformanceInput` | Thrust, Isp, thrust coefficient, expansion state |
| `optimal_area_ratio` | `OptimalAreaRatioInput` | Optimal A/A* for matched expansion to ambient pressure |

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
