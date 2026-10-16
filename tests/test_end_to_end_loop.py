import pytest

from meso_crct import (
    ActionTendencyKind,
    AssociationMemory,
    CircuitState,
    EventSequencer,
    ExperienceLearningSpec,
    PlasticityPolicy,
    Provenance,
    ProvenanceVerifier,
    RecallLedger,
    RewardState,
    SalienceState,
    SemanticEvidence,
    SourceKind,
    TargetAppraisalInput,
    TargetState,
    apply_recall_motivation,
    build_target_appraisal,
    derive_action_tendency,
    evaluate_transition,
    process_appraised_experience,
    recall_association,
    select_target,
)


def verified_source(source_id: str):
    claim = Provenance(
        source_kind=SourceKind.ENVIRONMENT,
        source_id=source_id,
        source_revision="v1",
    )
    return ProvenanceVerifier(
        [claim],
        verifier_id="end-to-end-verifier",
    ).verify(claim)


def learn_association(*, prediction_error: float):
    appraisal = build_target_appraisal(
        TargetAppraisalInput(
            target_id="cue-target",
            semantic_evidence=SemanticEvidence(context_relevance=1.0),
            prediction_error=prediction_error,
            reward=RewardState(pleasure=0.0, hazard=0.0, avoidance=0.0),
        )
    )
    _, event = EventSequencer("learning-stream").issue()
    result = process_appraised_experience(
        before=CircuitState(),
        appraised=appraisal,
        provenance=verified_source("learning-observation"),
        event=event,
        memory=AssociationMemory(),
        learning=ExperienceLearningSpec(
            association_id="cue->outcome",
            policy=PlasticityPolicy(
                maximum_absolute_delta=1.0,
                minimum_salience_gate=0.4,
            ),
            expected_version=0,
        ),
    )
    return result.memory


def later_cue_receipt():
    cue_state = CircuitState(
        reward=RewardState(pleasure=0.0, hazard=0.0, avoidance=0.0),
        salience=SalienceState(perceptual_salience=0.7),
    )
    _, event = EventSequencer("later-cue-stream").issue()
    receipt = evaluate_transition(
        before=CircuitState(),
        after=cue_state,
        provenance=verified_source("later-cue-observation"),
        event=event,
    )
    return cue_state, receipt


def test_negative_learning_recall_selection_and_direction_end_to_end():
    memory = learn_association(prediction_error=-1.0)
    cue_state, cue_receipt = later_cue_receipt()

    recall = recall_association(
        memory=memory,
        association_id="cue->outcome",
        cue_match=0.8,
        cue_receipt=cue_receipt,
    )
    recalled_state, ledger = apply_recall_motivation(
        cue_state,
        recall,
        RecallLedger(),
    )

    selection = select_target([
        TargetState("cue-target", recalled_state),
        TargetState(
            "interesting-distractor",
            CircuitState(
                salience=SalienceState(epistemic_value=0.95),
            ),
        ),
    ])
    tendency = derive_action_tendency(
        selection,
        recall=recall,
        recall_target_id="cue-target",
    )

    assert selection.selected_target_id == "cue-target"
    assert tendency.kind is ActionTendencyKind.LEARNED_WITHDRAW
    assert tendency.strength == pytest.approx(0.8)
    assert recalled_state.reward.pleasure == 0.0
    assert recalled_state.reward.hazard == 0.0
    assert recalled_state.reward.avoidance == 0.0
    assert len(ledger.consumed) == 1


def test_positive_learning_recall_selection_and_direction_end_to_end():
    memory = learn_association(prediction_error=1.0)
    cue_state, cue_receipt = later_cue_receipt()

    recall = recall_association(
        memory=memory,
        association_id="cue->outcome",
        cue_match=0.75,
        cue_receipt=cue_receipt,
    )
    recalled_state, _ = apply_recall_motivation(
        cue_state,
        recall,
        RecallLedger(),
    )
    selection = select_target([TargetState("cue-target", recalled_state)])
    tendency = derive_action_tendency(
        selection,
        recall=recall,
        recall_target_id="cue-target",
    )

    assert tendency.kind is ActionTendencyKind.APPROACH
    assert tendency.strength == pytest.approx(0.75)
    assert recalled_state.reward.pleasure == 0.0


def test_same_priority_can_produce_different_action_direction_from_learning():
    negative_memory = learn_association(prediction_error=-1.0)
    positive_memory = learn_association(prediction_error=1.0)

    negative_cue, negative_receipt = later_cue_receipt()
    positive_cue, positive_receipt = later_cue_receipt()

    negative_recall = recall_association(
        memory=negative_memory,
        association_id="cue->outcome",
        cue_match=0.8,
        cue_receipt=negative_receipt,
    )
    positive_recall = recall_association(
        memory=positive_memory,
        association_id="cue->outcome",
        cue_match=0.8,
        cue_receipt=positive_receipt,
    )

    negative_state, _ = apply_recall_motivation(
        negative_cue,
        negative_recall,
        RecallLedger(),
    )
    positive_state, _ = apply_recall_motivation(
        positive_cue,
        positive_recall,
        RecallLedger(),
    )

    negative_selection = select_target([TargetState("target", negative_state)])
    positive_selection = select_target([TargetState("target", positive_state)])

    negative_tendency = derive_action_tendency(
        negative_selection,
        recall=negative_recall,
        recall_target_id="target",
    )
    positive_tendency = derive_action_tendency(
        positive_selection,
        recall=positive_recall,
        recall_target_id="target",
    )

    assert negative_selection.selected_decision.priority == pytest.approx(
        positive_selection.selected_decision.priority
    )
    assert negative_tendency.kind is ActionTendencyKind.LEARNED_WITHDRAW
    assert positive_tendency.kind is ActionTendencyKind.APPROACH
