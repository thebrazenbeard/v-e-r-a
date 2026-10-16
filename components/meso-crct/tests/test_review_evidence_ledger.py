import pytest

from meso_crct import (
    AssociationMemory,
    CircuitState,
    EventSequencer,
    LearningState,
    PlasticityPolicy,
    Provenance,
    ProvenanceVerifier,
    ReviewEvidenceConflictError,
    ReviewEvidenceKind,
    ReviewEvidenceMismatch,
    ReviewEvidenceOutcome,
    ReviewEvidenceReplayError,
    SalienceState,
    SourceKind,
    apply_candidate,
    bind_review_evidence,
    evaluate_transition,
    propose_plasticity,
    register_review_evidence,
)


def verified(source_id):
    claim = Provenance(
        source_kind=SourceKind.ENVIRONMENT,
        source_id=source_id,
        source_revision="v1",
    )
    return ProvenanceVerifier(
        [claim],
        verifier_id="evidence-ledger-verifier",
    ).verify(claim)


def learned_memory():
    state = CircuitState(
        salience=SalienceState(semantic_relevance=1.0),
        learning=LearningState(prediction_error=0.8),
    )
    _, event = EventSequencer("learn").issue()
    receipt = evaluate_transition(
        before=CircuitState(),
        after=state,
        provenance=verified("learn"),
        event=event,
    )
    candidate = propose_plasticity(
        state=state,
        association_id="cue->outcome",
        receipt=receipt,
        policy=PlasticityPolicy(
            maximum_absolute_delta=1.0,
            minimum_salience_gate=0.0,
        ),
    )
    return apply_candidate(AssociationMemory(), candidate, expected_version=0)


def evidence_for(memory, *, ref, receipt_obj=None, outcome=ReviewEvidenceOutcome.SUPPORTS):
    revision = memory.current("cue->outcome")
    assert revision is not None
    if receipt_obj is None:
        state = CircuitState(
            salience=SalienceState(semantic_relevance=0.5),
        )
        _, event = EventSequencer(ref).issue()
        receipt_obj = evaluate_transition(
            before=CircuitState(),
            after=state,
            provenance=verified(ref),
            event=event,
        )
    return bind_review_evidence(
        association_id="cue->outcome",
        memory_revision_id=revision.revision_id,
        kind=ReviewEvidenceKind.HOLDOUT,
        outcome=outcome,
        evidence_ref=ref,
        receipt=receipt_obj,
    )


def test_registered_evidence_is_append_only():
    memory = learned_memory()
    item = evidence_for(memory, ref="holdout-1")
    updated = register_review_evidence(memory, item)
    assert memory.review_evidence.evidence == ()
    assert updated.review_evidence.get(item.evidence_id) == item


def test_exact_same_evidence_cannot_be_registered_twice():
    memory = learned_memory()
    item = evidence_for(memory, ref="holdout-1")
    memory = register_review_evidence(memory, item)
    with pytest.raises(ReviewEvidenceReplayError):
        register_review_evidence(memory, item)


def test_same_event_cannot_be_relabelled_as_different_evidence():
    memory = learned_memory()
    state = CircuitState(
        salience=SalienceState(semantic_relevance=0.5),
    )
    _, event = EventSequencer("shared-event").issue()
    receipt_obj = evaluate_transition(
        before=CircuitState(),
        after=state,
        provenance=verified("shared-event"),
        event=event,
    )
    first = evidence_for(
        memory,
        ref="first-label",
        receipt_obj=receipt_obj,
        outcome=ReviewEvidenceOutcome.SUPPORTS,
    )
    second = evidence_for(
        memory,
        ref="second-label",
        receipt_obj=receipt_obj,
        outcome=ReviewEvidenceOutcome.CONTRADICTS,
    )
    memory = register_review_evidence(memory, first)
    with pytest.raises(ReviewEvidenceConflictError):
        register_review_evidence(memory, second)


def test_evidence_for_old_revision_cannot_be_registered_after_learning_changes():
    memory = learned_memory()
    old = evidence_for(memory, ref="old-review")

    state = CircuitState(
        salience=SalienceState(semantic_relevance=1.0),
        learning=LearningState(prediction_error=0.2),
    )
    _, event = EventSequencer("learn-again").issue()
    receipt = evaluate_transition(
        before=CircuitState(),
        after=state,
        provenance=verified("learn-again"),
        event=event,
    )
    candidate = propose_plasticity(
        state=state,
        association_id="cue->outcome",
        receipt=receipt,
        policy=PlasticityPolicy(
            maximum_absolute_delta=1.0,
            minimum_salience_gate=0.0,
        ),
    )
    changed = apply_candidate(memory, candidate, expected_version=1)

    with pytest.raises(ReviewEvidenceMismatch):
        register_review_evidence(changed, old)
