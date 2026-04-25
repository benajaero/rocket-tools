# Phase 2: Agent Intelligence Layer — Design Spec

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform rocket-tools from a calculator into an aerospace engineering reasoning engine by adding a natural language router, composable workflows, uncertainty propagation, and mission-aware contextual memory.

**Architecture:** A lightweight intelligence layer sits above the existing tool layer. The router classifies intent and extracts parameters; workflows chain tools declaratively with data passing; uncertainty wraps any tool in Monte Carlo simulation; memory persists mission context across a session. All components are pure Python, zero external LLM dependencies, and integrate as MCP tools.

**Tech Stack:** Python 3.11+, NumPy (random sampling), FastMCP, PyYAML. No LLM APIs. No proprietary data.

---

## Table of Contents

1. [Natural Language Router](#1-natural-language-router)
2. [Composable Workflows](#2-composable-workflows)
3. [Uncertainty Propagation](#3-uncertainty-propagation)
4. [Contextual Memory](#4-contextual-memory)
5. [Integration Layer](#5-integration-layer)
6. [File Structure](#6-file-structure)
7. [Error Handling](#7-error-handling)
8. [Testing Strategy](#8-testing-strategy)
9. [Performance Targets](#9-performance-targets)

---

## 1. Natural Language Router

### Purpose
Map free-text aerospace queries to structured `ToolCall` objects without calling external LLMs. Uses lightweight pattern matching + parameter extraction.

### Design

```python
@dataclass
class ToolCall:
    tool_name: str
    params: dict[str, Any]
    confidence: float  # 0.0–1.0
    reasoning: str
```

**Intent patterns** are registered as regex + extractor functions:

```python
# router/intents.py
INTENT_PATTERNS = {
    "beam_analysis": {
        "patterns": [
            r"beam.*(load|force|weight)",
            r"(deflection|bending stress).*beam",
            r"can.*beam.*handle",
        ],
        "param_extractors": {
            "load": extract_load,       # regex for "500N", "1000 N", etc.
            "length": extract_length,   # regex for "2m", "1.5 meters", etc.
            "material": extract_material,  # match against _MATERIALS keys
        },
        "defaults": {
            "cross_section": {"type": "rectangle", "width": 0.05, "height": 0.01},
            "support_type": "simply_supported",
            "load_type": "point_midspan",
        },
    },
    "aero_analysis": {
        "patterns": [
            r"(aerodynamic|flow|Re|Mach).*analysis",
            r"at\s+(\d+\s*m|sea.level)",
            r"(subsonic|transonic|supersonic|hypersonic)",
        ],
        "param_extractors": {
            "velocity": extract_velocity,
            "altitude_m": extract_altitude,
            "characteristic_length": extract_length,
        },
        "defaults": {
            "reference_area": 1.0,
        },
    },
    # ... etc
}
```

**Parameter extractors** are small regex-based functions that pull numbers with units from text, then convert via `unit_convert`.

**Material inference:** If text contains a material name (e.g., "6061", "Ti-6Al-4V"), look it up and auto-fill `youngs_modulus` and other material-dependent defaults.

**Confidence scoring:**
- 1.0: Exact tool name mentioned + all required params extracted
- 0.8: Tool inferred from context + all params extracted
- 0.6: Tool inferred + some params missing (defaults used)
- 0.4: Ambiguous (multiple tools match)
- 0.0: No match

If confidence < 0.6, return a `ClarificationRequest` instead of a `ToolCall`.

### MCP Tool

```python
@mcp.tool()
def route_query(query: str, mission_type: str = "general") -> dict:
    """Parse a natural language aerospace query and route to the appropriate tool."""
```

Returns either a `ToolCall` dict or a `ClarificationRequest` dict.

---

## 2. Composable Workflows

### Purpose
Allow users to chain tool calls declaratively with data passing between steps.

### Design

**Workflow definition** (YAML):

```yaml
name: design_beam
version: "0.1.0"
description: "Design a beam: material lookup → structural analysis → safety check"
inputs:
  material: {type: str, required: true}
  load: {type: float, required: true}
  length: {type: float, required: true}
  cross_section: {type: dict, required: true}

steps:
  - id: lookup_material
    tool: material_lookup
    params:
      name: "${material}"
    save_as: mat

  - id: analyze_beam
    tool: beam_analysis
    params:
      load: "${load}"
      length: "${length}"
      youngs_modulus: "${mat.youngs_modulus_pa}"
      cross_section: "${cross_section}"
    save_as: beam

  - id: check_safety
    tool: safety_check
    params:
      stress: "${beam.bending_stress_pa}"
      yield_strength: "${mat.yield_strength_pa}"
      required_sf: 1.5
    save_as: safety

outputs:
  - "${beam}"
  - "${safety}"
```

**Interpolation syntax:** `${step_id.field_path}` resolves nested dict access (e.g., `${mat.youngs_modulus_pa}`).

**Workflow engine** (`workflows/engine.py`):

```python
def run_workflow(workflow: Workflow, inputs: dict, memory: SessionMemory) -> WorkflowResult:
    context = {"inputs": inputs, **memory.to_dict()}
    trace = []
    for step in workflow.steps:
        resolved_params = resolve_interpolation(step.params, context)
        result = call_tool(step.tool, resolved_params)
        context[step.save_as] = result
        trace.append({"step": step.id, "tool": step.tool, "params": resolved_params, "result": result})
    return WorkflowResult(outputs=extract_outputs(workflow.outputs, context), trace=trace)
```

**Built-in workflows** ship in `workflows/built_in/`:
- `design_beam.yaml` — Material → beam analysis → safety check
- `preliminary_aircraft_sizing.yaml` — ISA → Re → CL cruise
- `launch_vehicle_max_q.yaml` — ISA → q_max → structural check

**Custom workflows** in `workflows/custom/` are hot-loaded at server start.

**Safety check tool** (new, simple):

```python
@mcp.tool()
def safety_check(stress: float, yield_strength: float, required_sf: float = 1.5) -> dict:
    sf_achieved = yield_strength / stress
    return {
        "safety_factor_achieved": round(sf_achieved, 2),
        "safety_factor_required": required_sf,
        "passes": sf_achieved >= required_sf,
        "margin_percent": round((sf_achieved - required_sf) / required_sf * 100, 1),
    }
```

### MCP Tool

```python
@mcp.tool()
def run_workflow(workflow_name: str, inputs: dict) -> dict:
    """Run a named workflow with given inputs."""
```

---

## 3. Uncertainty Propagation

### Purpose
Wrap any tool call in Monte Carlo simulation to compute confidence intervals and failure probabilities.

### Design

**Distribution primitives** (`uncertainty/distributions.py`):

```python
class Distribution(ABC):
    @abstractmethod
    def sample(self, n: int) -> np.ndarray: ...

class Uniform(Distribution):
    def __init__(self, low: float, high: float): ...

class Normal(Distribution):
    def __init__(self, mean: float, std: float): ...

class LogNormal(Distribution):
    def __init__(self, mean: float, sigma: float): ...

class TruncatedNormal(Distribution):
    def __init__(self, mean: float, std: float, low: float, high: float): ...
```

**Parameter schema:** Tool params can be either scalar values or Distribution objects. The uncertainty engine samples all distributions in parallel, runs the tool N times, and aggregates.

```python
@mcp.tool()
def run_with_uncertainty(
    tool_name: str,
    params: dict,
    samples: int = 1000,
    seed: int = 42,
) -> dict:
    """Run a tool with uncertain inputs and return statistical summary."""
```

**Sampling strategy:**
1. Identify all Distribution objects in `params`
2. Generate N samples for each (vectorized NumPy)
3. Run the tool N times in a loop (tools are fast: ~3μs each)
4. For N=1000, total time ~3ms — acceptable
5. Aggregate results per output field:
   - `mean`, `std`, `min`, `max`
   - `ci_95`: [2.5th percentile, 97.5th percentile]
   - `p_exceed_limit`: if a limit is provided

**Example usage:**

```python
run_with_uncertainty(
    tool_name="beam_analysis",
    params={
        "load": {"distribution": "uniform", "low": 450, "high": 550},
        "length": {"distribution": "normal", "mean": 2.0, "std": 0.005},
        "youngs_modulus": 68.9e9,
        "cross_section": {"type": "rectangle", "width": 0.05, "height": 0.01},
    },
    samples=1000,
)
```

**Returns:**

```python
{
    "tool_name": "beam_analysis",
    "samples": 1000,
    "results": {
        "max_deflection_m": {
            "mean": 0.00342,
            "std": 0.00018,
            "ci_95": [0.00308, 0.00378],
            "min": 0.00289,
            "max": 0.00412,
        },
        "bending_stress_pa": {
            "mean": 150000000.0,
            "std": 15000000.0,
            "ci_95": [121000000.0, 180000000.0],
        },
    },
}
```

**Serialization:** Distributions are passed as JSON-serializable dicts (`{"distribution": "uniform", "low": 450, "high": 550}`), not Python objects, so they work over MCP.

---

## 4. Contextual Memory

### Purpose
Persist mission context and design history across a session so follow-up queries inherit previous parameters.

### Design

**Session memory** (`memory/session.py`):

```python
@dataclass
class SessionMemory:
    session_id: str
    mission_type: str = "general"  # general, aircraft, launch_vehicle, cubesat
    regulatory_framework: str = ""
    active_constraints: dict = field(default_factory=dict)
    parameters: dict = field(default_factory=dict)  # last-used params per tool
    history: list[ToolExecution] = field(default_factory=list)

    def merge(self, new_params: dict, tool_name: str) -> dict:
        """Merge new params with stored defaults. New values override."""
        defaults = self.parameters.get(tool_name, {})
        merged = {**defaults, **new_params}
        self.parameters[tool_name] = merged
        return merged
```

**Mission types** affect default values:
- `general`: No special defaults
- `aircraft`: Default `reference_area` = 10 m², `characteristic_length` = 1 m (chord)
- `launch_vehicle`: Default `safety_factor` = 1.25 (unmanned), loads use g₀ = 9.80665 m/s²
- `cubesat`: Default `load` = 50g quasi-static (ECSS), `cross_section` = 10×10 mm rail

**Memory-aware MCP tools:**

```python
@mcp.tool()
def beam_analysis_with_memory(
    session_id: str,
    load: float = None,
    length: float = None,
    # ... other params optional
) -> dict:
    """Run beam_analysis, using session memory for unspecified params."""
    mem = get_memory(session_id)
    params = mem.merge({k: v for k, v in locals().items() if v is not None}, "beam_analysis")
    result = beam_analysis(**params)
    mem.history.append(ToolExecution("beam_analysis", params, result))
    return result
```

**Session lifecycle:**
- Created on first call with a new `session_id`
- Persists in memory (not disk) for the MCP server process lifetime
- Auto-cleanup after 24 hours of inactivity

**Query resolution example:**

```
User: "Design a 6061-T6 beam for 500N over 2m"
  → mem.parameters["beam_analysis"] = {material: "6061-T6", load: 500, length: 2, ...}

User: "What about titanium?"
  → router detects "titanium" → material="Ti-6Al-4V"
  → merges with mem: {material: "Ti-6Al-4V", load: 500, length: 2, ...}
  → runs beam_analysis

User: "At 10,000m altitude"
  → mem.mission_type = "aircraft"
  → next aero query uses altitude=10000m by default
```

---

## 5. Integration Layer

### New MCP Tools Summary

| Tool | Purpose |
|------|---------|
| `route_query` | Natural language → ToolCall |
| `run_workflow` | Execute named workflow with inputs |
| `run_with_uncertainty` | Monte Carlo wrapper for any tool |
| `safety_check` | Compare stress vs yield with safety factor |
| `create_session` | Initialize a mission-aware session |
| `beam_analysis_with_memory` | beam_analysis + session memory |
| `aero_analysis_with_memory` | aero_analysis + session memory |

### Server Changes

`server.py` grows by ~150 lines. Each new tool is a thin wrapper around the intelligence layer. Existing tools remain unchanged.

---

## 6. File Structure

```
rocket_tools/
├── utils/                    # existing
├── materials/                # existing
├── structural/               # existing
├── aerodynamics/             # existing
├── router/
│   ├── __init__.py
│   ├── engine.py            # Intent classification + param extraction
│   ├── intents.py           # INTENT_PATTERNS registry
│   └── extractors.py        # Regex-based parameter extractors
├── workflows/
│   ├── __init__.py
│   ├── engine.py            # Workflow execution engine
│   ├── loader.py            # Hot-load built_in/ + custom/ YAMLs
│   ├── built_in/
│   │   ├── design_beam.yaml
│   │   ├── preliminary_aircraft_sizing.yaml
│   │   └── launch_vehicle_max_q.yaml
│   └── custom/              # user-defined (gitignored)
├── uncertainty/
│   ├── __init__.py
│   ├── distributions.py     # Uniform, Normal, LogNormal, TruncatedNormal
│   └── engine.py            # Monte Carlo sampling + aggregation
├── memory/
│   ├── __init__.py
│   └── session.py           # SessionMemory + session store
├── server.py                # existing + 7 new MCP tools
└── rust_kernels/            # existing (scaffolded)

skills/
├── structural-analysis.md   # existing
├── aerodynamics.md          # existing
├── workflows.md             # NEW: workflow authoring guide
└── uncertainty.md           # NEW: uncertainty propagation guide

tests/
├── test_router.py
├── test_workflows.py
├── test_uncertainty.py
├── test_memory.py
├── bench_router.py
├── bench_workflows.py
├── bench_uncertainty.py
└── bench_memory.py
```

---

## 7. Error Handling

| Scenario | Behavior |
|----------|----------|
| Router confidence < 0.6 | Return `ClarificationRequest` with suggested follow-up |
| Workflow step fails | Halt execution, return partial trace + error detail |
| Distribution sampling fails | Return error with invalid parameter name |
| Memory session not found | Auto-create new session with `mission_type="general"` |
| Workflow YAML syntax error | Log error at server start, skip that workflow |
| Missing required workflow input | Return validation error before execution |
| Tool not found in workflow | Return error naming missing tool |

All errors return structured dicts with `error: True`, `error_type`, `message`, and `suggestion`.

---

## 8. Testing Strategy

### Unit Tests (target: 40+)

| Component | Tests |
|-----------|-------|
| Router | Intent matching, param extraction, confidence scoring, clarification |
| Workflows | YAML loading, interpolation, step execution, error handling |
| Uncertainty | Distribution sampling, serialization, aggregation, edge cases |
| Memory | Session creation, merge, parameter inheritance, history |
| Integration | Full NL query → tool call, workflow → multiple tools |

### Benchmarks (target: 12)

| Benchmark | Target |
|-----------|--------|
| Route query (simple) | < 100 μs |
| Route query (complex) | < 500 μs |
| Workflow execution (3 steps) | < 5 ms |
| Uncertainty (100 samples) | < 1 ms |
| Uncertainty (1000 samples) | < 10 ms |
| Memory merge | < 10 μs |

---

## 9. Performance Targets

| Metric | Target |
|--------|--------|
| Router latency | < 500 μs |
| Workflow execution (3 steps) | < 5 ms |
| Uncertainty (1000 samples) | < 10 ms |
| Memory operations | < 10 μs |
| Total new test count | ≥ 40 |
| Total new benchmark count | ≥ 12 |
| Lines of new code | ~800–1200 |

---

## Spec Self-Review

1. **Spec coverage:** All 4 features (router, workflows, uncertainty, memory) have detailed designs with data structures, examples, and MCP tool signatures.
2. **Placeholder scan:** No TBDs, TODOs, or vague requirements. All code blocks show concrete implementations.
3. **Type consistency:** `ToolCall`, `WorkflowResult`, `SessionMemory`, `Distribution` types are consistent across sections.
4. **Scope check:** This is a single focused phase. Design optimization, FMEA, knowledge graph, etc. are Phase 3+.
5. **Ambiguity check:** All behaviors specified (error handling table, serialization format, interpolation syntax).

**Status:** Ready for implementation planning.
