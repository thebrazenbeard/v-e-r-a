from unvtrslr.target_constructions import (
    FrozenTargetConstruction,
    TargetConstructionEpisode,
    fit_target_construction_model,
    render_semantic_sequence,
    target_construction_model_from_dict,
)


def ep(eid, source, atoms, tokens):
    return TargetConstructionEpisode.build(
        eid,
        source,
        atoms,
        tokens,
    )


def training():
    rows = []
    for source in ("speaker-1", "speaker-2"):
        rows.extend(
            [
                ep(
                    f"{source}-move-left-1",
                    source,
                    ["action:moved-left"],
                    ["moved", "left"],
                ),
                ep(
                    f"{source}-move-left-2",
                    source,
                    ["action:moved-left"],
                    ["moved", "left"],
                ),
                ep(
                    f"{source}-red-square-1",
                    source,
                    ["ctx:red", "shape:square"],
                    ["the", "red", "square"],
                ),
                ep(
                    f"{source}-red-square-2",
                    source,
                    ["ctx:red", "shape:square"],
                    ["the", "red", "square"],
                ),
                ep(
                    f"{source}-square-red-1",
                    source,
                    ["shape:square", "ctx:red"],
                    ["square", "that", "is", "red"],
                ),
                ep(
                    f"{source}-square-red-2",
                    source,
                    ["shape:square", "ctx:red"],
                    ["square", "that", "is", "red"],
                ),
                ep(
                    f"{source}-reorder-1",
                    source,
                    ["agent:alice", "action:sees", "patient:bob"],
                    ["bob", "ACC", "alice", "NOM", "sees"],
                ),
                ep(
                    f"{source}-reorder-2",
                    source,
                    ["agent:alice", "action:sees", "patient:bob"],
                    ["bob", "ACC", "alice", "NOM", "sees"],
                ),
            ]
        )
    return rows


def model(extra=()):
    return fit_target_construction_model(
        [*training(), *extra],
        target_language_id="target-reference",
        semantic_atoms={
            "action:moved-left",
            "ctx:red",
            "shape:square",
            "agent:alice",
            "action:sees",
            "patient:bob",
            "ctx:unknown",
        },
        upstream_model_ids={"translator-1", "target-lexeme-1"},
    )


def test_single_semantic_atom_can_learn_multiword_realization():
    m = model()
    result = render_semantic_sequence(
        m,
        ["action:moved-left"],
    )

    assert result.status == "TARGET_CONSTRUCTION_SUPPORTED"
    assert result.realizations == (("moved", "left"),)


def test_function_words_are_learned_as_observed_tokens_not_inserted_rules():
    m = model()
    result = render_semantic_sequence(
        m,
        ["ctx:red", "shape:square"],
    )

    assert result.status == "TARGET_CONSTRUCTION_SUPPORTED"
    assert result.realizations == (("the", "red", "square"),)


def test_reversed_semantic_pattern_can_have_different_target_construction():
    m = model()

    forward = render_semantic_sequence(
        m,
        ["ctx:red", "shape:square"],
    )
    reverse = render_semantic_sequence(
        m,
        ["shape:square", "ctx:red"],
    )

    assert forward.realizations == (("the", "red", "square"),)
    assert reverse.realizations == (("square", "that", "is", "red"),)


def test_target_specific_reordering_is_preserved_without_human_grammar():
    m = model()
    result = render_semantic_sequence(
        m,
        ["agent:alice", "action:sees", "patient:bob"],
    )

    assert result.status == "TARGET_CONSTRUCTION_SUPPORTED"
    assert result.realizations == (
        ("bob", "ACC", "alice", "NOM", "sees"),
    )


