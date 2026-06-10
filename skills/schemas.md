---
title: Schemas & Validation
skill_type: engineering
layer: infrastructure
tools:
  - all
version: 0.3.2
---

# Schemas & Validation

Pydantic models provide runtime validation, type safety, and JSON Schema generation for every tool.

## When to Use

- Validating inputs before calling tools
- Generating JSON schemas for LLM tool descriptions
- Understanding parameter constraints and types
- Handling validation errors gracefully

## Schema Organization

All schemas live in `rocket_tools/schemas/`:

```
schemas/
├── __init__.py        # Export all schemas
├── structural.py      # BeamAnalysisInput, SectionPropertiesInput, ColumnBucklingInput, PlateBucklingInput
├── aerodynamics.py    # ReynoldsNumberInput, MachNumberInput, AeroAnalysisInput, IsentropicFlowInput, NormalShockInput, ObliqueShockInput, PrandtlMeyerInput, LiftCurveSlopeInput, DragPolarInput, BreguetRangeInput, WingLoadingInput, NozzlePerformanceInput, OptimalAreaRatioInput
├── materials.py       # MaterialLookupInput, ISAAtmosphereInput
├── design.py          # RocketDeltaVInput, MultiStageDeltaVInput, OrbitalVelocityInput, PayloadFractionInput, ThrustToWeightInput, CompositeCGInput, PropellantTankSizingInput
└── utils.py           # UnitConvertInput
```

## Input Schemas

Every tool has a corresponding `*Input` Pydantic model with:
- **Type annotations** — `float`, `int`, `Literal[...]`, union types
- **Field validators** — `gt=0`, `ge=0`, `le=25000`, `min_length=1`
- **Descriptions** — Human-readable field docs for LLM schema generation

### Example: BeamAnalysisInput

```python
from rocket_tools.schemas import BeamAnalysisInput, RectangleSection

# Valid input
inp = BeamAnalysisInput(
    load=1000.0,
    length=2.0,
    youngs_modulus=68.9e9,
    cross_section=RectangleSection(width=0.05, height=0.01),
    load_type="point_midspan",
    support_type="simply_supported",
)

# Invalid: negative load raises ValidationError
BeamAnalysisInput(load=-100, length=2.0, youngs_modulus=68.9e9, cross_section={"type": "rectangle", "width": 0.05, "height": 0.01})
# ValidationError: load must be > 0

# Invalid: unsupported cross-section type
BeamAnalysisInput(load=100, length=2.0, youngs_modulus=68.9e9, cross_section={"type": "triangle", "width": 0.05, "height": 0.01})
# ValidationError: cross_section.type must be 'rectangle' or 'circle'
```

### Discriminated Unions

Cross-section types use discriminated unions:

```python
from rocket_tools.schemas import RectangleSection, CircleSection

# Both are valid for cross_section
rect = RectangleSection(width=0.05, height=0.01)
circle = CircleSection(diameter=0.1)
```

## Output Schemas

Every tool has a corresponding `*Output` model documenting the return structure:

```python
from rocket_tools.schemas import ReynoldsNumberOutput

# Output models are used for type hints and documentation
output: ReynoldsNumberOutput = ReynoldsNumberOutput(
    reynolds_number=1.2e6,
    density_kg_m3=1.225,
    dynamic_viscosity_pa_s=1.789e-5,
    velocity_m_s=100.0,
    characteristic_length_m=2.0,
    flow_regime="turbulent",
)
```

## Structured Errors

When validation fails, tools return structured error dicts:

```python
{
    "error": True,
    "error_code": "INVALID_PARAMETER",
    "message": "altitude_m must be <= 25000. Received: 50000",
    "parameter": "altitude_m",
    "constraint": "0 <= altitude_m <= 25000",
    "suggestion": "Valid range: 0 to 25000",
}
```

Error codes:
| Code | Meaning |
|------|---------|
| `INVALID_PARAMETER` | Input violates a constraint |
| `MISSING_REFERENCE` | Workflow interpolation reference not found |
| `INVALID_EXPRESSION` | Workflow expression syntax error |
| `UNKNOWN_TOOL` | Tool name not recognized |
| `INTERNAL_ERROR` | Unexpected server error |

## JSON Schema for LLMs

Pydantic models auto-generate JSON schemas:

```python
from rocket_tools.schemas import MachNumberInput

schema = MachNumberInput.model_json_schema()
# {
#   "properties": {
#     "velocity": {"description": "Velocity in m/s", "exclusiveMinimum": 0, "type": "number"},
#     "altitude_m": {"description": "Altitude in meters", "maximum": 25000, "minimum": 0, "type": "number"}
#   },
#   "required": ["velocity", "altitude_m"]
# }
```

## Common Pitfalls

1. **Raw dicts vs models** — The MCP server accepts raw dicts (FastMCP passes them), but Pydantic validates internally. Use the schema models in your own code.
2. **Literal constraints** — `load_type` must be exactly `"point_midspan"`, `"distributed"`, or `"axial"`. No abbreviations.
3. **Optional params** — Schema fields with `default=...` are optional; fields without are required.
4. **Union types** — `cross_section` accepts `RectangleSection | CircleSection`. Passing a raw dict works because Pydantic coerces it.
