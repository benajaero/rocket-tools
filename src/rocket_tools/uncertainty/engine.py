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
