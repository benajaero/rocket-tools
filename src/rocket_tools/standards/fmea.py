"""Failure Mode and Effects Analysis (FMEA) scaffolding.

Computes the Risk Priority Number RPN = Severity x Occurrence x Detection for each
failure mode, ranks modes by risk, and flags high-priority items. A reporting/scoring
tool over user-supplied failure modes, not a physics computation.

References:
    - MIL-STD-1629A — Procedures for Performing a FMECA.
    - SAE J1739 — Potential Failure Mode and Effects Analysis (RPN convention, 1-10 scales).
"""


def _factor(item: dict, key: str, i: int) -> int:
    """Validate and return an FMEA factor: a whole number in [1, 10].

    Rejects a missing key, a boolean, a non-numeric value, and a non-integer float
    (e.g. 9.9) rather than silently truncating it — a truncated 9.9 -> 9 would pass
    the range check and quietly corrupt the RPN. An integer-valued float (9.0) is fine.
    """
    if key not in item:
        raise ValueError(f"item {i}: missing '{key}'")
    val = item[key]
    if isinstance(val, bool) or not isinstance(val, (int, float)):
        raise ValueError(f"item {i}: {key} must be an integer in [1, 10]")
    if isinstance(val, float) and not val.is_integer():
        raise ValueError(f"item {i}: {key} must be a whole number in [1, 10], got {val}")
    iv = int(val)
    if not 1 <= iv <= 10:
        raise ValueError(f"item {i}: {key} must be in [1, 10]")
    return iv


def fmea_report(items: list[dict], rpn_threshold: int = 100) -> dict:
    """Rank failure modes by Risk Priority Number and flag high-risk items.

    Each item is a dict with ``failure_mode`` and integer ``severity``, ``occurrence``,
    and ``detection`` on 1-10 scales (optional ``function``, ``effect``, ``cause``).

    Args:
        items: The failure modes to score.
        rpn_threshold: Items with RPN >= this (or severity >= 9) are high priority.

    Returns:
        dict with the modes ranked by RPN (desc), the max/mean RPN, and the
        high-priority subset.
    """
    if not items:
        raise ValueError("at least one failure mode is required")

    scored = []
    for i, item in enumerate(items):
        s = _factor(item, "severity", i)
        o = _factor(item, "occurrence", i)
        d = _factor(item, "detection", i)
        rpn = s * o * d
        scored.append(
            {
                "function": item.get("function", ""),
                "failure_mode": item.get("failure_mode", f"mode_{i + 1}"),
                "effect": item.get("effect", ""),
                "cause": item.get("cause", ""),
                "severity": s,
                "occurrence": o,
                "detection": d,
                "rpn": rpn,
                "high_priority": rpn >= rpn_threshold or s >= 9,
            }
        )

    scored.sort(key=lambda r: r["rpn"], reverse=True)
    rpns = [r["rpn"] for r in scored]
    high = [r for r in scored if r["high_priority"]]

    return {
        "num_items": len(scored),
        "max_rpn": max(rpns),
        "mean_rpn": round(sum(rpns) / len(rpns), 2),
        "rpn_threshold": rpn_threshold,
        "num_high_priority": len(high),
        "items_ranked": scored,
        "high_priority": high,
    }
