# Contributing to rocket-tools

Thank you for considering a contribution. This document explains how to set up your environment, run tests, and submit changes.

---

## Table of Contents

1. [Development Setup](#development-setup)
2. [Project Structure](#project-structure)
3. [Running Tests](#running-tests)
4. [Code Quality](#code-quality)
5. [Adding a New Material](#adding-a-new-material)
6. [Adding a New Tool](#adding-a-new-tool)
7. [Pull Request Process](#pull-request-process)

---

## Development Setup

### Prerequisites

- Python 3.11 or later
- Git

### Step-by-Step

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/rocket-tools.git
cd rocket-tools

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # On Windows: .venv\Scripts\activate

# 3. Install in editable mode with dev dependencies
pip install -e ".[dev]"

# 4. Verify everything works
pytest -v
ruff check src/ tests/
mypy src/rocket_tools/
```

If all three commands pass, your environment is ready.

---

## Project Structure

```
rocket_tools/
├── schemas/           # Pydantic models for tool inputs/outputs
├── utils/             # Units, validation, caching, safe_eval
├── materials/         # Material database (database.py) + ISA (isa.py)
├── structural/        # Beam mechanics
├── aerodynamics/      # Re, Mach, q, CL, CD, Cf
├── router/            # NL intent classification + parameter extraction
├── memory/            # Session store
├── workflows/         # YAML workflow engine
├── config.py          # pydantic-settings
├── server.py          # FastMCP server
├── asgi.py            # Production ASGI app
└── observability.py   # Metrics & logging

tests/                 # Test files — mirror the src/ structure where possible
skills/                # Human-readable .md engineering references
docs/                  # Design docs, council deliberations, plans
```

**Rule of thumb:** If you add code in `src/rocket_tools/X/`, add tests in `tests/test_X.py`.

---

## Running Tests

### Full Suite

```bash
pytest -v
```

Runs 182 tests across all modules.

### With Coverage

```bash
pytest --cov=src/rocket_tools --cov-report=term-missing
```

Coverage must stay above 80% (configured in `pyproject.toml`).

### Benchmarks Only

```bash
pytest --benchmark-only -v
```

Runs 18 latency benchmarks. These help catch performance regressions.

### Single Test File

```bash
pytest tests/test_materials.py -v
```

### Single Test

```bash
pytest tests/test_materials.py::TestMaterialLookup::test_6061_t6 -v
```

---

## Code Quality

We enforce three quality gates. All must pass before a PR is merged.

### 1. Linting with ruff

```bash
ruff check src/ tests/
```

Line length limit: 100 characters. Target Python version: 3.11.

Auto-fix most issues:

```bash
ruff check src/ tests/ --fix
```

### 2. Type Checking with mypy

```bash
mypy src/rocket_tools/
```

We run with `strict = false` but `warn_return_any = true`. If mypy complains about a third-party library, add an ignore in `pyproject.toml` under `[tool.mypy]` — do not use `# type: ignore` inline unless there is no other option.

### 3. Tests Must Pass

```bash
pytest -v
```

---

## Adding a New Material

This is one of the easiest and most valuable contributions.

### 1. Edit `src/rocket_tools/materials/database.py`

Find the right category dict (`_ALUMINUM`, `_TITANIUM`, `_STEELS`, `_NICKEL`, `_COMPOSITES`, `_REFRACTORY`, or `_OTHER`). Add a new entry:

```python
"My-Alloy-T6": Material(
    name="My-Alloy-T6",
    youngs_modulus_pa=70.0e9,
    density_kg_m3=2700.0,
    yield_strength_pa=276e6,
    ultimate_strength_pa=310e6,
    poisson_ratio=0.33,
    thermal_expansion_1_k=2.36e-5,
    thermal_conductivity_w_m_k=167.0,
    specific_heat_j_kg_k=896.0,
    applications=frozenset({"aircraft", "drone", "rocket"}),
),
```

**Field reference:**
- `youngs_modulus_pa` — Young's modulus in Pascals (use `xxx_e9` for GPa)
- `density_kg_m3` — Density in kg/m³
- `yield_strength_pa` — 0.2% proof stress in Pascals
- `ultimate_strength_pa` — Tensile strength in Pascals
- `poisson_ratio` — Typical range 0.25–0.35 for metals
- `thermal_expansion_1_k` — Coefficient of thermal expansion in 1/K
- `thermal_conductivity_w_m_k` — In W/(m·K)
- `specific_heat_j_kg_k` — In J/(kg·K)
- `applications` — Tag with relevant domains: `aircraft`, `drone`, `rocket`, `helicopter`, `spacecraft`, `satellite`, `engine`, `general`

**Sources:** Use manufacturer datasheets, MIL-HDBK-5, or ASM Handbook. Add a `source="MIL-HDBK-5"` field if you have a specific reference.

### 2. Update Category Mappings

If you added a new category, update `_CATEGORIES`. If the material fits existing applications, it will auto-appear in `_APPLICATIONS` because that dict is computed dynamically from the `applications` field.

### 3. Add a Test

In `tests/test_materials.py`, add:

```python
def test_my_alloy_t6(self):
    result = material_lookup("My-Alloy-T6")
    assert result["material_name"] == "My-Alloy-T6"
    assert result["density_kg_m3"] == 2700.0
```

### 4. Run Tests

```bash
pytest tests/test_materials.py -v
```

---

## Adding a New Tool

Adding a tool is more involved but follows a clear pattern.

### Overview

A tool in rocket-tools has **5 layers**:

1. **Core function** — the actual computation (`src/rocket_tools/<domain>/`)
2. **Schema** — Pydantic input model (`src/rocket_tools/schemas/`)
3. **Server wrapper** — FastMCP `@mcp.tool()` decorator (`src/rocket_tools/server.py`)
4. **Router extractor** — NL parameter extraction (`src/rocket_tools/router/extractors.py`)
5. **Tests** — unit tests + server integration tests

### Step-by-Step

#### Step 1: Write the Core Function

```python
# src/rocket_tools/aerodynamics/my_tool.py
from rocket_tools.utils.validation import validate_positive


def my_tool(velocity: float, altitude_m: float) -> dict:
    """Compute something useful.

    Args:
        velocity: Freestream velocity in m/s (must be > 0)
        altitude_m: Altitude in meters (must be >= 0)

    Returns:
        dict with the result and metadata
    """
    validate_positive(velocity, "velocity")
    validate_non_negative(altitude_m, "altitude_m")

    # ... computation ...
    result_value = velocity * 2  # placeholder

    return {
        "result": result_value,
        "velocity": velocity,
        "altitude_m": altitude_m,
    }
```

#### Step 2: Create the Pydantic Schema

```python
# src/rocket_tools/schemas/aerodynamics.py (or new file)
from pydantic import BaseModel, Field


class MyToolInput(BaseModel):
    velocity: float = Field(..., gt=0)
    altitude_m: float = Field(..., ge=0)
```

#### Step 3: Register in `__init__.py`

```python
# src/rocket_tools/aerodynamics/__init__.py
from .my_tool import my_tool
```

#### Step 4: Add the MCP Server Wrapper

```python
# src/rocket_tools/server.py
from rocket_tools.schemas.aerodynamics import MyToolInput

@mcp.tool()
def my_tool(velocity, altitude_m) -> dict:
    """Compute something useful."""
    from rocket_tools.aerodynamics import my_tool as _my_tool
    try:
        validated = MyToolInput(velocity=velocity, altitude_m=altitude_m)
        return _my_tool(**validated.model_dump())
    except Exception as e:
        return _format_error(e)
```

#### Step 5: Add Router Support (Optional but Recommended)

```python
# src/rocket_tools/router/extractors.py

def extract_my_tool_params(text: str) -> dict:
    """Extract parameters for my_tool from natural language."""
    params = {}
    vel = extract_velocity(text)
    if vel is not None:
        params["velocity"] = vel
    alt = extract_altitude(text)
    if alt is not None:
        params["altitude_m"] = alt
    return params
```

Register the intent in `src/rocket_tools/router/intents.py`.

#### Step 6: Write Tests

```python
# tests/test_aerodynamics.py
class TestMyTool:
    def test_basic(self):
        result = my_tool(velocity=100.0, altitude_m=5000.0)
        assert result["result"] == 200.0

    def test_invalid_velocity(self):
        with pytest.raises(ValidationError):
            my_tool(velocity=-1.0, altitude_m=0.0)
```

```python
# tests/test_server.py
class TestServerMyTool:
    def test_my_tool(self):
        result = asyncio.run(_call_tool("my_tool", {"velocity": 100.0, "altitude_m": 5000.0}))
        data = json.loads(result[0].text)
        assert data["result"] == 200.0
```

#### Step 7: Update README and Skills

- Add the tool to the capability table in `README.md`
- Add a row to the MCP tool manifest in the Agent Discovery Zone
- Update relevant skills in `skills/`

---

## Pull Request Process

1. **Branch from `main`**
   ```bash
   git checkout -b feature/my-contribution
   ```

2. **Make your changes** with tests.

3. **Run quality gates locally**
   ```bash
   pytest -v
   ruff check src/ tests/
   mypy src/rocket_tools/
   ```

4. **Commit with a clear message**
   ```bash
   git commit -m "feat: add Ti-15V-3Cr-3Al-3Sn titanium alloy

   - Add material properties from MIL-HDBK-5J
   - Tag with rocket, aircraft applications
   - Add test for yield strength"
   ```

5. **Push and open a PR** against `main`.

6. **CI will run** the test matrix (Python 3.11, 3.12, 3.13) plus ruff and mypy. All must pass.

7. **Address review feedback.** We aim to review within 48 hours.

---

## Questions?

- Open an [issue](https://github.com/benajaero/rocket-tools/issues) for bugs or feature requests
- Start a discussion for architecture questions
- Tag `@benajaero` for urgent matters

---

*Thank you for helping make aerospace computation more accessible.*
