from unvtrslr.target_grounding import (
    NonEquivalenceObservation,
    TargetGroundingEpisode,
    fit_target_grounding_model,
    render_atom,
    render_relations,
    strict_renderer_mapping,
    target_grounding_model_from_dict,
)


def episode(eid, source, tokens, context):
    return TargetGroundingEpisode.build(
        eid,
        source,
        tokens,
        context,
    )


def target_training():
    rows = []
    for source in ("speaker-1", "speaker-2"):
        rows.extend(
            [
                episode(
                    f"{source}-red-1",
                    source,
                    ["red"],
                    ["ctx:red", f"shape:{source}:1"],
                ),
                episode(
                    f"{source}-red-2",
                    source,
                    ["red"],
                    ["ctx:red", f"shape:{source}:2"],
                ),
                episode(
                    f"{source}-scarlet-1",
                    source,
                    ["scarlet"],
                    ["ctx:red", f"shape:{source}:3"],
                ),
                episode(
                    f"{source}-scarlet-2",
                    source,
                    ["scarlet"],
                    ["ctx:red", f"shape:{source}:4"],
                ),
                episode(
                    f"{source}-blue-1",
                    source,
                    ["blue"],
                    ["ctx:blue", f"shape:{source}:5"],
                ),
                episode(
                    f"{source}-blue-2",
                    source,
                    ["blue"],
                    ["ctx:blue", f"shape:{source}:6"],
                ),
                episode(
                    f"{source}-green-1",
                    source,
                    ["green"],
                    ["ctx:green", f"shape:{source}:7"],
                ),
                episode(
                    f"{source}-green-2",
                    source,
                    ["green"],
                    ["ctx:green", f"shape:{source}:8"],
                ),
            ]
        )
    return rows


def no_equivalence(atom="ctx:untranslatable", scope="single-token"):
    return [
        NonEquivalenceObservation.build(
            "neq-1", "speaker-1", atom, scope
        ),
        NonEquivalenceObservation.build(
            "neq-2", "speaker-1", atom, scope
        ),
        NonEquivalenceObservation.build(
            "neq-3", "speaker-2", atom, scope
        ),
        NonEquivalenceObservation.build(
            "neq-4", "speaker-2", atom, scope
        ),
    ]


def model(extra_noeq=()):
    return fit_target_grounding_model(
        target_training(),
        target_language_id="en-reference",
        semantic_atoms={
            "ctx:red",
            "ctx:blue",
            "ctx:green",
            "ctx:unknown",
            "ctx:untranslatable",
        },
        upstream_model_ids={"translator-1"},
        non_equivalence_observations=[
            *no_equivalence(),
            *extra_noeq,
        ],
    )


def test_unique_target_rendering_is_learned_from_grounded_demonstrations():
    m = model()
    rendered = render_atom(m, "ctx:blue")

    assert rendered.status == "TARGET_RENDERING_SUPPORTED"
    assert rendered.realizations == ("blue",)


def test_synonyms_remain_multiple_supported_realizations():
    m = model()
    rendered = render_atom(m, "ctx:red")

    assert rendered.status == "MULTIPLE_TARGET_REALIZATIONS_SUPPORTED"
    assert rendered.realizations == ("red", "scarlet")
    assert "ctx:red" not in strict_renderer_mapping(m)


def test_scoped_non_equivalence_is_distinct_from_unknown():
    m = model()

    noeq = render_atom(m, "ctx:untranslatable")
    unknown = render_atom(m, "ctx:unknown")

    assert noeq.status == "NO_FAITHFUL_EQUIVALENT_FOUND_WITHIN_DECLARED_SCOPE"
    assert noeq.non_equivalence_scopes == ("single-token",)
    assert unknown.status == "UNKNOWN_TARGET_RENDERING"
    assert unknown.non_equivalence_scopes == ()


def test_atom_outside_bound_namespace_fails_explicitly():
    m = model()
    rendered = render_atom(m, "ctx:not-in-model")

    assert rendered.status == "OUTSIDE_TARGET_SEMANTIC_NAMESPACE"


def test_one_source_target_shortcut_is_not_frozen():
    rows = target_training()
    rows.extend(
        [
            episode("one-source-1", "speaker-1", ["crimson"], ["ctx:special"]),
            episode("one-source-2", "speaker-1", ["crimson"], ["ctx:special"]),
            episode("other-1", "speaker-2", ["other"], ["ctx:other"]),
            episode("other-2", "speaker-2", ["other"], ["ctx:other"]),
        ]
    )
    m = fit_target_grounding_model(
        rows,
        target_language_id="en-reference",
        semantic_atoms={"ctx:special", "ctx:other"},
        upstream_model_ids={"translator-1"},
    )

    rendered = render_atom(m, "ctx:special")
    assert rendered.status == "UNKNOWN_TARGET_RENDERING"


