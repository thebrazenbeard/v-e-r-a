"""Typed salience, learning, and recruitment primitives for meso-crct.

The point of this module is semantic separation.  It intentionally does not
collapse meaning, attention, wanting, learning, and pleasure into one reward
number.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum
import math


_MIN_UNIT = 0.0
_MAX_UNIT = 1.0
_MIN_SIGNED = -1.0
_MAX_SIGNED = 1.0


def _finite(value: float, *, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _unit(value: float, *, name: str) -> float:
    value = _finite(value, name=name)
    return min(_MAX_UNIT, max(_MIN_UNIT, value))


def _signed_unit(value: float, *, name: str) -> float:
    value = _finite(value, name=name)
    return min(_MAX_SIGNED, max(_MIN_SIGNED, value))


class SignalKind(StrEnum):
    """Operational signal names; none are aliases for plain 'salience'."""

    PERCEPTUAL_SALIENCE = "perceptual_salience"
    SEMANTIC_RELEVANCE = "semantic_relevance"
    MOTIVATIONAL_SALIENCE = "motivational_salience"
    INCENTIVE_SALIENCE = "incentive_salience"
    EPISTEMIC_VALUE = "epistemic_value"
    ATTENTIONAL_PRIORITY = "attentional_priority"


@dataclass(frozen=True, slots=True)
class SalienceState:
    """Independent bounded channels that can contribute to prioritization."""

    perceptual_salience: float = 0.0
    semantic_relevance: float = 0.0
    motivational_salience: float = 0.0
    incentive_salience: float = 0.0
    epistemic_value: float = 0.0
    attentional_priority: float = 0.0

    def __post_init__(self) -> None:
        for name in (
            "perceptual_salience",
            "semantic_relevance",
            "motivational_salience",
            "incentive_salience",
            "epistemic_value",
            "attentional_priority",
        ):
            object.__setattr__(self, name, _unit(getattr(self, name), name=name))

    def with_signals(self, **signals: float) -> "SalienceState":
        """Return an updated state while preserving type/range checks."""
        unknown = set(signals) - {kind.value for kind in SignalKind}
        if unknown:
            names = ", ".join(sorted(unknown))
            raise KeyError(f"unknown salience signal(s): {names}")
        return replace(self, **signals)


@dataclass(frozen=True, slots=True)
class LearningState:
    """Learning-related state kept separate from hedonic state."""

    prediction_error: float = 0.0
    novelty: float = 0.0
    learning_progress: float = 0.0
    satiation: float = 0.0

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "prediction_error",
            _signed_unit(self.prediction_error, name="prediction_error"),
        )
        for name in ("novelty", "learning_progress", "satiation"):
            object.__setattr__(self, name, _unit(getattr(self, name), name=name))


@dataclass(frozen=True, slots=True)
class RecruitmentState:
    """Transient cross-system recruitment without domain-specific semantics."""

    activation: float = 0.0
    coherence: float = 0.0
    persistence: float = 0.0
    resolution: float = 0.0

    def __post_init__(self) -> None:
        for name in ("activation", "coherence", "persistence", "resolution"):
            object.__setattr__(self, name, _unit(getattr(self, name), name=name))
