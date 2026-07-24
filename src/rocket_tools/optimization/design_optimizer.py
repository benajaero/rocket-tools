"""General single-variable design optimizer over any computational tool.

The natural generalization of ``parameter_sweep`` from a grid scan to an optimizer:
it evaluates any tool in the dispatch registry across one variable and finds the value
that minimizes or maximizes one output key, using a golden-section search (pure numpy,
no scipy). The full evaluated trace is returned so a non-unimodal response is visible
rather than silently mis-optimized.

Golden-section assumes the objective is unimodal on the interval; inspect the returned
``trace`` if the response may have multiple optima.
"""

from rocket_tools.utils.validation import ToolError

_INV_PHI = (5.0**0.5 - 1.0) / 2.0  # 1/phi ~ 0.618
_INV_PHI2 = (3.0 - 5.0**0.5) / 2.0  # 1/phi^2 ~ 0.382


def optimize_design(
    tool_name: str,
    fixed_params: dict,
    variable: str,
    bounds: list[float],
    objective_key: str,
    sense: str = "max",
    iterations: int = 40,
) -> dict:
    """Optimize one output of any tool over a single input variable.

    Args:
        tool_name: A computational tool in the dispatch registry.
        fixed_params: The tool's other arguments held constant.
        variable: The name of the input to vary.
        bounds: [low, high] search interval for ``variable``.
        objective_key: The output-dict key to optimize.
        sense: "max" or "min".
        iterations: Golden-section iterations (interval shrinks by ~0.618 each).

    Returns:
        dict with the optimal variable value, the objective value there, the tool's
        full output at the optimum, and the evaluated ``trace``.
    """
    from rocket_tools.workflows.engine import _call_tool

    if sense not in ("max", "min"):
        raise ValueError("sense must be 'max' or 'min'")
    if len(bounds) != 2 or bounds[0] >= bounds[1]:
        raise ValueError("bounds must be [low, high] with low < high")
    if iterations < 1:
        raise ValueError("iterations must be >= 1")

    trace: list[dict] = []
    sign = 1.0 if sense == "max" else -1.0

    def objective(x: float) -> float:
        params = dict(fixed_params)
        params[variable] = x
        result = _call_tool(tool_name, params)
        if not isinstance(result, dict) or objective_key not in result:
            raise ToolError(
                f"objective_key '{objective_key}' not in output of '{tool_name}'",
                error_code="INVALID_PARAMETER",
                parameter="objective_key",
                constraint="one of the tool's numeric output keys",
            )
        val = result[objective_key]
        if not isinstance(val, (int, float)):
            raise ToolError(
                f"output '{objective_key}' is not numeric",
                error_code="INVALID_PARAMETER",
                parameter="objective_key",
                constraint="numeric output",
            )
        trace.append({"value": round(float(x), 6), "objective": round(float(val), 6)})
        return sign * float(val)

    a, b = float(bounds[0]), float(bounds[1])
    c = a + _INV_PHI2 * (b - a)
    d = a + _INV_PHI * (b - a)
    fc = objective(c)
    fd = objective(d)
    for _ in range(iterations):
        if fc > fd:  # maximizing sign*val => keep the larger side
            b, d, fd = d, c, fc
            c = a + _INV_PHI2 * (b - a)
            fc = objective(c)
        else:
            a, c, fc = c, d, fd
            d = a + _INV_PHI * (b - a)
            fd = objective(d)

    x_opt = 0.5 * (a + b)
    best = _call_tool(tool_name, {**fixed_params, variable: x_opt})
    obj_opt = float(best[objective_key])

    return {
        "tool_name": tool_name,
        "variable": variable,
        "objective_key": objective_key,
        "sense": sense,
        "optimal_value": round(x_opt, 6),
        "optimal_objective": round(obj_opt, 6),
        "optimal_result": best,
        "evaluations": len(trace),
        "trace": trace,
    }
