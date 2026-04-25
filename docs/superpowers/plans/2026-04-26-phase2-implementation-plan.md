# Phase 2 Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development. Fresh subagent per task + two-stage review.

**Goal:** Implement the Agent Intelligence Layer (router, workflows, uncertainty, memory) as specified in `docs/superpowers/specs/2026-04-26-phase2-agent-intelligence-design.md`.

**Tech Stack:** Python 3.11+, NumPy, PyYAML, FastMCP. No LLM APIs.

**Repo:** `~/Code/rocket-tools/`

---

## Task 1: Router — Intent Classification + Parameter Extraction

**Files:**
- Create: `src/rocket_tools/router/__init__.py`
- Create: `src/rocket_tools/router/engine.py`
- Create: `src/rocket_tools/router/intents.py`
- Create: `src/rocket_tools/router/extractors.py`
- Test: `tests/test_router.py`

- [ ] **Step 1: Write `extractors.py`**

```python
"""Regex-based parameter extraction from natural language."""

import re
from typing import Optional


def extract_number_with_unit(text: str, unit_pattern: str) -> Optional[tuple[float, str]]:
    pattern = rf"(\d+\.?\d*)\s*({unit_pattern})"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return float(match.group(1)), match.group(2).lower()
    return None


def extract_load(text: str) -> Optional[float]:
    result = extract_number_with_unit(text, r"N|n|Newtons?|newtons?|kN|kn")
    if result:
        val, unit = result
        if unit in ("kn", "kN"):
            return val * 1000
        return val
    return None


def extract_length(text: str) -> Optional[float]:
    result = extract_number_with_unit(text, r"m|mm|cm|km|meters?|metres?")
    if result:
        val, unit = result
        if unit in ("mm",):
            return val / 1000
        if unit in ("cm",):
            return val / 100
        if unit in ("km",):
            return val * 1000
        return val
    return None


def extract_velocity(text: str) -> Optional[float]:
    result = extract_number_with_unit(text, r"m/s|mps|km/h|kmh|mph")
    if result:
        val, unit = result
        if unit in ("km/h", "kmh"):
            return val / 3.6
        if unit in ("mph",):
            return val * 0.44704
        return val
    return None


def extract_altitude(text: str) -> Optional[float]:
    result = extract_number_with_unit(text, r"m|km|ft|feet|kft")
    if result:
        val, unit = result
        if unit in ("km",):
            return val * 1000
        if unit in ("ft", "feet"):
            return val * 0.3048
        if unit in ("kft",):
            return val * 304.8
        return val
    return None


def extract_material(text: str) -> Optional[str]:
    from rocket_tools.materials.database import _MATERIALS
    for key in _MATERIALS:
        if key.lower() in text.lower():
            return key
    return None
```

- [ ] **Step 2: Write `intents.py`**

```python
"""Intent pattern registry for aerospace queries."""

from dataclasses import dataclass, field
from typing import Callable

from .extractors import (
    extract_load,
    extract_length,
    extract_velocity,
    extract_altitude,
    extract_material,
)


@dataclass
class IntentConfig:
    patterns: list[str]
    param_extractors: dict[str, Callable]
    defaults: dict = field(default_factory=dict)
    required_params: list[str] = field(default_factory=list)


INTENT_REGISTRY = {
    "beam_analysis": IntentConfig(
        patterns=[
            r"beam.*(load|force|weight|carry|support)",
            r"(deflection|bending stress|bending moment).*beam",
            r"can.*beam.*handle",
            r"will.*beam.*fail",
        ],
        param_extractors={
            "load": extract_load,
            "length": extract_length,
            "material": extract_material,
        },
        defaults={
            "cross_section": {"type": "rectangle", "width": 0.05, "height": 0.01},
            "support_type": "simply_supported",
            "load_type": "point_midspan",
        },
        required_params=["load", "length"],
    ),
    "aero_analysis": IntentConfig(
        patterns=[
            r"(aerodynamic|flow|Re|Reynolds|Mach).*analysis",
            r"(subsonic|transonic|supersonic|hypersonic)",
            r"at\s+(altitude|height)",
        ],
        param_extractors={
            "velocity": extract_velocity,
            "altitude_m": extract_altitude,
            "characteristic_length": extract_length,
        },
        defaults={
            "reference_area": 1.0,
            "lift": 0.0,
            "drag": 0.0,
        },
        required_params=["velocity", "altitude_m"],
    ),
    "material_lookup": IntentConfig(
        patterns=[
            r"(properties|property|specs) of",
            r"look up.*material",
            r"what is.*(6061|7075|titanium|inconel|steel)",
        ],
        param_extractors={
            "name": extract_material,
        },
        defaults={},
        required_params=["name"],
    ),
    "isa_atmosphere": IntentConfig(
        patterns=[
            r"(ISA|atmosphere|density|pressure).*at\s+(\d+)",
            r"what is the (temperature|pressure|density) at",
        ],
        param_extractors={
            "altitude_m": extract_altitude,
        },
        defaults={},
        required_params=["altitude_m"],
    ),
}
```

- [ ] **Step 3: Write `engine.py`**

