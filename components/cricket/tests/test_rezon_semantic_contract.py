from cricket.semantic.rezon_contract import (
    REZON_CONTRACT,
    RezonSemanticDimension,
)


def test_rezon_is_declared_as_crickets_reasoning_semantic_upstream() -> None:
    assert REZON_CONTRACT.repository == "thebrazenbeard/rezon"
    assert REZON_CONTRACT.commit == "ec401810990337bf07a5d6473782ba13eba1bb3f"
    assert REZON_CONTRACT.relationship == "SEMANTIC_UPSTREAM"
    assert REZON_CONTRACT.runtime_required is False


def test_rezon_contract_covers_crickets_core_semantic_dimensions() -> None:
    required = {
        RezonSemanticDimension.PROPOSITION,
        RezonSemanticDimension.REFERENT,
        RezonSemanticDimension.SCOPE,
        RezonSemanticDimension.MODALITY,
        RezonSemanticDimension.TEMPORAL_SCOPE,
        RezonSemanticDimension.PROVENANCE,
        RezonSemanticDimension.AUTHORITY,
        RezonSemanticDimension.ADVERSARIAL_FIDELITY,
    }
    assert set(REZON_CONTRACT.dimensions) == required


def test_rezon_dependency_is_semantic_not_import_coupling() -> None:
    assert REZON_CONTRACT.package_import == ""
    assert "pip" not in REZON_CONTRACT.relationship.casefold()
