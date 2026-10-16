from unvtrslr.bridge import Episode
from unvtrslr.ordered_relations import (
    OrderedRelationLearner,
    fit_ordered_relation_model,
    ordered_relation_model_from_dict,
    translate_ordered_sequence,
)


def ep(signal, context, source):
    return Episode.build(signal, context, source=source)


def ordered_training():
    rows = []
    for source in ("s1", "s2"):
        rows.extend(
            [
                ep(["a", "b"], ["order:ab", f"noise:{source}:ab:1"], source),
                ep(["a", "b"], ["order:ab", f"noise:{source}:ab:2"], source),
                ep(["b", "a"], ["order:ba", f"noise:{source}:ba:1"], source),
                ep(["b", "a"], ["order:ba", f"noise:{source}:ba:2"], source),
            ]
        )
    return rows


def test_ordered_pair_learning_distinguishes_ab_from_ba():
    learner = OrderedRelationLearner().fit(ordered_training())

    ab = learner.infer("a", "b")
    ba = learner.infer("b", "a")

    assert ab.status == "ORDERED_OPERATIONAL_RELATION_SUPPORTED"
    assert ab.candidates[0].atom == "order:ab"
    assert ba.status == "ORDERED_OPERATIONAL_RELATION_SUPPORTED"
    assert ba.candidates[0].atom == "order:ba"


def test_frozen_order_model_translates_directional_structure():
    model = fit_ordered_relation_model(
        ordered_training(),
        translator_model_id="translator-1",
        acoustic_model_id="acoustic-1",
        valid_token_ids={"a", "b"},
    )

    ab = translate_ordered_sequence(
        model,
        ["a", "b"],
        renderer={"order:ab": "A-before-B"},
    )
    ba = translate_ordered_sequence(
        model,
        ["b", "a"],
        renderer={"order:ba": "B-before-A"},
    )

    assert ab.status == "ORDERED_TRANSLATION_SUPPORTED"
    assert ab.relations == ("A-before-B",)
    assert ba.status == "ORDERED_TRANSLATION_SUPPORTED"
    assert ba.relations == ("B-before-A",)


def test_missing_reverse_direction_fails_order_contrast():
    rows = [
        ep(["a", "b"], ["order:ab"], "s1"),
        ep(["a", "b"], ["order:ab"], "s1"),
        ep(["a", "b"], ["order:ab"], "s2"),
        ep(["a", "b"], ["order:ab"], "s2"),
    ]
    learner = OrderedRelationLearner().fit(rows)
    result = learner.infer("a", "b")
    assert result.status == "INSUFFICIENT_ORDER_CONTRAST"


def test_source_confounded_order_does_not_get_credit():
    rows = [
        ep(["a", "b"], ["order:ab"], "s1"),
        ep(["a", "b"], ["order:ab"], "s1"),
        ep(["a", "b"], ["order:ab"], "s1"),
        ep(["a", "b"], ["order:ab"], "s1"),
        ep(["b", "a"], ["order:ba"], "s2"),
        ep(["b", "a"], ["order:ba"], "s2"),
        ep(["b", "a"], ["order:ba"], "s2"),
        ep(["b", "a"], ["order:ba"], "s2"),
    ]
    learner = OrderedRelationLearner().fit(rows)
    result = learner.infer("a", "b")
    assert result.status == "SOURCE_CONFOUNDED_ORDER_CONTRAST"


def test_one_source_positive_relation_fails_replication():
    rows = [
        ep(["a", "b"], ["order:ab"], "s1"),
        ep(["a", "b"], ["order:ab"], "s1"),
        ep(["a", "b"], ["other:1"], "s2"),
        ep(["a", "b"], ["other:2"], "s2"),
        ep(["b", "a"], ["order:ba"], "s1"),
        ep(["b", "a"], ["order:ba"], "s1"),
        ep(["b", "a"], ["order:ba"], "s2"),
        ep(["b", "a"], ["order:ba"], "s2"),
    ]
    learner = OrderedRelationLearner(
        min_probability=0.40,
        min_effect=0.10,
    ).fit(rows)

    result = learner.infer("a", "b")
    assert result.status == "INSUFFICIENT_CROSS_SOURCE_REPLICATION"


def test_two_equally_supported_order_atoms_remain_ambiguous():
    rows = []
    for source in ("s1", "s2"):
        rows.extend(
            [
                ep(["a", "b"], ["x:1", "x:2"], source),
                ep(["a", "b"], ["x:1", "x:2"], source),
                ep(["b", "a"], ["y:1"], source),
                ep(["b", "a"], ["y:2"], source),
            ]
        )
    learner = OrderedRelationLearner().fit(rows)
    result = learner.infer("a", "b")
    assert result.status == "AMBIGUOUS"
    assert {result.candidates[0].atom, result.candidates[1].atom} == {"x:1", "x:2"}


