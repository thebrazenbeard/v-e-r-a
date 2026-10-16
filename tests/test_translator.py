from unvtrslr.bridge import BridgeLearner, Episode
from unvtrslr.translator import (
    AcousticContextEpisode,
    fit_reference_translator,
    fit_source_calibration_profile,
    freeze_operational_relations,
    reference_translator_model_from_dict,
    source_calibration_profile_from_dict,
    translate_query_evidence,
    translate_source_evidence,
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
    s1_low = (-2.0, -1.0)
    s1_mid = (0.0, 0.0)
    s1_high = (2.0, 1.0)
    s2_low = (80.0, -34.0)
    s2_mid = (100.0, -30.0)
    s2_high = (120.0, -26.0)

    contexts = [
        ("s1-low-a", "s1", s1_low, {"ctx:red", "shape:circle"}),
        ("s1-low-b", "s1", s1_low, {"ctx:red", "shape:triangle"}),
        ("s2-low-a", "s2", s2_low, {"ctx:red", "shape:star"}),
        ("s2-low-b", "s2", s2_low, {"ctx:red", "shape:hex"}),
        ("s1-high-a", "s1", s1_high, {"ctx:blue", "shape:square"}),
        ("s1-high-b", "s1", s1_high, {"ctx:green", "shape:square"}),
        ("s2-high-a", "s2", s2_high, {"ctx:yellow", "shape:square"}),
        ("s2-high-b", "s2", s2_high, {"ctx:purple", "shape:square"}),
        ("s1-mid-a", "s1", s1_mid, {"mid:a"}),
        ("s1-mid-b", "s1", s1_mid, {"mid:b"}),
        ("s2-mid-a", "s2", s2_mid, {"mid:c"}),
        ("s2-mid-b", "s2", s2_mid, {"mid:d"}),
    ]

    for recording, source, vector, context in contexts:
        rows.append(
            AcousticContextEpisode.build(
                recording,
                source,
                context,
                [evidence(recording, source, vector)],
            )
        )
    return rows


def fit_model():
    return fit_reference_translator(
        training_episodes(),
        cluster_distance=0.30,
        match_threshold=0.30,
    )[0]


def source_calibration():
    return [
        evidence("cal-low", "s3", (980.0, 40.0)),
        evidence("cal-mid", "s3", (1000.0, 50.0)),
        evidence("cal-high", "s3", (1020.0, 60.0)),
    ]


def test_source_calibration_then_query_translation():
    model = fit_model()
    result = translate_source_evidence(
        model,
        source_calibration(),
        [
            evidence("q-low", "s3", (980.0, 40.0)),
            evidence("q-high", "s3", (1020.0, 60.0)),
        ],
        renderer={
            "ctx:red": "red",
            "shape:square": "square",
        },
    )

    assert result.status == "REFERENCE_TRANSLATION_SUPPORTED"
    assert result.relations == ("red", "square")
    assert result.unresolved_local_units == ()
    assert result.source_profile_id.startswith("usp_")


def test_query_batch_cannot_renormalize_existing_query():
    model = fit_model()
    profile = fit_source_calibration_profile(model, source_calibration())
    low = evidence("q-low", "s3", (980.0, 40.0))
    extreme = evidence("q-extreme", "s3", (5000.0, 500.0))

    alone = translate_query_evidence(model, profile, [low])
    with_extreme = translate_query_evidence(model, profile, [low, extreme])

    assert alone.global_units[0] == with_extreme.global_units[0]
    assert alone.assignments[0].best_distance == with_extreme.assignments[0].best_distance
    assert alone.relations == ("ctx:red",)
    assert with_extreme.relations[0] == "ctx:red"


def test_single_query_unit_is_allowed_after_profile_is_frozen():
    model = fit_model()
    profile = fit_source_calibration_profile(model, source_calibration())

    result = translate_query_evidence(
        model,
        profile,
        [evidence("q-high", "s3", (1020.0, 60.0))],
    )

    assert result.status == "REFERENCE_TRANSLATION_SUPPORTED"
    assert result.relations == ("shape:square",)


def test_source_profile_requires_three_calibration_contrasts():
    model = fit_model()

    try:
        fit_source_calibration_profile(
            model,
            source_calibration()[:2],
        )
    except ValueError as exc:
        assert "at least 3" in str(exc)
    else:
        raise AssertionError("two-point source calibration should fail closed")


def test_query_source_must_match_frozen_profile():
    model = fit_model()
    profile = fit_source_calibration_profile(model, source_calibration())

    try:
        translate_query_evidence(
            model,
            profile,
            [evidence("q-low", "other-source", (980.0, 40.0))],
        )
    except ValueError as exc:
        assert "does not match" in str(exc)
    else:
        raise AssertionError("cross-source profile reuse should fail")


def test_source_profile_roundtrip_and_tamper_detection():
    model = fit_model()
    profile = fit_source_calibration_profile(model, source_calibration())
    restored = source_calibration_profile_from_dict(profile.to_dict(), model)

    assert restored == profile

    payload = profile.to_dict()
    payload["center"] = list(payload["center"])
    payload["center"][0] += 1.0
    try:
        source_calibration_profile_from_dict(payload, model)
    except ValueError as exc:
        assert "integrity" in str(exc)
    else:
        raise AssertionError("tampered source profile should fail")


def test_semantic_gate_requires_repeated_positive_evidence_per_source():
    episodes = []

    for i in range(6):
        episodes.append(
            Episode.build(
                ["g"],
                ["ctx:red", f"s1-noise:{i}"],
                source="s1",
            )
        )

    episodes.append(
        Episode.build(
            ["g"],
            ["ctx:red", "s2-one-positive"],
            source="s2",
        )
    )
    episodes.append(
        Episode.build(
            ["g"],
            ["s2-other"],
            source="s2",
        )
    )

    for source in ("s1", "s2"):
        for i in range(4):
            episodes.append(
                Episode.build(
                    ["h"],
                    ["ctx:neutral", f"h-noise:{source}:{i}"],
                    source=source,
                )
            )

    bridge = BridgeLearner().fit(episodes)
    assert bridge.infer("g").status == "OPERATIONAL_RELATION_SUPPORTED"

    frozen = freeze_operational_relations(
        bridge,
        min_sources=2,
        min_positive_per_source=2,
    )
    assert all(row.token != "g" for row in frozen)


def test_end_to_end_fit_rejects_two_acoustic_contrasts_per_source():
    try:
        fit_reference_translator(
            training_episodes(),
            min_units_per_source=2,
        )
    except ValueError as exc:
        assert "at least three acoustic contrasts" in str(exc)
    else:
        raise AssertionError("two-point source normalization should fail closed")


def test_translator_model_roundtrip_preserves_source_calibrated_inference():
    model = fit_model()
    restored = reference_translator_model_from_dict(model.to_dict())
    profile = fit_source_calibration_profile(restored, source_calibration())

    result = translate_query_evidence(
        restored,
        profile,
        [evidence("q-low", "s3", (980.0, 40.0))],
    )

    assert restored.model_id == model.model_id
    assert result.relations == ("ctx:red",)


def test_translator_model_rejects_tampered_semantic_relation():
    model = fit_model()
    payload = model.to_dict()
    payload["semantic_relations"][0]["atom"] = "ctx:tampered"

    try:
        reference_translator_model_from_dict(payload)
    except ValueError as exc:
        assert "integrity" in str(exc)
    else:
        raise AssertionError("tampered translator model should fail")


def test_translator_model_rejects_tampered_claim_ceiling():
    model = fit_model()
    payload = model.to_dict()
    payload["claim_ceiling"] = "UNBOUNDED_TRANSLATION"

    try:
        reference_translator_model_from_dict(payload)
    except ValueError as exc:
        assert "claim ceiling" in str(exc)
    else:
        raise AssertionError("tampered claim ceiling should fail")


def test_translator_model_rejects_duplicate_token_relations():
    model = fit_model()
    payload = model.to_dict()
    payload["semantic_relations"] = (
        list(payload["semantic_relations"])
        + [dict(payload["semantic_relations"][0])]
    )

    try:
        reference_translator_model_from_dict(payload)
    except ValueError as exc:
        assert "duplicate token" in str(exc)
    else:
        raise AssertionError("duplicate token relation should fail")


def test_source_profile_rejects_duplicate_acoustic_states():
    model = fit_model()
    duplicate = [
        evidence("cal-a", "s3", (1000.0, 50.0)),
        evidence("cal-b", "s3", (1000.0, 50.0)),
        evidence("cal-c", "s3", (1000.0, 50.0)),
    ]

    try:
        fit_source_calibration_profile(model, duplicate)
    except ValueError as exc:
        assert "distinct acoustic states" in str(exc)
    else:
        raise AssertionError("duplicate calibration states should fail closed")


def test_training_episode_ids_must_be_unique():
    rows = training_episodes()
    duplicate = AcousticContextEpisode.build(
        rows[0].episode_id,
        rows[0].source_id,
        rows[0].context,
        rows[0].evidence,
    )

    try:
        fit_reference_translator(
            rows + [duplicate],
            cluster_distance=0.30,
            match_threshold=0.30,
        )
    except ValueError as exc:
        assert "episode_id" in str(exc)
    else:
        raise AssertionError("duplicate episode IDs should fail closed")


def test_training_requires_three_distinct_acoustic_states_per_source():
    rows = training_episodes()
    rebuilt = []
    for episode in rows:
        if episode.source_id == "s1":
            replacement = [
                evidence(
                    row.recording_id,
                    row.source_id,
                    (0.0, 0.0),
                )
                for row in episode.evidence
            ]
            rebuilt.append(
                AcousticContextEpisode.build(
                    episode.episode_id,
                    episode.source_id,
                    episode.context,
                    replacement,
                )
            )
        else:
            rebuilt.append(episode)

    try:
        fit_reference_translator(
            rebuilt,
            cluster_distance=0.30,
            match_threshold=0.30,
        )
    except ValueError as exc:
        assert "distinct acoustic states" in str(exc)
    else:
        raise AssertionError("duplicate training states should fail closed")
