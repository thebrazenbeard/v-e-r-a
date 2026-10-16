import pytest

from meso_crct import (
    ActionTendency,
    ActionTendencyKind,
    ActionTendencyPolicy,
    AssociationMemory,
    CircuitState,
    EventSequencer,
    LearningState,
    PlasticityPolicy,
    Provenance,
    ProvenanceVerifier,
    RewardState,
    SalienceState,
    SourceKind,
    TargetState,
    apply_candidate,
    derive_action_tendency,
    evaluate_transition,
    propose_plasticity,
    recall_association,
    select_target,
)


def recall_for(*, prediction_error: float, cue_match: float = 1.0):
    learning_state = CircuitState(
        salience=SalienceState(semantic_relevance=1.0),
        learning=LearningState(prediction_error=prediction_error),
    )
    learning_claim = Provenance(
        source_kind=SourceKind.ENVIRONMENT,
        source_id=f"learn:{prediction_error}",
        source_revision="v1",
    )
    verified_learning = ProvenanceVerifier(
        [learning_claim],
        verifier_id="tendency-verifier",
    ).verify(learning_claim)
    _, learning_event = EventSequencer("learn-stream").issue()
    learning_receipt = evaluate_transition(
        before=CircuitState(),
        after=learning_state,
        provenance=verified_learning,
        event=learning_event,
    )
    candidate = propose_plasticity(
        state=learning_state,
        association_id="cue->outcome",
        receipt=learning_receipt,
        policy=PlasticityPolicy(
            maximum_absolute_delta=1.0,
            minimum_salience_gate=0.0,
        ),
    )
    memory = apply_candidate(
        AssociationMemory(),
        candidate,
        expected_version=0,
    )

    cue_state = CircuitState(
        salience=SalienceState(perceptual_salience=0.8),
    )
    cue_claim = Provenance(
        source_kind=SourceKind.ENVIRONMENT,
        source_id="cue",
        source_revision="v1",
    )
    verified_cue = ProvenanceVerifier(
        [cue_claim],
        verifier_id="tendency-verifier",
    ).verify(cue_claim)
    _, cue_event = EventSequencer("cue-stream").issue()
    cue_receipt = evaluate_transition(
        before=CircuitState(),
        after=cue_state,
        provenance=verified_cue,
        event=cue_event,
    )
    return recall_association(
        memory=memory,
        association_id="cue->outcome",
        cue_match=cue_match,
        cue_receipt=cue_receipt,
    )


def test_action_tendency_cannot_be_constructed_directly():
    with pytest.raises(TypeError):
        ActionTendency(
            target_id="target",
            kind=ActionTendencyKind.APPROACH,
            strength=1.0,
            source="fake",
            selection_mode="motivational",
        )


def test_protection_produces_protective_withdraw():
    selection = select_target([
        TargetState(
            "danger",
            CircuitState(
                reward=RewardState(hazard=1.0, avoidance=1.0),
            ),
        ),
        TargetState(
            "want",
            CircuitState(
                salience=SalienceState(incentive_salience=1.0),
            ),
        ),
    ])
    tendency = derive_action_tendency(selection)
    assert tendency.target_id == "danger"
    assert tendency.kind is ActionTendencyKind.PROTECTIVE_WITHDRAW
    assert tendency.strength == 1.0


def test_negative_learned_direction_is_withdraw_not_approach():
    recall = recall_for(prediction_error=-0.8)
    selection = select_target([
        TargetState(
            "target",
            CircuitState(
                salience=SalienceState(motivational_salience=0.8),
            ),
        )
    ])
    tendency = derive_action_tendency(
        selection,
        recall=recall,
        recall_target_id="target",
    )
    assert tendency.kind is ActionTendencyKind.LEARNED_WITHDRAW
    assert tendency.strength == pytest.approx(0.8)


def test_positive_learned_direction_is_approach():
    recall = recall_for(prediction_error=0.7)
    selection = select_target([
        TargetState(
            "target",
            CircuitState(
                salience=SalienceState(motivational_salience=0.7),
            ),
        )
    ])
    tendency = derive_action_tendency(
        selection,
        recall=recall,
        recall_target_id="target",
    )
    assert tendency.kind is ActionTendencyKind.APPROACH
    assert tendency.strength == pytest.approx(0.7)


def test_incentive_salience_is_approach_direction():
    selection = select_target([
        TargetState(
            "target",
            CircuitState(
                salience=SalienceState(incentive_salience=0.9),
            ),
        )
    ])
    tendency = derive_action_tendency(selection)
    assert tendency.kind is ActionTendencyKind.APPROACH
    assert tendency.source == "incentive_salience"


def test_epistemic_priority_is_inspect_not_approach():
    selection = select_target([
        TargetState(
            "target",
            CircuitState(
                salience=SalienceState(epistemic_value=0.9),
            ),
        )
    ])
    assert derive_action_tendency(selection).kind is ActionTendencyKind.INSPECT


def test_semantic_orienting_priority_is_inspect():
    selection = select_target([
        TargetState(
            "target",
            CircuitState(
                salience=SalienceState(semantic_relevance=0.9),
            ),
        )
    ])
    assert derive_action_tendency(selection).kind is ActionTendencyKind.INSPECT


def test_generic_motivational_salience_stays_directionally_uncommitted():
    selection = select_target([
        TargetState(
            "target",
            CircuitState(
                salience=SalienceState(motivational_salience=0.9),
            ),
        )
    ])
    tendency = derive_action_tendency(selection)
    assert tendency.kind is ActionTendencyKind.UNCOMMITTED
    assert tendency.strength == pytest.approx(0.9)


def test_weak_recall_below_directional_gate_does_not_force_direction():
    recall = recall_for(prediction_error=-0.1)
    selection = select_target([
        TargetState(
            "target",
            CircuitState(
                salience=SalienceState(motivational_salience=0.9),
            ),
        )
    ])
    tendency = derive_action_tendency(
        selection,
        recall=recall,
        recall_target_id="target",
        policy=ActionTendencyPolicy(
            minimum_recall_directional_support=0.2,
        ),
    )
    assert tendency.kind is ActionTendencyKind.UNCOMMITTED


def test_recall_evidence_must_bind_to_selected_target():
    recall = recall_for(prediction_error=-0.8)
    selection = select_target([
        TargetState(
            "target",
            CircuitState(
                salience=SalienceState(motivational_salience=0.8),
            ),
        )
    ])
    with pytest.raises(ValueError):
        derive_action_tendency(
            selection,
            recall=recall,
            recall_target_id="different-target",
        )


def test_no_selection_has_no_committed_direction():
    selection = select_target([TargetState("target")])
    tendency = derive_action_tendency(selection)
    assert tendency.target_id is None
    assert tendency.kind is ActionTendencyKind.UNCOMMITTED
    assert tendency.strength == 0.0


def test_direction_derivation_does_not_mutate_reward_state():
    state = CircuitState(
        reward=RewardState(
            pleasure=3.0,
            hazard=0.0,
            avoidance=0.0,
        ),
        salience=SalienceState(motivational_salience=0.8),
    )
    selection = select_target([TargetState("target", state)])
    recall = recall_for(prediction_error=-0.8)
    _ = derive_action_tendency(
        selection,
        recall=recall,
        recall_target_id="target",
    )
    assert state.reward.pleasure == 3.0
    assert state.reward.hazard == 0.0
    assert state.reward.avoidance == 0.0
