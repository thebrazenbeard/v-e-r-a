"""Auditable appraised-experience transaction for MESO-CRCT."""

from __future__ import annotations

from dataclasses import dataclass

from .appraisal import AppraisedTarget
from .circuit import CircuitState
from .events import EventIdentity
from .memory import AssociationMemory, AssociationRevision, apply_candidate
from .plasticity import PlasticityCandidate, PlasticityPolicy, propose_plasticity
from .provenance import TransitionReceipt, VerifiedProvenance
from .runtime import evaluate_transition


@dataclass(frozen=True, slots=True)
class ExperienceLearningSpec:
    association_id: str
    policy: PlasticityPolicy
    expected_version: int

    def __post_init__(self) -> None:
        if not self.association_id.strip():
            raise ValueError("association_id must be non-empty")
        if self.expected_version < 0:
            raise ValueError("expected_version must be >= 0")


@dataclass(frozen=True, slots=True)
class ExperienceTransactionResult:
    target_id: str
    after_state: CircuitState
    receipt: TransitionReceipt
    memory: AssociationMemory
    plasticity_candidate: PlasticityCandidate | None
    applied_revision: AssociationRevision | None

    @property
    def learning_applied(self) -> bool:
        return self.applied_revision is not None


def process_appraised_experience(
    *,
    before: CircuitState,
    appraised: AppraisedTarget,
    provenance: VerifiedProvenance,
    event: EventIdentity,
    memory: AssociationMemory,
    learning: ExperienceLearningSpec | None = None,
) -> ExperienceTransactionResult:
    """Bind one canonical appraisal to event/provenance and optional learning."""
    receipt = evaluate_transition(
        before=before,
        after=appraised.state,
        provenance=provenance,
        event=event,
    )

    if learning is None:
        return ExperienceTransactionResult(
            target_id=appraised.target_id,
            after_state=appraised.state,
            receipt=receipt,
            memory=memory,
            plasticity_candidate=None,
            applied_revision=None,
        )

    candidate = propose_plasticity(
        state=appraised.state,
        association_id=learning.association_id,
        receipt=receipt,
        policy=learning.policy,
    )

    if candidate.delta == 0.0:
        return ExperienceTransactionResult(
            target_id=appraised.target_id,
            after_state=appraised.state,
            receipt=receipt,
            memory=memory,
            plasticity_candidate=candidate,
            applied_revision=None,
        )

    updated_memory = apply_candidate(
        memory,
        candidate,
        expected_version=learning.expected_version,
    )
    revision = updated_memory.current(learning.association_id)
    assert revision is not None

    return ExperienceTransactionResult(
        target_id=appraised.target_id,
        after_state=appraised.state,
        receipt=receipt,
        memory=updated_memory,
        plasticity_candidate=candidate,
        applied_revision=revision,
    )
