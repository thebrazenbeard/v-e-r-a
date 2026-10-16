import pytest

from meso_crct import (
    AssociationMemory,
    CircuitState,
    EventSequencer,
    LearningState,
    PlasticityPolicy,
    Provenance,
    ProvenanceVerifier,
    RecallDirection,
    RecallInfluence,
    RecallLedger,
    RecallReplayError,
    RewardState,
    SalienceState,
    SourceKind,
    apply_candidate,
    apply_recall_motivation,
    evaluate_transition,
    propose_plasticity,
    recall_association,
)


def transition_receipt(state, *, source_id, event=None):
    claim = Provenance(
        source_kind=SourceKind.ENVIRONMENT,
        source_id=source_id,
        source_revision="v1",
    )
    verified = ProvenanceVerifier(
        [claim],
        verifier_id="recall-test-verifier",
    ).verify(claim)
    if event is None:
        _, event = EventSequencer(source_id).issue()
    return evaluate_transition(
        before=CircuitState(),
        after=state,
        provenance=verified,
        event=event,
    )


def learned_memory(*, prediction_error=1.0):
    learning_state = CircuitState(
        salience=SalienceState(semantic_relevance=1.0),
        learning=LearningState(prediction_error=prediction_error),
    )
    receipt = transition_receipt(
        learning_state,
        source_id=f"observation:learn:{prediction_error}",
    )
    candidate = propose_plasticity(
        state=learning_state,
        association_id="cue->outcome",
        receipt=receipt,
        policy=PlasticityPolicy(
            maximum_absolute_delta=1.0,
            minimum_salience_gate=0.4,
        ),
    )
    return apply_candidate(
        AssociationMemory(),
        candidate,
        expected_version=0,
    )


def current_cue_receipt(*, event=None):
    cue_state = CircuitState(
        salience=SalienceState(perceptual_salience=0.7),
    )
    return transition_receipt(
        cue_state,
        source_id="observation:current-cue",
        event=event,
    )


def test_recall_influence_cannot_be_constructed_directly():
    with pytest.raises(TypeError):
        RecallInfluence(
            association_id="cue->outcome",
            memory_revision_id="fake-revision",
            cue_receipt_id="fake-receipt",
            cue_event_id="fake-event",
            cue_match=1.0,
            learned_strength=1.0,
            signed_influence=1.0,
            motivational_support=1.0,
            approach_support=1.0,
            learned_avoidance_support=0.0,
            direction=RecallDirection.APPROACH,
        )


def test_memory_strength_does_nothing_without_current_cue_match():
    influence = recall_association(
        memory=learned_memory(),
        association_id="cue->outcome",
        cue_match=0.0,
        cue_receipt=current_cue_receipt(),
    )
    assert influence.signed_influence == 0.0
    assert influence.motivational_support == 0.0
    assert influence.direction is RecallDirection.NEUTRAL


def test_positive_learned_association_supports_approach_motivation():
    memory = learned_memory(prediction_error=0.8)
    influence = recall_association(
        memory=memory,
        association_id="cue->outcome",
        cue_match=0.5,
        cue_receipt=current_cue_receipt(),
    )
    assert influence.signed_influence == pytest.approx(0.4)
    assert influence.approach_support == pytest.approx(0.4)
    assert influence.learned_avoidance_support == 0.0
    assert influence.direction is RecallDirection.APPROACH


def test_negative_learned_association_preserves_avoid_direction():
    memory = learned_memory(prediction_error=-0.8)
    influence = recall_association(
        memory=memory,
        association_id="cue->outcome",
        cue_match=0.5,
        cue_receipt=current_cue_receipt(),
    )
    assert influence.signed_influence == pytest.approx(-0.4)
    assert influence.approach_support == 0.0
    assert influence.learned_avoidance_support == pytest.approx(0.4)
    assert influence.direction is RecallDirection.AVOID


def test_recall_can_raise_motivation_without_changing_pleasure_or_hazard():
    memory = learned_memory(prediction_error=-1.0)
    influence = recall_association(
        memory=memory,
        association_id="cue->outcome",
        cue_match=0.8,
        cue_receipt=current_cue_receipt(),
    )
    state = CircuitState(
        reward=RewardState(
            pleasure=3.0,
            hazard=0.2,
            avoidance=0.1,
        ),
        salience=SalienceState(motivational_salience=0.1),
    )
    updated, _ = apply_recall_motivation(
        state,
        influence,
        RecallLedger(),
    )
    assert updated.salience.motivational_salience == pytest.approx(0.8)
    assert updated.reward == state.reward


def test_recall_never_reduces_existing_motivation():
    influence = recall_association(
        memory=learned_memory(prediction_error=0.2),
        association_id="cue->outcome",
        cue_match=0.5,
        cue_receipt=current_cue_receipt(),
    )
    state = CircuitState(
        salience=SalienceState(motivational_salience=0.9),
    )
    updated, _ = apply_recall_motivation(
        state,
        influence,
        RecallLedger(),
    )
    assert updated.salience.motivational_salience == 0.9


def test_same_cue_event_cannot_refresh_same_association_twice():
    influence = recall_association(
        memory=learned_memory(),
        association_id="cue->outcome",
        cue_match=1.0,
        cue_receipt=current_cue_receipt(),
    )
    state, ledger = apply_recall_motivation(
        CircuitState(),
        influence,
        RecallLedger(),
    )
    with pytest.raises(RecallReplayError):
        apply_recall_motivation(state, influence, ledger)


def test_distinct_occurrence_of_same_cue_can_recall_again():
    sequencer = EventSequencer("observation:current-cue")
    sequencer, event1 = sequencer.issue()
    _, event2 = sequencer.issue()
    memory = learned_memory()

    first = recall_association(
        memory=memory,
        association_id="cue->outcome",
        cue_match=1.0,
        cue_receipt=current_cue_receipt(event=event1),
    )
    second = recall_association(
        memory=memory,
        association_id="cue->outcome",
        cue_match=1.0,
        cue_receipt=current_cue_receipt(event=event2),
    )

    state, ledger = apply_recall_motivation(
        CircuitState(),
        first,
        RecallLedger(),
    )
    state, ledger = apply_recall_motivation(state, second, ledger)
    assert len(ledger.consumed) == 2


def test_recall_binds_memory_revision_current_receipt_and_event():
    memory = learned_memory()
    cue_receipt = current_cue_receipt()
    influence = recall_association(
        memory=memory,
        association_id="cue->outcome",
        cue_match=1.0,
        cue_receipt=cue_receipt,
    )
    assert influence.memory_revision_id == memory.current("cue->outcome").revision_id
    assert influence.cue_receipt_id == cue_receipt.receipt_id
    assert influence.cue_event_id == cue_receipt.event_id
