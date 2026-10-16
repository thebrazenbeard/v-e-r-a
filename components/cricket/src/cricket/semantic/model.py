from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Force(str, Enum):
    POSSIBLE = "POSSIBLE"
    PROBABLE = "PROBABLE"
    ASSERTED = "ASSERTED"
    CERTAIN = "CERTAIN"


FORCE_RANK = {
    Force.POSSIBLE: 0,
    Force.PROBABLE: 1,
    Force.ASSERTED: 2,
    Force.CERTAIN: 3,
}


class Polarity(str, Enum):
    AFFIRMED = "AFFIRMED"
    DENIED = "DENIED"


class SpeechAct(str, Enum):
    DESCRIPTION = "DESCRIPTION"
    HYPOTHESIS = "HYPOTHESIS"
    QUESTION = "QUESTION"
    PREFERENCE = "PREFERENCE"
    REQUEST = "REQUEST"
    PERMISSION = "PERMISSION"
    INSTRUCTION = "INSTRUCTION"
    COMMITMENT = "COMMITMENT"
    QUOTATION = "QUOTATION"


class TemporalStatus(str, Enum):
    CURRENT = "CURRENT"
    HISTORICAL = "HISTORICAL"
    PROPOSED = "PROPOSED"
    UNKNOWN = "UNKNOWN"


class ProvenanceKind(str, Enum):
    USER_CURRENT = "USER_CURRENT"
    USER_HISTORICAL = "USER_HISTORICAL"
    MODEL_INFERENCE = "MODEL_INFERENCE"
    EXTERNAL_EVIDENCE = "EXTERNAL_EVIDENCE"
    TOOL_RESULT = "TOOL_RESULT"
    EFFECT_RECEIPT = "EFFECT_RECEIPT"
    QUOTATION = "QUOTATION"
    UNKNOWN = "UNKNOWN"


class TransformationKind(str, Enum):
    PRESERVED = "PRESERVED"
    STRENGTHENED = "STRENGTHENED"
    WEAKENED = "WEAKENED"
    REFERENT_CHANGED = "REFERENT_CHANGED"
    PREDICATE_CHANGED = "PREDICATE_CHANGED"
    CONTRADICTED = "CONTRADICTED"
    SCOPE_BROADENED = "SCOPE_BROADENED"
    SCOPE_NARROWED = "SCOPE_NARROWED"
    SCOPE_CHANGED = "SCOPE_CHANGED"
    AUTHORITY_ESCALATED = "AUTHORITY_ESCALATED"
    SPEECH_ACT_CHANGED = "SPEECH_ACT_CHANGED"
    CURRENTNESS_PROMOTED = "CURRENTNESS_PROMOTED"
    TEMPORAL_CHANGED = "TEMPORAL_CHANGED"
    PROVENANCE_CHANGED = "PROVENANCE_CHANGED"
    AMBIGUITY_COLLAPSED = "AMBIGUITY_COLLAPSED"
    DROPPED = "DROPPED"
    ADDED = "ADDED"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class SemanticScope:
    members: frozenset[str]

    def __post_init__(self) -> None:
        if not isinstance(self.members, frozenset) or not all(
            isinstance(item, str) and item.strip() for item in self.members
        ):
            raise ValueError("scope members must be a frozenset of non-empty strings")


@dataclass(frozen=True)
class SemanticProposition:
    anchor_id: str
    referent: str
    predicate: str
    force: Force = Force.ASSERTED
    polarity: Polarity = Polarity.AFFIRMED
    scope: SemanticScope | None = None
    speech_act: SpeechAct = SpeechAct.DESCRIPTION
    temporal_status: TemporalStatus = TemporalStatus.CURRENT
    provenance: ProvenanceKind = ProvenanceKind.UNKNOWN

    def __post_init__(self) -> None:
        for name, value in (
            ("anchor_id", self.anchor_id),
            ("referent", self.referent),
            ("predicate", self.predicate),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be non-empty text")
        if not isinstance(self.force, Force):
            raise ValueError("force must be a Force")
        if not isinstance(self.polarity, Polarity):
            raise ValueError("polarity must be a Polarity")
        if self.scope is not None and not isinstance(self.scope, SemanticScope):
            raise ValueError("scope must be a SemanticScope or None")
        if not isinstance(self.speech_act, SpeechAct):
            raise ValueError("speech_act must be a SpeechAct")
        if not isinstance(self.temporal_status, TemporalStatus):
            raise ValueError("temporal_status must be a TemporalStatus")
        if not isinstance(self.provenance, ProvenanceKind):
            raise ValueError("provenance must be a ProvenanceKind")


@dataclass(frozen=True)
class SemanticFrame:
    propositions: tuple[SemanticProposition, ...] = ()
    unresolved_interpretations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.propositions, tuple) or not all(
            isinstance(item, SemanticProposition) for item in self.propositions
        ):
            raise ValueError("propositions must be a tuple of SemanticProposition objects")
        anchors = [item.anchor_id for item in self.propositions]
        if len(anchors) != len(set(anchors)):
            raise ValueError("semantic proposition anchor_id values must be unique")
        if not isinstance(self.unresolved_interpretations, tuple) or not all(
            isinstance(item, str) and item.strip() for item in self.unresolved_interpretations
        ):
            raise ValueError("unresolved_interpretations must be a tuple of non-empty strings")


@dataclass(frozen=True)
class SemanticChange:
    anchor_id: str
    kind: TransformationKind
    source: SemanticProposition | None
    candidate: SemanticProposition | None
    material: bool
    rationale: str


@dataclass(frozen=True)
class SemanticIntegrityReport:
    changes: tuple[SemanticChange, ...]

    @property
    def material_change(self) -> bool:
        return any(change.material for change in self.changes)
