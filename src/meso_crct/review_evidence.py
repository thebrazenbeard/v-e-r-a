"""Evidence-bound negative-transfer review for learned associations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import hashlib
import json
from typing import Iterable

from .provenance import TransitionReceipt


class ReviewEvidenceKind(StrEnum):
    COUNTEREXAMPLE = "counterexample"
    HOLDOUT = "holdout"


class ReviewEvidenceOutcome(StrEnum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    INCONCLUSIVE = "inconclusive"


class ReviewRiskClass(StrEnum):
    CLEAR = "clear"
    SUSPECTED_OVERGENERALIZATION = "suspected_overgeneralization"
    CONTRADICTED = "contradicted"
    INSUFFICIENT = "insufficient"


class ReviewEvidenceMismatch(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ReviewEvidencePolicy:
    minimum_supporting_holdout_events: int = 2

    def __post_init__(self) -> None:
        if self.minimum_supporting_holdout_events < 1:
            raise ValueError(
                "minimum_supporting_holdout_events must be >= 1"
            )


_EVIDENCE_TOKEN = object()
_ASSESSMENT_TOKEN = object()


@dataclass(frozen=True, slots=True, init=False)
class ReviewEvidence:
    association_id: str
    memory_revision_id: str
    kind: ReviewEvidenceKind
    outcome: ReviewEvidenceOutcome
    evidence_ref: str
    transition_receipt_id: str
    event_id: str
    evidence_id: str

    def __init__(
        self,
        *,
        association_id: str,
        memory_revision_id: str,
        kind: ReviewEvidenceKind,
        outcome: ReviewEvidenceOutcome,
        evidence_ref: str,
        transition_receipt_id: str,
        event_id: str,
        evidence_id: str,
        _token: object | None = None,
    ) -> None:
        if _token is not _EVIDENCE_TOKEN:
            raise TypeError("ReviewEvidence must be created by bind_review_evidence")
        for name, value in (
            ("association_id", association_id),
            ("memory_revision_id", memory_revision_id),
            ("evidence_ref", evidence_ref),
            ("transition_receipt_id", transition_receipt_id),
            ("event_id", event_id),
            ("evidence_id", evidence_id),
        ):
            if not value.strip():
                raise ValueError(f"{name} must be non-empty")
        object.__setattr__(self, "association_id", association_id)
        object.__setattr__(self, "memory_revision_id", memory_revision_id)
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "outcome", outcome)
        object.__setattr__(self, "evidence_ref", evidence_ref)
        object.__setattr__(self, "transition_receipt_id", transition_receipt_id)
        object.__setattr__(self, "event_id", event_id)
        object.__setattr__(self, "evidence_id", evidence_id)


@dataclass(frozen=True, slots=True, init=False)
class ReviewEvidenceAssessment:
    association_id: str
    memory_revision_id: str
    risk_class: ReviewRiskClass
    evidence_ids: tuple[str, ...]
    supporting_holdout_ids: tuple[str, ...]
    supporting_holdout_event_ids: tuple[str, ...]
    contradicting_evidence_ids: tuple[str, ...]
    required_supporting_holdout_events: int
    assessment_id: str

    def __init__(
        self,
        *,
        association_id: str,
        memory_revision_id: str,
        risk_class: ReviewRiskClass,
        evidence_ids: tuple[str, ...],
        supporting_holdout_ids: tuple[str, ...],
        supporting_holdout_event_ids: tuple[str, ...],
        contradicting_evidence_ids: tuple[str, ...],
        required_supporting_holdout_events: int,
        assessment_id: str,
        _token: object | None = None,
    ) -> None:
        if _token is not _ASSESSMENT_TOKEN:
            raise TypeError(
                "ReviewEvidenceAssessment must be created by assess_review_evidence"
            )
        if not association_id.strip():
            raise ValueError("association_id must be non-empty")
        if not memory_revision_id.strip():
            raise ValueError("memory_revision_id must be non-empty")
        if not evidence_ids:
            raise ValueError("assessment requires at least one evidence item")
        if required_supporting_holdout_events < 1:
            raise ValueError("required_supporting_holdout_events must be >= 1")
        if not assessment_id.strip():
            raise ValueError("assessment_id must be non-empty")
        object.__setattr__(self, "association_id", association_id)
        object.__setattr__(self, "memory_revision_id", memory_revision_id)
        object.__setattr__(self, "risk_class", risk_class)
        object.__setattr__(self, "evidence_ids", tuple(evidence_ids))
        object.__setattr__(self, "supporting_holdout_ids", tuple(supporting_holdout_ids))
        object.__setattr__(
            self,
            "supporting_holdout_event_ids",
            tuple(supporting_holdout_event_ids),
        )
        object.__setattr__(
            self,
            "contradicting_evidence_ids",
            tuple(contradicting_evidence_ids),
        )
        object.__setattr__(
            self,
            "required_supporting_holdout_events",
            required_supporting_holdout_events,
        )
        object.__setattr__(self, "assessment_id", assessment_id)


def bind_review_evidence(
    *,
    association_id: str,
    memory_revision_id: str,
    kind: ReviewEvidenceKind,
    outcome: ReviewEvidenceOutcome,
    evidence_ref: str,
    receipt: TransitionReceipt,
) -> ReviewEvidence:
    """Bind one review observation to exact learned revision + verified event."""
    payload = {
        "association_id": association_id,
        "memory_revision_id": memory_revision_id,
        "kind": kind.value,
        "outcome": outcome.value,
        "evidence_ref": evidence_ref,
        "transition_receipt_id": receipt.receipt_id,
        "event_id": receipt.event_id,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    evidence_id = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return ReviewEvidence(
        association_id=association_id,
        memory_revision_id=memory_revision_id,
        kind=kind,
        outcome=outcome,
        evidence_ref=evidence_ref,
        transition_receipt_id=receipt.receipt_id,
        event_id=receipt.event_id,
        evidence_id=evidence_id,
        _token=_EVIDENCE_TOKEN,
    )


def assess_review_evidence(
    evidence: Iterable[ReviewEvidence],
    *,
    policy: ReviewEvidencePolicy | None = None,
) -> ReviewEvidenceAssessment:
    """Classify exact-revision negative-transfer evidence deterministically."""
    policy = ReviewEvidencePolicy() if policy is None else policy
    evidence = tuple(evidence)
    if not evidence:
        raise ValueError("at least one review evidence item is required")

    association_ids = {item.association_id for item in evidence}
    revision_ids = {item.memory_revision_id for item in evidence}
    if len(association_ids) != 1 or len(revision_ids) != 1:
        raise ReviewEvidenceMismatch(
            "all review evidence must bind the same association revision"
        )

    association_id = evidence[0].association_id
    memory_revision_id = evidence[0].memory_revision_id
    contradicting = tuple(
        sorted(
            item.evidence_id
            for item in evidence
            if item.outcome is ReviewEvidenceOutcome.CONTRADICTS
        )
    )
    supporting_holdouts = tuple(
        sorted(
            item.evidence_id
            for item in evidence
            if (
                item.kind is ReviewEvidenceKind.HOLDOUT
                and item.outcome is ReviewEvidenceOutcome.SUPPORTS
            )
        )
    )
    supporting_holdout_events = tuple(
        sorted(
            {
                item.event_id
                for item in evidence
                if (
                    item.kind is ReviewEvidenceKind.HOLDOUT
                    and item.outcome is ReviewEvidenceOutcome.SUPPORTS
                )
            }
        )
    )

    counterexample_contradiction = any(
        item.kind is ReviewEvidenceKind.COUNTEREXAMPLE
        and item.outcome is ReviewEvidenceOutcome.CONTRADICTS
        for item in evidence
    )
    holdout_contradiction = any(
        item.kind is ReviewEvidenceKind.HOLDOUT
        and item.outcome is ReviewEvidenceOutcome.CONTRADICTS
        for item in evidence
    )

    if counterexample_contradiction:
        risk = ReviewRiskClass.CONTRADICTED
    elif holdout_contradiction:
        risk = ReviewRiskClass.SUSPECTED_OVERGENERALIZATION
    elif (
        len(supporting_holdout_events)
        >= policy.minimum_supporting_holdout_events
        and not contradicting
    ):
        risk = ReviewRiskClass.CLEAR
    else:
        risk = ReviewRiskClass.INSUFFICIENT

    evidence_ids = tuple(sorted(item.evidence_id for item in evidence))
    payload = {
        "association_id": association_id,
        "memory_revision_id": memory_revision_id,
        "risk_class": risk.value,
        "evidence_ids": list(evidence_ids),
        "supporting_holdout_ids": list(supporting_holdouts),
        "supporting_holdout_event_ids": list(supporting_holdout_events),
        "contradicting_evidence_ids": list(contradicting),
        "required_supporting_holdout_events": (
            policy.minimum_supporting_holdout_events
        ),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    assessment_id = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    return ReviewEvidenceAssessment(
        association_id=association_id,
        memory_revision_id=memory_revision_id,
        risk_class=risk,
        evidence_ids=evidence_ids,
        supporting_holdout_ids=supporting_holdouts,
        supporting_holdout_event_ids=supporting_holdout_events,
        contradicting_evidence_ids=contradicting,
        required_supporting_holdout_events=(
            policy.minimum_supporting_holdout_events
        ),
        assessment_id=assessment_id,
        _token=_ASSESSMENT_TOKEN,
    )



class ReviewEvidenceReplayError(ValueError):
    pass


class ReviewEvidenceConflictError(ValueError):
    pass


class ReviewEvidenceNotRegistered(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ReviewEvidenceLedger:
    """Append-only admission ledger for exact-revision review evidence."""

    evidence: tuple[ReviewEvidence, ...] = ()

    def __post_init__(self) -> None:
        ids: set[str] = set()
        events: set[tuple[str, str, str]] = set()
        for item in self.evidence:
            if item.evidence_id in ids:
                raise ReviewEvidenceReplayError(
                    f"duplicate review evidence ID: {item.evidence_id}"
                )
            ids.add(item.evidence_id)

            event_key = (
                item.association_id,
                item.memory_revision_id,
                item.event_id,
            )
            if event_key in events:
                raise ReviewEvidenceConflictError(
                    "one event may supply at most one admitted evidence record "
                    "for an exact association revision"
                )
            events.add(event_key)

    @property
    def fingerprint(self) -> str:
        payload = json.dumps(
            [item.evidence_id for item in self.evidence],
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def get(self, evidence_id: str) -> ReviewEvidence | None:
        for item in reversed(self.evidence):
            if item.evidence_id == evidence_id:
                return item
        return None

    def register(self, item: ReviewEvidence) -> "ReviewEvidenceLedger":
        if self.get(item.evidence_id) is not None:
            raise ReviewEvidenceReplayError(
                "review evidence has already been registered"
            )
        for prior in self.evidence:
            if (
                prior.association_id == item.association_id
                and prior.memory_revision_id == item.memory_revision_id
                and prior.event_id == item.event_id
            ):
                raise ReviewEvidenceConflictError(
                    "event is already registered as review evidence for this "
                    "association revision"
                )
        return ReviewEvidenceLedger(evidence=self.evidence + (item,))

    def items_for_ids(
        self,
        evidence_ids: tuple[str, ...],
        *,
        association_id: str,
        memory_revision_id: str,
    ) -> tuple[ReviewEvidence, ...]:
        items: list[ReviewEvidence] = []
        for evidence_id in evidence_ids:
            item = self.get(evidence_id)
            if item is None:
                raise ReviewEvidenceNotRegistered(
                    f"review evidence is not registered: {evidence_id}"
                )
            if (
                item.association_id != association_id
                or item.memory_revision_id != memory_revision_id
            ):
                raise ReviewEvidenceMismatch(
                    "registered evidence does not match exact review binding"
                )
            items.append(item)
        return tuple(items)

    def validate_assessment(
        self,
        assessment: ReviewEvidenceAssessment,
    ) -> tuple[ReviewEvidence, ...]:
        items = self.items_for_ids(
            assessment.evidence_ids,
            association_id=assessment.association_id,
            memory_revision_id=assessment.memory_revision_id,
        )
        recomputed = assess_review_evidence(
            items,
            policy=ReviewEvidencePolicy(
                minimum_supporting_holdout_events=(
                    assessment.required_supporting_holdout_events
                )
            ),
        )
        if recomputed != assessment:
            raise ReviewEvidenceMismatch(
                "assessment does not match registered evidence"
            )
        return items
