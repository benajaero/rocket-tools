# 🚀 rocket-tools

> Aerospace engineering intelligence for AI agents.

[![Tests](https://img.shields.io/badge/tests-130%20passing-brightgreen)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-83%25-green)](tests/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml)
[![License](https://img.shields.io/badge/license-Apache--2.0-yellow)](LICENSE)

---

## What is rocket-tools?

A **dual-interface** engineering computation engine:

- **MCP Server** — 11 aerospace tools with Pydantic input validation, structured errors, and Prometheus metrics
- **Natural Language Router** — Turn plain-english questions into precise tool calls
- **Workflow Engine** — Chain tools into multi-step design reviews with YAML
- **Skills Library** — Human-readable `.md` references with formulas, worked examples, and pitfalls

Built for speed, precision, and composability.

---

## Tools at a Glance

| Domain | Tool | What it does |
|--------|------|--------------|
| **Structural** | `beam_analysis` | Bending, deflection, shear, Euler buckling |
| **Materials** | `material_lookup` | 5 aerospace alloys with full thermal/mechanical properties |
| **Atmosphere** | `isa_atmosphere` | ISA 0–25,000 m with pre-computed cache |
| **Aerodynamics** | `aero_analysis` | Comprehensive Re, Mach, q, CL, CD, Cf in one call |
| | `reynolds_number` | Reynolds number at altitude |
| | `mach_number` | Mach number at altitude |
| | `dynamic_pressure` | Dynamic pressure q = ½ρV² |
| | `lift_coefficient` | CL from lift, velocity, altitude, area |
| | `drag_coefficient` | CD from drag, velocity, altitude, area |
| | `skin_friction_coefficient` | Blasius skin friction (laminar / turbulent) |
| **Utilities** | `unit_convert` | NIST-traceable SI ↔ imperial conversions |

---

## Performance

| Operation | Latency |
|-----------|---------|
| ISA lookup (cached) | ~54 ns |
| Material lookup | ~342 ns |
| Unit conversion | ~205–546 ns |
| Reynolds number | ~1.4 μs |
| Beam analysis (Numba JIT) | ~3.0 μs |
| Full aerodynamic analysis | ~6.6 μs |

*All under the 1 ms per-tool target.*

---

## Quick Start

### Install

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest -v                    # 130 tests
pytest --benchmark-only -v   # 18 benchmarks
```

### Use as Python Library

```python
from rocket_tools.aerodynamics import aero_analysis
from rocket_tools.structural import beam_analysis

# Comprehensive aerodynamic characterization
result = aero_analysis(
    velocity=250.0,
    altitude_m=5000.0,
    characteristic_length=20.0,
    reference_area=40.0,
    lift=50000.0,
    drag=5000.0,
)
print(f"Re = {result['reynolds_number']:.1e}")
print(f"Mach = {result['mach_number']:.3f} ({result['mach_regime']})")
print(f"L/D = {result['lift_to_drag_ratio']:.1f}")

# Beam design check
beam = beam_analysis(
    load=100.0,
    length=1.0,
    youngs_modulus=68.9e9,  # 6061-T6
    cross_section={"type": "rectangle", "width": 0.05, "height": 0.01},
)
print(f"Deflection: {beam['max_deflection_m']*1000:.3f} mm")
print(f"Bending stress: {beam['bending_stress_pa']/1e6:.2f} MPa")
```

### Natural Language Router

```python
from rocket_tools.router import route_query

result = route_query("Mach number at 250 m/s and 10,000 m")
# ToolCall(tool_name='mach_number', params={...}, confidence=1.0)

# Contextual follow-up with session memory
from rocket_tools.memory import SessionMemory
session = SessionMemory(session_id="design-1")
session.parameters["beam_analysis"] = {"load": 1000.0, "length": 1.5}

result = route_query("What is the deflection?", session=session)
# ToolCall(tool_name='beam_analysis', params={...}, confidence=0.50)
```

### Run the MCP Server

```bash
rocket-tools              # Starts FastMCP stdio server
uvicorn rocket_tools.asgi:app --host 0.0.0.0 --port 8000   # SSE server
```

---

## Production

A production-ready Dockerfile is included:

```bash
docker build -t rocket-tools .
docker run -p 8000:8000 rocket-tools
```

The container exposes:
- MCP server via SSE on `/sse`
- Health check on `/health`
- Readiness probe on `/ready`
- Prometheus metrics on `/metrics`

All on port `8000`.

---

## Workflow Engine

Chain tools into reusable design reviews with YAML workflows:

```yaml
# workflows/built_in/aero_characterization.yaml
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
```

Run a workflow:

```python
from rocket_tools.workflows import load_workflow, run_workflow

wf = load_workflow("aero_characterization.yaml")
result = run_workflow(wf, {
    "velocity": 100.0,
    "altitude_m": 5000.0,
    "characteristic_length": 2.0,
    "reference_area": 10.0,
    "lift": 50000.0,
    "drag": 5000.0,
    "flow_regime": "laminar",
})
```

---

## Skills Library

Human-readable engineering references in `skills/`:

- [`skills/structural-analysis.md`](skills/structural-analysis.md) — Beam theory, Euler buckling, section properties
- [`skills/aerodynamics.md`](skills/aerodynamics.md) — Reynolds, Mach, dynamic pressure, lift/drag
- [`skills/router.md`](skills/router.md) — Intent classification, confidence scoring, session memory

Each skill includes:
- LaTeX formulas
- MCP tool cross-references
- Worked Python examples
- Common pitfalls

---

## Architecture

```
rocket_tools/
├── schemas/        # Pydantic models for all tool inputs/outputs
├── utils/          # Units, validation, caching, safe_eval
├── materials/      # Material database + ISA atmosphere
├── structural/     # Beam mechanics (Numba JIT)
├── aerodynamics/   # Re, Mach, q, CL, CD, Cf (Numba JIT)
├── router/         # Natural language intent + parameter extraction
├── memory/         # Session store for contextual conversations
├── workflows/      # YAML workflow engine + safe interpolation
├── config.py       # pydantic-settings configuration
├── server.py       # FastMCP tool definitions with schema validation
├── asgi.py         # Production SSE + health/metrics endpoints
└── rust_kernels/   # Rust PyO3 extension (deferred)
```

**Numba JIT** accelerates all hot paths.
**Rust kernels** are scaffolded for future PyO3 integration.

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

1. Fork the repo
2. Create a feature branch
3. Write tests first (TDD)
4. Ensure `pytest -v` passes
5. Commit and push

## License

Apache-2.0 — See [LICENSE](LICENSE)

---

*Built by [Human Engine labs](https://www.humanengine.co/) for the agentic era.*
