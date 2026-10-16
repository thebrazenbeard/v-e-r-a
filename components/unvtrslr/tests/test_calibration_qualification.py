from unvtrslr.calibration_qualification import (
    fit_and_qualify_source_profile,
    qualified_source_profile_from_dict,
    translate_qualified_query,
)
from unvtrslr.translator import (
    AcousticContextEpisode,
    fit_reference_translator,
)
from unvtrslr.unit_registry import LocalUnitEvidence


def evidence(recording, source, vector):
    return LocalUnitEvidence(
        recording_id=recording,
        source_id=source,
        local_unit_id="u0",
        vector=tuple(vector),
    )


def training_episodes():
    rows = []
    states = {
        "s1": {
            "low": (-2.0, -1.0),
            "mid": (0.0, 0.0),
            "high": (2.0, 1.0),
        },
        "s2": {
            "low": (80.0, -34.0),
            "mid": (100.0, -30.0),
            "high": (120.0, -26.0),
        },
    }
    contexts = {
        "low": [
            {"ctx:red", "shape:circle"},
            {"ctx:red", "shape:triangle"},
        ],
        "mid": [
            {"mid:a"},
            {"mid:b"},
        ],
        "high": [
            {"ctx:blue", "shape:square"},
            {"ctx:green", "shape:square"},
        ],
    }

    for source in ("s1", "s2"):
        for state in ("low", "mid", "high"):
            for repeat, context in enumerate(contexts[state]):
                recording = f"{source}-{state}-{repeat}"
                effective_context = set(context)
                if source == "s2" and state == "high":
                    effective_context.discard("ctx:blue")
                    effective_context.discard("ctx:green")
                    effective_context.add(
                        "ctx:yellow" if repeat == 0 else "ctx:purple"
                    )
                rows.append(
                    AcousticContextEpisode.build(
                        recording,
                        source,
                        effective_context,
                        [
                            evidence(
                                recording,
                                source,
                                states[source][state],
                            )
                        ],
                    )
                )
    return rows


def model():
    return fit_reference_translator(
        training_episodes(),
        cluster_distance=0.30,
        match_threshold=0.30,
    )[0]


def calibration():
    return [
        evidence("cal-low", "s3", (980.0, 40.0)),
        evidence("cal-mid", "s3", (1000.0, 50.0)),
        evidence("cal-high", "s3", (1020.0, 60.0)),
    ]


def held_out():
    return [
        evidence("hold-low", "s3", (981.0, 40.5)),
        evidence("hold-mid", "s3", (1001.0, 50.5)),
        evidence("hold-high", "s3", (1019.0, 59.5)),
    ]


def test_held_out_calibration_qualifies_multiple_prototypes():
    fitted = fit_and_qualify_source_profile(
        model(),
        calibration(),
        held_out(),
        min_supported_fraction=1.0,
        min_distinct_global_units=3,
    )

    q = fitted.qualification
    assert q.status == "HELD_OUT_ACOUSTIC_CALIBRATION_QUALIFIED"
    assert q.supported_unit_count == 3
    assert q.supported_fraction == 1.0
    assert q.distinct_global_unit_count == 3
    assert len(q.matched_global_units) == 3


def test_same_state_repetition_fails_prototype_coverage():
    fitted = fit_and_qualify_source_profile(
        model(),
        calibration(),
        [
            evidence("hold-low-a", "s3", (981.0, 40.5)),
            evidence("hold-low-b", "s3", (981.2, 40.6)),
            evidence("hold-low-c", "s3", (980.8, 40.4)),
        ],
        min_supported_fraction=1.0,
        min_distinct_global_units=3,
    )

    assert (
        fitted.qualification.status
        == "INSUFFICIENT_HELD_OUT_PROTOTYPE_COVERAGE"
    )
    assert fitted.qualification.supported_fraction == 1.0
    assert fitted.qualification.distinct_global_unit_count == 1


