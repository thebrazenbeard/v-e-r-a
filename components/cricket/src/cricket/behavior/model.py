from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BehavioralPattern(str, Enum):
    MOTIVATED_REASONING = "MOTIVATED_REASONING"
    RATIONALIZATION = "RATIONALIZATION"
    STATUS_DEFENSE = "STATUS_DEFENSE"
    GRIEVANCE_ESCALATION = "GRIEVANCE_ESCALATION"
    MANIPULATION = "MANIPULATION"
    DEPENDENCY_ENGINEERING = "DEPENDENCY_ENGINEERING"
    DECEPTION_RISK = "DECEPTION_RISK"
    AVOIDANCE = "AVOIDANCE"
    RELATIONAL_BID = "RELATIONAL_BID"
    DOMINANCE = "DOMINANCE"
    IDENTITY_PROTECTION = "IDENTITY_PROTECTION"
    SELF_JUSTIFICATION = "SELF_JUSTIFICATION"


class HypothesisState(str, Enum):
    PROPOSED = "PROPOSED"
    SUPPORTED = "SUPPORTED"
    CONTESTED = "CONTESTED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class BehavioralObservation:
    observation_id: str
    subject: str
    description: str
    source_ref: str

    def __post_init__(self) -> None:
        for name, value in (
            ("observation_id", self.observation_id),
            ("subject", self.subject),
            ("description", self.description),
            ("source_ref", self.source_ref),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be non-empty text")


@dataclass(frozen=True)
class BehavioralHypothesis:
    hypothesis_id: str
    pattern: BehavioralPattern
    subject: str
    evidence_refs: tuple[str, ...]
    rationale: str
    alternative_explanations: tuple[str, ...] = ()
    state: HypothesisState = HypothesisState.PROPOSED

    def __post_init__(self) -> None:
        if not isinstance(self.hypothesis_id, str) or not self.hypothesis_id.strip():
            raise ValueError("hypothesis_id must be non-empty text")
        if not isinstance(self.pattern, BehavioralPattern):
            raise ValueError("pattern must be a BehavioralPattern")
        if not isinstance(self.subject, str) or not self.subject.strip():
            raise ValueError("subject must be non-empty text")
        if not isinstance(self.evidence_refs, tuple) or not self.evidence_refs or not all(
            isinstance(item, str) and item.strip() for item in self.evidence_refs
        ):
            raise ValueError("behavioral hypothesis evidence_refs must contain evidence")
        if not isinstance(self.rationale, str) or not self.rationale.strip():
            raise ValueError("rationale must be non-empty text")
        if not isinstance(self.alternative_explanations, tuple) or not all(
            isinstance(item, str) and item.strip() for item in self.alternative_explanations
        ):
            raise ValueError("alternative_explanations must be a tuple of non-empty strings")
        if not isinstance(self.state, HypothesisState):
            raise ValueError("state must be a HypothesisState")


@dataclass(frozen=True)
class BehavioralAssessment:
    observations: tuple[BehavioralObservation, ...] = ()
    hypotheses: tuple[BehavioralHypothesis, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.observations, tuple) or not all(
            isinstance(item, BehavioralObservation) for item in self.observations
        ):
            raise ValueError("observations must be a tuple of BehavioralObservation objects")
        if not isinstance(self.hypotheses, tuple) or not all(
            isinstance(item, BehavioralHypothesis) for item in self.hypotheses
        ):
            raise ValueError("hypotheses must be a tuple of BehavioralHypothesis objects")
        observation_ids = [item.observation_id for item in self.observations]
        hypothesis_ids = [item.hypothesis_id for item in self.hypotheses]
        if len(observation_ids) != len(set(observation_ids)):
            raise ValueError("behavioral observation ids must be unique")
        if len(hypothesis_ids) != len(set(hypothesis_ids)):
            raise ValueError("behavioral hypothesis ids must be unique")
