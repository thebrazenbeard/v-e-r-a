"""Append-only review state for learned associations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import hashlib
import json

from .review_evidence import ReviewEvidenceAssessment, ReviewRiskClass


class ReviewDisposition(StrEnum):
    ACTIVE = "active"
    QUARANTINED = "quarantined"


class ReviewAdmission(StrEnum):
    ADMITTED = "admitted"
    QUARANTINED = "quarantined"
    STALE = "stale"


class ReviewNoOpError(ValueError):
    pass


class ReviewIntegrityError(ValueError):
    pass


class ReviewAssessmentMismatch(ValueError):
    pass


class ReviewAssessmentInsufficient(ValueError):
    pass


class AssociationQuarantinedError(ValueError):
    pass


class AssociationReviewStaleError(ValueError):
    pass


_REVIEW_RECORD_TOKEN = object()


@dataclass(frozen=True, slots=True, init=False)
class AssociationReviewRecord:
    association_id: str
    review_version: int
    memory_revision_id: str
    disposition: ReviewDisposition
    risk_class: ReviewRiskClass
    assessment_id: str
    evidence_ids: tuple[str, ...]
    required_supporting_holdout_events: int
    parent_review_id: str | None
    review_id: str

    def __init__(
        self,
        *,
        association_id: str,
        review_version: int,
        memory_revision_id: str,
        disposition: ReviewDisposition,
        risk_class: ReviewRiskClass,
        assessment_id: str,
        evidence_ids: tuple[str, ...],
        required_supporting_holdout_events: int,
        parent_review_id: str | None,
        review_id: str,
        _token: object | None = None,
    ) -> None:
        if _token is not _REVIEW_RECORD_TOKEN:
            raise TypeError(
                "AssociationReviewRecord must be created by AssociationReviewRegistry"
            )
        for name, value in (
            ("association_id", association_id),
            ("memory_revision_id", memory_revision_id),
            ("assessment_id", assessment_id),
            ("review_id", review_id),
        ):
            if not value.strip():
                raise ValueError(f"{name} must be non-empty")
        if review_version < 1:
            raise ValueError("review_version must be >= 1")
        if not evidence_ids:
            raise ValueError("review record requires evidence IDs")
        if required_supporting_holdout_events < 1:
            raise ValueError(
                "required_supporting_holdout_events must be >= 1"
            )
        object.__setattr__(self, "association_id", association_id)
        object.__setattr__(self, "review_version", review_version)
        object.__setattr__(self, "memory_revision_id", memory_revision_id)
        object.__setattr__(self, "disposition", disposition)
        object.__setattr__(self, "risk_class", risk_class)
        object.__setattr__(self, "assessment_id", assessment_id)
        object.__setattr__(self, "evidence_ids", tuple(evidence_ids))
        object.__setattr__(
            self,
            "required_supporting_holdout_events",
            required_supporting_holdout_events,
        )
        object.__setattr__(self, "parent_review_id", parent_review_id)
        object.__setattr__(self, "review_id", review_id)


def _review_id(
    *,
    association_id: str,
    review_version: int,
    memory_revision_id: str,
    disposition: ReviewDisposition,
    risk_class: ReviewRiskClass,
    assessment_id: str,
    evidence_ids: tuple[str, ...],
    required_supporting_holdout_events: int,
    parent_review_id: str | None,
) -> str:
    payload = json.dumps(
        {
            "association_id": association_id,
            "review_version": review_version,
            "memory_revision_id": memory_revision_id,
            "disposition": disposition.value,
            "risk_class": risk_class.value,
            "assessment_id": assessment_id,
            "evidence_ids": list(evidence_ids),
            "required_supporting_holdout_events": (
                required_supporting_holdout_events
            ),
            "parent_review_id": parent_review_id,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class AssociationReviewRegistry:
    records: tuple[AssociationReviewRecord, ...] = ()

    def __post_init__(self) -> None:
        latest: dict[str, AssociationReviewRecord] = {}
        for record in self.records:
            prior = latest.get(record.association_id)
            expected_version = 1 if prior is None else prior.review_version + 1
            expected_parent = None if prior is None else prior.review_id
            if record.review_version != expected_version:
                raise ReviewIntegrityError(
                    f"invalid review version chain for {record.association_id}"
                )
            if record.parent_review_id != expected_parent:
                raise ReviewIntegrityError(
                    f"invalid review parent for {record.association_id}"
                )
            expected_id = _review_id(
                association_id=record.association_id,
                review_version=record.review_version,
                memory_revision_id=record.memory_revision_id,
                disposition=record.disposition,
                risk_class=record.risk_class,
                assessment_id=record.assessment_id,
                evidence_ids=record.evidence_ids,
                required_supporting_holdout_events=(
                    record.required_supporting_holdout_events
                ),
                parent_review_id=record.parent_review_id,
            )
            if record.review_id != expected_id:
                raise ReviewIntegrityError(
                    f"invalid review digest for {record.association_id}"
                )
            latest[record.association_id] = record

    def current(self, association_id: str) -> AssociationReviewRecord | None:
        for record in reversed(self.records):
            if record.association_id == association_id:
                return record
        return None

    def history(self, association_id: str) -> tuple[AssociationReviewRecord, ...]:
        return tuple(
            record
            for record in self.records
            if record.association_id == association_id
        )

    def admission(
        self,
        *,
        association_id: str,
        memory_revision_id: str,
    ) -> ReviewAdmission:
        record = self.current(association_id)
        if record is None:
            return ReviewAdmission.ADMITTED
        if record.memory_revision_id != memory_revision_id:
            return ReviewAdmission.STALE
        if record.disposition is ReviewDisposition.QUARANTINED:
            return ReviewAdmission.QUARANTINED
        return ReviewAdmission.ADMITTED

    def quarantine(
        self,
        *,
        association_id: str,
        memory_revision_id: str,
        assessment: ReviewEvidenceAssessment,
    ) -> "AssociationReviewRegistry":
        self._validate_assessment_binding(
            association_id=association_id,
            memory_revision_id=memory_revision_id,
            assessment=assessment,
        )
        if assessment.risk_class not in {
            ReviewRiskClass.SUSPECTED_OVERGENERALIZATION,
            ReviewRiskClass.CONTRADICTED,
        }:
            raise ReviewAssessmentInsufficient(
                "quarantine requires contradictory counterexample or holdout evidence"
            )
        return self._append(
            association_id=association_id,
            memory_revision_id=memory_revision_id,
            disposition=ReviewDisposition.QUARANTINED,
            assessment=assessment,
        )

    def release(
        self,
        *,
        association_id: str,
        memory_revision_id: str,
        assessment: ReviewEvidenceAssessment,
    ) -> "AssociationReviewRegistry":
        self._validate_assessment_binding(
            association_id=association_id,
            memory_revision_id=memory_revision_id,
            assessment=assessment,
        )
        if (
            assessment.risk_class is not ReviewRiskClass.CLEAR
            or not assessment.supporting_holdout_ids
            or assessment.contradicting_evidence_ids
        ):
            raise ReviewAssessmentInsufficient(
                "release requires current clear holdout support and no contradictions"
            )
        return self._append(
            association_id=association_id,
            memory_revision_id=memory_revision_id,
            disposition=ReviewDisposition.ACTIVE,
            assessment=assessment,
        )

    @staticmethod
    def _validate_assessment_binding(
        *,
        association_id: str,
        memory_revision_id: str,
        assessment: ReviewEvidenceAssessment,
    ) -> None:
        if (
            assessment.association_id != association_id
            or assessment.memory_revision_id != memory_revision_id
        ):
            raise ReviewAssessmentMismatch(
                "review assessment does not bind the exact association revision"
            )

    def _append(
        self,
        *,
        association_id: str,
        memory_revision_id: str,
        disposition: ReviewDisposition,
        assessment: ReviewEvidenceAssessment,
    ) -> "AssociationReviewRegistry":
        prior = self.current(association_id)
        if (
            prior is not None
            and prior.memory_revision_id == memory_revision_id
            and prior.disposition is disposition
            and prior.assessment_id == assessment.assessment_id
        ):
            raise ReviewNoOpError(
                "review state already reflects this exact evidence assessment"
            )

        review_version = 1 if prior is None else prior.review_version + 1
        parent_review_id = None if prior is None else prior.review_id
        review_id = _review_id(
            association_id=association_id,
            review_version=review_version,
            memory_revision_id=memory_revision_id,
            disposition=disposition,
            risk_class=assessment.risk_class,
            assessment_id=assessment.assessment_id,
            evidence_ids=assessment.evidence_ids,
            required_supporting_holdout_events=(
                assessment.required_supporting_holdout_events
            ),
            parent_review_id=parent_review_id,
        )
        record = AssociationReviewRecord(
            association_id=association_id,
            review_version=review_version,
            memory_revision_id=memory_revision_id,
            disposition=disposition,
            risk_class=assessment.risk_class,
            assessment_id=assessment.assessment_id,
            evidence_ids=assessment.evidence_ids,
            required_supporting_holdout_events=(
                assessment.required_supporting_holdout_events
            ),
            parent_review_id=parent_review_id,
            review_id=review_id,
            _token=_REVIEW_RECORD_TOKEN,
        )
        return AssociationReviewRegistry(records=self.records + (record,))
