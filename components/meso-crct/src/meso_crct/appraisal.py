"""Canonical typed appraisal composition for MESO-CRCT."""

from __future__ import annotations

from dataclasses import dataclass, field

from .circuit import CircuitState
from .evaluation_env import derive_epistemic_value
from .homeostasis import (
    HomeostaticModulation,
    HomeostaticState,
    NeedAffordance,
    modulate_incentive_salience,
)
from .salience import LearningState, RecruitmentState, SalienceState
from .selection import TargetState
from .semantic import SemanticAssessment, SemanticEvidence, assess_semantic_relevance
from .state import RewardState


@dataclass(frozen=True, slots=True)
class TargetAppraisalInput:
    target_id: str
    perceptual_salience: float = 0.0
    semantic_evidence: SemanticEvidence = field(default_factory=SemanticEvidence)
    base_motivational_salience: float = 0.0
    base_incentive_salience: float = 0.0
    novelty: float = 0.0
    learning_progress: float = 0.0
    prediction_error: float = 0.0
    satiation: float = 0.0
    reward: RewardState = field(default_factory=RewardState)
    recruitment: RecruitmentState = field(default_factory=RecruitmentState)
    homeostasis: HomeostaticState = field(default_factory=HomeostaticState)
    affordances: tuple[NeedAffordance, ...] = ()

    def __post_init__(self) -> None:
        if not self.target_id.strip():
            raise ValueError("target_id must be non-empty")


_APPRAISED_TARGET_TOKEN = object()


@dataclass(frozen=True, slots=True, init=False)
class AppraisedTarget:
    target_id: str
    state: CircuitState
    semantic: SemanticAssessment
    homeostatic: HomeostaticModulation

    def __init__(
        self,
        *,
        target_id: str,
        state: CircuitState,
        semantic: SemanticAssessment,
        homeostatic: HomeostaticModulation,
        _token: object | None = None,
    ) -> None:
        if _token is not _APPRAISED_TARGET_TOKEN:
            raise TypeError("AppraisedTarget must be created by build_target_appraisal")
        object.__setattr__(self, "target_id", target_id)
        object.__setattr__(self, "state", state)
        object.__setattr__(self, "semantic", semantic)
        object.__setattr__(self, "homeostatic", homeostatic)

    def as_target_state(self) -> TargetState:
        return TargetState(self.target_id, self.state)


def build_target_appraisal(spec: TargetAppraisalInput) -> AppraisedTarget:
    """Build one target state through the canonical typed appraisal path.

    Attentional priority is intentionally not accepted as an input because it is
    downstream of arbitration/selection.
    """
    semantic = assess_semantic_relevance(spec.semantic_evidence)
    epistemic_value = derive_epistemic_value(
        novelty=spec.novelty,
        learning_progress=spec.learning_progress,
    )
    homeostatic = modulate_incentive_salience(
        base_incentive=spec.base_incentive_salience,
        homeostasis=spec.homeostasis,
        affordances=spec.affordances,
    )

    salience = SalienceState(
        perceptual_salience=spec.perceptual_salience,
        semantic_relevance=semantic.relevance,
        motivational_salience=spec.base_motivational_salience,
        incentive_salience=homeostatic.effective_incentive,
        epistemic_value=epistemic_value,
        attentional_priority=0.0,
    )
    learning = LearningState(
        prediction_error=spec.prediction_error,
        novelty=spec.novelty,
        learning_progress=spec.learning_progress,
        satiation=spec.satiation,
    )
    state = CircuitState(
        reward=spec.reward,
        salience=salience,
        learning=learning,
        recruitment=spec.recruitment,
        homeostasis=spec.homeostasis,
    )
    return AppraisedTarget(
        target_id=spec.target_id,
        state=state,
        semantic=semantic,
        homeostatic=homeostatic,
        _token=_APPRAISED_TARGET_TOKEN,
    )
