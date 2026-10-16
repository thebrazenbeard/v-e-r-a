"""Deterministic recruitment transition from typed salience channels.

This is a synthetic reference mechanism, not a biological model. It keeps
recruitment distinct from pleasure, truth, authority, and action execution.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from .salience import RecruitmentState, SalienceState


def _unit(value: float, *, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be within [0, 1]")
    return value


@dataclass(frozen=True, slots=True)
class RecruitmentPolicy:
    """Reference persistence policy.

    persistence_retention carries only prior persistence. New persistence
    requires activation to remain present across consecutive transitions.
    """

    persistence_retention: float = 0.75

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "persistence_retention",
            _unit(
                self.persistence_retention,
                name="persistence_retention",
            ),
        )


@dataclass(frozen=True, slots=True)
class RecruitmentTransition:
    """Auditable decomposition of one recruitment update."""

    previous: RecruitmentState
    salience: SalienceState
    strongest_driver: str | None
    activation: float
    coherence: float
    persistence: float
    resolution: float
    next_state: RecruitmentState


def advance_recruitment(
    previous: RecruitmentState,
    salience: SalienceState,
    *,
    policy: RecruitmentPolicy | None = None,
) -> RecruitmentTransition:
    """Advance recruitment without collapsing typed salience into utility.

    Rules:
    - activation is the strongest upstream salience driver;
    - coherence is the weakest/strongest ratio across upstream drivers, so a
      single extreme channel cannot masquerade as cross-channel agreement;
    - persistence is earned only by repeated activation and otherwise decays;
    - resolution is the normalized margin between the strongest and
      second-strongest drivers.

    attentional_priority is excluded because it is downstream of
    arbitration/selection in the canonical appraisal contract.
    """

    if type(previous) is not RecruitmentState:
        raise TypeError("previous must be exact RecruitmentState")
    if type(salience) is not SalienceState:
        raise TypeError("salience must be exact SalienceState")
    policy = RecruitmentPolicy() if policy is None else policy
    if type(policy) is not RecruitmentPolicy:
        raise TypeError("policy must be exact RecruitmentPolicy")

    drivers = (
        ("perceptual_salience", salience.perceptual_salience),
        ("semantic_relevance", salience.semantic_relevance),
        ("motivational_salience", salience.motivational_salience),
        ("incentive_salience", salience.incentive_salience),
        ("epistemic_value", salience.epistemic_value),
    )
    ranked = sorted(drivers, key=lambda item: (-item[1], item[0]))
    strongest_driver, activation = ranked[0]

    if activation <= 0.0:
        strongest_driver = None
        coherence = 0.0
        resolution = 0.0
    else:
        weakest = min(value for _, value in drivers)
        second = ranked[1][1]
        coherence = weakest / activation
        resolution = (activation - second) / activation

    repeated_activation = min(previous.activation, activation)
    retained_persistence = (
        previous.persistence * policy.persistence_retention
    )
    persistence = max(repeated_activation, retained_persistence)

    next_state = RecruitmentState(
        activation=activation,
        coherence=coherence,
        persistence=persistence,
        resolution=resolution,
    )
    return RecruitmentTransition(
        previous=previous,
        salience=salience,
        strongest_driver=strongest_driver,
        activation=next_state.activation,
        coherence=next_state.coherence,
        persistence=next_state.persistence,
        resolution=next_state.resolution,
        next_state=next_state,
    )