def test_multiple_grounded_constructions_remain_multiple():
    extra = []
    for source in ("speaker-1", "speaker-2"):
        extra.extend(
            [
                ep(
                    f"{source}-red-square-alt-1",
                    source,
                    ["ctx:red", "shape:square"],
                    ["red", "square"],
                ),
                ep(
                    f"{source}-red-square-alt-2",
                    source,
                    ["ctx:red", "shape:square"],
                    ["red", "square"],
                ),
            ]
        )
    m = model(extra)

    result = render_semantic_sequence(
        m,
        ["ctx:red", "shape:square"],
    )

    assert result.status == "MULTIPLE_TARGET_CONSTRUCTIONS_SUPPORTED"
    assert set(result.realizations) == {
        ("red", "square"),
        ("the", "red", "square"),
    }


def test_unknown_semantic_sequence_does_not_fall_back_to_invented_grammar():
    m = model()
    result = render_semantic_sequence(
        m,
        ["ctx:unknown"],
    )

    assert result.status == "UNKNOWN_TARGET_CONSTRUCTION"
    assert result.realizations == ()


def test_one_source_construction_does_not_freeze():
    weak = [
        ep(
            "weak-1",
            "speaker-1",
            ["ctx:unknown"],
            ["mystery", "word"],
        ),
        ep(
            "weak-2",
            "speaker-1",
            ["ctx:unknown"],
            ["mystery", "word"],
        ),
    ]
    m = model(weak)

    assert (
        render_semantic_sequence(
            m,
            ["ctx:unknown"],
        ).status
        == "UNKNOWN_TARGET_CONSTRUCTION"
    )


def test_outside_namespace_is_explicit():
    m = model()
    result = render_semantic_sequence(
        m,
        ["outside:atom"],
    )

    assert result.status == "OUTSIDE_TARGET_CONSTRUCTION_NAMESPACE"


def test_model_roundtrip_preserves_multiword_realization():
    m = model()
    restored = target_construction_model_from_dict(m.to_dict())

    assert restored == m
    assert render_semantic_sequence(
        restored,
        ["action:moved-left"],
    ).realizations == (("moved", "left"),)


def test_tampered_construction_is_rejected():
    m = model()
    payload = m.to_dict()
    payload["constructions"][0]["target_tokens"] = ["forged"]

    try:
        target_construction_model_from_dict(payload)
    except ValueError as exc:
        assert "integrity" in str(exc)
    else:
        raise AssertionError("tampered construction should fail")


def test_recomputed_checksum_cannot_legitimize_impossible_support():
    from unvtrslr.target_constructions import _construction_model_id

    m = model()
    payload = m.to_dict()
    payload["constructions"][0]["support"] = 1

    forged = tuple(
        FrozenTargetConstruction(
            semantic_atoms=tuple(row["semantic_atoms"]),
            target_tokens=tuple(row["target_tokens"]),
            support=row["support"],
            source_coverage=row["source_coverage"],
        )
        for row in payload["constructions"]
    )
    payload["model_id"] = _construction_model_id(
        target_language_id=payload["target_language_id"],
        upstream_model_ids=tuple(payload["upstream_model_ids"]),
        semantic_atoms=tuple(payload["semantic_atoms"]),
        min_sources=payload["min_sources"],
        min_positive_per_source=payload["min_positive_per_source"],
        constructions=forged,
    )

    try:
        target_construction_model_from_dict(payload)
    except ValueError as exc:
        assert (
            "replicated-positive count exceeds total support"
            in str(exc)
            or "source coverage exceeds support" in str(exc)
        )
    else:
        raise AssertionError(
            "impossible construction should fail despite recomputed checksum"
        )


def test_duplicate_episode_ids_fail_closed():
    rows = training()
    duplicate = TargetConstructionEpisode.build(
        rows[0].episode_id,
        rows[0].source_id,
        rows[0].semantic_atoms,
        rows[0].target_tokens,
    )

    try:
        fit_target_construction_model(
            [*rows, duplicate],
            target_language_id="target-reference",
            semantic_atoms={
                atom
                for row in rows
                for atom in row.semantic_atoms
            },
            upstream_model_ids={"translator-1"},
        )
    except ValueError as exc:
        assert "episode_id" in str(exc)
    else:
        raise AssertionError("duplicate episode IDs should fail closed")
