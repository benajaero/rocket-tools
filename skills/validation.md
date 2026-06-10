---
title: Validation & Benchmarks
skill_type: engineering
layer: validation
tools:
  - all
version: 0.3.3
---

# Validation & Benchmarks

rocket-tools includes a curated validation dataset for verifying tool accuracy against established references.

## Available Benchmarks

| Benchmark | Tool | Reference |
|-----------|------|-----------|
| `isa_sea_level` | `isa_atmosphere` | NASA-TM-X-74335, Table 1 |
| `isa_11000m` | `isa_atmosphere` | NASA-TM-X-74335, Table 1 (Tropopause) |
| `isa_25000m` | `isa_atmosphere` | NASA-TM-X-74335, Table 1 (25 km) |
| `beam_simply_supported_point` | `beam_analysis` | Roark's Formulas, Table 8.1, Case 1 |
| `beam_cantilever_point` | `beam_analysis` | Roark's Formulas, Table 8.1, Case 4 |
| `skin_friction_laminar` | `skin_friction_coefficient` | Blasius (1908) |
| `skin_friction_turbulent` | `skin_friction_coefficient` | Blasius turbulent correlation |
| `rocket_delta_v_standard` | `rocket_delta_v` | Sutton & Biblarz, Eq. 4-6 |
| `isentropic_mach_2` | `isentropic_flow` | Anderson, Table A.1 |
| `normal_shock_mach_2` | `normal_shock` | Anderson, Table A.2 |
| `orbital_velocity_leo` | `orbital_velocity` | Vallado, Eq. 1-28 |
| `section_rectangle` | `section_properties` | Roark's Formulas, Table A.1 |

## Using Benchmarks

```python
from rocket_tools.validation import get_benchmark, list_benchmarks

# List all benchmarks
print(list_benchmarks())

# Get a specific benchmark
bench = get_benchmark("isa_sea_level")
print(bench["expected"])  # Expected values
print(bench["reference"])  # Primary source
print(bench["tolerance"])  # Acceptable error margin
```

## Running Validation

```python
from rocket_tools.validation import validate_benchmark
from rocket_tools.materials import isa_atmosphere

result = isa_atmosphere(0.0)
validation = validate_benchmark("isa_sea_level", result)
print(validation["passed"])  # True if within tolerance
print(validation["reference"])  # Source of expected value
```

## Full Validation Suite

```python
from rocket_tools.validation.benchmarks import _BENCHMARKS, validate_benchmark

# Import all tools
from rocket_tools.materials import isa_atmosphere
from rocket_tools.structural import beam_analysis, section_properties
from rocket_tools.aerodynamics import (
    skin_friction_coefficient, isentropic_flow, normal_shock
)
from rocket_tools.design import rocket_delta_v, orbital_velocity

TOOL_MAP = {
    "isa_atmosphere": isa_atmosphere,
    "beam_analysis": beam_analysis,
    "section_properties": section_properties,
    "skin_friction_coefficient": skin_friction_coefficient,
    "rocket_delta_v": rocket_delta_v,
    "isentropic_flow": isentropic_flow,
    "normal_shock": normal_shock,
    "orbital_velocity": orbital_velocity,
}

passed = 0
failed = 0
for name, bench in _BENCHMARKS.items():
    tool = TOOL_MAP.get(bench["tool_name"])
    if tool:
        result = tool(**bench["inputs"])
        check = validate_benchmark(name, result)
        if check["passed"]:
            passed += 1
        else:
            failed += 1
            print(f"FAIL: {name} — {check['errors']}")

print(f"\nValidation: {passed} passed, {failed} failed")
```

## Adding New Benchmarks

To add a benchmark, edit `src/rocket_tools/validation/benchmarks.py`:

```python
"my_benchmark": {
    "tool_name": "my_tool",
    "inputs": {"param": 1.0},
    "expected": {"result": 2.0},
    "tolerance": 0.01,
    "reference": "Author, Title, Edition, Page/Equation",
},
```

## References

- Abbott & von Doenhoff, "Theory of Wing Sections", Dover 1959
- Blasius (1908), ZAMM
- Roark's Formulas for Stress and Strain, 8th Ed.
- NASA-TM-X-74335: U.S. Standard Atmosphere, 1976
- Sutton & Biblarz, "Rocket Propulsion Elements", 9th Ed.
- Anderson, "Fundamentals of Aerodynamics", 6th Ed.
- Vallado, "Fundamentals of Astrodynamics and Applications", 4th Ed.
