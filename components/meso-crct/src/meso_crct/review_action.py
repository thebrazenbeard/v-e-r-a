"""Non-mutating review-action proposals from evidence assessments."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from .review import ReviewDisposition
from .review_evidence import (
    ReviewEvidenceAssessment,
    ReviewEvidenceLedger,
    ReviewRiskClass,
)

if TYPE_CHECKING:
    from .memory import AssociationMemory


class ReviewActionKind(StrEnum):
    QUARANTINE = "quarantine"
    RELEASE = "release"
    HOLD = "hold"


class ReviewActionStaleError(ValueError):
    pass


_ACTION_PROPOSAL_TOKEN = object()


@dataclass(frozen=True, slots=True, init=False)
class ReviewActionProposal:
    association_id: str
    memory_revision_id: str
    assessment_id: str
    action: ReviewActionKind
    risk_class: ReviewRiskClass
    evidence_ids: tuple[str, ...]
    evidence_ledger_fingerprint: str
    current_disposition: ReviewDisposition | None
    mutation_authorized: bool

    def __init__(
        self,
        *,
        association_id: str,
        memory_revision_id: str,
        assessment_id: str,
        action: ReviewActionKind,
        risk_class: ReviewRiskClass,
        evidence_ids: tuple[str, ...],
        evidence_ledger_fingerprint: str,
        current_disposition: ReviewDisposition | None,
        _token: object | None = None,
    ) -> None:
        if _token is not _ACTION_PROPOSAL_TOKEN:
            raise TypeError(
                "ReviewActionProposal must be created by propose_review_action"
            )
        if not evidence_ledger_fingerprint.strip():
            raise ValueError("evidence_ledger_fingerprint must be non-empty")
        object.__setattr__(self, "association_id", association_id)
        object.__setattr__(self, "memory_revision_id", memory_revision_id)
        object.__setattr__(self, "assessment_id", assessment_id)
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "risk_class", risk_class)
        object.__setattr__(self, "evidence_ids", tuple(evidence_ids))
        object.__setattr__(
            self,
            "evidence_ledger_fingerprint",
            evidence_ledger_fingerprint,
        )
        object.__setattr__(self, "current_disposition", current_disposition)
        object.__setattr__(self, "mutation_authorized", False)

    @property
    def can_mutate(self) -> bool:
        return False


def propose_review_action(
    assessment: ReviewEvidenceAssessment,
    *,
    evidence_ledger: ReviewEvidenceLedger,
    current_disposition: ReviewDisposition | None = None,
) -> ReviewActionProposal:
    """Map admitted evidence state to a non-mutating governance proposal."""
    evidence_ledger.validate_assessment(assessment)

    if assessment.risk_class in {
        ReviewRiskClass.CONTRADICTED,
        ReviewRiskClass.SUSPECTED_OVERGENERALIZATION,
    }:
        action = (
            ReviewActionKind.HOLD
            if current_disposition is ReviewDisposition.QUARANTINED
            else ReviewActionKind.QUARANTINE
        )
    elif assessment.risk_class is ReviewRiskClass.CLEAR:
        action = (
            ReviewActionKind.RELEASE
            if current_disposition is ReviewDisposition.QUARANTINED
            else ReviewActionKind.HOLD
        )
    else:
        action = ReviewActionKind.HOLD

    return ReviewActionProposal(
        association_id=assessment.association_id,
        memory_revision_id=assessment.memory_revision_id,
        assessment_id=assessment.assessment_id,
        action=action,
        risk_class=assessment.risk_class,
        evidence_ids=assessment.evidence_ids,
        evidence_ledger_fingerprint=evidence_ledger.fingerprint,
        current_disposition=current_disposition,
        _token=_ACTION_PROPOSAL_TOKEN,
    )


def validate_review_action_proposal(
    memory: "AssociationMemory",
    proposal: ReviewActionProposal,
    assessment: ReviewEvidenceAssessment,
) -> None:
    """Fail if a proposal no longer matches current memory/review/evidence state."""
    current = memory.current(proposal.association_id)
    if current is None or current.revision_id != proposal.memory_revision_id:
        raise ReviewActionStaleError(
            "review proposal no longer matches current learned revision"
        )

    current_review = memory.reviews.current(proposal.association_id)
    current_disposition = (
        None if current_review is None else current_review.disposition
    )
    if current_disposition is not proposal.current_disposition:
        raise ReviewActionStaleError(
            "review proposal no longer matches current review disposition"
        )

    if memory.review_evidence.fingerprint != proposal.evidence_ledger_fingerprint:
        raise ReviewActionStaleError(
            "review proposal no longer matches current evidence ledger"
        )

    if assessment.assessment_id != proposal.assessment_id:
        raise ReviewActionStaleError(
            "review proposal assessment ID does not match supplied assessment"
        )

    memory.review_evidence.validate_assessment(assessment)
    expected = propose_review_action(
        assessment,
        evidence_ledger=memory.review_evidence,
        current_disposition=current_disposition,
    )
    if expected != proposal:
        raise ReviewActionStaleError(
            "review proposal no longer matches current derived recommendation"
        )
