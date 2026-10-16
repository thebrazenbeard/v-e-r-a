"""Composed MESO-CRCT reference state.

Composition is explicit so consumers can depend on only the state family they
need. No field here is granted authority over truth, permission, or identity.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .homeostasis import HomeostaticState
from .salience import LearningState, RecruitmentState, SalienceState
from .state import RewardState


@dataclass(frozen=True, slots=True)
class CircuitState:
    reward: RewardState = field(default_factory=RewardState)
    salience: SalienceState = field(default_factory=SalienceState)
    learning: LearningState = field(default_factory=LearningState)
    recruitment: RecruitmentState = field(default_factory=RecruitmentState)
    homeostasis: HomeostaticState = field(default_factory=HomeostaticState)
