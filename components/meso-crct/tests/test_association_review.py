import pytest

from meso_crct import (
    AssociationIntegrityError,
    AssociationMemory,
    AssociationQuarantinedError,
    AssociationReviewRecord,
    AssociationReviewStaleError,
    CircuitState,
    EventSequencer,
    LearningState,
    PlasticityPolicy,
    Provenance,
    ProvenanceVerifier,
    ReviewAssessmentInsufficient,
    ReviewAssessmentMismatch,
    ReviewDisposition,
    ReviewEvidenceKind,
    ReviewEvidenceNotRegistered,
    ReviewEvidenceOutcome,
    ReviewNoOpError,
    ReviewRiskClass,
    SalienceState,
    SourceKind,
    apply_candidate,
    assess_review_evidence,
    bind_review_evidence,
    evaluate_transition,
    propose_plasticity,
    quarantine_association,
    recall_association,
    register_review_evidence,
    release_association,
)


def verified(source_id: str):
    claim = Provenance(
        source_kind=SourceKind.ENVIRONMENT,
        source_id=source_id,
        source_revision="v1",
    )
    return ProvenanceVerifier(
        [claim],
        verifier_id="review-test-verifier",
    ).verify(claim)


def learned_memory(*, prediction_error=0.8, stream="learn-1"):
    state = CircuitState(
        salience=SalienceState(semantic_relevance=1.0),
        learning=LearningState(prediction_error=prediction_error),
    )
    _, event = EventSequencer(stream).issue()
    receipt = evaluate_transition(
        before=CircuitState(),
        after=state,
        provenance=verified(stream),
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
    return apply_candidate(
        AssociationMemory(),
        candidate,
        expected_version=0,
    )


def add_learning(memory, *, prediction_error=0.2, stream="learn-2"):
    state = CircuitState(
        salience=SalienceState(semantic_relevance=1.0),
        learning=LearningState(prediction_error=prediction_error),
    )
    _, event = EventSequencer(stream).issue()
    receipt = evaluate_transition(
        before=CircuitState(),
        after=state,
        provenance=verified(stream),
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
    return apply_candidate(
        memory,
        candidate,
        expected_version=memory.current_version("cue->outcome"),
    )


def cue_receipt(stream="cue"):
    state = CircuitState(
        salience=SalienceState(perceptual_salience=0.8),
    )
    _, event = EventSequencer(stream).issue()
    return evaluate_transition(
        before=CircuitState(),
        after=state,
        provenance=verified(stream),
        event=event,
    )


def register_assessment(memory, specs):
    revision = memory.current("cue->outcome")
    assert revision is not None
    items = []
    for kind, outcome, ref in specs:
        item = bind_review_evidence(
            association_id="cue->outcome",
            memory_revision_id=revision.revision_id,
            kind=kind,
            outcome=outcome,
            evidence_ref=ref,
            receipt=cue_receipt(ref),
        )
        memory = register_review_evidence(memory, item)
        items.append(item)
    return memory, assess_review_evidence(items)


def quarantine_assessment(memory, ref="negative-transfer"):
    return register_assessment(
        memory,
        [
            (
                ReviewEvidenceKind.HOLDOUT,
                ReviewEvidenceOutcome.CONTRADICTS,
                ref,
            )
        ],
    )


def clear_assessment(memory, ref="clear-holdout"):
    return register_assessment(
        memory,
        [
            (
                ReviewEvidenceKind.HOLDOUT,
                ReviewEvidenceOutcome.SUPPORTS,
                f"{ref}-a",
            ),
            (
                ReviewEvidenceKind.HOLDOUT,
                ReviewEvidenceOutcome.SUPPORTS,
                f"{ref}-b",
            ),
        ],
    )


def test_review_record_cannot_be_constructed_directly():
    with pytest.raises(TypeError):
        AssociationReviewRecord(
            association_id="cue->outcome",
            review_version=1,
            memory_revision_id="fake",
            disposition=ReviewDisposition.QUARANTINED,
            risk_class=ReviewRiskClass.CONTRADICTED,
            assessment_id="fake",
            evidence_ids=("fake",),
            required_supporting_holdout_events=2,
            parent_review_id=None,
            review_id="fake",
        )


def test_unregistered_assessment_cannot_mutate_review_state():
    memory = learned_memory()
    revision = memory.current("cue->outcome")
    item = bind_review_evidence(
        association_id="cue->outcome",
        memory_revision_id=revision.revision_id,
        kind=ReviewEvidenceKind.HOLDOUT,
        outcome=ReviewEvidenceOutcome.CONTRADICTS,
        evidence_ref="not-registered",
        receipt=cue_receipt("not-registered"),
    )
    assessment = assess_review_evidence([item])
    with pytest.raises(ReviewEvidenceNotRegistered):
        quarantine_association(
            memory,
            "cue->outcome",
            assessment=assessment,
        )


def test_quarantine_preserves_learning_but_blocks_recall():
    memory = learned_memory()
    revision = memory.current("cue->outcome")
    memory, assessment = quarantine_assessment(memory)
    quarantined = quarantine_association(
        memory,
        "cue->outcome",
        assessment=assessment,
    )

    assert quarantined.current_strength("cue->outcome") == pytest.approx(0.8)
    assert quarantined.current("cue->outcome").revision_id == revision.revision_id
    assert quarantined.review_evidence.evidence
    assert quarantined.reviews.current("cue->outcome").assessment_id == assessment.assessment_id

    with pytest.raises(AssociationQuarantinedError):
        recall_association(
            memory=quarantined,
            association_id="cue->outcome",
            cue_match=1.0,
            cue_receipt=cue_receipt(),
        )


def test_release_requires_registered_clear_holdout_evidence():
    memory = learned_memory()
    memory, bad = quarantine_assessment(memory)
    memory = quarantine_association(
        memory,
        "cue->outcome",
        assessment=bad,
    )

    memory, still_bad = quarantine_assessment(memory, ref="still-bad")
    with pytest.raises(ReviewAssessmentInsufficient):
        release_association(
            memory,
            "cue->outcome",
            assessment=still_bad,
        )

    memory, clear = clear_assessment(memory)
    released = release_association(
        memory,
        "cue->outcome",
        assessment=clear,
    )
    influence = recall_association(
        memory=released,
        association_id="cue->outcome",
        cue_match=1.0,
        cue_receipt=cue_receipt(),
    )
    assert influence.review_record_id == released.reviews.current(
        "cue->outcome"
    ).review_id


def test_learning_change_after_release_makes_review_stale_until_new_evidence():
    memory = learned_memory()
    memory, bad = quarantine_assessment(memory)
    memory = quarantine_association(memory, "cue->outcome", assessment=bad)
    memory, clear = clear_assessment(memory)
    memory = release_association(memory, "cue->outcome", assessment=clear)
    changed = add_learning(memory)

    with pytest.raises(AssociationReviewStaleError):
        recall_association(
            memory=changed,
            association_id="cue->outcome",
            cue_match=1.0,
            cue_receipt=cue_receipt("cue-after-change"),
        )

    with pytest.raises(ReviewAssessmentMismatch):
        release_association(
            changed,
            "cue->outcome",
            assessment=clear,
        )

    changed, new_clear = clear_assessment(
        changed,
        ref="new-revision-holdout",
    )
    re_reviewed = release_association(
        changed,
        "cue->outcome",
        assessment=new_clear,
    )
    assert recall_association(
        memory=re_reviewed,
        association_id="cue->outcome",
        cue_match=1.0,
        cue_receipt=cue_receipt("cue-after-rereview"),
    ).learned_strength == pytest.approx(1.0)


def test_manual_review_registry_without_evidence_ledger_fails_memory_integrity():
    memory = learned_memory()
    memory_with_evidence, assessment = quarantine_assessment(memory)
    registry = memory_with_evidence.reviews.quarantine(
        association_id="cue->outcome",
        memory_revision_id=memory.current("cue->outcome").revision_id,
        assessment=assessment,
    )
    with pytest.raises(AssociationIntegrityError):
        AssociationMemory(
            revisions=memory.revisions,
            reviews=registry,
        )


def test_review_log_is_append_only_and_rejects_exact_same_assessment_noop():
    memory = learned_memory()
    memory, assessment = quarantine_assessment(memory)
    quarantined = quarantine_association(
        memory,
        "cue->outcome",
        assessment=assessment,
    )
    first = quarantined.reviews.current("cue->outcome")

    with pytest.raises(ReviewNoOpError):
        quarantine_association(
            quarantined,
            "cue->outcome",
            assessment=assessment,
        )

    quarantined, clear = clear_assessment(quarantined)
    released = release_association(
        quarantined,
        "cue->outcome",
        assessment=clear,
    )
    history = released.reviews.history("cue->outcome")
    assert len(history) == 2
    assert history[1].parent_review_id == first.review_id


def test_unreviewed_association_remains_recallable():
    memory = learned_memory()
    influence = recall_association(
        memory=memory,
        association_id="cue->outcome",
        cue_match=1.0,
        cue_receipt=cue_receipt(),
    )
    assert influence.review_record_id is None
