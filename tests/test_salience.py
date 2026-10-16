import math

import pytest

from meso_crct import (
    CircuitState,
    LearningState,
    RecruitmentState,
    SalienceState,
    SignalKind,
)


def test_signal_kinds_are_semantically_typed():
    assert SignalKind.SEMANTIC_RELEVANCE.value == "semantic_relevance"
    assert SignalKind.INCENTIVE_SALIENCE.value == "incentive_salience"
    assert SignalKind.ATTENTIONAL_PRIORITY.value == "attentional_priority"


def test_salience_channels_are_independent():
    state = SalienceState(
        semantic_relevance=1.0,
        incentive_salience=0.0,
        attentional_priority=0.8,
    )
    assert state.semantic_relevance == 1.0
    assert state.incentive_salience == 0.0
    assert state.attentional_priority == 0.8


def test_salience_channels_are_bounded():
    state = SalienceState(
        perceptual_salience=-10,
        semantic_relevance=10,
        motivational_salience=2,
        incentive_salience=-2,
        epistemic_value=999,
        attentional_priority=-999,
    )
    assert state.perceptual_salience == 0.0
    assert state.semantic_relevance == 1.0
    assert state.motivational_salience == 1.0
    assert state.incentive_salience == 0.0
    assert state.epistemic_value == 1.0
    assert state.attentional_priority == 0.0


def test_unknown_naked_or_untyped_signal_fails():
    with pytest.raises(KeyError):
        SalienceState().with_signals(salience=1.0)


def test_prediction_error_is_signed_and_separate():
    positive = LearningState(prediction_error=50)
    negative = LearningState(prediction_error=-50)
    assert positive.prediction_error == 1.0
    assert negative.prediction_error == -1.0
    assert positive.satiation == 0.0


def test_learning_state_is_bounded_without_implying_reward():
    state = LearningState(novelty=3, learning_progress=2, satiation=-1)
    assert state.novelty == 1.0
    assert state.learning_progress == 1.0
    assert state.satiation == 0.0


def test_recruitment_is_domain_neutral_and_bounded():
    state = RecruitmentState(activation=2, coherence=0.9, persistence=0.7, resolution=-5)
    assert state.activation == 1.0
    assert state.coherence == 0.9
    assert state.persistence == 0.7
    assert state.resolution == 0.0


@pytest.mark.parametrize("field", [
    "perceptual_salience",
    "semantic_relevance",
    "motivational_salience",
    "incentive_salience",
    "epistemic_value",
    "attentional_priority",
])
def test_nonfinite_salience_fails_closed(field):
    with pytest.raises(ValueError):
        SalienceState(**{field: math.nan})


def test_composed_circuit_can_be_highly_meaningful_without_pleasure():
    circuit = CircuitState(
        salience=SalienceState(
            semantic_relevance=1.0,
            motivational_salience=1.0,
            attentional_priority=1.0,
        )
    )
    assert circuit.reward.pleasure == 0.0
    assert circuit.salience.semantic_relevance == 1.0
    assert circuit.salience.attentional_priority == 1.0
