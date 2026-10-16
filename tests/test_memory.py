import pytest

from meso_crct import (
    AssociationIntegrityError,
    AssociationMemory,
    AssociationNotFound,
    AssociationRevision,
    CircuitState,
    EventSequencer,
    LearningState,
    MemoryVersionConflict,
    PlasticityNoOpError,
    PlasticityPolicy,
    PlasticityReplayError,
    Provenance,
    ProvenanceVerifier,
    SalienceState,
    SourceKind,
    apply_candidate,
    evaluate_transition,
    propose_plasticity,
    revert_last,
)


def state_and_receipt(
    *,
    prediction_error=1.0,
    salience=1.0,
    source_id="observation:memory-test-1",
):
    state = CircuitState(
        salience=SalienceState(semantic_relevance=salience),
        learning=LearningState(prediction_error=prediction_error),
    )
    claim = Provenance(
        source_kind=SourceKind.ENVIRONMENT,
        source_id=source_id,
        source_revision="v1",
    )
    verified = ProvenanceVerifier(
        [claim],
        verifier_id="memory-test-verifier",
    ).verify(claim)
    _, event = EventSequencer(source_id).issue()
    receipt = evaluate_transition(
        before=CircuitState(),
        after=state,
        provenance=verified,
        event=event,
    )
    return state, receipt


def candidate_for(
    association_id="cue->outcome",
    *,
    prediction_error=1.0,
    salience=1.0,
    source_id="observation:memory-test-1",
):
    state, receipt = state_and_receipt(
        prediction_error=prediction_error,
        salience=salience,
        source_id=source_id,
    )
    return propose_plasticity(
        state=state,
        association_id=association_id,
        receipt=receipt,
        policy=PlasticityPolicy(
            maximum_absolute_delta=0.1,
            minimum_salience_gate=0.4,
        ),
    )


def test_apply_candidate_creates_first_version():
    memory = AssociationMemory()
    updated = apply_candidate(
        memory,
        candidate_for(),
        expected_version=0,
    )
    current = updated.current("cue->outcome")
    assert current is not None
    assert current.version == 1
    assert current.strength == pytest.approx(0.1)
    assert current.parent_revision_id is None
    assert memory.current("cue->outcome") is None


def test_stale_writer_fails_version_check():
    memory = apply_candidate(
        AssociationMemory(),
        candidate_for(),
        expected_version=0,
    )
    with pytest.raises(MemoryVersionConflict):
        apply_candidate(
            memory,
            candidate_for(source_id="observation:memory-test-2"),
            expected_version=0,
        )


def test_same_transition_receipt_cannot_be_replayed_for_same_association():
    candidate = candidate_for()
    memory = apply_candidate(
        AssociationMemory(),
        candidate,
        expected_version=0,
    )
    with pytest.raises(PlasticityReplayError):
        apply_candidate(
            memory,
            candidate,
            expected_version=1,
        )


def test_one_transition_may_update_distinct_associations():
    state, receipt = state_and_receipt()
    policy = PlasticityPolicy(
        maximum_absolute_delta=0.1,
        minimum_salience_gate=0.4,
    )
    first = propose_plasticity(
        state=state,
        association_id="cue->outcome",
        receipt=receipt,
        policy=policy,
    )
    second = propose_plasticity(
        state=state,
        association_id="context->outcome",
        receipt=receipt,
        policy=policy,
    )
    memory = apply_candidate(
        AssociationMemory(),
        first,
        expected_version=0,
    )
    memory = apply_candidate(
        memory,
        second,
        expected_version=0,
    )
    assert memory.current_strength("cue->outcome") == pytest.approx(0.1)
    assert memory.current_strength("context->outcome") == pytest.approx(0.1)


def test_zero_delta_candidate_is_not_persisted():
    candidate = candidate_for(prediction_error=0.0)
    with pytest.raises(PlasticityNoOpError):
        apply_candidate(
            AssociationMemory(),
            candidate,
            expected_version=0,
        )


def test_second_distinct_candidate_appends_parent_bound_history():
    first = candidate_for(source_id="observation:memory-test-1")
    second = candidate_for(
        prediction_error=-0.5,
        source_id="observation:memory-test-2",
    )
    memory = apply_candidate(
        AssociationMemory(),
        first,
        expected_version=0,
    )
    memory = apply_candidate(
        memory,
        second,
        expected_version=1,
    )
    history = memory.history("cue->outcome")
    assert len(history) == 2
    assert history[-1].version == 2
    assert history[-1].strength == pytest.approx(0.05)
    assert history[-1].parent_revision_id == history[-2].revision_id


def test_revert_appends_new_parent_bound_revision_without_deleting_history():
    candidate = candidate_for()
    memory = apply_candidate(
        AssociationMemory(),
        candidate,
        expected_version=0,
    )
    reverted = revert_last(
        memory,
        "cue->outcome",
        expected_version=1,
    )
    history = reverted.history("cue->outcome")
    assert len(history) == 2
    assert history[0].operation == "apply"
    assert history[1].operation == "revert"
    assert history[1].version == 2
    assert history[1].strength == 0.0
    assert history[1].parent_revision_id == history[0].revision_id


def test_revert_missing_association_fails():
    with pytest.raises(AssociationNotFound):
        revert_last(
            AssociationMemory(),
            "missing",
            expected_version=0,
        )


def test_strength_remains_bounded_across_repeated_distinct_updates():
    memory = AssociationMemory()
    for index in range(20):
        candidate = candidate_for(
            source_id=f"observation:memory-test-{index}",
        )
        memory = apply_candidate(
            memory,
            candidate,
            expected_version=index,
        )
    assert memory.current_strength("cue->outcome") == 1.0


def test_revision_ids_are_deterministic_for_same_history():
    candidate = candidate_for()
    first = apply_candidate(
        AssociationMemory(),
        candidate,
        expected_version=0,
    )
    second = apply_candidate(
        AssociationMemory(),
        candidate,
        expected_version=0,
    )
    assert first.revisions[0].revision_id == second.revisions[0].revision_id


def test_tampered_parent_chain_is_rejected():
    memory = apply_candidate(
        AssociationMemory(),
        candidate_for(),
        expected_version=0,
    )
    original = memory.revisions[0]
    tampered = AssociationRevision(
        association_id=original.association_id,
        version=original.version,
        strength=original.strength,
        previous_strength=original.previous_strength,
        applied_delta=original.applied_delta,
        transition_receipt_id=original.transition_receipt_id,
        operation=original.operation,
        parent_revision_id="not-the-parent",
        revision_id=original.revision_id,
    )
    with pytest.raises(AssociationIntegrityError):
        AssociationMemory(revisions=(tampered,))