```python
"""Router engine: classify intent + extract parameters."""

import re
from dataclasses import dataclass
from typing import Any

from .intents import INTENT_REGISTRY
from rocket_tools.materials.database import material_lookup


@dataclass
class ToolCall:
    tool_name: str
    params: dict[str, Any]
    confidence: float
    reasoning: str


@dataclass
class ClarificationRequest:
    message: str
    possible_tools: list[str]
    missing_params: list[str]


def classify_intent(query: str) -> list[tuple[str, float]]:
    scores = []
    query_lower = query.lower()
    for tool_name, config in INTENT_REGISTRY.items():
        score = 0.0
        for pattern in config.patterns:
            if re.search(pattern, query_lower):
                score += 0.25
        scores.append((tool_name, min(score, 1.0)))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores


def extract_params(query: str, config) -> dict[str, Any]:
    params = {}
    for param_name, extractor in config.param_extractors.items():
        value = extractor(query)
        if value is not None:
            params[param_name] = value
    return params


def route_query(query: str) -> ToolCall | ClarificationRequest:
    scores = classify_intent(query)
    if not scores or scores[0][1] == 0.0:
        return ClarificationRequest(
            message="I couldn't understand your query. Try rephrasing with specific numbers and units.",
            possible_tools=list(INTENT_REGISTRY.keys()),
            missing_params=[],
        )

    best_tool, best_score = scores[0]
    config = INTENT_REGISTRY[best_tool]
    params = extract_params(query, config)

    merged = {**config.defaults, **params}

    if "material" in merged and best_tool == "beam_analysis":
        try:
            mat = material_lookup(merged["material"])
            merged["youngs_modulus"] = mat["youngs_modulus_pa"]
            del merged["material"]
        except ValueError:
            pass

    missing = [p for p in config.required_params if p not in merged or merged[p] is None]

    confidence = best_score
    if missing:
        confidence *= 0.6
    elif len(params) < len(config.param_extractors):
        confidence *= 0.8

    if confidence < 0.4:
        return ClarificationRequest(
            message=f"I think you want '{best_tool}' but I'm missing: {missing}",
            possible_tools=[best_tool],
            missing_params=missing,
        )

    return ToolCall(
        tool_name=best_tool,
        params=merged,
        confidence=round(confidence, 2),
        reasoning=f"Matched intent '{best_tool}' with confidence {confidence:.2f}",
    )
```

- [ ] **Step 4: Write `__init__.py`**

```python
from .engine import route_query, ToolCall, ClarificationRequest

__all__ = ["route_query", "ToolCall", "ClarificationRequest"]
```

- [ ] **Step 5: Write tests**

```python
"""Tests for the natural language router."""

import pytest
from rocket_tools.router import route_query, ToolCall, ClarificationRequest


class TestRouterBeam:
    def test_beam_simple(self):
        result = route_query("Can a beam handle 500N over 2m?")
        assert isinstance(result, ToolCall)
        assert result.tool_name == "beam_analysis"
        assert result.params["load"] == 500.0
        assert result.params["length"] == 2.0
        assert result.confidence >= 0.6

    def test_beam_with_material(self):
        result = route_query("Design a 6061-T6 beam for 1000N, 1.5m")
        assert isinstance(result, ToolCall)
        assert result.tool_name == "beam_analysis"
        assert result.params["load"] == 1000.0
        assert result.params["length"] == 1.5
        assert result.params["youngs_modulus"] == 68.9e9

    def test_beam_missing_params(self):
        result = route_query("Beam analysis")
        assert isinstance(result, ClarificationRequest)


class TestRouterAero:
    def test_aero_analysis(self):
        result = route_query("What is the Reynolds number at 100 m/s and 5000m?")
        assert isinstance(result, ToolCall)
        assert result.tool_name == "aero_analysis"
        assert result.params["velocity"] == 100.0
        assert result.params["altitude_m"] == 5000.0


class TestRouterMaterial:
    def test_material_lookup(self):
        result = route_query("What are the properties of Ti-6Al-4V?")
        assert isinstance(result, ToolCall)
        assert result.tool_name == "material_lookup"
        assert result.params["name"] == "Ti-6Al-4V"


class TestRouterUnknown:
    def test_no_match(self):
        result = route_query("Hello world")
        assert isinstance(result, ClarificationRequest)
```

- [ ] **Step 6: Run tests**

Run: `PYTHONPATH=src pytest tests/test_router.py -v`
Expected: 6 tests PASS

- [ ] **Step 7: Commit**

```bash
git add src/rocket_tools/router/ tests/test_router.py
git commit -m "feat: natural language router with intent classification"
```

---

## Task 2: Workflows — Engine + Loader + Built-in Templates

**Files:**
- Create: `src/rocket_tools/workflows/__init__.py`
- Create: `src/rocket_tools/workflows/engine.py`
- Create: `src/rocket_tools/workflows/loader.py`
- Create: `src/rocket_tools/workflows/built_in/design_beam.yaml`
- Create: `src/rocket_tools/workflows/built_in/preliminary_aircraft_sizing.yaml`
- Create: `src/rocket_tools/workflows/built_in/launch_vehicle_max_q.yaml`
- Test: `tests/test_workflows.py`

- [ ] **Step 1: Write `engine.py`**

