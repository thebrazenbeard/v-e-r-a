"""Versioned association-memory owner for MESO-CRCT.

This module owns only bounded learned association strengths. It does not admit
autobiographical memories, identity facts, relationship state, or arbitrary
text. Updates are append-only revisions tied to plasticity candidates and their
verified transition receipt lineage.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import math

from .plasticity import PlasticityCandidate
from .review import AssociationReviewRegistry
from .review_evidence import (
    ReviewEvidence,
    ReviewEvidenceAssessment,
    ReviewEvidenceLedger,
    ReviewEvidenceMismatch,
    ReviewEvidenceNotRegistered,
    ReviewEvidencePolicy,
    assess_review_evidence,
)


def _signed_unit(value: float, *, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return min(1.0, max(-1.0, value))


@dataclass(frozen=True, slots=True)
class AssociationRevision:
    association_id: str
    version: int
    strength: float
    previous_strength: float
    applied_delta: float
    transition_receipt_id: str
    operation: str
    parent_revision_id: str | None
    revision_id: str

    def __post_init__(self) -> None:
        if not self.association_id.strip():
            raise ValueError("association_id must be non-empty")
        if self.version < 1:
            raise ValueError("version must be >= 1")
        object.__setattr__(self, "strength", _signed_unit(self.strength, name="strength"))
        object.__setattr__(
            self,
            "previous_strength",
            _signed_unit(self.previous_strength, name="previous_strength"),
        )
        object.__setattr__(
            self,
            "applied_delta",
            _signed_unit(self.applied_delta, name="applied_delta"),
        )
        if not self.transition_receipt_id.strip():
            raise ValueError("transition_receipt_id must be non-empty")
        if self.operation not in {"apply", "revert"}:
            raise ValueError("operation must be 'apply' or 'revert'")
        if not self.revision_id.strip():
            raise ValueError("revision_id must be non-empty")


class MemoryVersionConflict(ValueError):
    pass


class PlasticityReplayError(ValueError):
    pass


class PlasticityNoOpError(ValueError):
    pass


class AssociationIntegrityError(ValueError):
    pass


class AssociationNotFound(KeyError):
    pass


def _revision_id(
    *,
    association_id: str,
    version: int,
    strength: float,
    previous_strength: float,
    applied_delta: float,
    transition_receipt_id: str,
    operation: str,
    parent_revision_id: str | None,
) -> str:
    payload = json.dumps(
        {
            "association_id": association_id,
            "version": version,
            "strength": strength,
            "previous_strength": previous_strength,
            "applied_delta": applied_delta,
            "transition_receipt_id": transition_receipt_id,
            "operation": operation,
            "parent_revision_id": parent_revision_id,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _validate_integrity(revisions: tuple[AssociationRevision, ...]) -> None:
    latest: dict[str, AssociationRevision] = {}
    used_receipts: set[tuple[str, str]] = set()

    for revision in revisions:
        prior = latest.get(revision.association_id)
        expected_version = 1 if prior is None else prior.version + 1
        expected_previous = 0.0 if prior is None else prior.strength
        expected_parent = None if prior is None else prior.revision_id

        if revision.version != expected_version:
            raise AssociationIntegrityError(
                f"invalid version chain for {revision.association_id}"
            )
        if revision.previous_strength != expected_previous:
            raise AssociationIntegrityError(
                f"invalid previous strength for {revision.association_id}"
            )
        if revision.parent_revision_id != expected_parent:
            raise AssociationIntegrityError(
                f"invalid parent revision for {revision.association_id}"
            )
        if revision.operation == "revert" and prior is None:
            raise AssociationIntegrityError(
                "a revert cannot be the first association revision"
            )

        expected_id = _revision_id(
            association_id=revision.association_id,
            version=revision.version,
            strength=revision.strength,
            previous_strength=revision.previous_strength,
            applied_delta=revision.applied_delta,
            transition_receipt_id=revision.transition_receipt_id,
            operation=revision.operation,
            parent_revision_id=revision.parent_revision_id,
        )
        if revision.revision_id != expected_id:
            raise AssociationIntegrityError(
                f"invalid revision digest for {revision.association_id}"
            )

        if revision.operation == "apply":
            receipt_key = (
                revision.association_id,
                revision.transition_receipt_id,
            )
            if receipt_key in used_receipts:
                raise AssociationIntegrityError(
                    "duplicate transition receipt for association"
                )
            used_receipts.add(receipt_key)

        latest[revision.association_id] = revision


@dataclass(frozen=True, slots=True)
class AssociationMemory:
    """Immutable append-only association revision log."""

    revisions: tuple[AssociationRevision, ...] = ()
    reviews: AssociationReviewRegistry = field(
        default_factory=AssociationReviewRegistry
    )
    review_evidence: ReviewEvidenceLedger = field(
        default_factory=ReviewEvidenceLedger
    )

    def __post_init__(self) -> None:
        _validate_integrity(self.revisions)
        self._validate_review_integrity()

    def _validate_review_integrity(self) -> None:
        for record in self.reviews.records:
            try:
                items = self.review_evidence.items_for_ids(
                    record.evidence_ids,
                    association_id=record.association_id,
                    memory_revision_id=record.memory_revision_id,
                )
            except (ReviewEvidenceNotRegistered, ReviewEvidenceMismatch) as exc:
                raise AssociationIntegrityError(
                    f"review evidence integrity failed for {record.association_id}"
                ) from exc

            recomputed = assess_review_evidence(
                items,
                policy=ReviewEvidencePolicy(
                    minimum_supporting_holdout_events=(
                        record.required_supporting_holdout_events
                    )
                ),
            )
            if (
                recomputed.assessment_id != record.assessment_id
                or recomputed.risk_class is not record.risk_class
            ):
                raise AssociationIntegrityError(
                    f"review assessment integrity failed for {record.association_id}"
                )

    def current(self, association_id: str) -> AssociationRevision | None:
        for revision in reversed(self.revisions):
            if revision.association_id == association_id:
                return revision
        return None

    def current_strength(self, association_id: str) -> float:
        current = self.current(association_id)
        return 0.0 if current is None else current.strength

    def current_version(self, association_id: str) -> int:
        current = self.current(association_id)
        return 0 if current is None else current.version

    def receipt_used(
        self,
        transition_receipt_id: str,
        association_id: str,
    ) -> bool:
        return any(
            revision.transition_receipt_id == transition_receipt_id
            and revision.association_id == association_id
            and revision.operation == "apply"
            for revision in self.revisions
        )

    def history(self, association_id: str) -> tuple[AssociationRevision, ...]:
        return tuple(
            revision
            for revision in self.revisions
            if revision.association_id == association_id
        )


def apply_candidate(
    memory: AssociationMemory,
    candidate: PlasticityCandidate,
    *,
    expected_version: int,
) -> AssociationMemory:
    """Apply one candidate as a new immutable association revision."""
    current_version = memory.current_version(candidate.association_id)
    if expected_version != current_version:
        raise MemoryVersionConflict(
            f"expected version {expected_version}, current version {current_version}"
        )

    if candidate.delta == 0.0:
        raise PlasticityNoOpError(
            "zero-delta plasticity candidates are not persistent learning events"
        )

    if memory.receipt_used(
        candidate.transition_receipt_id,
        candidate.association_id,
    ):
        raise PlasticityReplayError(
            "transition receipt already used for this association"
        )

    prior = memory.current(candidate.association_id)
    previous = 0.0 if prior is None else prior.strength
    parent_revision_id = None if prior is None else prior.revision_id
    strength = _signed_unit(
        previous + candidate.delta,
        name="resulting_strength",
    )
    version = current_version + 1
    revision_id = _revision_id(
        association_id=candidate.association_id,
        version=version,
        strength=strength,
        previous_strength=previous,
        applied_delta=candidate.delta,
        transition_receipt_id=candidate.transition_receipt_id,
        operation="apply",
        parent_revision_id=parent_revision_id,
    )
    revision = AssociationRevision(
        association_id=candidate.association_id,
        version=version,
        strength=strength,
        previous_strength=previous,
        applied_delta=candidate.delta,
        transition_receipt_id=candidate.transition_receipt_id,
        operation="apply",
        parent_revision_id=parent_revision_id,
        revision_id=revision_id,
    )
    return AssociationMemory(
        revisions=memory.revisions + (revision,),
        reviews=memory.reviews,
        review_evidence=memory.review_evidence,
    )


def revert_last(
    memory: AssociationMemory,
    association_id: str,
    *,
    expected_version: int,
) -> AssociationMemory:
    """Append a reversal revision instead of deleting history."""
    history = memory.history(association_id)
    if not history:
        raise AssociationNotFound(association_id)

    current = history[-1]
    if expected_version != current.version:
        raise MemoryVersionConflict(
            f"expected version {expected_version}, current version {current.version}"
        )

    prior_strength = history[-2].strength if len(history) >= 2 else 0.0
    version = current.version + 1
    applied_delta = prior_strength - current.strength
    receipt_ref = current.transition_receipt_id
    parent_revision_id = current.revision_id
    revision_id = _revision_id(
        association_id=association_id,
        version=version,
        strength=prior_strength,
        previous_strength=current.strength,
        applied_delta=applied_delta,
        transition_receipt_id=receipt_ref,
        operation="revert",
        parent_revision_id=parent_revision_id,
    )

    revision = AssociationRevision(
        association_id=association_id,
        version=version,
        strength=prior_strength,
        previous_strength=current.strength,
        applied_delta=applied_delta,
        transition_receipt_id=receipt_ref,
        operation="revert",
        parent_revision_id=parent_revision_id,
        revision_id=revision_id,
    )
    return AssociationMemory(
        revisions=memory.revisions + (revision,),
        reviews=memory.reviews,
        review_evidence=memory.review_evidence,
    )



def register_review_evidence(
    memory: AssociationMemory,
    evidence: ReviewEvidence,
) -> AssociationMemory:
    """Admit one review-evidence item against the exact current revision."""
    current = memory.current(evidence.association_id)
    if current is None:
        raise AssociationNotFound(evidence.association_id)
    if current.revision_id != evidence.memory_revision_id:
        raise ReviewEvidenceMismatch(
            "review evidence does not bind the current association revision"
        )
    ledger = memory.review_evidence.register(evidence)
    return AssociationMemory(
        revisions=memory.revisions,
        reviews=memory.reviews,
        review_evidence=ledger,
    )


def quarantine_association(
    memory: AssociationMemory,
    association_id: str,
    *,
    assessment: ReviewEvidenceAssessment,
) -> AssociationMemory:
    """Quarantine the exact current revision from evidence assessment."""
    current = memory.current(association_id)
    if current is None:
        raise AssociationNotFound(association_id)
    memory.review_evidence.validate_assessment(assessment)
    reviews = memory.reviews.quarantine(
        association_id=association_id,
        memory_revision_id=current.revision_id,
        assessment=assessment,
    )
    return AssociationMemory(
        revisions=memory.revisions,
        reviews=reviews,
        review_evidence=memory.review_evidence,
    )


def release_association(
    memory: AssociationMemory,
    association_id: str,
    *,
    assessment: ReviewEvidenceAssessment,
) -> AssociationMemory:
    """Admit the exact current revision only from clear review evidence."""
    current = memory.current(association_id)
    if current is None:
        raise AssociationNotFound(association_id)
    memory.review_evidence.validate_assessment(assessment)
    reviews = memory.reviews.release(
        association_id=association_id,
        memory_revision_id=current.revision_id,
        assessment=assessment,
    )
    return AssociationMemory(
        revisions=memory.revisions,
        reviews=reviews,
        review_evidence=memory.review_evidence,
    )
