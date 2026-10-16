import pytest

from meso_crct import (
    ArbitrationMode,
    CircuitState,
    EventIdentity,
    EventSequencer,
    LearningState,
    Provenance,
    ProvenanceVerificationError,
    ProvenanceVerifier,
    RecruitmentState,
    RewardState,
    RuntimePhase,
    SalienceState,
    SourceKind,
    TransitionReceipt,
    arbitrate,
    classify_phase,
    evaluate_transition,
    run_reference_probes,
)


def issued_event(stream_id="runtime-test"):
    _, event = EventSequencer(stream_id).issue()
    return event


def test_event_identity_cannot_be_constructed_directly():
    with pytest.raises(TypeError):
        EventIdentity(
            stream_id="runtime-test",
            sequence=1,
            event_id="fake",
        )


def test_hazard_path_is_independent_and_dominant():
    state = CircuitState(
        reward=RewardState(pleasure=10.0, hazard=1.0, avoidance=1.0),
        salience=SalienceState(incentive_salience=1.0),
    )
    decision = arbitrate(state)
    assert decision.mode is ArbitrationMode.PROTECTIVE
    assert decision.priority == 1.0


def test_satiation_suppresses_incentive_not_semantic_relevance():
    state = CircuitState(
        salience=SalienceState(
            incentive_salience=1.0,
            semantic_relevance=0.6,
        ),
        learning=LearningState(satiation=1.0),
    )
    decision = arbitrate(state)
    assert decision.incentive_after_satiation == 0.0
    assert decision.dominant_driver == "semantic_relevance"


def test_attentional_priority_is_not_recursive_input():
    state = CircuitState(salience=SalienceState(attentional_priority=1.0))
    decision = arbitrate(state)
    assert decision.mode is ArbitrationMode.QUIESCENT
    assert decision.prior_attentional_priority == 1.0


def test_high_semantic_relevance_orients_with_neutral_pleasure():
    state = CircuitState(salience=SalienceState(semantic_relevance=1.0))
    decision = arbitrate(state)
    assert decision.mode is ArbitrationMode.ORIENTING
    assert state.reward.pleasure == 0.0


def test_recruitment_requires_priority_coherence_and_persistence():
    state = CircuitState(
        salience=SalienceState(semantic_relevance=0.9),
        recruitment=RecruitmentState(
            activation=0.9,
            coherence=0.8,
            persistence=0.7,
        ),
    )
    assert classify_phase(state) is RuntimePhase.RECRUITED


def test_high_priority_without_coherence_only_orients():
    state = CircuitState(
        salience=SalienceState(semantic_relevance=0.9),
        recruitment=RecruitmentState(
            activation=0.9,
            coherence=0.1,
            persistence=0.9,
        ),
    )
    assert classify_phase(state) is RuntimePhase.ORIENTED


def test_resolution_has_explicit_phase():
    state = CircuitState(
        salience=SalienceState(semantic_relevance=1.0),
        recruitment=RecruitmentState(resolution=1.0),
    )
    assert classify_phase(state) is RuntimePhase.RESOLVING


def test_transition_receipt_cannot_be_constructed_directly():
    with pytest.raises(TypeError):
        TransitionReceipt(
            receipt_id="fake",
            event_id="fake-event",
            event_stream_id="test",
            event_sequence=1,
            before_phase="quiescent",
            after_phase="oriented",
            mode="orienting",
            priority=1.0,
            dominant_driver="semantic_relevance",
            supporting_drivers=(),
            source_kind="environment",
            source_id="fake",
            source_revision="v1",
            verifier_id="fake",
            before_fingerprint="before",
            after_fingerprint="after",
        )


def test_direct_register_write_cannot_become_accepted_source():
    claim = Provenance(
        source_kind=SourceKind.DIRECT_REGISTER_WRITE,
        source_id="self/pleasure-register",
    )
    with pytest.raises(ValueError):
        ProvenanceVerifier([claim], verifier_id="runtime-root-v1")


