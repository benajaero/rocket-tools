# 🚀 rocket-tools

> Aerospace engineering intelligence for AI agents.

[![Tests](https://img.shields.io/badge/tests-34%20passing-brightgreen)](tests/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml)
[![License](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)

## What is rocket-tools?

A dual-interface engineering computation engine:

- **MCP Server** — 11+ aerospace engineering tools callable by AI agents via the [Model Context Protocol](https://modelcontextprotocol.io/)
- **Skills Library** — Human-readable `.md` references with formulas, worked examples, and pitfalls

Built for speed, precision, and composability.

## Features

| Domain | Tools | Description |
|--------|-------|-------------|
| **Structural** | `beam_analysis` | Bending, deflection, shear, Euler buckling — rectangle & circle sections |
| **Materials** | `material_lookup` | 5 aerospace alloys with full thermal/mechanical properties |
| **Atmosphere** | `isa_atmosphere` | ISA 0–25,000 m with pre-computed cache + linear interpolation |
| **Aerodynamics** | `reynolds_number`, `mach_number`, `dynamic_pressure`, `lift_coefficient`, `drag_coefficient`, `skin_friction_coefficient`, `aero_analysis` | Flow regime, compressibility, forces |
| **Utilities** | `unit_convert` | NIST-traceable conversions (SI ↔ imperial, temperature) |

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

## Quick Start

### Install

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest -v                    # 34 tests
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

### Use as MCP Server

```bash
rocket-tools  # Starts FastMCP server
```

Then connect your MCP client (Claude, Cursor, etc.) to the running server. Available tools:

- `unit_convert` — Convert engineering units
- `material_lookup` — Look up material properties
- `isa_atmosphere` — ISA atmosphere at altitude
- `beam_analysis` — Structural beam analysis
- `reynolds_number` — Reynolds number calculation
- `mach_number` — Mach number at altitude
- `dynamic_pressure` — Dynamic pressure
- `lift_coefficient` — Lift coefficient
- `drag_coefficient` — Drag coefficient
- `skin_friction_coefficient` — Skin friction (Blasius)
- `aero_analysis` — Comprehensive aerodynamic analysis

## Skills Library

Human-readable engineering references in `skills/`:

- [`skills/structural-analysis.md`](skills/structural-analysis.md) — Beam theory, Euler buckling, section properties
- [`skills/aerodynamics.md`](skills/aerodynamics.md) — Reynolds, Mach, dynamic pressure, lift/drag

Each skill includes:
- LaTeX formulas
- MCP tool cross-references
- Worked Python examples
- Common pitfalls

## Architecture

```
rocket_tools/
├── utils/          # Units, validation, caching
├── materials/      # Material database + ISA atmosphere
├── structural/     # Beam mechanics (Numba JIT)
├── aerodynamics/   # Re, Mach, q, CL, CD, Cf (Numba JIT)
├── server.py       # FastMCP tool definitions
└── rust_kernels/   # Rust PyO3 extension (scaffolded)
```

**Numba JIT** accelerates all hot paths. **Rust kernels** are scaffolded for future PyO3 integration when network/toolchain issues resolve.

## Project Roadmap

| Phase | Status | Features |
|-------|--------|----------|
| **Phase 1** | ✅ Complete | Core tools (structural, materials, aerodynamics), tests, benchmarks, skills |
| **Phase 2** | 🔄 Next | Natural language router, composable workflows, uncertainty propagation, contextual memory |
| **Phase 3** | 📋 Planned | Visual intelligence (plots/diagrams), design optimization, standards compliance |
| **Phase 4** | 📋 Planned | Knowledge graph, FMEA, multi-agent sessions, plugin architecture |

## Contributing

1. Fork the repo
2. Create a feature branch
3. Write tests first (TDD)
4. Ensure `pytest -v` passes
5. Commit and push

## License

MIT — See [LICENSE](LICENSE)

---

*Built by Human Engine for the agentic era.*
