import pytest

from meso_crct import (
    CircuitState,
    EventSequencer,
    LearningState,
    PlasticityCandidate,
    PlasticityPolicy,
    PlasticityReceiptMismatch,
    Provenance,
    ProvenanceVerifier,
    RewardState,
    SalienceState,
    SourceKind,
    evaluate_transition,
    preview_association_strength,
    propose_plasticity,
)


def receipt_for(state):
    before = CircuitState()
    claim = Provenance(
        source_kind=SourceKind.ENVIRONMENT,
        source_id="observation:plasticity-test",
        source_revision="v1",
    )
    verified = ProvenanceVerifier(
        [claim],
        verifier_id="plasticity-test-verifier",
    ).verify(claim)
    _, event = EventSequencer("plasticity-test-stream").issue()
    return evaluate_transition(
        before=before,
        after=state,
        provenance=verified,
        event=event,
    )


def policy():
    return PlasticityPolicy(
        maximum_absolute_delta=0.1,
        minimum_salience_gate=0.4,
    )


def test_plasticity_candidate_cannot_be_constructed_directly():
    with pytest.raises(TypeError):
        PlasticityCandidate(
            association_id="cue->outcome",
            delta=1.0,
            teaching_signal=1.0,
            salience_gate=1.0,
            gate_driver="semantic_relevance",
            transition_receipt_id="pretend-receipt",
        )


def test_plasticity_requires_receipt_for_same_after_state():
    receipt_state = CircuitState(
        salience=SalienceState(semantic_relevance=0.8),
        learning=LearningState(prediction_error=1.0),
    )
    different_state = CircuitState(
        salience=SalienceState(semantic_relevance=0.9),
        learning=LearningState(prediction_error=1.0),
    )
    with pytest.raises(PlasticityReceiptMismatch):
        propose_plasticity(
            state=different_state,
            association_id="cue->outcome",
            receipt=receipt_for(receipt_state),
            policy=policy(),
        )


def test_positive_prediction_error_proposes_bounded_strengthening():
    state = CircuitState(
        salience=SalienceState(semantic_relevance=0.8),
        learning=LearningState(prediction_error=1.0),
    )
    candidate = propose_plasticity(
        state=state,
        association_id="cue->outcome",
        receipt=receipt_for(state),
        policy=policy(),
    )
    assert candidate.delta == pytest.approx(0.08)
    assert candidate.gate_driver == "semantic_relevance"


def test_negative_prediction_error_proposes_weakening():
    state = CircuitState(
        salience=SalienceState(motivational_salience=1.0),
        learning=LearningState(prediction_error=-0.5),
    )
    candidate = propose_plasticity(
        state=state,
        association_id="cue->outcome",
        receipt=receipt_for(state),
        policy=policy(),
    )
    assert candidate.delta == pytest.approx(-0.05)


def test_no_teaching_signal_means_no_persistent_update_candidate():
    state = CircuitState(
        salience=SalienceState(incentive_salience=1.0),
        learning=LearningState(prediction_error=0.0),
    )
    candidate = propose_plasticity(
        state=state,
        association_id="cue->outcome",
        receipt=receipt_for(state),
        policy=policy(),
    )
    assert candidate.delta == 0.0


def test_salience_below_gate_blocks_update():
    state = CircuitState(
        salience=SalienceState(semantic_relevance=0.2),
        learning=LearningState(prediction_error=1.0),
    )
    candidate = propose_plasticity(
        state=state,
        association_id="cue->outcome",
        receipt=receipt_for(state),
        policy=policy(),
    )
    assert candidate.delta == 0.0


def test_pleasure_alone_does_not_create_permanent_preference_update():
    state = CircuitState(
        reward=RewardState(pleasure=10.0),
        learning=LearningState(prediction_error=0.0),
    )
    candidate = propose_plasticity(
        state=state,
        association_id="cue->outcome",
        receipt=receipt_for(state),
        policy=policy(),
    )
    assert candidate.delta == 0.0


def test_candidate_is_bound_to_transition_receipt():
    state = CircuitState(
        salience=SalienceState(epistemic_value=0.9),
        learning=LearningState(prediction_error=0.5),
    )
    receipt = receipt_for(state)
    candidate = propose_plasticity(
        state=state,
        association_id="question->answer",
        receipt=receipt,
        policy=policy(),
    )
    assert candidate.transition_receipt_id == receipt.receipt_id


def test_preview_is_bounded_and_nonpersistent():
    state = CircuitState(
        salience=SalienceState(semantic_relevance=1.0),
        learning=LearningState(prediction_error=1.0),
    )
    candidate = propose_plasticity(
        state=state,
        association_id="cue->outcome",
        receipt=receipt_for(state),
        policy=PlasticityPolicy(
            maximum_absolute_delta=1.0,
            minimum_salience_gate=0.0,
        ),
    )
    assert preview_association_strength(0.8, candidate) == 1.0
