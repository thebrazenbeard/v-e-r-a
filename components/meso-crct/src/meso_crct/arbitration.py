"""Rule-based arbitration for typed MESO-CRCT signals.

The arbiter deliberately avoids a weighted sum across semantically different
signals. It preserves the dominant driver, records coalition support, applies
satiation only to incentive salience, and gives protection an independent
priority path.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .circuit import CircuitState
from .salience import SignalKind


PROTECTIVE_THRESHOLD: float = 0.75
ORIENT_THRESHOLD: float = 0.20
SUPPORT_MARGIN: float = 0.15


class ArbitrationMode(StrEnum):
    QUIESCENT = "quiescent"
    ORIENTING = "orienting"
    MOTIVATIONAL = "motivational"
    EPISTEMIC = "epistemic"
    PROTECTIVE = "protective"


@dataclass(frozen=True, slots=True)
class ArbitrationDecision:
    mode: ArbitrationMode
    priority: float
    dominant_driver: str | None
    supporting_drivers: tuple[str, ...]
    incentive_after_satiation: float
    prior_attentional_priority: float

    @property
    def active(self) -> bool:
        return self.mode is not ArbitrationMode.QUIESCENT


def _incentive_after_satiation(state: CircuitState) -> float:
    return state.salience.incentive_salience * (1.0 - state.learning.satiation)


def _upstream_candidates(state: CircuitState) -> tuple[tuple[str, float], ...]:
    """Return only upstream drivers.

    attentional_priority is intentionally excluded: it is a downstream
    allocation result and must not recursively reinforce itself.
    """
    return (
        (SignalKind.PERCEPTUAL_SALIENCE.value, state.salience.perceptual_salience),
        (SignalKind.SEMANTIC_RELEVANCE.value, state.salience.semantic_relevance),
        (SignalKind.MOTIVATIONAL_SALIENCE.value, state.salience.motivational_salience),
        (SignalKind.INCENTIVE_SALIENCE.value, _incentive_after_satiation(state)),
        (SignalKind.EPISTEMIC_VALUE.value, state.salience.epistemic_value),
    )


def arbitrate(state: CircuitState) -> ArbitrationDecision:
    """Select a typed priority path without scalarizing every signal together."""

    hazard = state.reward.hazard
    avoidance = state.reward.avoidance
    effective_incentive = _incentive_after_satiation(state)

    if max(hazard, avoidance) >= PROTECTIVE_THRESHOLD:
        dominant = "hazard" if hazard >= avoidance else "avoidance"
        supporting = tuple(
            name
            for name, value in (("hazard", hazard), ("avoidance", avoidance))
            if name != dominant and value >= PROTECTIVE_THRESHOLD
        )
        return ArbitrationDecision(
            mode=ArbitrationMode.PROTECTIVE,
            priority=max(hazard, avoidance),
            dominant_driver=dominant,
            supporting_drivers=supporting,
            incentive_after_satiation=effective_incentive,
            prior_attentional_priority=state.salience.attentional_priority,
        )

    candidates = _upstream_candidates(state)
    dominant, priority = max(candidates, key=lambda item: item[1])

    if priority < ORIENT_THRESHOLD:
        return ArbitrationDecision(
            mode=ArbitrationMode.QUIESCENT,
            priority=priority,
            dominant_driver=None,
            supporting_drivers=(),
            incentive_after_satiation=effective_incentive,
            prior_attentional_priority=state.salience.attentional_priority,
        )

    support_floor = max(ORIENT_THRESHOLD, priority - SUPPORT_MARGIN)
    supporting = tuple(
        name
        for name, value in candidates
        if name != dominant and value >= support_floor
    )

    if dominant in {
        SignalKind.MOTIVATIONAL_SALIENCE.value,
        SignalKind.INCENTIVE_SALIENCE.value,
    }:
        mode = ArbitrationMode.MOTIVATIONAL
    elif dominant == SignalKind.EPISTEMIC_VALUE.value:
        mode = ArbitrationMode.EPISTEMIC
    else:
        mode = ArbitrationMode.ORIENTING

    return ArbitrationDecision(
        mode=mode,
        priority=priority,
        dominant_driver=dominant,
        supporting_drivers=supporting,
        incentive_after_satiation=effective_incentive,
        prior_attentional_priority=state.salience.attentional_priority,
    )