def test_ambiguous_homonym_is_not_promoted():
    rows = target_training()
    for source in ("speaker-1", "speaker-2"):
        rows.extend(
            [
                episode(
                    f"{source}-bank-river",
                    source,
                    ["bank"],
                    ["ctx:river-bank"],
                ),
                episode(
                    f"{source}-bank-finance",
                    source,
                    ["bank"],
                    ["ctx:financial-bank"],
                ),
            ]
        )

    m = fit_target_grounding_model(
        rows,
        target_language_id="en-reference",
        semantic_atoms={
            "ctx:river-bank",
            "ctx:financial-bank",
        },
        upstream_model_ids={"translator-1"},
    )

    assert render_atom(m, "ctx:river-bank").status == "UNKNOWN_TARGET_RENDERING"
    assert render_atom(m, "ctx:financial-bank").status == "UNKNOWN_TARGET_RENDERING"


def test_supported_lexeme_plus_non_equivalence_is_preserved_as_conflict():
    conflicting = [
        NonEquivalenceObservation.build(
            "red-neq-1", "speaker-1", "ctx:red", "single-token"
        ),
        NonEquivalenceObservation.build(
            "red-neq-2", "speaker-1", "ctx:red", "single-token"
        ),
        NonEquivalenceObservation.build(
            "red-neq-3", "speaker-2", "ctx:red", "single-token"
        ),
        NonEquivalenceObservation.build(
            "red-neq-4", "speaker-2", "ctx:red", "single-token"
        ),
    ]
    m = model(conflicting)
    rendered = render_atom(m, "ctx:red")

    assert rendered.status == "CONFLICTING_TARGET_EVIDENCE"
    assert rendered.realizations == ("red", "scarlet")
    assert rendered.non_equivalence_scopes == ("single-token",)


def test_relation_rendering_does_not_force_unknown_or_non_equivalent_atoms():
    m = model()
    result = render_relations(
        m,
        ["ctx:blue", "ctx:unknown", "ctx:untranslatable"],
    )

    assert result.status == "TARGET_RENDERING_PARTIAL"
    assert [row.status for row in result.renderings] == [
        "TARGET_RENDERING_SUPPORTED",
        "UNKNOWN_TARGET_RENDERING",
        "NO_FAITHFUL_EQUIVALENT_FOUND_WITHIN_DECLARED_SCOPE",
    ]


def test_model_roundtrip_preserves_target_evidence():
    m = model()
    restored = target_grounding_model_from_dict(m.to_dict())

    assert restored == m
    assert render_atom(restored, "ctx:blue").realizations == ("blue",)


def test_tampered_target_relation_is_rejected():
    m = model()
    payload = m.to_dict()
    payload["lexemes"][0]["atom"] = "ctx:forged"

    try:
        target_grounding_model_from_dict(payload)
    except ValueError as exc:
        assert "semantic namespace" in str(exc) or "integrity" in str(exc)
    else:
        raise AssertionError("tampered target relation should fail")


def test_recomputed_checksum_cannot_legitimize_impossible_target_metrics():
    from unvtrslr.target_grounding import (
        FrozenNonEquivalence,
        FrozenTargetLexeme,
        _target_model_id,
    )

    m = model()
    payload = m.to_dict()
    payload["lexemes"][0]["effect"] = 9.0

    lexemes = tuple(
        FrozenTargetLexeme(**row)
        for row in payload["lexemes"]
    )
    non_equivalences = tuple(
        FrozenNonEquivalence(**row)
        for row in payload["non_equivalences"]
    )
    payload["model_id"] = _target_model_id(
        target_language_id=payload["target_language_id"],
        upstream_model_ids=tuple(payload["upstream_model_ids"]),
        semantic_atoms=tuple(payload["semantic_atoms"]),
        bridge_alpha=payload["bridge_alpha"],
        bridge_min_support=payload["bridge_min_support"],
        bridge_min_probability=payload["bridge_min_probability"],
        bridge_min_effect=payload["bridge_min_effect"],
        bridge_min_information_bits=payload["bridge_min_information_bits"],
        bridge_ambiguity_margin=payload["bridge_ambiguity_margin"],
        min_positive_sources=payload["min_positive_sources"],
        min_positive_per_source=payload["min_positive_per_source"],
        min_non_equivalence_sources=payload["min_non_equivalence_sources"],
        min_non_equivalence_per_source=payload["min_non_equivalence_per_source"],
        lexemes=lexemes,
        non_equivalences=non_equivalences,
    )

    try:
        target_grounding_model_from_dict(payload)
    except ValueError as exc:
        assert "effect is inconsistent" in str(exc)
    else:
        raise AssertionError(
            "logically impossible target model should fail despite recomputed checksum"
        )


def test_non_equivalence_requires_repeated_multi_source_evidence():
    weak = [
        NonEquivalenceObservation.build(
            "weak-1", "speaker-1", "ctx:untranslatable", "single-token"
        ),
        NonEquivalenceObservation.build(
            "weak-2", "speaker-2", "ctx:untranslatable", "single-token"
        ),
    ]
    m = fit_target_grounding_model(
        target_training(),
        target_language_id="en-reference",
        semantic_atoms={"ctx:untranslatable"},
        upstream_model_ids={"translator-1"},
        non_equivalence_observations=weak,
    )

    assert render_atom(m, "ctx:untranslatable").status == "UNKNOWN_TARGET_RENDERING"
