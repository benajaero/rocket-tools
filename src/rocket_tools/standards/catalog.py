"""Static catalog of aerospace design standards referenced by rocket-tools.

A lightweight, citable index of the standards that inform the factors of safety,
margin conventions, and reliability methods used across the tools. Exposed via
``list_standards`` and the ``rocket-tools://standards`` MCP resource.
"""

from typing import Any

_STANDARDS: dict[str, dict[str, Any]] = {
    "FAR-25.303": {
        "title": "14 CFR 25.303 — Factor of safety",
        "domain": "structures",
        "scope": (
            "Transport-category aircraft: 1.5 ultimate factor of safety unless otherwise specified."
        ),
        "typical_factors": {"ultimate": 1.5},
    },
    "FAA-AC-25.571-1D": {
        "title": "FAA AC 25.571-1D — Damage Tolerance and Fatigue Evaluation of Structure",
        "domain": "structures",
        "scope": "Fatigue and damage-tolerance evaluation of transport airframe structure.",
        "typical_factors": {"fatigue_life": 4.0},
    },
    "NASA-STD-5001": {
        "title": (
            "NASA-STD-5001B — Structural Design and Test Factors of Safety for Spaceflight Hardware"
        ),
        "domain": "structures",
        "scope": "Design and test factors of safety for spaceflight hardware.",
        "typical_factors": {"yield": 1.25, "ultimate": 1.4},
    },
    "MMPDS-15": {
        "title": "MMPDS-15 — Metallic Materials Properties Development and Standardization",
        "domain": "materials",
        "scope": "Statistically-based (A/B-basis) allowables for metallic aerospace materials.",
        "typical_factors": {},
    },
    "MIL-STD-1629A": {
        "title": (
            "MIL-STD-1629A — Procedures for Performing a Failure Mode, Effects and "
            "Criticality Analysis"
        ),
        "domain": "reliability",
        "scope": "FMEA/FMECA methodology; risk priority via severity/occurrence/detection.",
        "typical_factors": {},
    },
    "SAE-J1739": {
        "title": "SAE J1739 — Potential Failure Mode and Effects Analysis",
        "domain": "reliability",
        "scope": "FMEA with Risk Priority Number RPN = Severity x Occurrence x Detection (1-10).",
        "typical_factors": {},
    },
}


def list_standards() -> dict:
    """Enumerate the standards catalog (id, title, domain, scope, typical factors)."""
    return {
        "standards": [{"id": sid, **entry} for sid, entry in sorted(_STANDARDS.items())],
        "count": len(_STANDARDS),
    }