def test_order_model_roundtrip_preserves_identity_and_translation():
    model = fit_ordered_relation_model(
        ordered_training(),
        translator_model_id="translator-1",
        acoustic_model_id="acoustic-1",
        valid_token_ids={"a", "b"},
    )
    restored = ordered_relation_model_from_dict(model.to_dict())

    assert restored == model
    assert translate_ordered_sequence(restored, ["a", "b"]).relations == ("order:ab",)


def test_order_model_rejects_tampered_relation():
    model = fit_ordered_relation_model(
        ordered_training(),
        translator_model_id="translator-1",
        acoustic_model_id="acoustic-1",
        valid_token_ids={"a", "b"},
    )
    payload = model.to_dict()
    payload["relations"][0]["atom"] = "forged"

    try:
        ordered_relation_model_from_dict(payload)
    except ValueError as exc:
        assert "integrity" in str(exc)
    else:
        raise AssertionError("tampered ordered model should fail")


def test_unknown_ordered_pair_fails_closed():
    model = fit_ordered_relation_model(
        ordered_training(),
        translator_model_id="translator-1",
        acoustic_model_id="acoustic-1",
        valid_token_ids={"a", "b"},
    )
    result = translate_ordered_sequence(model, ["a", "never-seen"])
    assert result.status == "UNRESOLVED"
    assert result.unresolved_patterns == (("a", "never-seen"),)


def test_order_model_fit_rejects_tokens_outside_frozen_vocabulary():
    try:
        fit_ordered_relation_model(
            ordered_training() + [
                ep(["a", "alien"], ["x:new"], "s1"),
                ep(["alien", "a"], ["x:reverse"], "s2"),
            ],
            translator_model_id="translator-1",
            acoustic_model_id="acoustic-1",
            valid_token_ids={"a", "b"},
        )
    except ValueError as exc:
        assert "outside the frozen acoustic vocabulary" in str(exc)
    else:
        raise AssertionError("unknown training token should fail closed")


def test_recomputed_hash_cannot_legitimize_impossible_relation():
    from unvtrslr.ordered_relations import (
        OrderedRelationLearner,
        _ordered_model_id,
    )

    model = fit_ordered_relation_model(
        ordered_training(),
        translator_model_id="translator-1",
        acoustic_model_id="acoustic-1",
        valid_token_ids={"a", "b"},
    )
    payload = model.to_dict()
    payload["relations"][0]["ordered_support"] = 0

    relation_type = type(model.relations[0])
    forged_relations = tuple(
        relation_type(**row)
        for row in payload["relations"]
    )
    learner = OrderedRelationLearner(
        min_ordered_support=payload["min_ordered_support"],
        min_reverse_support=payload["min_reverse_support"],
        min_order_source_coverage=payload["min_order_source_coverage"],
        min_positive_sources=payload["min_positive_sources"],
        min_positive_per_source=payload["min_positive_per_source"],
        min_probability=payload["min_probability"],
        min_effect=payload["min_effect"],
        min_information_bits=payload["min_information_bits"],
        ambiguity_margin=payload["ambiguity_margin"],
    )
    payload["model_id"] = _ordered_model_id(
        learner,
        forged_relations,
        payload["translator_model_id"],
        payload["acoustic_model_id"],
    )

    try:
        ordered_relation_model_from_dict(payload)
    except ValueError as exc:
        assert "ordered-support gate" in str(exc)
    else:
        raise AssertionError(
            "logically impossible order model should fail despite recomputed hash"
        )


def test_recomputed_hash_cannot_legitimize_inconsistent_effect():
    from unvtrslr.ordered_relations import (
        OrderedRelationLearner,
        _ordered_model_id,
    )

    model = fit_ordered_relation_model(
        ordered_training(),
        translator_model_id="translator-1",
        acoustic_model_id="acoustic-1",
        valid_token_ids={"a", "b"},
    )
    payload = model.to_dict()
    payload["relations"][0]["effect"] = 9.0

    relation_type = type(model.relations[0])
    forged_relations = tuple(
        relation_type(**row)
        for row in payload["relations"]
    )
    learner = OrderedRelationLearner(
        min_ordered_support=payload["min_ordered_support"],
        min_reverse_support=payload["min_reverse_support"],
        min_order_source_coverage=payload["min_order_source_coverage"],
        min_positive_sources=payload["min_positive_sources"],
        min_positive_per_source=payload["min_positive_per_source"],
        min_probability=payload["min_probability"],
        min_effect=payload["min_effect"],
        min_information_bits=payload["min_information_bits"],
        ambiguity_margin=payload["ambiguity_margin"],
    )
    payload["model_id"] = _ordered_model_id(
        learner,
        forged_relations,
        payload["translator_model_id"],
        payload["acoustic_model_id"],
    )

    try:
        ordered_relation_model_from_dict(payload)
    except ValueError as exc:
        assert "effect is inconsistent" in str(exc)
    else:
        raise AssertionError(
            "inconsistent effect should fail despite recomputed hash"
        )
