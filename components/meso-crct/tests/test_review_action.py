import pytest

from meso_crct import (
    AssociationMemory,
    CircuitState,
    EventSequencer,
    LearningState,
    PlasticityPolicy,
    Provenance,
    ProvenanceVerifier,
    ReviewActionKind,
    ReviewActionProposal,
    ReviewActionStaleError,
    ReviewDisposition,
    ReviewEvidenceKind,
    ReviewEvidenceLedger,
    ReviewEvidenceOutcome,
    SalienceState,
    SourceKind,
    apply_candidate,
    assess_review_evidence,
    bind_review_evidence,
    evaluate_transition,
    propose_plasticity,
    propose_review_action,
    quarantine_association,
    register_review_evidence,
    validate_review_action_proposal,
)


def receipt(stream):
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
        verifier_id="review-action-verifier",
    ).verify(claim)
    _, event = EventSequencer(stream).issue()
    return evaluate_transition(
        before=CircuitState(),
        after=state,
        provenance=verified,
        event=event,
    )


def assessment_and_ledger(outcome, *, kind=ReviewEvidenceKind.HOLDOUT, count=1):
    items = []
    ledger = ReviewEvidenceLedger()
    for index in range(count):
        ref = f"case-{index}"
        item = bind_review_evidence(
            association_id="cue->outcome",
            memory_revision_id="rev-1",
            kind=kind,
            outcome=outcome,
            evidence_ref=ref,
            receipt=receipt(ref),
        )
        ledger = ledger.register(item)
        items.append(item)
    return assess_review_evidence(items), ledger


def learned_memory():
    state = CircuitState(
        salience=SalienceState(semantic_relevance=1.0),
        learning=LearningState(prediction_error=0.8),
    )
    _, event = EventSequencer("learn").issue()
    receipt_obj = evaluate_transition(
        before=CircuitState(),
        after=state,
        provenance=ProvenanceVerifier(
            [
                Provenance(
                    source_kind=SourceKind.ENVIRONMENT,
                    source_id="learn",
                    source_revision="v1",
                )
            ],
            verifier_id="review-action-verifier",
        ).verify(
            Provenance(
                source_kind=SourceKind.ENVIRONMENT,
                source_id="learn",
                source_revision="v1",
            )
        ),
        event=event,
    )
    candidate = propose_plasticity(
        state=state,
        association_id="cue->outcome",
        receipt=receipt_obj,
        policy=PlasticityPolicy(
            maximum_absolute_delta=1.0,
            minimum_salience_gate=0.0,
        ),
    )
    return apply_candidate(AssociationMemory(), candidate, expected_version=0)


def memory_assessment(memory, *, outcome, count=1, prefix="review"):
    revision = memory.current("cue->outcome")
    items = []
    for index in range(count):
        ref = f"{prefix}-{index}"
        item = bind_review_evidence(
            association_id="cue->outcome",
            memory_revision_id=revision.revision_id,
            kind=ReviewEvidenceKind.HOLDOUT,
            outcome=outcome,
            evidence_ref=ref,
            receipt=receipt(ref),
        )
        memory = register_review_evidence(memory, item)
        items.append(item)
    return memory, assess_review_evidence(items)


def test_review_action_proposal_cannot_be_constructed_directly():
    assessed, ledger = assessment_and_ledger(
        ReviewEvidenceOutcome.CONTRADICTS,
        kind=ReviewEvidenceKind.COUNTEREXAMPLE,
    )
    with pytest.raises(TypeError):
        ReviewActionProposal(
            association_id=assessed.association_id,
            memory_revision_id=assessed.memory_revision_id,
            assessment_id=assessed.assessment_id,
            action=ReviewActionKind.QUARANTINE,
            risk_class=assessed.risk_class,
            evidence_ids=assessed.evidence_ids,
            evidence_ledger_fingerprint=ledger.fingerprint,
            current_disposition=None,
        )


def test_contradicted_active_association_proposes_quarantine():
    assessed, ledger = assessment_and_ledger(
        ReviewEvidenceOutcome.CONTRADICTS,
        kind=ReviewEvidenceKind.COUNTEREXAMPLE,
    )
    proposal = propose_review_action(
        assessed,
        evidence_ledger=ledger,
        current_disposition=ReviewDisposition.ACTIVE,
    )
    assert proposal.action is ReviewActionKind.QUARANTINE
    assert not proposal.mutation_authorized
    assert not proposal.can_mutate


