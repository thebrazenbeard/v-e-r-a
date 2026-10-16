"""Reference runtime classification and transition admission."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .arbitration import ArbitrationDecision, ArbitrationMode, ORIENT_THRESHOLD, arbitrate
from .circuit import CircuitState
from .events import EventIdentity
from .provenance import TransitionReceipt, VerifiedProvenance


RECRUIT_PRIORITY_THRESHOLD: float = 0.65
RECRUIT_COHERENCE_THRESHOLD: float = 0.60
RECRUIT_PERSISTENCE_THRESHOLD: float = 0.25
RESOLUTION_THRESHOLD: float = 0.50


class RuntimePhase(StrEnum):
    QUIESCENT = "quiescent"
    ORIENTED = "oriented"
    RECRUITED = "recruited"
    PROTECTIVE = "protective"
    RESOLVING = "resolving"


@dataclass(frozen=True, slots=True)
class RuntimeFrame:
    phase: RuntimePhase
    decision: ArbitrationDecision


def classify_phase(
    state: CircuitState,
    decision: ArbitrationDecision | None = None,
) -> RuntimePhase:
    decision = arbitrate(state) if decision is None else decision

    if state.recruitment.resolution >= RESOLUTION_THRESHOLD:
        return RuntimePhase.RESOLVING

    if decision.mode is ArbitrationMode.PROTECTIVE:
        return RuntimePhase.PROTECTIVE

    if (
        decision.priority >= RECRUIT_PRIORITY_THRESHOLD
        and state.recruitment.coherence >= RECRUIT_COHERENCE_THRESHOLD
        and state.recruitment.persistence >= RECRUIT_PERSISTENCE_THRESHOLD
    ):
        return RuntimePhase.RECRUITED

    if decision.priority >= ORIENT_THRESHOLD:
        return RuntimePhase.ORIENTED

    return RuntimePhase.QUIESCENT


def frame(state: CircuitState) -> RuntimeFrame:
    decision = arbitrate(state)
    return RuntimeFrame(phase=classify_phase(state, decision), decision=decision)


def evaluate_transition(
    *,
    before: CircuitState,
    after: CircuitState,
    provenance: VerifiedProvenance,
    event: EventIdentity,
) -> TransitionReceipt:
    """Evaluate one distinct runtime event and emit its receipt."""
    before_frame = frame(before)
    after_frame = frame(after)

    return TransitionReceipt.build(
        before=before,
        after=after,
        before_phase=before_frame.phase.value,
        after_phase=after_frame.phase.value,
        decision=after_frame.decision,
        provenance=provenance,
        event=event,
    )