def test_verified_provenance_cannot_be_constructed_directly():
    from meso_crct import VerifiedProvenance

    claim = Provenance(
        source_kind=SourceKind.ENVIRONMENT,
        source_id="sensor/front-camera",
        source_revision="v1",
    )
    with pytest.raises(TypeError):
        VerifiedProvenance(claim=claim, verifier_id="pretend-verifier")


def test_unregistered_source_relabel_fails_verification():
    accepted = Provenance(
        source_kind=SourceKind.ENVIRONMENT,
        source_id="sensor/front-camera",
        source_revision="v1",
    )
    relabeled = Provenance(
        source_kind=SourceKind.ENVIRONMENT,
        source_id="self/pleasure-register",
        source_revision="v1",
    )
    verifier = ProvenanceVerifier([accepted], verifier_id="runtime-root-v1")
    with pytest.raises(ProvenanceVerificationError):
        verifier.verify(relabeled)


def test_revision_mismatch_fails_exact_binding():
    accepted = Provenance(
        source_kind=SourceKind.ENVIRONMENT,
        source_id="sensor/front-camera",
        source_revision="v1",
    )
    changed = Provenance(
        source_kind=SourceKind.ENVIRONMENT,
        source_id="sensor/front-camera",
        source_revision="v2",
    )
    verifier = ProvenanceVerifier([accepted], verifier_id="runtime-root-v1")
    with pytest.raises(ProvenanceVerificationError):
        verifier.verify(changed)


def test_same_event_and_transition_is_deterministic():
    before = CircuitState()
    after = CircuitState(salience=SalienceState(semantic_relevance=0.9))
    claim = Provenance(
        source_kind=SourceKind.ENVIRONMENT,
        source_id="observation:test-case-1",
        source_revision="v1",
    )
    verified = ProvenanceVerifier([claim], verifier_id="runtime-root-v1").verify(claim)
    event = issued_event()
    first = evaluate_transition(
        before=before,
        after=after,
        provenance=verified,
        event=event,
    )
    second = evaluate_transition(
        before=before,
        after=after,
        provenance=verified,
        event=event,
    )
    assert first == second
    assert first.receipt_id == second.receipt_id


def test_identical_state_transitions_can_be_distinct_events():
    before = CircuitState()
    after = CircuitState(salience=SalienceState(semantic_relevance=0.9))
    claim = Provenance(
        source_kind=SourceKind.ENVIRONMENT,
        source_id="observation:test-case-1",
        source_revision="v1",
    )
    verified = ProvenanceVerifier([claim], verifier_id="runtime-root-v1").verify(claim)
    sequencer = EventSequencer("runtime-stream")
    sequencer, event1 = sequencer.issue()
    _, event2 = sequencer.issue()

    first = evaluate_transition(
        before=before,
        after=after,
        provenance=verified,
        event=event1,
    )
    second = evaluate_transition(
        before=before,
        after=after,
        provenance=verified,
        event=event2,
    )
    assert first.before_fingerprint == second.before_fingerprint
    assert first.after_fingerprint == second.after_fingerprint
    assert first.event_id != second.event_id
    assert first.receipt_id != second.receipt_id


def test_transition_receipt_binds_verified_source_and_event():
    before = CircuitState()
    after = CircuitState(salience=SalienceState(semantic_relevance=0.9))
    claim = Provenance(
        source_kind=SourceKind.ENVIRONMENT,
        source_id="observation:test-case-1",
        source_revision="v1",
    )
    verified = ProvenanceVerifier([claim], verifier_id="runtime-root-v1").verify(claim)
    event = issued_event("observation-stream")
    receipt = evaluate_transition(
        before=before,
        after=after,
        provenance=verified,
        event=event,
    )
    assert receipt.before_fingerprint != receipt.after_fingerprint
    assert receipt.before_phase == RuntimePhase.QUIESCENT.value
    assert receipt.after_phase == RuntimePhase.ORIENTED.value
    assert receipt.verifier_id == "runtime-root-v1"
    assert receipt.event_id == event.event_id
    assert receipt.event_stream_id == event.stream_id
    assert receipt.event_sequence == event.sequence


def test_reference_adversarial_probes_pass():
    results = run_reference_probes()
    assert results
    assert all(result.passed for result in results), results