```python
"""Workflow execution engine with interpolation."""

from dataclasses import dataclass
from typing import Any

from rocket_tools.utils.validation import ValidationError


@dataclass
class WorkflowStep:
    id: str
    tool: str
    params: dict
    save_as: str


@dataclass
class Workflow:
    name: str
    version: str
    description: str
    inputs: dict
    steps: list[WorkflowStep]
    outputs: list[str]


@dataclass
class WorkflowResult:
    outputs: dict
    trace: list[dict]


def resolve_interpolation(value: Any, context: dict) -> Any:
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        path = value[2:-1]
        parts = path.split(".")
        current = context
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                raise ValidationError(
                    f"Cannot resolve '{path}'", "interpolation", "valid reference"
                )
        return current
    if isinstance(value, dict):
        return {k: resolve_interpolation(v, context) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve_interpolation(v, context) for v in value]
    return value


def run_workflow(workflow: Workflow, inputs: dict) -> WorkflowResult:
    context = {"inputs": inputs}
    trace = []

    for step in workflow.steps:
        resolved_params = resolve_interpolation(step.params, context)
        result = _call_tool(step.tool, resolved_params)
        context[step.save_as] = result
        trace.append({
            "step_id": step.id,
            "tool": step.tool,
            "params": resolved_params,
            "result": result,
        })

    outputs = {}
    for out_expr in workflow.outputs:
        key = out_expr.replace("${", "").replace("}", "").replace(".", "_")
        outputs[key] = resolve_interpolation(out_expr, context)

    return WorkflowResult(outputs=outputs, trace=trace)


def _call_tool(tool_name: str, params: dict) -> dict:
    from rocket_tools import structural, aerodynamics, materials

    if tool_name == "beam_analysis":
        return structural.beam_analysis(**params)
    elif tool_name == "aero_analysis":
        return aerodynamics.aero_analysis(**params)
    elif tool_name == "material_lookup":
        return materials.material_lookup(**params)
    elif tool_name == "isa_atmosphere":
        return materials.isa_atmosphere(**params)
    elif tool_name == "reynolds_number":
        return aerodynamics.reynolds_number(**params)
    elif tool_name == "mach_number":
        return aerodynamics.mach_number(**params)
    elif tool_name == "dynamic_pressure":
        return aerodynamics.dynamic_pressure(**params)
    elif tool_name == "lift_coefficient":
        return aerodynamics.lift_coefficient(**params)
    elif tool_name == "drag_coefficient":
        return aerodynamics.drag_coefficient(**params)
    elif tool_name == "unit_convert":
        from rocket_tools.utils import unit_convert
        return unit_convert(**params)
    else:
        raise ValueError(f"Unknown tool: {tool_name}")
```

- [ ] **Step 2: Write `loader.py`**

```python
"""Load workflows from YAML files."""

import yaml
from pathlib import Path

from .engine import Workflow, WorkflowStep


def load_workflow(path: Path) -> Workflow:
    with open(path) as f:
        data = yaml.safe_load(f)

    steps = []
    for step_data in data["steps"]:
        steps.append(WorkflowStep(
            id=step_data["id"],
            tool=step_data["tool"],
            params=step_data.get("params", {}),
            save_as=step_data["save_as"],
        ))

    return Workflow(
        name=data["name"],
        version=data.get("version", "0.1.0"),
        description=data.get("description", ""),
        inputs=data.get("inputs", {}),
        steps=steps,
        outputs=data.get("outputs", []),
    )


def load_all_workflows(built_in_dir: Path, custom_dir: Path | None = None) -> dict[str, Workflow]:
    workflows = {}
    for path in built_in_dir.glob("*.yaml"):
        wf = load_workflow(path)
        workflows[wf.name] = wf
    if custom_dir and custom_dir.exists():
        for path in custom_dir.glob("*.yaml"):
            wf = load_workflow(path)
            workflows[wf.name] = wf
    return workflows
```

- [ ] **Step 3: Write `__init__.py`**

```python
from .engine import Workflow, WorkflowStep, WorkflowResult, run_workflow
from .loader import load_workflow, load_all_workflows

__all__ = ["Workflow", "WorkflowStep", "WorkflowResult", "run_workflow", "load_workflow", "load_all_workflows"]
```

- [ ] **Step 4: Write built-in YAML workflows**

`design_beam.yaml`:
```yaml
name: design_beam
version: "0.1.0"
description: "Material lookup → beam analysis → safety check"
inputs:
  material: {type: str, required: true}
  load: {type: float, required: true}
  length: {type: float, required: true}
  cross_section: {type: dict, required: true}

steps:
  - id: lookup_material
    tool: material_lookup
    params:
      name: "${inputs.material}"
    save_as: mat

  - id: analyze_beam
    tool: beam_analysis
    params:
      load: "${inputs.load}"
      length: "${inputs.length}"
      youngs_modulus: "${mat.youngs_modulus_pa}"
      cross_section: "${inputs.cross_section}"
    save_as: beam

outputs:
  - "${beam}"
```

`preliminary_aircraft_sizing.yaml`:
```yaml
name: preliminary_aircraft_sizing
version: "0.1.0"
description: "ISA → Re → CL for cruise conditions"
inputs:
  cruise_altitude_m: {type: float, required: true}
  cruise_velocity_m_s: {type: float, required: true}
  mean_aerodynamic_chord_m: {type: float, required: true}
  wing_area_m2: {type: float, required: true}
  mass_kg: {type: float, required: true}

steps:
  - id: cruise_env
    tool: isa_atmosphere
    params:
      altitude_m: "${inputs.cruise_altitude_m}"
    save_as: env

  - id: re_cruise
    tool: reynolds_number
    params:
      velocity: "${inputs.cruise_velocity_m_s}"
      characteristic_length: "${inputs.mean_aerodynamic_chord_m}"
      altitude_m: "${inputs.cruise_altitude_m}"
    save_as: re

  - id: cl_cruise
    tool: lift_coefficient
    params:
      lift: "${inputs.mass_kg * 9.80665}"
      velocity: "${inputs.cruise_velocity_m_s}"
      altitude_m: "${inputs.cruise_altitude_m}"
      reference_area: "${inputs.wing_area_m2}"
    save_as: cl

outputs:
  - "${env}"
  - "${re}"
  - "${cl}"
```