def test_clear_quarantined_association_proposes_release():
    assessed, ledger = assessment_and_ledger(
        ReviewEvidenceOutcome.SUPPORTS,
        count=2,
    )
    proposal = propose_review_action(
        assessed,
        evidence_ledger=ledger,
        current_disposition=ReviewDisposition.QUARANTINED,
    )
    assert proposal.action is ReviewActionKind.RELEASE


def test_insufficient_evidence_holds():
    assessed, ledger = assessment_and_ledger(
        ReviewEvidenceOutcome.SUPPORTS,
        count=1,
    )
    proposal = propose_review_action(
        assessed,
        evidence_ledger=ledger,
        current_disposition=ReviewDisposition.QUARANTINED,
    )
    assert proposal.action is ReviewActionKind.HOLD


def test_current_proposal_validates_against_unchanged_memory():
    memory = learned_memory()
    memory, assessed = memory_assessment(
        memory,
        outcome=ReviewEvidenceOutcome.CONTRADICTS,
    )
    proposal = propose_review_action(
        assessed,
        evidence_ledger=memory.review_evidence,
        current_disposition=None,
    )
    validate_review_action_proposal(memory, proposal, assessed)


def test_proposal_goes_stale_if_evidence_ledger_changes():
    memory = learned_memory()
    memory, assessed = memory_assessment(
        memory,
        outcome=ReviewEvidenceOutcome.CONTRADICTS,
        prefix="initial",
    )
    proposal = propose_review_action(
        assessed,
        evidence_ledger=memory.review_evidence,
        current_disposition=None,
    )

    revision = memory.current("cue->outcome")
    extra = bind_review_evidence(
        association_id="cue->outcome",
        memory_revision_id=revision.revision_id,
        kind=ReviewEvidenceKind.HOLDOUT,
        outcome=ReviewEvidenceOutcome.INCONCLUSIVE,
        evidence_ref="extra",
        receipt=receipt("extra"),
    )
    changed = register_review_evidence(memory, extra)

    with pytest.raises(ReviewActionStaleError):
        validate_review_action_proposal(changed, proposal, assessed)


def test_proposal_goes_stale_if_review_disposition_changes():
    memory = learned_memory()
    memory, assessed = memory_assessment(
        memory,
        outcome=ReviewEvidenceOutcome.CONTRADICTS,
    )
    proposal = propose_review_action(
        assessed,
        evidence_ledger=memory.review_evidence,
        current_disposition=None,
    )
    changed = quarantine_association(
        memory,
        "cue->outcome",
        assessment=assessed,
    )

    with pytest.raises(ReviewActionStaleError):
        validate_review_action_proposal(changed, proposal, assessed)


def test_proposal_goes_stale_if_learned_revision_changes():
    memory = learned_memory()
    memory, assessed = memory_assessment(
        memory,
        outcome=ReviewEvidenceOutcome.CONTRADICTS,
    )
    proposal = propose_review_action(
        assessed,
        evidence_ledger=memory.review_evidence,
        current_disposition=None,
    )

    state = CircuitState(
        salience=SalienceState(semantic_relevance=1.0),
        learning=LearningState(prediction_error=0.1),
    )
    _, event = EventSequencer("learn-again").issue()
    receipt_obj = evaluate_transition(
        before=CircuitState(),
        after=state,
        provenance=ProvenanceVerifier(
            [
                Provenance(
                    source_kind=SourceKind.ENVIRONMENT,
                    source_id="learn-again",
                    source_revision="v1",
                )
            ],
            verifier_id="review-action-verifier",
        ).verify(
            Provenance(
                source_kind=SourceKind.ENVIRONMENT,
                source_id="learn-again",
                source_revision="v1",
            )
        ),
        event=event,
    )
    candidate = propose_plasticity(
        state=state,
        association_id="cue->outcome",
        receipt=receipt_obj,
        policy=PlasticityPolicy(
            maximum_absolute_delta=1.0,
            minimum_salience_gate=0.0,
        ),
    )
    changed = apply_candidate(memory, candidate, expected_version=1)

    with pytest.raises(ReviewActionStaleError):
        validate_review_action_proposal(changed, proposal, assessed)
