import pytest

from meso_crct import (
    AppraisedTarget,
    AssociationMemory,
    CircuitState,
    EventSequencer,
    ExperienceLearningSpec,
    LearningState,
    MemoryVersionConflict,
    PlasticityPolicy,
    PlasticityReplayError,
    Provenance,
    ProvenanceVerifier,
    RewardState,
    SemanticEvidence,
    SourceKind,
    TargetAppraisalInput,
    build_target_appraisal,
    process_appraised_experience,
)


def verified_source():
    claim = Provenance(
        source_kind=SourceKind.ENVIRONMENT,
        source_id="sensor:episode",
        source_revision="v1",
    )
    return ProvenanceVerifier(
        [claim],
        verifier_id="episode-test-verifier",
    ).verify(claim)


def learning_spec(expected_version=0):
    return ExperienceLearningSpec(
        association_id="cue->outcome",
        policy=PlasticityPolicy(
            maximum_absolute_delta=0.1,
            minimum_salience_gate=0.4,
        ),
        expected_version=expected_version,
    )


def appraised_learning_target(*, prediction_error=1.0, pleasure=0.0):
    return build_target_appraisal(
        TargetAppraisalInput(
            target_id="target",
            semantic_evidence=SemanticEvidence(context_relevance=1.0),
            prediction_error=prediction_error,
            reward=RewardState(pleasure=pleasure),
        )
    )


def test_appraised_target_cannot_be_constructed_directly():
    genuine = appraised_learning_target()
    with pytest.raises(TypeError):
        AppraisedTarget(
            target_id="fake",
            state=genuine.state,
            semantic=genuine.semantic,
            homeostatic=genuine.homeostatic,
        )


def test_episode_binds_appraisal_event_receipt_and_memory_update():
    appraised = appraised_learning_target()
    _, event = EventSequencer("episode-stream").issue()

    result = process_appraised_experience(
        before=CircuitState(),
        appraised=appraised,
        provenance=verified_source(),
        event=event,
        memory=AssociationMemory(),
        learning=learning_spec(),
    )

    assert result.receipt.event_id == event.event_id
    assert result.receipt.after_fingerprint
    assert result.learning_applied
    assert result.applied_revision.version == 1
    assert result.memory.current_strength("cue->outcome") == pytest.approx(0.1)


def test_zero_teaching_signal_leaves_durable_memory_unchanged():
    appraised = appraised_learning_target(prediction_error=0.0)
    _, event = EventSequencer("episode-stream").issue()
    memory = AssociationMemory()

    result = process_appraised_experience(
        before=CircuitState(),
        appraised=appraised,
        provenance=verified_source(),
        event=event,
        memory=memory,
        learning=learning_spec(),
    )

    assert not result.learning_applied
    assert result.plasticity_candidate is not None
    assert result.plasticity_candidate.delta == 0.0
    assert result.memory == memory


def test_maximum_pleasure_without_teaching_signal_does_not_persist_preference():
    appraised = appraised_learning_target(
        prediction_error=0.0,
        pleasure=10.0,
    )
    _, event = EventSequencer("episode-stream").issue()

    result = process_appraised_experience(
        before=CircuitState(),
        appraised=appraised,
        provenance=verified_source(),
        event=event,
        memory=AssociationMemory(),
        learning=learning_spec(),
    )

    assert result.after_state.reward.pleasure == 10.0
    assert not result.learning_applied
    assert result.memory.current("cue->outcome") is None


def test_stale_memory_version_is_rejected_when_learning_would_apply():
    appraised = appraised_learning_target()
    sequencer = EventSequencer("episode-stream")
    sequencer, event1 = sequencer.issue()
    _, event2 = sequencer.issue()

    first = process_appraised_experience(
        before=CircuitState(),
        appraised=appraised,
        provenance=verified_source(),
        event=event1,
        memory=AssociationMemory(),
        learning=learning_spec(expected_version=0),
    )

    with pytest.raises(MemoryVersionConflict):
        process_appraised_experience(
            before=CircuitState(),
            appraised=appraised,
            provenance=verified_source(),
            event=event2,
            memory=first.memory,
            learning=learning_spec(expected_version=0),
        )


def test_distinct_identical_experiences_can_each_contribute_learning():
    appraised = appraised_learning_target()
    sequencer = EventSequencer("episode-stream")
    sequencer, event1 = sequencer.issue()
    _, event2 = sequencer.issue()

    first = process_appraised_experience(
        before=CircuitState(),
        appraised=appraised,
        provenance=verified_source(),
        event=event1,
        memory=AssociationMemory(),
        learning=learning_spec(expected_version=0),
    )
    second = process_appraised_experience(
        before=CircuitState(),
        appraised=appraised,
        provenance=verified_source(),
        event=event2,
        memory=first.memory,
        learning=learning_spec(expected_version=1),
    )

    assert first.receipt.after_fingerprint == second.receipt.after_fingerprint
    assert first.receipt.event_id != second.receipt.event_id
    assert first.receipt.receipt_id != second.receipt.receipt_id
    assert second.memory.current_version("cue->outcome") == 2
    assert second.memory.current_strength("cue->outcome") == pytest.approx(0.2)


def test_replaying_same_event_cannot_apply_learning_twice():
    appraised = appraised_learning_target()
    _, event = EventSequencer("episode-stream").issue()

    first = process_appraised_experience(
        before=CircuitState(),
        appraised=appraised,
        provenance=verified_source(),
        event=event,
        memory=AssociationMemory(),
        learning=learning_spec(expected_version=0),
    )

    with pytest.raises(PlasticityReplayError):
        process_appraised_experience(
            before=CircuitState(),
            appraised=appraised,
            provenance=verified_source(),
            event=event,
            memory=first.memory,
            learning=learning_spec(expected_version=1),
        )


def test_episode_can_be_receipt_only_without_learning_directive():
    appraised = appraised_learning_target()
    _, event = EventSequencer("episode-stream").issue()
    memory = AssociationMemory()

    result = process_appraised_experience(
        before=CircuitState(),
        appraised=appraised,
        provenance=verified_source(),
        event=event,
        memory=memory,
    )

    assert result.plasticity_candidate is None
    assert not result.learning_applied
    assert result.memory == memory