`launch_vehicle_max_q.yaml`:
```yaml
name: launch_vehicle_max_q
version: "0.1.0"
description: "ISA → q_max for launch vehicle structural check"
inputs:
  max_q_altitude_m: {type: float, required: true}
  max_q_velocity_m_s: {type: float, required: true}

steps:
  - id: max_q_env
    tool: isa_atmosphere
    params:
      altitude_m: "${inputs.max_q_altitude_m}"
    save_as: env

  - id: q_max
    tool: dynamic_pressure
    params:
      velocity: "${inputs.max_q_velocity_m_s}"
      altitude_m: "${inputs.max_q_altitude_m}"
    save_as: q

outputs:
  - "${env}"
  - "${q}"
```

- [ ] **Step 5: Write tests**

```python
"""Tests for workflow engine."""

import pytest
from pathlib import Path
from rocket_tools.workflows import load_workflow, load_all_workflows, run_workflow


BUILT_IN_DIR = Path(__file__).parent.parent / "src" / "rocket_tools" / "workflows" / "built_in"


class TestLoadWorkflow:
    def test_load_design_beam(self):
        wf = load_workflow(BUILT_IN_DIR / "design_beam.yaml")
        assert wf.name == "design_beam"
        assert len(wf.steps) == 2

    def test_load_all(self):
        wfs = load_all_workflows(BUILT_IN_DIR)
        assert "design_beam" in wfs
        assert "preliminary_aircraft_sizing" in wfs


class TestRunWorkflow:
    def test_design_beam(self):
        wfs = load_all_workflows(BUILT_IN_DIR)
        wf = wfs["design_beam"]
        result = run_workflow(wf, {
            "material": "6061-T6",
            "load": 500.0,
            "length": 2.0,
            "cross_section": {"type": "rectangle", "width": 0.05, "height": 0.01},
        })
        assert "beam" in result.outputs
        assert result.outputs["beam"]["bending_stress_pa"] > 0
        assert len(result.trace) == 2

    def test_preliminary_aircraft_sizing(self):
        wfs = load_all_workflows(BUILT_IN_DIR)
        wf = wfs["preliminary_aircraft_sizing"]
        result = run_workflow(wf, {
            "cruise_altitude_m": 5000.0,
            "cruise_velocity_m_s": 100.0,
            "mean_aerodynamic_chord_m": 1.0,
            "wing_area_m2": 10.0,
            "mass_kg": 500.0,
        })
        assert "re" in result.outputs
        assert "cl" in result.outputs

    def test_interpolation_error(self):
        from rocket_tools.workflows.engine import resolve_interpolation
        with pytest.raises(Exception):
            resolve_interpolation("${missing.key}", {})
```

- [ ] **Step 6: Run tests**

Run: `PYTHONPATH=src pytest tests/test_workflows.py -v`
Expected: 4 tests PASS

- [ ] **Step 7: Commit**

```bash
git add src/rocket_tools/workflows/ tests/test_workflows.py
git commit -m "feat: composable workflow engine with 3 built-in templates"
```

---

## Task 3: Uncertainty Propagation — Distributions + Monte Carlo Engine

**Files:**
- Create: `src/rocket_tools/uncertainty/__init__.py`
- Create: `src/rocket_tools/uncertainty/distributions.py`
- Create: `src/rocket_tools/uncertainty/engine.py`
- Test: `tests/test_uncertainty.py`

- [ ] **Step 1: Write `distributions.py`**

```python
"""Probability distributions for uncertainty propagation."""

import numpy as np
from abc import ABC, abstractmethod


class Distribution(ABC):
    @abstractmethod
    def sample(self, n: int, seed: int | None = None) -> np.ndarray: ...

    @abstractmethod
    def to_dict(self) -> dict: ...

    @staticmethod
    def from_dict(data: dict) -> "Distribution":
        dtype = data["distribution"]
        if dtype == "uniform":
            return Uniform(data["low"], data["high"])
        elif dtype == "normal":
            return Normal(data["mean"], data["std"])
        elif dtype == "lognormal":
            return LogNormal(data["mean"], data["sigma"])
        elif dtype == "truncated_normal":
            return TruncatedNormal(data["mean"], data["std"], data["low"], data["high"])
        else:
            raise ValueError(f"Unknown distribution: {dtype}")


class Uniform(Distribution):
    def __init__(self, low: float, high: float):
        self.low = low
        self.high = high

    def sample(self, n: int, seed: int | None = None) -> np.ndarray:
        rng = np.random.default_rng(seed)
        return rng.uniform(self.low, self.high, n)

    def to_dict(self) -> dict:
        return {"distribution": "uniform", "low": self.low, "high": self.high}


class Normal(Distribution):
    def __init__(self, mean: float, std: float):
        self.mean = mean
        self.std = std

    def sample(self, n: int, seed: int | None = None) -> np.ndarray:
        rng = np.random.default_rng(seed)
        return rng.normal(self.mean, self.std, n)

    def to_dict(self) -> dict:
        return {"distribution": "normal", "mean": self.mean, "std": self.std}


class LogNormal(Distribution):
    def __init__(self, mean: float, sigma: float):
        self.mean = mean
        self.sigma = sigma

    def sample(self, n: int, seed: int | None = None) -> np.ndarray:
        rng = np.random.default_rng(seed)
        return rng.lognormal(self.mean, self.sigma, n)

    def to_dict(self) -> dict:
        return {"distribution": "lognormal", "mean": self.mean, "sigma": self.sigma}


class TruncatedNormal(Distribution):
    def __init__(self, mean: float, std: float, low: float, high: float):
        self.mean = mean
        self.std = std
        self.low = low
        self.high = high

    def sample(self, n: int, seed: int | None = None) -> np.ndarray:
        rng = np.random.default_rng(seed)
        samples = rng.normal(self.mean, self.std, n * 10)
        samples = samples[(samples >= self.low) & (samples <= self.high)]
        if len(samples) < n:
            raise ValueError("TruncatedNormal: too few samples in bounds")
        return samples[:n]

    def to_dict(self) -> dict:
        return {"distribution": "truncated_normal", "mean": self.mean, "std": self.std, "low": self.low, "high": self.high}
```

