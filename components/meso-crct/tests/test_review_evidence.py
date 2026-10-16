import pytest

from meso_crct import (
    CircuitState,
    EventSequencer,
    Provenance,
    ProvenanceVerifier,
    ReviewEvidence,
    ReviewEvidenceAssessment,
    ReviewEvidenceKind,
    ReviewEvidenceMismatch,
    ReviewEvidenceOutcome,
    ReviewEvidencePolicy,
    ReviewRiskClass,
    SalienceState,
    SourceKind,
    assess_review_evidence,
    bind_review_evidence,
    evaluate_transition,
)


def receipt(stream: str):
    state = CircuitState(
        salience=SalienceState(semantic_relevance=0.5),
    )
    claim = Provenance(
        source_kind=SourceKind.ENVIRONMENT,
        source_id=stream,
        source_revision="v1",
    )
    verified = ProvenanceVerifier(
        [claim],
        verifier_id="review-evidence-verifier",
    ).verify(claim)
    _, event = EventSequencer(stream).issue()
    return evaluate_transition(
        before=CircuitState(),
        after=state,
        provenance=verified,
        event=event,
    )


def evidence(kind, outcome, *, association="cue->outcome", revision="rev-1", ref="case", receipt_obj=None):
    return bind_review_evidence(
        association_id=association,
        memory_revision_id=revision,
        kind=kind,
        outcome=outcome,
        evidence_ref=ref,
        receipt=receipt(ref) if receipt_obj is None else receipt_obj,
    )


def test_review_evidence_cannot_be_constructed_directly():
    with pytest.raises(TypeError):
        ReviewEvidence(
            association_id="cue->outcome",
            memory_revision_id="rev-1",
            kind=ReviewEvidenceKind.HOLDOUT,
            outcome=ReviewEvidenceOutcome.SUPPORTS,
            evidence_ref="fake",
            transition_receipt_id="fake",
            event_id="fake",
            evidence_id="fake",
        )


def test_assessment_cannot_be_constructed_directly():
    with pytest.raises(TypeError):
        ReviewEvidenceAssessment(
            association_id="cue->outcome",
            memory_revision_id="rev-1",
            risk_class=ReviewRiskClass.CLEAR,
            evidence_ids=("fake",),
            supporting_holdout_ids=("fake",),
            supporting_holdout_event_ids=("fake-event",),
            contradicting_evidence_ids=(),
            required_supporting_holdout_events=1,
            assessment_id="fake",
        )


def test_counterexample_contradiction_is_contradicted():
    assessment = assess_review_evidence([
        evidence(
            ReviewEvidenceKind.COUNTEREXAMPLE,
            ReviewEvidenceOutcome.CONTRADICTS,
        )
    ])
    assert assessment.risk_class is ReviewRiskClass.CONTRADICTED


def test_holdout_contradiction_is_suspected_overgeneralization():
    assessment = assess_review_evidence([
        evidence(
            ReviewEvidenceKind.HOLDOUT,
            ReviewEvidenceOutcome.CONTRADICTS,
        )
    ])
    assert (
        assessment.risk_class
        is ReviewRiskClass.SUSPECTED_OVERGENERALIZATION
    )


def test_one_supporting_holdout_is_insufficient_under_default_policy():
    assessment = assess_review_evidence([
        evidence(
            ReviewEvidenceKind.HOLDOUT,
            ReviewEvidenceOutcome.SUPPORTS,
        )
    ])
    assert assessment.risk_class is ReviewRiskClass.INSUFFICIENT
    assert assessment.required_supporting_holdout_events == 2


def test_two_distinct_supporting_holdout_events_are_clear():
    assessment = assess_review_evidence([
        evidence(
            ReviewEvidenceKind.HOLDOUT,
            ReviewEvidenceOutcome.SUPPORTS,
            ref="holdout-1",
        ),
        evidence(
            ReviewEvidenceKind.HOLDOUT,
            ReviewEvidenceOutcome.SUPPORTS,
            ref="holdout-2",
        ),
    ])
    assert assessment.risk_class is ReviewRiskClass.CLEAR
    assert len(assessment.supporting_holdout_event_ids) == 2


def test_duplicate_labels_on_same_holdout_event_do_not_satisfy_diversity():
    shared_receipt = receipt("same-holdout-event")
    assessment = assess_review_evidence([
        evidence(
            ReviewEvidenceKind.HOLDOUT,
            ReviewEvidenceOutcome.SUPPORTS,
            ref="label-a",
            receipt_obj=shared_receipt,
        ),
        evidence(
            ReviewEvidenceKind.HOLDOUT,
            ReviewEvidenceOutcome.SUPPORTS,
            ref="label-b",
            receipt_obj=shared_receipt,
        ),
    ])
    assert len(assessment.supporting_holdout_ids) == 2
    assert len(assessment.supporting_holdout_event_ids) == 1
    assert assessment.risk_class is ReviewRiskClass.INSUFFICIENT


def test_policy_can_explicitly_require_more_distinct_holdout_events():
    assessment = assess_review_evidence(
        [
            evidence(
                ReviewEvidenceKind.HOLDOUT,
                ReviewEvidenceOutcome.SUPPORTS,
                ref="holdout-1",
            ),
            evidence(
                ReviewEvidenceKind.HOLDOUT,
                ReviewEvidenceOutcome.SUPPORTS,
                ref="holdout-2",
            ),
        ],
        policy=ReviewEvidencePolicy(
            minimum_supporting_holdout_events=3
        ),
    )
    assert assessment.risk_class is ReviewRiskClass.INSUFFICIENT


def test_inconclusive_only_evidence_is_insufficient():
    assessment = assess_review_evidence([
        evidence(
            ReviewEvidenceKind.HOLDOUT,
            ReviewEvidenceOutcome.INCONCLUSIVE,
        )
    ])
    assert assessment.risk_class is ReviewRiskClass.INSUFFICIENT


def test_mixed_revision_evidence_cannot_be_collapsed_into_one_assessment():
    with pytest.raises(ReviewEvidenceMismatch):
        assess_review_evidence([
            evidence(
                ReviewEvidenceKind.HOLDOUT,
                ReviewEvidenceOutcome.SUPPORTS,
                revision="rev-1",
                ref="one",
            ),
            evidence(
                ReviewEvidenceKind.HOLDOUT,
                ReviewEvidenceOutcome.SUPPORTS,
                revision="rev-2",
                ref="two",
            ),
        ])
