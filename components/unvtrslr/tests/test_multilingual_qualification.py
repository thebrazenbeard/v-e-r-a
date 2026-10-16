from unvtrslr.multilingual_qualification import (
    EvaluationRecord,
    QualificationThresholds,
    TrainingExposure,
    audit_holdout_split,
    evaluate_multilingual_holdout,
)


def train(
    record,
    language,
    content,
    *,
    corpus="demo",
    version="v1",
    source=None,
):
    return TrainingExposure.build(
        corpus,
        version,
        record,
        language,
        content,
        source,
    )


def evaluate(
    record,
    language,
    content,
    references,
    candidates,
    *,
    corpus="demo",
    version="v1",
    source=None,
    target="eng",
    status="OK",
):
    return EvaluationRecord.build(
        corpus,
        version,
        record,
        language,
        content,
        target,
        references,
        candidates,
        source_id=source,
        system_status=status,
    )


def thresholds(**overrides):
    values = dict(
        min_corpora=1,
        min_languages=1,
        min_records_per_slice=1,
        min_coverage=0.5,
        min_exact_match=0.5,
        min_token_similarity=0.5,
        max_ambiguity_rate=0.5,
    )
    values.update(overrides)
    return QualificationThresholds(**values)


def test_language_holdout_detects_overlap():
    training = [train("t1", "fra", "c1")]
    heldout = [
        evaluate(
            "e1",
            "fra",
            "c2",
            [["bonjour"]],
            [["bonjour"]],
        )
    ]

    violations = audit_holdout_split(
        training,
        heldout,
        regime="HELD_OUT_LANGUAGE",
    )

    assert any("language leakage" in item for item in violations)


def test_parallel_language_transfer_requires_new_language_same_content():
    training = [
        train("t1", "eng", "c1"),
        train("t2", "eng", "c2"),
    ]
    heldout = [
        evaluate(
            "e1",
            "fra",
            "c1",
            [["bonjour"]],
            [["bonjour"]],
        ),
        evaluate(
            "e2",
            "fra",
            "c2",
            [["merci"]],
            [["merci"]],
        ),
    ]

    report = evaluate_multilingual_holdout(
        training,
        heldout,
        regime="PARALLEL_LANGUAGE_TRANSFER",
        thresholds=thresholds(
            min_records_per_slice=2,
            min_coverage=1.0,
            min_exact_match=1.0,
            min_token_similarity=1.0,
            max_ambiguity_rate=0.0,
        ),
    )

    assert report.status == "QUALIFIED_WITHIN_DECLARED_MULTILINGUAL_HOLDOUT"
    assert report.leakage_violations == ()


def test_parallel_transfer_fails_when_content_was_not_seen_in_training_language():
    training = [train("t1", "eng", "c1")]
    heldout = [
        evaluate(
            "e1",
            "fra",
            "new-content",
            [["bonjour"]],
            [["bonjour"]],
        )
    ]

    report = evaluate_multilingual_holdout(
        training,
        heldout,
        regime="PARALLEL_LANGUAGE_TRANSFER",
        thresholds=thresholds(),
    )

    assert report.status == "LEAKAGE_DETECTED"
    assert any(
        "parallel-transfer control missing" in item
        for item in report.leakage_violations
    )


def test_source_holdout_detects_reused_speaker():
    training = [
        train(
            "t1",
            "eng",
            "c1",
            source="speaker-1",
        )
    ]
    heldout = [
        evaluate(
            "e1",
            "eng",
            "c2",
            [["hello"]],
            [["hello"]],
            source="speaker-1",
        )
    ]

    violations = audit_holdout_split(
        training,
        heldout,
        regime="HELD_OUT_SOURCE",
    )

    assert any("source leakage" in item for item in violations)


def test_content_holdout_allows_same_language_but_rejects_same_content():
    training = [train("t1", "eng", "c1")]
    good = [
        evaluate(
            "e1",
            "eng",
            "c2",
            [["new"]],
            [["new"]],
        )
    ]
    bad = [
        evaluate(
            "e2",
            "eng",
            "c1",
            [["old"]],
            [["old"]],
        )
    ]

    assert (
        audit_holdout_split(
            training,
            good,
            regime="HELD_OUT_CONTENT",
        )
        == ()
    )
    assert any(
        "content leakage" in item
        for item in audit_holdout_split(
            training,
            bad,
            regime="HELD_OUT_CONTENT",
        )
    )