- [ ] **Step 2: Write `engine.py`**

```python
"""Monte Carlo uncertainty propagation engine."""

import numpy as np
from typing import Any

from .distributions import Distribution
from rocket_tools.workflows.engine import _call_tool


def _is_distribution(value: Any) -> bool:
    return isinstance(value, dict) and "distribution" in value


def _resolve_param_distributions(params: dict, n: int, seed: int) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    param_samples = {}
    for key, value in params.items():
        if _is_distribution(value):
            dist = Distribution.from_dict(value)
            param_samples[key] = dist.sample(n, rng.integers(0, 2**31))
        elif isinstance(value, dict):
            resolved = {}
            for k, v in value.items():
                if _is_distribution(v):
                    dist = Distribution.from_dict(v)
                    resolved[k] = dist.sample(n, rng.integers(0, 2**31))
                else:
                    resolved[k] = np.full(n, v)
            param_samples[key] = resolved
        else:
            param_samples[key] = np.full(n, value)
    return param_samples


def _build_param_dict(param_samples: dict, idx: int) -> dict:
    params = {}
    for key, value in param_samples.items():
        if isinstance(value, dict):
            params[key] = {k: v[idx] for k, v in value.items()}
        else:
            params[key] = value[idx]
    return params


def run_with_uncertainty(tool_name: str, params: dict, samples: int = 1000, seed: int = 42) -> dict:
    param_samples = _resolve_param_distributions(params, samples, seed)
    results = []
    for i in range(samples):
        p = _build_param_dict(param_samples, i)
        result = _call_tool(tool_name, p)
        results.append(result)

    return _aggregate_results(results, samples)


def _aggregate_results(results: list[dict], samples: int) -> dict:
    if not results:
        return {"error": "No results"}

    aggregated = {}
    keys = [k for k in results[0].keys() if isinstance(results[0][k], (int, float))]

    for key in keys:
        values = np.array([r[key] for r in results if key in r and isinstance(r[key], (int, float))])
        if len(values) == 0:
            continue
        aggregated[key] = {
            "mean": round(float(np.mean(values)), 6),
            "std": round(float(np.std(values)), 6),
            "min": round(float(np.min(values)), 6),
            "max": round(float(np.max(values)), 6),
            "ci_95": [
                round(float(np.percentile(values, 2.5)), 6),
                round(float(np.percentile(values, 97.5)), 6),
            ],
        }

    return {
        "samples": samples,
        "results": aggregated,
    }
```

- [ ] **Step 3: Write `__init__.py`**

```python
from .distributions import Distribution, Uniform, Normal, LogNormal, TruncatedNormal
from .engine import run_with_uncertainty

__all__ = ["Distribution", "Uniform", "Normal", "LogNormal", "TruncatedNormal", "run_with_uncertainty"]
```

- [ ] **Step 4: Write tests**

```python
"""Tests for uncertainty propagation."""

import pytest
import numpy as np
from rocket_tools.uncertainty import Uniform, Normal, run_with_uncertainty


class TestDistributions:
    def test_uniform(self):
        d = Uniform(0, 10)
        samples = d.sample(1000, seed=42)
        assert len(samples) == 1000
        assert np.min(samples) >= 0
        assert np.max(samples) <= 10

    def test_normal(self):
        d = Normal(5, 1)
        samples = d.sample(10000, seed=42)
        assert pytest.approx(np.mean(samples), 0.1) == 5.0
        assert pytest.approx(np.std(samples), 0.1) == 1.0

    def test_serialization(self):
        d = Uniform(1, 2)
        assert d.to_dict() == {"distribution": "uniform", "low": 1, "high": 2}
        d2 = Uniform.from_dict(d.to_dict())
        assert d2.low == 1


class TestUncertaintyEngine:
    def test_beam_uncertainty(self):
        result = run_with_uncertainty(
            tool_name="beam_analysis",
            params={
                "load": {"distribution": "uniform", "low": 450, "high": 550},
                "length": 2.0,
                "youngs_modulus": 68.9e9,
                "cross_section": {"type": "rectangle", "width": 0.05, "height": 0.01},
            },
            samples=100,
            seed=42,
        )
        assert result["samples"] == 100
        assert "bending_stress_pa" in result["results"]
        stress = result["results"]["bending_stress_pa"]
        assert stress["mean"] > 0
        assert stress["ci_95"][0] < stress["ci_95"][1]

    def test_no_uncertainty(self):
        result = run_with_uncertainty(
            tool_name="beam_analysis",
            params={
                "load": 500.0,
                "length": 2.0,
                "youngs_modulus": 68.9e9,
                "cross_section": {"type": "rectangle", "width": 0.05, "height": 0.01},
            },
            samples=10,
            seed=42,
        )
        assert result["samples"] == 10
        stress = result["results"]["bending_stress_pa"]
        assert stress["std"] == pytest.approx(0, abs=1e-6)
```

- [ ] **Step 5: Run tests**

