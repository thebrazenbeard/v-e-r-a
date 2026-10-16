from types import SimpleNamespace

from unvtrslr.event_evidence import (
    evidence_from_event_frames,
)
from unvtrslr.unit_registry import (
    build_unit_registry,
)


def frame(
    time_s,
    f0,
    centroid=1000.0,
):
    return SimpleNamespace(
        time_s=time_s,
        f0_hz=f0,
        rms_db=-10.0,
        spectral_centroid_hz=centroid,
        spectral_bandwidth_hz=400.0,
        spectral_flatness=0.1,
        spectral_slope_db_octave=-8.0,
        periodicity=0.9,
        h1_h2_db=4.0,
        mfcc=(
            1.0,
            2.0,
            3.0,
            4.0,
            5.0,
        ),
    )


def one_event_result():
    return SimpleNamespace(
        events=[
            SimpleNamespace(
                start_s=0.0,
                end_s=1.0,
            )
        ],
        units=[
            SimpleNamespace(
                event_index=0,
                unit_id="u0",
            )
        ],
    )


def evidence(
    recording,
    source,
    f0,
    centroid=1000.0,
):
    frames = [
        frame(
            0.1,
            f0,
            centroid,
        ),
        frame(
            0.5,
            f0,
            centroid,
        ),
        frame(
            0.9,
            f0,
            centroid,
        ),
    ]

    return evidence_from_event_frames(
        recording,
        source,
        frames,
        one_event_result(),
    )[0]


def test_raw_event_descriptor_preserves_absolute_pitch_between_recordings():
    low = evidence(
        "low",
        "s1",
        150.0,
    )
    high = evidence(
        "high",
        "s1",
        300.0,
    )

    assert (
        low.vector[0]
        < high.vector[0]
    )


def test_separate_single_event_recordings_can_align_across_shifted_sources():
    rows = [
        evidence(
            "s1-low",
            "s1",
            150.0,
        ),
        evidence(
            "s1-high",
            "s1",
            300.0,
        ),
        evidence(
            "s2-low",
            "s2",
            300.0,
        ),
        evidence(
            "s2-high",
            "s2",
            600.0,
        ),
    ]

    result = build_unit_registry(
        rows,
        cluster_distance=0.25,
    )
    by_recording = {
        assignment.recording_id:
        assignment
        for assignment
        in result.assignments
    }

    assert (
        by_recording[
            "s1-low"
        ].global_unit_id
        == by_recording[
            "s2-low"
        ].global_unit_id
    )
    assert (
        by_recording[
            "s1-high"
        ].global_unit_id
        == by_recording[
            "s2-high"
        ].global_unit_id
    )
    assert (
        by_recording[
            "s1-low"
        ].global_unit_id
        != by_recording[
            "s1-high"
        ].global_unit_id
    )


def test_descriptor_preserves_spectral_difference_as_separate_dimension():
    dark = evidence(
        "dark",
        "s1",
        200.0,
        centroid=800.0,
    )
    bright = evidence(
        "bright",
        "s1",
        200.0,
        centroid=1800.0,
    )

    assert (
        dark.vector[4]
        < bright.vector[4]
    )


def test_missing_supporting_frames_fails_closed():
    result = SimpleNamespace(
        events=[
            SimpleNamespace(
                start_s=2.0,
                end_s=3.0,
            )
        ],
        units=[
            SimpleNamespace(
                event_index=0,
                unit_id="u0",
            )
        ],
    )

    try:
        evidence_from_event_frames(
            "r",
            "s",
            [frame(0.1, 200.0)],
            result,
        )

    except ValueError as exc:
        assert (
            "no supporting"
            in str(exc)
        )

    else:
        raise AssertionError(
            "unsupported event should "
            "fail closed"
        )
