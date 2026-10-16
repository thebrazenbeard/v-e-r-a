"""Grounded semantic-relevance appraisal.

A source may claim that something is important. That assertion is recorded but
does not itself become semantic relevance. Relevance is grounded in the
receiving system's context, goals, memory, or unresolved model state.
"""

from __future__ import annotations

from dataclasses import dataclass
import math


def _unit(value: float, *, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return min(1.0, max(0.0, value))


@dataclass(frozen=True, slots=True)
class SemanticEvidence:
    context_relevance: float = 0.0
    goal_relevance: float = 0.0
    memory_relevance: float = 0.0
    unresolved_relevance: float = 0.0
    source_asserts_importance: bool = False

    def __post_init__(self) -> None:
        for name in (
            "context_relevance",
            "goal_relevance",
            "memory_relevance",
            "unresolved_relevance",
        ):
            object.__setattr__(self, name, _unit(getattr(self, name), name=name))


@dataclass(frozen=True, slots=True)
class SemanticAssessment:
    relevance: float
    grounded_drivers: tuple[str, ...]
    untrusted_importance_claim: bool


def assess_semantic_relevance(evidence: SemanticEvidence) -> SemanticAssessment:
    """Derive grounded relevance without rewarding self-asserted importance."""
    candidates = (
        ("context_relevance", evidence.context_relevance),
        ("goal_relevance", evidence.goal_relevance),
        ("memory_relevance", evidence.memory_relevance),
        ("unresolved_relevance", evidence.unresolved_relevance),
    )
    relevance = max(value for _, value in candidates)
    drivers = tuple(
        name
        for name, value in candidates
        if value == relevance and value > 0.0
    )
    return SemanticAssessment(
        relevance=relevance,
        grounded_drivers=drivers,
        untrusted_importance_claim=evidence.source_asserts_importance,
    )
