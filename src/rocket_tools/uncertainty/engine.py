"""Monte Carlo uncertainty propagation engine."""

from typing import Any

import numpy as np

from rocket_tools.utils.validation import ValidationError
from rocket_tools.workflows.engine import _call_tool

from .distributions import Distribution, _validate_sample_count


def _is_distribution(value: Any) -> bool:
    return isinstance(value, dict) and "distribution" in value


def _resolve_value(value: Any, n: int, rng: np.random.Generator) -> Any:
    if _is_distribution(value):
        dist = Distribution.from_dict(value)
        return dist.sample(n, int(rng.integers(0, 2**31)))
    if isinstance(value, dict):
        return {k: _resolve_value(v, n, rng) for k, v in value.items()}
    return np.full(n, value, dtype=object)


def _resolve_param_distributions(params: dict, n: int, seed: int) -> dict[str, Any]:
    if not isinstance(params, dict):
        raise ValidationError("Uncertainty params must be a dictionary", "params", "dict")
    _validate_sample_count(n)
    rng = np.random.default_rng(seed)
    return {key: _resolve_value(value, n, rng) for key, value in params.items()}


def _sample_value(value: Any, idx: int) -> Any:
    if isinstance(value, dict):
        return {k: _sample_value(v, idx) for k, v in value.items()}
    return value[idx]


def _build_param_dict(param_samples: dict, idx: int) -> dict:
    return {key: _sample_value(value, idx) for key, value in param_samples.items()}


def run_with_uncertainty(tool_name: str, params: dict, samples: int = 1000, seed: int = 42) -> dict:
    _validate_sample_count(samples)
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
        values = np.array(
            [r[key] for r in results if key in r and isinstance(r[key], (int, float))]
        )
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
