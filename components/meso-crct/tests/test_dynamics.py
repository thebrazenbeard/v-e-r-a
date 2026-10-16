import math

import pytest

from meso_crct import (
    CircuitState,
    DynamicsConfig,
    HomeostaticState,
    LearningState,
    NeedAxis,
    RecruitmentState,
    RewardState,
    SalienceState,
    advance_without_input,
    decay_toward,
)


def config():
    return DynamicsConfig(
        hedonic_half_life_seconds=10.0,
        salience_half_life_seconds=10.0,
        learning_half_life_seconds=10.0,
        satiation_half_life_seconds=20.0,
        recruitment_half_life_seconds=5.0,
    )


def test_half_life_halves_value_toward_zero():
    assert decay_toward(
        1.0,
        baseline=0.0,
        elapsed_seconds=10.0,
        half_life_seconds=10.0,
    ) == pytest.approx(0.5)


def test_signed_prediction_error_decays_toward_zero():
    assert decay_toward(
        -1.0,
        baseline=0.0,
        elapsed_seconds=10.0,
        half_life_seconds=10.0,
    ) == pytest.approx(-0.5)


def test_zero_elapsed_is_identity():
    state = CircuitState(
        reward=RewardState(pleasure=4.0, hazard=0.7, avoidance=0.8),
        salience=SalienceState(semantic_relevance=0.8),
    )
    assert advance_without_input(
        state,
        elapsed_seconds=0.0,
        config=config(),
    ) == state


def test_transient_state_relaxes_without_new_input():
    state = CircuitState(
        reward=RewardState(pleasure=4.0),
        salience=SalienceState(
            semantic_relevance=1.0,
            incentive_salience=0.8,
            attentional_priority=0.6,
        ),
        learning=LearningState(
            prediction_error=1.0,
            novelty=1.0,
            learning_progress=0.8,
            satiation=1.0,
        ),
        recruitment=RecruitmentState(
            activation=1.0,
            coherence=1.0,
            persistence=1.0,
            resolution=1.0,
        ),
    )
    advanced = advance_without_input(
        state,
        elapsed_seconds=10.0,
        config=config(),
    )
    assert advanced.reward.pleasure == pytest.approx(2.0)
    assert advanced.salience.semantic_relevance == pytest.approx(0.5)
    assert advanced.salience.incentive_salience == pytest.approx(0.4)
    assert advanced.learning.prediction_error == pytest.approx(0.5)
    assert advanced.learning.satiation == pytest.approx(2 ** -0.5)
    assert advanced.recruitment.activation == pytest.approx(0.25)


def test_protective_channels_do_not_decay_from_clock_alone():
    state = CircuitState(
        reward=RewardState(pleasure=-0.1, hazard=1.0, avoidance=1.0),
    )
    advanced = advance_without_input(
        state,
        elapsed_seconds=1000.0,
        config=config(),
    )
    assert advanced.reward.hazard == 1.0
    assert advanced.reward.avoidance == 1.0
    assert -0.1 <= advanced.reward.pleasure <= 0.0


def test_homeostatic_state_is_not_changed_by_generic_clock_decay():
    homeostasis = HomeostaticState(
        axes=(NeedAxis("energy", setpoint=0.8, current_level=0.2),)
    )
    state = CircuitState(homeostasis=homeostasis)
    advanced = advance_without_input(
        state,
        elapsed_seconds=100.0,
        config=config(),
    )
    assert advanced.homeostasis == homeostasis


@pytest.mark.parametrize("elapsed", [-1.0, math.nan, math.inf])
def test_bad_elapsed_time_fails_closed(elapsed):
    with pytest.raises(ValueError):
        advance_without_input(
            CircuitState(),
            elapsed_seconds=elapsed,
            config=config(),
        )


def test_half_life_must_be_positive():
    with pytest.raises(ValueError):
        DynamicsConfig(
            hedonic_half_life_seconds=0.0,
            salience_half_life_seconds=1.0,
            learning_half_life_seconds=1.0,
            satiation_half_life_seconds=1.0,
            recruitment_half_life_seconds=1.0,
        )
