from unvtrslr.unit_model import (
    assign_source_units,
    fit_frozen_unit_model,
    frozen_unit_model_from_dict,
)
from unvtrslr.unit_registry import (
    LocalUnitEvidence,
)


def training_rows():
    return [
        LocalUnitEvidence(
            "r1", "s1", "u0",
            (-1.0, -0.5),
        ),
        LocalUnitEvidence(
            "r1", "s1", "u1",
            (1.0, 0.5),
        ),
        LocalUnitEvidence(
            "r2", "s2", "u0",
            (90.0, -32.0),
        ),
        LocalUnitEvidence(
            "r2", "s2", "u1",
            (110.0, -28.0),
        ),
    ]


def test_frozen_model_preserves_training_registry_ids_for_new_source():
    model, registry = (
        fit_frozen_unit_model(
            training_rows(),
            cluster_distance=0.25,
        )
    )
    expected = {
        a.local_unit_id: a.global_unit_id
        for a in registry.assignments
        if a.source_id == "s1"
    }

    new = [
        LocalUnitEvidence(
            "r3", "s3", "x",
            (990.0, 45.0),
        ),
        LocalUnitEvidence(
            "r3", "s3", "y",
            (1010.0, 55.0),
        ),
    ]

    assigned = assign_source_units(
        model,
        new,
    )
    by_local = {
        a.local_unit_id: a
        for a in assigned
    }

    assert (
        by_local["x"].global_unit_id
        == expected["u0"]
    )
    assert (
        by_local["y"].global_unit_id
        == expected["u1"]
    )
    assert all(
        a.status
        == "FROZEN_MATCH_SUPPORTED"
        for a in assigned
    )


def test_frozen_model_id_does_not_change_during_inference():
    model, _ = fit_frozen_unit_model(
        training_rows(),
        cluster_distance=0.25,
    )
    before = model.model_id

    assign_source_units(
        model,
        [
            LocalUnitEvidence(
                "r3", "s3", "x",
                (10.0, 20.0),
            ),
            LocalUnitEvidence(
                "r3", "s3", "y",
                (20.0, 30.0),
            ),
        ],
    )

    assert model.model_id == before


def test_single_unit_new_source_fails_closed():
    model, _ = fit_frozen_unit_model(
        training_rows(),
        cluster_distance=0.25,
    )
    assigned = assign_source_units(
        model,
        [
            LocalUnitEvidence(
                "r3", "s3", "x",
                (999.0, 999.0),
            )
        ],
    )

    assert assigned[0].status == (
        "INSUFFICIENT_SOURCE_CONTRAST"
    )
    assert (
        assigned[0].global_unit_id
        is None
    )


def test_dimension_mismatch_is_rejected():
    model, _ = fit_frozen_unit_model(
        training_rows(),
        cluster_distance=0.25,
    )

    try:
        assign_source_units(
            model,
            [
                LocalUnitEvidence(
                    "r3", "s3", "x",
                    (1.0, 2.0, 3.0),
                ),
                LocalUnitEvidence(
                    "r3", "s3", "y",
                    (4.0, 5.0, 6.0),
                ),
            ],
        )
    except ValueError as exc:
        assert "dimension" in str(exc)
    else:
        raise AssertionError(
            "dimension mismatch should fail"
        )


def test_model_roundtrip_preserves_identity_and_inference():
    model, _ = fit_frozen_unit_model(
        training_rows(),
        cluster_distance=0.25,
    )
    restored = (
        frozen_unit_model_from_dict(
            model.to_dict()
        )
    )

    evidence = [
        LocalUnitEvidence(
            "r3", "s3", "x",
            (990.0, 45.0),
        ),
        LocalUnitEvidence(
            "r3", "s3", "y",
            (1010.0, 55.0),
        ),
    ]

    assert (
        restored.model_id
        == model.model_id
    )
    assert (
        assign_source_units(
            restored,
            evidence,
        )
        == assign_source_units(
            model,
            evidence,
        )
    )


def test_model_roundtrip_rejects_tampered_model_id():
    model, _ = fit_frozen_unit_model(
        training_rows(),
        cluster_distance=0.25,
    )
    payload = model.to_dict()
    payload["model_id"] = (
        "urm_tampered"
    )

    try:
        frozen_unit_model_from_dict(
            payload
        )
    except ValueError as exc:
        assert "integrity" in str(exc)
    else:
        raise AssertionError(
            "tampered model should fail "
            "integrity check"
        )