Run: `PYTHONPATH=src pytest tests/test_uncertainty.py -v`
Expected: 4 tests PASS

- [ ] **Step 6: Commit**

```bash
git add src/rocket_tools/uncertainty/ tests/test_uncertainty.py
git commit -m "feat: uncertainty propagation with Monte Carlo + 4 distributions"
```

---

## Task 4: Memory — Session-Aware Context

**Files:**
- Create: `src/rocket_tools/memory/__init__.py`
- Create: `src/rocket_tools/memory/session.py`
- Test: `tests/test_memory.py`

- [ ] **Step 1: Write `session.py`**

```python
"""Session memory for contextual engineering conversations."""

import time
import uuid
from dataclasses import dataclass, field


@dataclass
class ToolExecution:
    tool_name: str
    params: dict
    result: dict
    timestamp: float = field(default_factory=time.time)


@dataclass
class SessionMemory:
    session_id: str
    mission_type: str = "general"
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    parameters: dict[str, dict] = field(default_factory=dict)
    history: list[ToolExecution] = field(default_factory=list)

    def merge(self, new_params: dict, tool_name: str) -> dict:
        defaults = self.parameters.get(tool_name, {})
        merged = {**defaults, **{k: v for k, v in new_params.items() if v is not None}}
        self.parameters[tool_name] = merged
        self.last_accessed = time.time()
        return merged

    def record(self, tool_name: str, params: dict, result: dict):
        self.history.append(ToolExecution(tool_name, params, result))
        self.last_accessed = time.time()


class SessionStore:
    def __init__(self, ttl_seconds: float = 86400):
        self._sessions: dict[str, SessionMemory] = {}
        self._ttl = ttl_seconds

    def create(self, mission_type: str = "general") -> str:
        sid = str(uuid.uuid4())[:8]
        self._sessions[sid] = SessionMemory(session_id=sid, mission_type=mission_type)
        return sid

    def get(self, sid: str) -> SessionMemory:
        self._cleanup()
        if sid not in self._sessions:
            return SessionMemory(session_id=sid)
        return self._sessions[sid]

    def _cleanup(self):
        now = time.time()
        expired = [sid for sid, mem in self._sessions.items() if now - mem.last_accessed > self._ttl]
        for sid in expired:
            del self._sessions[sid]


_store = SessionStore()


def get_store() -> SessionStore:
    return _store
```

- [ ] **Step 2: Write `__init__.py`**

```python
from .session import SessionMemory, SessionStore, ToolExecution, get_store

__all__ = ["SessionMemory", "SessionStore", "ToolExecution", "get_store"]
```

- [ ] **Step 3: Write tests**

```python
"""Tests for session memory."""

import pytest
from rocket_tools.memory import get_store


class TestSessionStore:
    def test_create_session(self):
        store = get_store()
        sid = store.create(mission_type="aircraft")
        assert len(sid) == 8
        mem = store.get(sid)
        assert mem.mission_type == "aircraft"

    def test_merge_params(self):
        store = get_store()
        sid = store.create()
        mem = store.get(sid)
        p1 = mem.merge({"load": 500, "length": 2}, "beam_analysis")
        assert p1 == {"load": 500, "length": 2}
        p2 = mem.merge({"material": "6061-T6"}, "beam_analysis")
        assert p2 == {"load": 500, "length": 2, "material": "6061-T6"}

    def test_merge_override(self):
        store = get_store()
        sid = store.create()
        mem = store.get(sid)
        mem.merge({"load": 500}, "beam_analysis")
        p2 = mem.merge({"load": 1000}, "beam_analysis")
        assert p2["load"] == 1000

    def test_record_history(self):
        store = get_store()
        sid = store.create()
        mem = store.get(sid)
        mem.record("beam_analysis", {"load": 500}, {"stress": 100})
        assert len(mem.history) == 1
        assert mem.history[0].tool_name == "beam_analysis"
```

- [ ] **Step 4: Run tests**

Run: `PYTHONPATH=src pytest tests/test_memory.py -v`
Expected: 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/rocket_tools/memory/ tests/test_memory.py
git commit -m "feat: mission-aware session memory with parameter inheritance"
```

---

## Task 5: Integration — New MCP Tools + Safety Check

**Files:**
- Modify: `src/rocket_tools/server.py`
- Test: `tests/test_integration.py`

- [ ] **Step 1: Add safety_check tool**

```python
@mcp.tool()
def safety_check(stress: float, yield_strength: float, required_sf: float = 1.5) -> dict:
    """Check if stress is within safety factor of yield strength."""
    if stress <= 0 or yield_strength <= 0:
        raise ValueError("Stress and yield strength must be > 0")
    sf_achieved = yield_strength / stress
    return {
        "safety_factor_achieved": round(float(sf_achieved), 2),
        "safety_factor_required": required_sf,
        "passes": sf_achieved >= required_sf,
        "margin_percent": round((sf_achieved - required_sf) / required_sf * 100, 1) if required_sf > 0 else 0.0,
    }
```

- [ ] **Step 2: Add route_query tool**

```python
@mcp.tool()
def route_query(query: str) -> dict:
    """Parse a natural language aerospace query and route to the appropriate tool."""
    from rocket_tools.router import route_query as _rq
    result = _rq(query)
    if hasattr(result, "to_dict"):
        return result.__dict__
    return {"tool_call": result.__dict__}
