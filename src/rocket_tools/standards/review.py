"""Design-review margin rollup across a set of structural items.

Aggregates margins of safety (or allowable/actual pairs) into a single go/no-go
report: the governing (minimum) margin, the failing items, and a PASS/FAIL verdict.
Reuses :func:`rocket_tools.structural.margin.margin_of_safety` for stress-pair items
rather than recomputing the definition.

Reference:
    - MIL-HDBK-5J / MMPDS-15 and FAR 25.303: margin of safety MS = allowable/(FoS*actual) - 1.
"""

from rocket_tools.structural.margin import margin_of_safety


def design_review_report(items: list[dict], min_acceptable_margin: float = 0.0) -> dict:
    """Roll up margins of safety across design items into a go/no-go report.

    Each item is a dict with ``name`` and either a precomputed ``margin_of_safety``,
    or an ``allowable_stress_pa``/``actual_stress_pa`` pair (with optional
    ``factor_of_safety``, default 1.5) from which the margin is computed.

    Args:
        items: The design items to roll up.
        min_acceptable_margin: Margins below this flag the item as failing (default 0).

    Returns:
        dict with a per-item table, the governing (minimum) margin and item, the number
        of failing items, and a PASS/FAIL verdict.
    """
    if not items:
        raise ValueError("at least one item is required")

    rows = []
    for i, item in enumerate(items):
        name = item.get("name", f"item_{i + 1}")
        if item.get("margin_of_safety") is not None:
            ms = float(item["margin_of_safety"])
        elif (
            item.get("allowable_stress_pa") is not None and item.get("actual_stress_pa") is not None
        ):
            res = margin_of_safety(
                allowable_stress_pa=float(item["allowable_stress_pa"]),
                actual_stress_pa=float(item["actual_stress_pa"]),
                factor_of_safety=float(item.get("factor_of_safety", 1.5)),
                failure_mode=item.get("failure_mode", "yield"),
            )
            ms = float(res["margin_of_safety"])
        else:
            raise ValueError(
                f"item '{name}': provide margin_of_safety or allowable_stress_pa + actual_stress_pa"
            )
        rows.append(
            {
                "name": name,
                "margin_of_safety": round(ms, 4),
                "pass": ms >= min_acceptable_margin,
            }
        )

    governing = min(rows, key=lambda r: r["margin_of_safety"])
    num_failing = sum(1 for r in rows if not r["pass"])

    return {
        "summary": {
            "num_items": len(rows),
            "num_failing": num_failing,
            "min_margin": governing["margin_of_safety"],
            "governing_item": governing["name"],
            "min_acceptable_margin": min_acceptable_margin,
        },
        "items": rows,
        "verdict": "PASS" if num_failing == 0 else "FAIL",
    }