def test_bad_held_out_match_rate_fails_qualification():
    fitted = fit_and_qualify_source_profile(
        model(),
        calibration(),
        [
            evidence("bad-a", "s3", (5000.0, 500.0)),
            evidence("bad-b", "s3", (7000.0, -800.0)),
            evidence("hold-mid", "s3", (1001.0, 50.5)),
        ],
        min_supported_fraction=0.80,
        min_distinct_global_units=2,
    )

    assert (
        fitted.qualification.status
        == "INSUFFICIENT_HELD_OUT_MATCH_RATE"
    )


def test_calibration_and_qualification_identities_must_be_disjoint():
    m = model()
    try:
        fit_and_qualify_source_profile(
            m,
            calibration(),
            calibration(),
        )
    except ValueError as exc:
        assert "disjoint" in str(exc)
    else:
        raise AssertionError("reused evidence identity should fail closed")


def test_unqualified_profile_cannot_use_qualified_translation_path():
    m = model()
    fitted = fit_and_qualify_source_profile(
        m,
        calibration(),
        [
            evidence("hold-low-a", "s3", (981.0, 40.5)),
            evidence("hold-low-b", "s3", (981.2, 40.6)),
            evidence("hold-low-c", "s3", (980.8, 40.4)),
        ],
        min_supported_fraction=1.0,
        min_distinct_global_units=3,
    )

    try:
        translate_qualified_query(
            m,
            fitted,
            [evidence("query", "s3", (980.0, 40.0))],
        )
    except ValueError as exc:
        assert "not held-out qualified" in str(exc)
    else:
        raise AssertionError("unqualified source profile should not translate")


def test_qualified_profile_roundtrip_preserves_certificate():
    m = model()
    fitted = fit_and_qualify_source_profile(
        m,
        calibration(),
        held_out(),
        min_supported_fraction=1.0,
        min_distinct_global_units=3,
    )

    restored = qualified_source_profile_from_dict(
        fitted.to_dict(),
        m,
    )
    assert restored == fitted

    result = translate_qualified_query(
        m,
        restored,
        [evidence("query-low", "s3", (980.0, 40.0))],
    )
    assert result.status == "REFERENCE_TRANSLATION_SUPPORTED"
    assert result.relations == ("ctx:red",)


def test_qualification_certificate_tamper_is_rejected():
    m = model()
    fitted = fit_and_qualify_source_profile(
        m,
        calibration(),
        held_out(),
        min_supported_fraction=1.0,
        min_distinct_global_units=3,
    )
    payload = fitted.to_dict()
    payload["qualification"]["supported_fraction"] = 0.5

    try:
        qualified_source_profile_from_dict(payload, m)
    except ValueError as exc:
        assert "integrity" in str(exc)
    else:
        raise AssertionError("tampered qualification should fail closed")


def test_self_consistent_hash_cannot_bypass_metric_logic():
    from unvtrslr.calibration_qualification import (
        _qualification_id,
    )

    m = model()
    fitted = fit_and_qualify_source_profile(
        m,
        calibration(),
        held_out(),
        min_supported_fraction=1.0,
        min_distinct_global_units=3,
    )
    payload = fitted.to_dict()
    q = payload["qualification"]
    q["supported_fraction"] = 0.5
    q["qualification_id"] = _qualification_id(
        m,
        fitted.profile,
        q["qualification_evidence_digest"],
        q["qualification_unit_count"],
        q["supported_unit_count"],
        q["supported_fraction"],
        q["distinct_global_unit_count"],
        tuple(q["matched_global_units"]),
        q["max_supported_distance"],
        q["min_supported_fraction"],
        q["min_distinct_global_units"],
        q["status"],
    )

    try:
        qualified_source_profile_from_dict(payload, m)
    except ValueError as exc:
        assert "fraction is inconsistent" in str(exc)
    else:
        raise AssertionError(
            "logically impossible certificate should fail even with recomputed hash"
        )
