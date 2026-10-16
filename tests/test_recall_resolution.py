import pytest

from meso_crct import (
    AssociationMemory,
    CircuitState,
    EventSequencer,
    LearningState,
    PlasticityPolicy,
    Provenance,
    ProvenanceVerifier,
    RecallDisposition,
    RecallEventMismatch,
    RecallResolution,
    RecallResolutionPolicy,
    SalienceState,
    SourceKind,
    apply_candidate,
    evaluate_transition,
    propose_plasticity,
    recall_association,
    resolve_recall_influences,
)


def recall_for(
    association_id: str,
    *,
    prediction_error: float,
    cue_receipt,
):
    learning_state = CircuitState(
        salience=SalienceState(semantic_relevance=1.0),
        learning=LearningState(prediction_error=prediction_error),
    )
    claim = Provenance(
        source_kind=SourceKind.ENVIRONMENT,
        source_id=f"learn:{association_id}",
        source_revision="v1",
    )
    verified = ProvenanceVerifier(
        [claim],
        verifier_id="recall-resolution-verifier",
    ).verify(claim)
    _, event = EventSequencer(f"learn:{association_id}").issue()
    receipt = evaluate_transition(
        before=CircuitState(),
        after=learning_state,
        provenance=verified,
        event=event,
    )
    candidate = propose_plasticity(
        state=learning_state,
        association_id=association_id,
        receipt=receipt,
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
    return recall_association(
        memory=memory,
        association_id=association_id,
        cue_match=1.0,
        cue_receipt=cue_receipt,
    )


def cue_receipt(stream="cue-stream"):
    state = CircuitState(
        salience=SalienceState(perceptual_salience=0.8),
    )
    claim = Provenance(
        source_kind=SourceKind.ENVIRONMENT,
        source_id=stream,
        source_revision="v1",
    )
    verified = ProvenanceVerifier(
        [claim],
        verifier_id="recall-resolution-verifier",
    ).verify(claim)
    _, event = EventSequencer(stream).issue()
    return evaluate_transition(
        before=CircuitState(),
        after=state,
        provenance=verified,
        event=event,
    )


def test_recall_resolution_cannot_be_constructed_directly():
    with pytest.raises(TypeError):
        RecallResolution(
            disposition=RecallDisposition.NEUTRAL,
            cue_event_id=None,
            approach_support=0.0,
            learned_avoidance_support=0.0,
            dominant_support=0.0,
            memory_revision_ids=(),
        )


def test_opposed_near_equal_recall_is_preserved_as_conflict():
    cue = cue_receipt()
    positive = recall_for("positive", prediction_error=0.8, cue_receipt=cue)
    negative = recall_for("negative", prediction_error=-0.75, cue_receipt=cue)
    result = resolve_recall_influences(
        [positive, negative],
        policy=RecallResolutionPolicy(conflict_margin=0.10),
    )
    assert result.disposition is RecallDisposition.CONFLICT
    assert result.approach_support == pytest.approx(0.8)
    assert result.learned_avoidance_support == pytest.approx(0.75)


def test_stronger_negative_recall_resolves_to_avoid():
    cue = cue_receipt()
    positive = recall_for("positive", prediction_error=0.3, cue_receipt=cue)
    negative = recall_for("negative", prediction_error=-0.9, cue_receipt=cue)
    result = resolve_recall_influences([positive, negative])
    assert result.disposition is RecallDisposition.AVOID
    assert result.dominant_support == pytest.approx(0.9)


def test_many_weak_same_direction_memories_do_not_sum_into_strong_direction():
    cue = cue_receipt()
    influences = [
        recall_for(f"weak-{index}", prediction_error=0.15, cue_receipt=cue)
        for index in range(5)
    ]
    result = resolve_recall_influences(influences)
    assert result.approach_support == pytest.approx(0.15)
    assert result.disposition is RecallDisposition.NEUTRAL


def test_different_cue_events_cannot_be_resolved_as_one_moment():
    first = recall_for(
        "first",
        prediction_error=0.8,
        cue_receipt=cue_receipt("cue-1"),
    )
    second = recall_for(
        "second",
        prediction_error=-0.8,
        cue_receipt=cue_receipt("cue-2"),
    )
    with pytest.raises(RecallEventMismatch):
        resolve_recall_influences([first, second])


def test_empty_recall_set_is_neutral():
    result = resolve_recall_influences([])
    assert result.disposition is RecallDisposition.NEUTRAL
    assert result.cue_event_id is None
    assert result.dominant_support == 0.0
