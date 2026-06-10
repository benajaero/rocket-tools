# Natural Language Router

The router turns plain‑english aerospace questions into precise tool calls.

## How It Works

1. **Intent Classification** – The query is matched against regex patterns for each registered tool.
2. **Parameter Extraction** – Numbers and units are pulled from the text using domain‑specific extractors.
3. **Confidence Scoring** – The final confidence reflects both pattern match strength *and* parameter completeness:

   ```
   confidence = pattern_score × (extracted_params / total_extractors)
   ```

   A query that names a tool but omits optional parameters will score lower than one that supplies everything.

## Confidence Rules

| Condition | Behaviour |
|-----------|-----------|
| `confidence < 0.4` | Router returns a **ClarificationRequest** rather than guessing. |
| Missing *required* parameters | Router immediately asks for the missing values. |
| Partial optional parameters | Confidence is reduced proportionally. |
| Session memory present | Confidence floor is raised to `0.5` so contextual follow-ups don't get blocked. |

## Worked Example

### Full‑confidence query

```python
from rocket_tools.router import route_query

result = route_query("Design a 6061-T6 beam for 1000N, 1.5m")
# ToolCall(
#   tool_name="beam_analysis",
#   params={"load": 1000.0, "length": 1.5, "youngs_modulus": 68.9e9, ...},
#   confidence=1.0
# )
```

### Partial‑confidence query

```python
result = route_query("Can a beam handle 500N over 2m?")
# ToolCall(
#   tool_name="beam_analysis",
#   params={"load": 500.0, "length": 2.0, ...},
#   confidence≈0.67   # material was not specified
# )
```

### Contextual follow‑up with session memory

```python
from rocket_tools.memory import SessionMemory

session = SessionMemory(session_id="design-1")
session.parameters["beam_analysis"] = {"load": 1000.0, "length": 1.5}

result = route_query("What is the deflection?", session=session)
# ToolCall(
#   tool_name="beam_analysis",
#   params={"load": 1000.0, "length": 1.5, ...},
#   confidence=0.50   # boosted by session context
# )
```

Session memory is merged **after** defaults but **before** the current query, so explicit values in the new query always override stored context.

### No‑match query

```python
result = route_query("Hello world")
# ClarificationRequest(
#   message="I couldn't understand your query. Try rephrasing...",
#   possible_tools=["beam_analysis", "aero_analysis", ...]
# )
```

## Supported Intents

| Intent | Required Params | Example Query |
|--------|-----------------|---------------|
| `beam_analysis` | `load`, `length` | "Design a 6061-T6 beam for 1000N, 1.5m" |
| `aero_analysis` | `velocity`, `altitude_m` | "What is the Reynolds number at 100 m/s and 5000m?" |
| `material_lookup` | `name` | "What are the properties of Ti-6Al-4V?" |
| `isa_atmosphere` | `altitude_m` | "ISA at 10,000 ft" |
| `reynolds_number` | `velocity`, `characteristic_length` | "Reynolds number at 100 m/s with 2m chord at 5000m" |
| `mach_number` | `velocity`, `altitude_m` | "Mach number at 250 m/s and 10000m" |
| `dynamic_pressure` | `velocity`, `altitude_m` | "Dynamic pressure at 150 m/s at sea level" |
| `lift_coefficient` | `lift`, `velocity`, `altitude_m`, `reference_area` | "Lift coefficient for 50000N at 100 m/s, 5000m, 10m2" |
| `drag_coefficient` | `drag`, `velocity`, `altitude_m`, `reference_area` | "Drag coefficient for 5000N at 100 m/s, 5000m, 10m2" |
| `skin_friction_coefficient` | `reynolds_number` | "Skin friction at Re 1e6" |
| `unit_convert` | `value`, `from_unit`, `to_unit` | "Convert 100 mm to m" |

## Adding a New Intent

1. Register the intent in `src/rocket_tools/router/intents.py`.
2. Add parameter extractors in `src/rocket_tools/router/extractors.py` if needed.
3. Write a router test in `tests/test_router.py`.

## Pitfalls

- **Greedy extractors** – A velocity like `100 m/s` can be mis‑read as a length because the extractor sees `100 m`. Use explicit units (e.g. `km/h`, `ft`) when possible.
- **Low confidence on short queries** – One‑word queries (e.g. `"beam"`) hit the intent but score low on parameters; the router will ask for clarification rather than silently defaulting.
