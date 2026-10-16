from pathlib import Path

import pytest
import yaml

from tools.on_theo_registry.materializer import TARGETS, MaterializationError, materialize_rehearsal
from tools.on_theo_registry.validator import validate_repository


def _source_extension_count(root: Path) -> int:
    manifest = yaml.safe_load(
        (root / "registry/extension-manifest.yaml").read_text(encoding="utf-8")
    )
    assert isinstance(manifest, dict)
    extensions = manifest.get("extensions", [])
    assert isinstance(extensions, list)
    return len(extensions)


def _expected_materialized_witness_count(root: Path) -> int:
    base = yaml.safe_load(
        (root / "registry/witnesses.yaml").read_text(encoding="utf-8")
    )
    assert isinstance(base, dict)
    base_witnesses = base.get("witnesses", [])
    assert isinstance(base_witnesses, list)

    manifest = yaml.safe_load(
        (root / "registry/extension-manifest.yaml").read_text(encoding="utf-8")
    )
    assert isinstance(manifest, dict)
    extensions = manifest.get("extensions", [])
    assert isinstance(extensions, list)

    additions = 0
    for entry in extensions:
        extension = yaml.safe_load((root / entry["path"]).read_text(encoding="utf-8"))
        assert isinstance(extension, dict)
        witness_additions = extension.get("witness_additions", []) or []
        assert isinstance(witness_additions, list)
        additions += len(witness_additions)

    return len(base_witnesses) + additions


def test_current_repository_materialization_rehearsal_validates() -> None:
    root = Path(__file__).resolve().parents[1]

    result = materialize_rehearsal(root)

    assert result.receipt["status"] == "REHEARSAL_ONLY_NOT_CANONICAL"
    assert result.receipt["applied_extension_count"] == _source_extension_count(root)
    assert result.receipt["collision_count"] == 0
    assert result.receipt["unresolved_reference_count"] == 0
    assert result.receipt["source_validation"]["ok"] is True
    assert result.receipt["output_validation"]["ok"] is True
    assert result.receipt["effect_boundary"]["source_tree_modified"] is False
    assert result.receipt["effect_boundary"]["canonical_materialized"] is False
    assert result.receipt["effect_boundary"]["merge_authority"] is False

    manifest = result.output_documents["registry/extension-manifest.yaml"]
    assert manifest["extensions"] == []
    assert manifest["materialization_state"]["canonical_materialized"] is False
    assert manifest["materialization_state"]["rehearsal_materialized"] is True

    witnesses = result.output_documents["registry/witnesses.yaml"]
    assert witnesses["materialization_state"] == "REHEARSAL_MATERIALIZED_NOT_CANONICAL"
    assert witnesses["pending_extension_records"] == []
    assert len(witnesses["witnesses"]) == _expected_materialized_witness_count(root)


def test_rehearsal_is_deterministic() -> None:
    root = Path(__file__).resolve().parents[1]

    first = materialize_rehearsal(root)
    second = materialize_rehearsal(root)

    assert first.receipt["source_manifest_sha256"] == second.receipt["source_manifest_sha256"]
    assert first.receipt["applied_extensions"] == second.receipt["applied_extensions"]
    assert first.receipt["output_registry_sha256"] == second.receipt["output_registry_sha256"]
    assert first.receipt["before_counts"] == second.receipt["before_counts"]
    assert first.receipt["after_counts"] == second.receipt["after_counts"]


def test_rehearsal_accepts_already_materialized_source(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    first_output = tmp_path / "materialized"

    first = materialize_rehearsal(root, first_output)
    second = materialize_rehearsal(first_output)

    assert second.receipt["already_materialized_input"] is True
    assert second.receipt["applied_extension_count"] == 0
    assert second.receipt["collision_count"] == 0
    assert second.receipt["unresolved_reference_count"] == 0
    assert second.receipt["source_validation"]["ok"] is True
    assert second.receipt["output_validation"]["ok"] is True
    assert second.receipt["before_counts"] == second.receipt["after_counts"]
    assert second.output_documents == first.output_documents
    assert second.receipt["output_registry_sha256"] == first.receipt["output_registry_sha256"]
    assert (
        second.output_documents["registry/extension-manifest.yaml"]["materialization_state"][
            "applied_extension_ids"
        ]
        == first.output_documents["registry/extension-manifest.yaml"]["materialization_state"][
            "applied_extension_ids"
        ]
    )


def test_rehearsal_output_directory_must_be_outside_source_tree(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()

    with pytest.raises(MaterializationError, match="outside the source repository"):
        materialize_rehearsal(root, root / "generated")


def test_rehearsal_writes_separate_validatable_output(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "materialized"

    result = materialize_rehearsal(root, output)

    assert (output / "registry/sources.yaml").is_file()
    assert (output / "registry/claims.yaml").is_file()
    assert (output / "registry/concepts.yaml").is_file()
    assert (output / "registry/transmissions.yaml").is_file()
    assert (output / "registry/witnesses.yaml").is_file()
    assert (output / "receipts/MATERIALIZATION_REHEARSAL_V1.yaml").is_file()
    assert validate_repository(output).ok

    persisted = yaml.safe_load(
        (output / "receipts/MATERIALIZATION_REHEARSAL_V1.yaml").read_text(encoding="utf-8")
    )
    assert persisted["output_registry_sha256"] == result.receipt["output_registry_sha256"]


def test_rehearsal_refuses_nonempty_output_directory(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "materialized"
    output.mkdir()
    (output / "stale.txt").write_text("stale", encoding="utf-8")

    with pytest.raises(MaterializationError, match="must be empty"):
        materialize_rehearsal(root, output)


def test_rehearsal_proves_source_registry_bytes_unchanged() -> None:
    root = Path(__file__).resolve().parents[1]

    result = materialize_rehearsal(root)

    assert result.receipt["source_tree_readback_unchanged"] is True
    assert (
        result.receipt["source_registry_sha256_before"]
        == result.receipt["source_registry_sha256_after"]
    )


def test_every_extension_record_materializes_exactly_once() -> None:
    root = Path(__file__).resolve().parents[1]
    result = materialize_rehearsal(root)

    manifest = yaml.safe_load(
        (root / "registry/extension-manifest.yaml").read_text(encoding="utf-8")
    )

    for entry in manifest["extensions"]:
        extension = yaml.safe_load((root / entry["path"]).read_text(encoding="utf-8"))
        for addition_key, (target_path, target_key) in TARGETS.items():
            for source_record in extension.get(addition_key, []) or []:
                matches = [
                    candidate
                    for candidate in result.output_documents[target_path][target_key]
                    if candidate.get("id") == source_record.get("id")
                ]
                assert matches == [source_record], (
                    entry["extension_id"],
                    addition_key,
                    source_record.get("id"),
                )


def test_materialized_counts_equal_base_plus_extension_additions() -> None:
    root = Path(__file__).resolve().parents[1]
    result = materialize_rehearsal(root)

    expected_additions_by_target: dict[str, int] = {}
    for addition_key, count in result.receipt["addition_counts"].items():
        target_path, target_key = TARGETS[addition_key]
        target = f"{target_path}:{target_key}"
        expected_additions_by_target[target] = (
            expected_additions_by_target.get(target, 0) + count
        )

    for target, after in result.receipt["after_counts"].items():
        assert after == (
            result.receipt["before_counts"][target]
            + expected_additions_by_target.get(target, 0)
        )
