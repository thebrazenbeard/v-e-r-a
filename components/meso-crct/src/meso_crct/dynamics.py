"""Time evolution for MESO-CRCT when no new evidence arrives.

Transient state relaxes toward baseline. Protective hazard/avoidance channels do
not automatically decay merely because time passes; they require an explicit
trusted update.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from .circuit import CircuitState
from .salience import LearningState, RecruitmentState, SalienceState
from .state import RewardState


def _positive_finite(value: float, *, name: str) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be finite and > 0")
    return value


def _nonnegative_finite(value: float, *, name: str) -> float:
    value = float(value)
    if not math.isfinite(value) or value < 0.0:
        raise ValueError(f"{name} must be finite and >= 0")
    return value


def decay_toward(
    value: float,
    *,
    baseline: float,
    elapsed_seconds: float,
    half_life_seconds: float,
) -> float:
    """Exponential relaxation toward baseline."""
    value = float(value)
    baseline = float(baseline)
    if not math.isfinite(value) or not math.isfinite(baseline):
        raise ValueError("value and baseline must be finite")
    elapsed = _nonnegative_finite(elapsed_seconds, name="elapsed_seconds")
    half_life = _positive_finite(half_life_seconds, name="half_life_seconds")
    if elapsed == 0.0:
        return value
    factor = 0.5 ** (elapsed / half_life)
    return baseline + (value - baseline) * factor


@dataclass(frozen=True, slots=True)
class DynamicsConfig:
    hedonic_half_life_seconds: float
    salience_half_life_seconds: float
    learning_half_life_seconds: float
    satiation_half_life_seconds: float
    recruitment_half_life_seconds: float

    def __post_init__(self) -> None:
        for name in (
            "hedonic_half_life_seconds",
            "salience_half_life_seconds",
            "learning_half_life_seconds",
            "satiation_half_life_seconds",
            "recruitment_half_life_seconds",
        ):
            object.__setattr__(
                self,
                name,
                _positive_finite(getattr(self, name), name=name),
            )


def advance_without_input(
    state: CircuitState,
    *,
    elapsed_seconds: float,
    config: DynamicsConfig,
) -> CircuitState:
    """Advance transient state with no new observation/appraisal.

    The caller must explicitly refresh context, goals, sensory evidence,
    homeostatic state, and protective state when new evidence exists.
    """
    elapsed = _nonnegative_finite(elapsed_seconds, name="elapsed_seconds")
    if elapsed == 0.0:
        return state

    reward = RewardState(
        pleasure=decay_toward(
            state.reward.pleasure,
            baseline=0.0,
            elapsed_seconds=elapsed,
            half_life_seconds=config.hedonic_half_life_seconds,
        ),
        hazard=state.reward.hazard,
        avoidance=state.reward.avoidance,
    )

    salience = SalienceState(
        perceptual_salience=decay_toward(
            state.salience.perceptual_salience,
            baseline=0.0,
            elapsed_seconds=elapsed,
            half_life_seconds=config.salience_half_life_seconds,
        ),
        semantic_relevance=decay_toward(
            state.salience.semantic_relevance,
            baseline=0.0,
            elapsed_seconds=elapsed,
            half_life_seconds=config.salience_half_life_seconds,
        ),
        motivational_salience=decay_toward(
            state.salience.motivational_salience,
            baseline=0.0,
            elapsed_seconds=elapsed,
            half_life_seconds=config.salience_half_life_seconds,
        ),
        incentive_salience=decay_toward(
            state.salience.incentive_salience,
            baseline=0.0,
            elapsed_seconds=elapsed,
            half_life_seconds=config.salience_half_life_seconds,
        ),
        epistemic_value=decay_toward(
            state.salience.epistemic_value,
            baseline=0.0,
            elapsed_seconds=elapsed,
            half_life_seconds=config.salience_half_life_seconds,
        ),
        attentional_priority=decay_toward(
            state.salience.attentional_priority,
            baseline=0.0,
            elapsed_seconds=elapsed,
            half_life_seconds=config.salience_half_life_seconds,
        ),
    )

    learning = LearningState(
        prediction_error=decay_toward(
            state.learning.prediction_error,
            baseline=0.0,
            elapsed_seconds=elapsed,
            half_life_seconds=config.learning_half_life_seconds,
        ),
        novelty=decay_toward(
            state.learning.novelty,
            baseline=0.0,
            elapsed_seconds=elapsed,
            half_life_seconds=config.learning_half_life_seconds,
        ),
        learning_progress=decay_toward(
            state.learning.learning_progress,
            baseline=0.0,
            elapsed_seconds=elapsed,
            half_life_seconds=config.learning_half_life_seconds,
        ),
        satiation=decay_toward(
            state.learning.satiation,
            baseline=0.0,
            elapsed_seconds=elapsed,
            half_life_seconds=config.satiation_half_life_seconds,
        ),
    )

    recruitment = RecruitmentState(
        activation=decay_toward(
            state.recruitment.activation,
            baseline=0.0,
            elapsed_seconds=elapsed,
            half_life_seconds=config.recruitment_half_life_seconds,
        ),
        coherence=decay_toward(
            state.recruitment.coherence,
            baseline=0.0,
            elapsed_seconds=elapsed,
            half_life_seconds=config.recruitment_half_life_seconds,
        ),
        persistence=decay_toward(
            state.recruitment.persistence,
            baseline=0.0,
            elapsed_seconds=elapsed,
            half_life_seconds=config.recruitment_half_life_seconds,
        ),
        resolution=decay_toward(
            state.recruitment.resolution,
            baseline=0.0,
            elapsed_seconds=elapsed,
            half_life_seconds=config.recruitment_half_life_seconds,
        ),
    )

    return CircuitState(
        reward=reward,
        salience=salience,
        learning=learning,
        recruitment=recruitment,
        homeostasis=state.homeostasis,
    )
