"""Router engine: classify intent + extract parameters."""

import re
from dataclasses import dataclass
from typing import Any

from rocket_tools.config import settings
from rocket_tools.materials.database import material_lookup

from .intents import INTENT_REGISTRY


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
        matched_patterns = [
            p for p in config.patterns if re.search(p, query_lower, re.IGNORECASE)
        ]
        score = 1.0 if matched_patterns else 0.0
        # Reward queries that contain multiple relevant keywords for the tool.
        if len(matched_patterns) > 1:
            score += 0.05 * (len(matched_patterns) - 1)
        # Reward presence of tool-name words (capped so generic terms don't dominate).
        tool_words = [w for w in tool_name.replace("_", " ").split() if len(w) > 2]
        matched_words = [w for w in tool_words if w in query_lower]
        score += min(0.05 * len(matched_words), 0.2)
        scores.append((tool_name, score))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores


def extract_params(query: str, config) -> dict[str, Any]:
    params = {}
    for param_name, extractor in config.param_extractors.items():
        value = extractor(query)
        if value is not None:
            params[param_name] = value
    return params


def route_query(query: str, session=None) -> ToolCall | ClarificationRequest:
    if not isinstance(query, str) or not query.strip():
        return ClarificationRequest(
            message="Please provide an engineering query with specific numbers and units.",
            possible_tools=list(INTENT_REGISTRY.keys()),
            missing_params=[],
        )

    scores = classify_intent(query)
    if not scores or scores[0][1] == 0.0:
        return ClarificationRequest(
            message=(
                "I couldn't understand your query. Try rephrasing with specific numbers and units."
            ),
            possible_tools=list(INTENT_REGISTRY.keys()),
            missing_params=[],
        )

    best_tool, best_score = scores[0]
    config = INTENT_REGISTRY[best_tool]
    params = extract_params(query, config)

    session_defaults = {}
    if session is not None:
        session_defaults = getattr(session, "parameters", {}).get(best_tool, {})
        if not isinstance(session_defaults, dict):
            session_defaults = {}

    merged = {**session_defaults, **config.defaults, **params}

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
    if config.param_extractors:
        confidence *= len(params) / len(config.param_extractors)

    if session is not None:
        confidence = max(confidence, settings.router_session_confidence_floor)

    confidence = min(confidence, 1.0)

    if confidence < settings.router_confidence_threshold:
        msg = (
            f"I think you want '{best_tool}' but I'm not confident enough "
            f"(confidence={confidence:.2f}). Could you provide more details?"
        )
        return ClarificationRequest(
            message=msg,
            possible_tools=[best_tool],
            missing_params=missing,
        )

    return ToolCall(
        tool_name=best_tool,
        params=merged,
        confidence=round(confidence, 2),
        reasoning=f"Matched intent '{best_tool}' with confidence {confidence:.2f}",
    )
