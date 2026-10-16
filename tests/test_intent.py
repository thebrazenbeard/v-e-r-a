import pytest

from meso_crct import (
    ActionTendencyKind,
    CircuitState,
    IntentKind,
    IntentPolicy,
    IntentProposal,
    RewardState,
    SalienceState,
    TargetState,
    derive_action_tendency,
    propose_action_intent,
    select_target,
)


def tendency_for(state):
    return derive_action_tendency(
        select_target([TargetState("target", state)])
    )


def test_intent_proposal_cannot_be_constructed_directly():
    with pytest.raises(TypeError):
        IntentProposal(
            target_id="target",
            kind=IntentKind.APPROACH,
            strength=1.0,
            source_tendency="approach",
            source="fake",
        )


def test_protective_withdraw_becomes_non_executable_withdraw_proposal():
    tendency = tendency_for(
        CircuitState(
            reward=RewardState(hazard=1.0, avoidance=1.0),
        )
    )
    assert tendency.kind is ActionTendencyKind.PROTECTIVE_WITHDRAW
    intent = propose_action_intent(tendency)
    assert intent.kind is IntentKind.WITHDRAW
    assert not intent.effect_authorized
    assert not intent.can_execute


def test_incentive_approach_becomes_non_executable_approach_proposal():
    tendency = tendency_for(
        CircuitState(
            salience=SalienceState(incentive_salience=0.9),
        )
    )
    intent = propose_action_intent(tendency)
    assert intent.kind is IntentKind.APPROACH
    assert intent.strength == pytest.approx(0.9)
    assert not intent.can_execute


def test_epistemic_inspection_becomes_inspect_proposal():
    tendency = tendency_for(
        CircuitState(
            salience=SalienceState(epistemic_value=0.8),
        )
    )
    intent = propose_action_intent(tendency)
    assert intent.kind is IntentKind.INSPECT
    assert not intent.effect_authorized


def test_generic_motivation_stays_hold():
    tendency = tendency_for(
        CircuitState(
            salience=SalienceState(motivational_salience=0.9),
        )
    )
    assert tendency.kind is ActionTendencyKind.UNCOMMITTED
    assert propose_action_intent(tendency).kind is IntentKind.HOLD


def test_weak_direction_below_policy_gate_stays_hold():
    tendency = tendency_for(
        CircuitState(
            salience=SalienceState(incentive_salience=0.30),
        )
    )
    intent = propose_action_intent(
        tendency,
        policy=IntentPolicy(minimum_committed_strength=0.50),
    )
    assert tendency.kind is ActionTendencyKind.APPROACH
    assert intent.kind is IntentKind.HOLD
    assert intent.strength == pytest.approx(0.30)


def test_no_selection_produces_hold_without_target():
    tendency = derive_action_tendency(
        select_target([TargetState("target")])
    )
    intent = propose_action_intent(tendency)
    assert intent.target_id is None
    assert intent.kind is IntentKind.HOLD
    assert not intent.can_execute
