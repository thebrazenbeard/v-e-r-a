import pytest

from meso_crct import (
    RecruitmentPolicy,
    RecruitmentState,
    SalienceState,
    advance_recruitment,
)


def test_single_semantic_driver_recruits_without_cross_channel_coherence():
    result = advance_recruitment(
        RecruitmentState(),
        SalienceState(semantic_relevance=1.0),
    )
    assert result.strongest_driver == "semantic_relevance"
    assert result.activation == 1.0
    assert result.coherence == 0.0
    assert result.resolution == 1.0
    assert result.persistence == 0.0


def test_equal_cross_channel_support_is_coherent_but_driver_unresolved():
    result = advance_recruitment(
        RecruitmentState(),
        SalienceState(
            perceptual_salience=0.8,
            semantic_relevance=0.8,
            motivational_salience=0.8,
            incentive_salience=0.8,
            epistemic_value=0.8,
        ),
    )
    assert result.activation == pytest.approx(0.8)
    assert result.coherence == pytest.approx(1.0)
    assert result.resolution == pytest.approx(0.0)


def test_persistence_requires_repeated_activation():
    first = advance_recruitment(
        RecruitmentState(),
        SalienceState(motivational_salience=0.9),
    )
    assert first.persistence == 0.0

    second = advance_recruitment(
        first.next_state,
        SalienceState(motivational_salience=0.9),
    )
    assert second.persistence == pytest.approx(0.9)


def test_existing_persistence_decays_when_new_activation_disappears():
    result = advance_recruitment(
        RecruitmentState(
            activation=1.0,
            persistence=0.8,
        ),
        SalienceState(),
        policy=RecruitmentPolicy(persistence_retention=0.5),
    )
    assert result.activation == 0.0
    assert result.persistence == pytest.approx(0.4)
    assert result.strongest_driver is None


def test_attentional_priority_does_not_feed_back_into_recruitment():
    result = advance_recruitment(
        RecruitmentState(),
        SalienceState(attentional_priority=1.0),
    )
    assert result.activation == 0.0
    assert result.next_state == RecruitmentState()


def test_transition_is_auditable_and_does_not_mutate_inputs():
    previous = RecruitmentState(activation=0.3, persistence=0.2)
    salience = SalienceState(
        perceptual_salience=0.4,
        semantic_relevance=0.7,
        motivational_salience=0.2,
        incentive_salience=0.1,
        epistemic_value=0.3,
    )
    result = advance_recruitment(previous, salience)

    assert result.previous is previous
    assert result.salience is salience
    assert previous == RecruitmentState(activation=0.3, persistence=0.2)
    assert salience.attentional_priority == 0.0


def test_policy_rejects_out_of_range_retention():
    with pytest.raises(ValueError):
        RecruitmentPolicy(persistence_retention=1.1)


def test_exact_types_are_required():
    with pytest.raises(TypeError):
        advance_recruitment(object(), SalienceState())
    with pytest.raises(TypeError):
        advance_recruitment(RecruitmentState(), object())