```

- [ ] **Step 3: Add run_workflow tool**

```python
@mcp.tool()
def run_workflow(workflow_name: str, inputs: dict) -> dict:
    """Run a named workflow with given inputs."""
    from pathlib import Path
    from rocket_tools.workflows import load_all_workflows, run_workflow as _rw
    built_in = Path(__file__).parent / "workflows" / "built_in"
    wfs = load_all_workflows(built_in)
    if workflow_name not in wfs:
        raise ValueError(f"Workflow '{workflow_name}' not found. Available: {list(wfs.keys())}")
    result = _rw(wfs[workflow_name], inputs)
    return {
        "outputs": result.outputs,
        "trace": [{"step_id": t["step_id"], "tool": t["tool"]} for t in result.trace],
    }
```

- [ ] **Step 4: Add run_with_uncertainty tool**

```python
@mcp.tool()
def run_with_uncertainty(tool_name: str, params: dict, samples: int = 1000, seed: int = 42) -> dict:
    """Run a tool with uncertain inputs using Monte Carlo simulation."""
    from rocket_tools.uncertainty import run_with_uncertainty as _ru
    return _ru(tool_name, params, samples, seed)
```

- [ ] **Step 5: Add create_session tool**

```python
@mcp.tool()
def create_session(mission_type: str = "general") -> dict:
    """Create a new mission-aware session for contextual memory."""
    from rocket_tools.memory import get_store
    sid = get_store().create(mission_type=mission_type)
    return {"session_id": sid, "mission_type": mission_type}
```

- [ ] **Step 6: Write integration tests**

```python
"""Integration tests for new MCP tools."""

import pytest
from rocket_tools.server import safety_check, run_workflow, create_session
from pathlib import Path


class TestSafetyCheck:
    def test_passes(self):
        result = safety_check(stress=100e6, yield_strength=276e6, required_sf=1.5)
        assert result["passes"] is True
        assert result["safety_factor_achieved"] == pytest.approx(2.76, 0.01)

    def test_fails(self):
        result = safety_check(stress=200e6, yield_strength=276e6, required_sf=1.5)
        assert result["passes"] is False


class TestRunWorkflowIntegration:
    def test_design_beam(self):
        result = run_workflow("design_beam", {
            "material": "6061-T6",
            "load": 500.0,
            "length": 2.0,
            "cross_section": {"type": "rectangle", "width": 0.05, "height": 0.01},
        })
        assert "beam" in result["outputs"]


class TestCreateSession:
    def test_create(self):
        result = create_session("aircraft")
        assert "session_id" in result
        assert result["mission_type"] == "aircraft"
```

- [ ] **Step 7: Run tests**

Run: `PYTHONPATH=src pytest tests/test_integration.py -v`
Expected: 4 tests PASS

- [ ] **Step 8: Run full test suite**

Run: `PYTHONPATH=src pytest -v`
Expected: All tests PASS

- [ ] **Step 9: Commit**

```bash
git add src/rocket_tools/server.py tests/test_integration.py
git commit -m "feat: MCP integration — safety_check, route_query, run_workflow, run_with_uncertainty, create_session"
```

---

## Task 6: Benchmarks

**Files:**
- Create: `tests/bench_router.py`
- Create: `tests/bench_workflows.py`
- Create: `tests/bench_uncertainty.py`
- Create: `tests/bench_memory.py`

- [ ] **Step 1: Write benchmark files**

`bench_router.py`:
```python
import pytest
from rocket_tools.router import route_query

class TestBenchRouter:
    def test_bench_beam_query(self, benchmark):
        benchmark(route_query, "Can a beam handle 500N over 2m?")

    def test_bench_aero_query(self, benchmark):
        benchmark(route_query, "Reynolds number at 100 m/s and 5000m")
```

`bench_workflows.py`:
```python
import pytest
from pathlib import Path
from rocket_tools.workflows import load_all_workflows, run_workflow

BUILT_IN = Path(__file__).parent.parent / "src" / "rocket_tools" / "workflows" / "built_in"
WFS = load_all_workflows(BUILT_IN)

class TestBenchWorkflows:
    def test_bench_design_beam(self, benchmark):
        benchmark(run_workflow, WFS["design_beam"], {
            "material": "6061-T6", "load": 500.0, "length": 2.0,
            "cross_section": {"type": "rectangle", "width": 0.05, "height": 0.01},
        })
```

`bench_uncertainty.py`:
```python
import pytest
from rocket_tools.uncertainty import run_with_uncertainty

class TestBenchUncertainty:
    def test_bench_100_samples(self, benchmark):
        benchmark(run_with_uncertainty, "beam_analysis", {
            "load": {"distribution": "uniform", "low": 450, "high": 550},
            "length": 2.0, "youngs_modulus": 68.9e9,
            "cross_section": {"type": "rectangle", "width": 0.05, "height": 0.01},
        }, 100, 42)
```

`bench_memory.py`:
```python
import pytest
from rocket_tools.memory import get_store

class TestBenchMemory:
    def test_bench_merge(self, benchmark):
        store = get_store()
        sid = store.create()
        mem = store.get(sid)
        mem.merge({"load": 500, "length": 2}, "beam_analysis")
        benchmark(mem.merge, {"material": "6061-T6"}, "beam_analysis")
```

- [ ] **Step 2: Run benchmarks**

Run: `PYTHONPATH=src pytest --benchmark-only -v`
Expected: All benchmarks PASS

- [ ] **Step 3: Commit**

```bash
git add tests/bench_*.py
git commit -m "bench: Phase 2 benchmarks (router, workflows, uncertainty, memory)"
```

---

## Task 7: Skills Documentation

**Files:**
- Create: `skills/workflows.md`
- Create: `skills/uncertainty.md`
- Modify: `skills/README.md`

- [ ] **Step 1: Write `skills/workflows.md`**

```markdown
---
title: Composable Workflows
skill_type: engineering
layer: workflows
tools:
  - run_workflow