def test_multiple_candidates_get_exact_credit_but_count_as_ambiguous():
    training = [train("t1", "eng", "c1")]
    heldout = [
        evaluate(
            "e1",
            "fra",
            "c2",
            [["the", "red", "square"]],
            [
                ["red", "square"],
                ["the", "red", "square"],
            ],
        )
    ]

    report = evaluate_multilingual_holdout(
        training,
        heldout,
        regime="HELD_OUT_LANGUAGE",
        thresholds=thresholds(
            min_coverage=1.0,
            min_exact_match=1.0,
            min_token_similarity=1.0,
            max_ambiguity_rate=1.0,
        ),
    )

    metrics = report.slices[0]
    assert metrics.exact_match == 1.0
    assert metrics.mean_token_similarity == 1.0
    assert metrics.ambiguity_rate == 1.0


def test_edit_similarity_scores_near_match_without_exact_credit():
    training = [train("t1", "eng", "c1")]
    heldout = [
        evaluate(
            "e1",
            "fra",
            "c2",
            [["the", "red", "square"]],
            [["red", "square"]],
        )
    ]

    report = evaluate_multilingual_holdout(
        training,
        heldout,
        regime="HELD_OUT_LANGUAGE",
        thresholds=thresholds(
            min_exact_match=0.0,
            min_token_similarity=0.6,
        ),
    )

    metrics = report.slices[0]
    assert metrics.exact_match == 0.0
    assert 0.6 < metrics.mean_token_similarity < 1.0


def test_unresolved_output_reduces_coverage_and_similarity():
    training = [train("t1", "eng", "c1")]
    heldout = [
        evaluate(
            "e1",
            "fra",
            "c2",
            [["bonjour"]],
            [],
            status="UNKNOWN_TARGET_CONSTRUCTION",
        )
    ]

    report = evaluate_multilingual_holdout(
        training,
        heldout,
        regime="HELD_OUT_LANGUAGE",
        thresholds=thresholds(
            min_coverage=0.1,
            min_exact_match=0.0,
            min_token_similarity=0.0,
        ),
    )

    assert report.status == "MULTILINGUAL_HOLDOUT_THRESHOLD_NOT_MET"
    assert report.slices[0].coverage == 0.0
    assert report.slices[0].mean_token_similarity == 0.0


def test_large_high_resource_slice_cannot_hide_small_failing_language():
    training = [train("t1", "eng", "c1")]
    heldout = []

    for index in range(20):
        heldout.append(
            evaluate(
                f"fra-{index}",
                "fra",
                f"fra-content-{index}",
                [["ok"]],
                [["ok"]],
            )
        )

    heldout.append(
        evaluate(
            "wol-1",
            "wol",
            "wol-content-1",
            [["reference"]],
            [],
            status="UNKNOWN_TARGET_CONSTRUCTION",
        )
    )

    report = evaluate_multilingual_holdout(
        training,
        heldout,
        regime="HELD_OUT_LANGUAGE",
        thresholds=thresholds(
            min_languages=2,
            min_records_per_slice=1,
            min_coverage=0.8,
            min_exact_match=0.5,
            min_token_similarity=0.5,
        ),
    )

    assert report.status == "MULTILINGUAL_HOLDOUT_THRESHOLD_NOT_MET"
    assert any(
        "/wol: coverage=" in failure
        for failure in report.threshold_failures
    )


def test_minimum_corpus_and_language_breadth_are_enforced():
    training = [train("t1", "eng", "c1")]
    heldout = [
        evaluate(
            "e1",
            "fra",
            "c2",
            [["bonjour"]],
            [["bonjour"]],
        )
    ]

    report = evaluate_multilingual_holdout(
        training,
        heldout,
        regime="HELD_OUT_LANGUAGE",
        thresholds=thresholds(
            min_corpora=2,
            min_languages=2,
        ),
    )

    assert report.status == "MULTILINGUAL_HOLDOUT_THRESHOLD_NOT_MET"
    assert any("corpus_count=" in item for item in report.threshold_failures)
    assert any("language_count=" in item for item in report.threshold_failures)


def test_duplicate_record_ids_fail_closed():
    training = [
        train("same", "eng", "c1"),
        train("same", "eng", "c2"),
    ]
    heldout = [
        evaluate(
            "e1",
            "fra",
            "c3",
            [["bonjour"]],
            [["bonjour"]],
        )
    ]

    try:
        audit_holdout_split(
            training,
            heldout,
            regime="HELD_OUT_LANGUAGE",
        )
    except ValueError as exc:
        assert "duplicate record IDs" in str(exc)
    else:
        raise AssertionError("duplicate training record IDs should fail closed")
