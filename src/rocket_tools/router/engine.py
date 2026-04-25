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
        matched = any(re.search(pattern, query_lower, re.IGNORECASE) for pattern in config.patterns)
        scores.append((tool_name, 1.0 if matched else 0.0))
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

    if missing:
        return ClarificationRequest(
            message=f"I think you want '{best_tool}' but I'm missing: {missing}",
            possible_tools=[best_tool],
            missing_params=missing,
        )

    confidence = best_score
    if len(params) < len(config.param_extractors):
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