version: 0.1.0
---

# Composable Workflows

Chain engineering tools into declarative multi-step analyses.

## When to Use

- Multi-step design processes (material selection → structural analysis → safety check)
- Parametric studies with shared inputs
- Reproducible analysis pipelines

## Built-in Workflows

### `design_beam`

Material lookup → beam analysis.

**Inputs:**
- `material` (str): e.g., "6061-T6"
- `load` (float): Applied load in N
- `length` (float): Beam span in m
- `cross_section` (dict): `{type: "rectangle", width: m, height: m}`

**Example:**
```python
result = run_workflow("design_beam", {
    "material": "6061-T6",
    "load": 500.0,
    "length": 2.0,
    "cross_section": {"type": "rectangle", "width": 0.05, "height": 0.01},
})
```

### `preliminary_aircraft_sizing`

ISA → Reynolds number → lift coefficient for cruise.

**Inputs:**
- `cruise_altitude_m`, `cruise_velocity_m_s`, `mean_aerodynamic_chord_m`, `wing_area_m2`, `mass_kg`

### `launch_vehicle_max_q`

ISA → dynamic pressure at max-q.

**Inputs:**
- `max_q_altitude_m`, `max_q_velocity_m_s`

## Writing Custom Workflows

Create a YAML file in `workflows/custom/`:

```yaml
name: my_analysis
steps:
  - id: step1
    tool: isa_atmosphere
    params: {altitude_m: "${inputs.altitude}"}
    save_as: env
outputs:
  - "${env}"
```

Interpolation uses `${step_id.field_path}` syntax.

## Common Pitfalls

1. **Missing `save_as`** — Each step must save its result for downstream steps
2. **Wrong field path** — Use dot notation: `${mat.youngs_modulus_pa}`
3. **Tool name typos** — Must match exact MCP tool names
```

- [ ] **Step 2: Write `skills/uncertainty.md`**

```markdown
---
title: Uncertainty Propagation
skill_type: engineering
layer: uncertainty
tools:
  - run_with_uncertainty
version: 0.1.0
---

# Uncertainty Propagation

Monte Carlo simulation for engineering safety analysis.

## When to Use

- Manufacturing tolerance analysis
- Material property scatter
- Load uncertainty
- Reliability assessment

## Distributions

| Distribution | JSON Syntax | Use Case |
|--------------|-------------|----------|
| Uniform | `{"distribution": "uniform", "low": 450, "high": 550}` | Tolerance bounds |
| Normal | `{"distribution": "normal", "mean": 2.0, "std": 0.005}` | Machining precision |
| LogNormal | `{"distribution": "lognormal", "mean": 276e6, "sigma": 0.05}` | Material scatter |
| TruncatedNormal | `{"distribution": "truncated_normal", "mean": 5, "std": 1, "low": 0, "high": 10}` | Bounded physical quantity |

## Example

```python
result = run_with_uncertainty(
    tool_name="beam_analysis",
    params={
        "load": {"distribution": "uniform", "low": 450, "high": 550},
        "length": {"distribution": "normal", "mean": 2.0, "std": 0.005},
        "youngs_modulus": 68.9e9,
        "cross_section": {"type": "rectangle", "width": 0.05, "height": 0.01},
    },
    samples=1000,
    seed=42,
)

print(f"Mean stress: {result['results']['bending_stress_pa']['mean']:.2e} Pa")
print(f"95% CI: [{result['results']['bending_stress_pa']['ci_95'][0]:.2e}, "
      f"{result['results']['bending_stress_pa']['ci_95'][1]:.2e}] Pa")
```

## Interpreting Results

- `mean` — Expected value
- `std` — Standard deviation
- `ci_95` — 95% confidence interval
- `min` / `max` — Observed extremes

## Common Pitfalls

1. **Too few samples** — 1000 minimum for stable percentiles
2. **Wrong distribution** — Use LogNormal for strictly positive properties
3. **Correlated variables** — This engine assumes independence
```

- [ ] **Step 3: Update `skills/README.md`**

Add to the skills table:
```markdown
| [Workflows](./workflows.md) | `run_workflow` | Declarative multi-step analysis |
| [Uncertainty](./uncertainty.md) | `run_with_uncertainty` | Monte Carlo safety analysis |
```

- [ ] **Step 4: Commit**

```bash
git add skills/
git commit -m "docs: skills for workflows and uncertainty propagation"
```

---

## Task 8: Final Verification + Version Bump

- [ ] **Step 1: Run full test suite**

```bash
PYTHONPATH=src pytest -v
```
Expected: ≥ 46 tests PASS

- [ ] **Step 2: Run all benchmarks**

```bash
PYTHONPATH=src pytest --benchmark-only -v
```
Expected: 22 benchmarks PASS (10 existing + 12 new)

- [ ] **Step 3: Bump version**

Modify `src/rocket_tools/__init__.py`:
```python
__version__ = "0.3.0"
```

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "release: v0.3.0 — Agent Intelligence Layer"
```

---

## Summary

| Task | Component | Tests | Benchmarks |
|------|-----------|-------|------------|
| 1 | Router | 6 | 2 |
| 2 | Workflows | 4 | 1 |
| 3 | Uncertainty | 4 | 1 |
| 4 | Memory | 4 | 1 |
| 5 | Integration | 4 | — |
| 6 | Benchmarks | — | 7 |
| 7 | Skills docs | — | — |
| **Total** | — | **≥ 22 new** | **≥ 12 new** |
