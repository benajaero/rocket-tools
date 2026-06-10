"""Workflow execution engine with safe interpolation."""

from dataclasses import dataclass
from typing import Any

from rocket_tools.utils.safe_eval import safe_eval
from rocket_tools.utils.validation import ToolError


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


class _DotDict:
    """Wrapper to allow attribute-style access on dicts for safe_eval."""

    def __init__(self, data):
        self._data = data

    def __getattr__(self, name):
        val = self._data[name]
        if isinstance(val, dict):
            return _DotDict(val)
        return val

    def __getitem__(self, name):
        return self.__getattr__(name)


def resolve_interpolation(value: Any, context: dict) -> Any:
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        path = value[2:-1]
        # Support simple arithmetic expressions like inputs.mass_kg * 9.80665
        if any(op in path for op in ("*", "+", "-", "/", "(", ")", "==", "!=", "<", ">")):
            eval_ctx = {k: _DotDict(v) if isinstance(v, dict) else v for k, v in context.items()}
            try:
                return safe_eval(path, eval_ctx)
            except ToolError:
                raise
            except Exception as e:
                raise ToolError(
                    f"Cannot evaluate '{path}': {e}",
                    error_code="INVALID_EXPRESSION",
                    parameter="interpolation",
                    constraint="valid arithmetic expression",
                ) from e
        parts = path.split(".")
        current = context
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                raise ToolError(
                    f"Cannot resolve '{path}'",
                    error_code="MISSING_REFERENCE",
                    parameter="interpolation",
                    constraint="valid reference",
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
        trace.append(
            {
                "step_id": step.id,
                "tool": step.tool,
                "params": resolved_params,
                "result": result,
            }
        )

    outputs = {}
    for out_expr in workflow.outputs:
        key = out_expr.replace("${", "").replace("}", "").replace(".", "_")
        outputs[key] = resolve_interpolation(out_expr, context)

    return WorkflowResult(outputs=outputs, trace=trace)


def _call_tool(tool_name: str, params: dict) -> dict:
    from rocket_tools import aerodynamics, materials, structural

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
    elif tool_name == "skin_friction_coefficient":
        return aerodynamics.skin_friction_coefficient(**params)
    elif tool_name == "unit_convert":
        from rocket_tools.utils import unit_convert

        return unit_convert(**params)
    else:
        raise ToolError(
            f"Unknown tool: {tool_name}",
            error_code="UNKNOWN_TOOL",
            parameter="tool_name",
            constraint=(
                "one of: beam_analysis, aero_analysis, material_lookup, "
                "isa_atmosphere, reynolds_number, mach_number, dynamic_pressure, "
                "lift_coefficient, drag_coefficient, skin_friction_coefficient, "
                "unit_convert"
            ),
        )
