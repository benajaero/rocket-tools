# 🚀 rocket-tools

> **Engineering-grade aerospace computation. AI-native interface.**

[![Tests](https://img.shields.io/badge/tests-182%20passing-brightgreen)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-82%25-green)](tests/)
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

**[→ Full Documentation](docs/)** · **[→ Quick Start for AI Agents](#for-ai-agents)** · **[→ Contributing](CONTRIBUTING.md)**

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
| **11 MCP Tools** | Exposed via [FastMCP](https://github.com/modelcontextprotocol/python-sdk) — AI agents can call aerospace computations with structured inputs and validated outputs |
| **49+ Materials** | Aluminum, titanium, steel, nickel superalloys, composites, refractory metals — with thermal & mechanical properties, filterable by application (rocket, drone, aircraft, spacecraft, engine) |
| **Natural Language Router** | Ask *"What's the Reynolds number at 250 m/s and 5 km?"* and get a validated tool call — no API memorization needed |
| **ISA Atmosphere** | Standard atmosphere 0–25,000 m with ~54 ns cached lookups |
| **Workflow Engine** | Chain tools into reusable YAML workflows for design reviews |
| **ASGI Server** | Production-ready SSE (Server-Sent Events) endpoint with `/health`, `/ready`, and Prometheus `/metrics` |
| **Unit Conversions** | NIST-traceable SI ↔ imperial (psi, psf, ft, in, lbf, mph, knots, Fahrenheit, Rankine) |

**Performance:** All hot paths are Numba JIT-compiled. Every tool runs in under 1 ms.

---

## How to Use It

### 1. As a Python Library

The simplest way — import and compute.

```python
from rocket_tools.structural import beam_analysis
from rocket_tools.materials import material_lookup, compare_materials
from rocket_tools.aerodynamics import aero_analysis, mach_number
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

# --- Units: convert anything ---
convert(14.7, "psi", "Pa")      # 101352.9...
convert(68, "F", "C")           # 20.0
convert(100, "mph", "m_s")      # 44.704
```

**Key concepts:**
- **`material_lookup(name)`** — Fuzzy-matches material names (`"6061"`, `"ti-6al-4v"`, `"inconel 718"` all work). Returns a dict with `youngs_modulus_pa`, `density_kg_m3`, `yield_strength_mpa`, `thermal_conductivity_w_m_k`, and more.
- **`compare_materials([...])`** — Side-by-side trade study sorted by specific strength (strength-to-weight ratio).
- **`beam_analysis(...)`** — Supports rectangle and circle cross-sections, point/distributed/axial loads, and simply-supported/cantilever/fixed-ends boundary conditions.
- **`aero_analysis(...)`** — One call returns Reynolds number, Mach number, dynamic pressure, lift coefficient, drag coefficient, and skin friction coefficient.

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
├── schemas/        # Pydantic models for all 11 tool inputs/outputs
├── utils/          # Units, validation, caching, safe_eval
├── materials/      # 49+ materials + ISA atmosphere
├── structural/     # Beam mechanics (Numba JIT)
├── aerodynamics/   # Re, Mach, q, CL, CD, Cf (Numba JIT)
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
- [`skills/aerodynamics.md`](skills/aerodynamics.md) — Reynolds, Mach, dynamic pressure, lift/drag
- [`skills/units.md`](skills/units.md) — Supported units, conversion reference, temperature handling
- [`skills/schemas.md`](skills/schemas.md) — Pydantic model reference for all tools
- [`skills/router.md`](skills/router.md) — Intent classification, confidence scoring, session memory

Each skill includes formulas, MCP tool cross-references, worked Python examples, and common pitfalls.

---

## Roadmap

| Phase | Status | Features |
|-------|--------|----------|
| **Phase 1** | ✅ Complete | Core tools, tests, benchmarks, skills |
| **Phase 2** | ✅ Mostly Complete | Router (11 intents), workflows, session memory, uncertainty propagation |
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
pytest -v                    # 182 tests
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

This repository exposes 11 tools via FastMCP:

| Tool | Schema | Description |
|------|--------|-------------|
| `beam_analysis` | `BeamAnalysisInput` | Structural beam analysis with bending, deflection, shear, buckling |
| `aero_analysis` | `AeroAnalysisInput` | Comprehensive aerodynamic characterization (Re, Mach, q, CL, CD, Cf) |
| `reynolds_number` | `ReynoldsNumberInput` | Reynolds number from velocity, altitude, and characteristic length |
| `mach_number` | `MachNumberInput` | Mach number at altitude |
| `dynamic_pressure` | `DynamicPressureInput` | Dynamic pressure q = ½ρV² |
| `lift_coefficient` | `LiftCoefficientInput` | CL from lift, velocity, altitude, area |
| `drag_coefficient` | `DragCoefficientInput` | CD from drag, velocity, altitude, area |
| `skin_friction_coefficient` | `SkinFrictionInput` | Blasius skin friction (laminar / turbulent) |
| `material_lookup` | `MaterialLookupInput` | Look up 49+ aerospace materials by name |
| `isa_atmosphere` | `ISAAtmosphereInput` | Standard atmosphere properties 0–25,000 m |
| `unit_convert` | `UnitConvertInput` | NIST-traceable unit conversion |

### ASGI Deployment

```bash
uvicorn rocket_tools.asgi:app --host 0.0.0.0 --port 8000
```

Endpoints:
- `GET /sse` — MCP SSE transport
- `GET /health` — `{"status": "ok", "version": "0.3.1"}`
- `GET /ready` — `{"status": "ready", "tools": 11}`
- `GET /metrics` — Prometheus metrics

### Natural Language Routing

```python
from rocket_tools.router import route_query
result = route_query("Calculate Reynolds number at 100 m/s, 5000 m, length 2 m")
# result.tool_name == 'reynolds_number'
# result.params == {'velocity': 100.0, 'altitude_m': 5000.0, 'characteristic_length': 2.0}
```

### Schema Files

- `src/rocket_tools/schemas/structural.py` — Beam analysis schemas
- `src/rocket_tools/schemas/aerodynamics.py` — Aerodynamics schemas
- `src/rocket_tools/schemas/materials.py` — Materials & unit conversion schemas

<!-- AGENT-MANIFEST-END -->
