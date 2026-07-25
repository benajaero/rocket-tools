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


def run_with_uncertainty(
    tool_name: str,
    params: dict,
    samples: int = 1000,
    seed: int = 42,
    sensitivity: bool = True,
) -> dict:
    _validate_sample_count(samples)
    param_samples = _resolve_param_distributions(params, samples, seed)
    results = []
    for i in range(samples):
        p = _build_param_dict(param_samples, i)
        result = _call_tool(tool_name, p)
        results.append(result)

    aggregated = _aggregate_results(results, samples)
    if sensitivity:
        aggregated["sensitivity"] = _compute_sensitivity(param_samples, results)
    return aggregated


def _flatten_samples(param_samples: dict, prefix: str = "") -> dict[str, Any]:
    """Flatten nested sample dicts to dotted keys (e.g. cross_section.width)."""
    flat: dict[str, Any] = {}
    for key, value in param_samples.items():
        name = f"{prefix}{key}"
        if isinstance(value, dict):
            flat.update(_flatten_samples(value, f"{name}."))
        else:
            flat[name] = value
    return flat


def _compute_sensitivity(param_samples: dict, results: list[dict]) -> dict[str, Any]:
    """Rank inputs by Pearson correlation with each numeric output (global SA).

    Only inputs that were actually varied (a distribution, non-zero variance) are
    ranked. A near +/-1 correlation means that input drives the output; near 0
    means it does not. This is a one-pass, variance-based sensitivity measure
    computed from the same Monte-Carlo samples used for propagation.
    """
    flat = _flatten_samples(param_samples)
    varied: dict[str, np.ndarray] = {}
    for key, arr in flat.items():
        try:
            a = np.asarray(arr, dtype=float)
        except (TypeError, ValueError):
            continue
        if a.ndim == 1 and float(np.std(a)) > 0.0:
            varied[key] = a
    if not varied or not results:
        return {}

    output_keys = [k for k, v in results[0].items() if isinstance(v, (int, float))]
    sensitivity: dict[str, Any] = {}
    for okey in output_keys:
        # Keep only samples where this output is present, numeric, AND finite. Building
        # `ovals` from the exact same predicate as `mask` keeps the two aligned (a weaker
        # ovals filter used to crash or mis-pair when a later sample was non-numeric), and
        # dropping non-finite outputs keeps the correlation from collapsing to NaN.
        mask = np.array(
            [
                okey in r and isinstance(r[okey], (int, float)) and np.isfinite(r[okey])
                for r in results
            ],
            dtype=bool,
        )
        if mask.sum() < 3:
            continue
        ovals = np.array([float(r[okey]) for r, keep in zip(results, mask) if keep], dtype=float)
        if float(np.std(ovals)) == 0.0:
            continue
        ranked: list[tuple[float, str, float]] = []
        for ikey, ivals in varied.items():
            iv = ivals[mask]
            if float(np.std(iv)) == 0.0:
                continue
            corr = float(np.corrcoef(iv, ovals)[0, 1])
            if np.isnan(corr):
                continue
            ranked.append((abs(corr), ikey, corr))
        ranked.sort(reverse=True)
        if ranked:
            sensitivity[okey] = [
                {"input": ikey, "correlation": round(corr, 4), "abs_correlation": round(abscorr, 4)}
                for abscorr, ikey, corr in ranked
            ]
    return sensitivity


def _aggregate_results(results: list[dict], samples: int) -> dict:
    if not results:
        return {"error": "No results"}

    aggregated = {}
    keys = [k for k in results[0].keys() if isinstance(results[0][k], (int, float))]

    for key in keys:
        raw = np.array(
            [r[key] for r in results if key in r and isinstance(r[key], (int, float))],
            dtype=float,
        )
        # Drop non-finite samples before aggregating: a single NaN/inf tail sample would
        # otherwise poison mean, std, min, max, and both CI bounds. Report how many were
        # dropped so the caller can judge whether the surviving statistics are trustworthy.
        values = raw[np.isfinite(raw)]
        n_dropped = int(raw.size - values.size)
        if values.size == 0:
            continue
        entry: dict[str, Any] = {
            "mean": round(float(np.mean(values)), 6),
            "std": round(float(np.std(values)), 6),
            "min": round(float(np.min(values)), 6),
            "max": round(float(np.max(values)), 6),
            "ci_95": [
                round(float(np.percentile(values, 2.5)), 6),
                round(float(np.percentile(values, 97.5)), 6),
            ],
        }
        if n_dropped:
            entry["non_finite_samples"] = n_dropped
        aggregated[key] = entry

    return {
        "samples": samples,
        "results": aggregated,
    }
