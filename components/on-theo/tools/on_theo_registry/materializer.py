from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import yaml

from tools.on_theo_registry.validator import validate_repository


class MaterializationError(RuntimeError):
    pass


TARGETS: dict[str, tuple[str, str]] = {
    "source_additions": ("registry/sources.yaml", "sources"),
    "scholarly_context_additions": ("registry/sources.yaml", "sources"),
    "claim_additions": ("registry/claims.yaml", "claims"),
    "concept_additions": ("registry/concepts.yaml", "concepts"),
    "witness_additions": ("registry/witnesses.yaml", "witnesses"),
    "transmission_additions": ("registry/transmissions.yaml", "edges"),
}

BASE_REGISTRY_PATHS = (
    "registry/sources.yaml",
    "registry/claims.yaml",
    "registry/concepts.yaml",
    "registry/transmissions.yaml",
    "registry/witnesses.yaml",
    "registry/reviews.yaml",
    "registry/source-access.yaml",
    "registry/extension-manifest.yaml",
)


@dataclass(frozen=True)
class MaterializationResult:
    receipt: dict[str, Any]
    output_documents: dict[str, dict[str, Any]]


def _load_yaml(root: Path, relative: str) -> dict[str, Any]:
    path = root / relative
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise MaterializationError(f"cannot load {relative}: {exc}") from exc
    if not isinstance(data, dict):
        raise MaterializationError(f"{relative} must contain a YAML mapping")
    return data


def _yaml_bytes(data: dict[str, Any]) -> bytes:
    return yaml.safe_dump(
        data,
        sort_keys=False,
        allow_unicode=True,
        width=120,
    ).encode("utf-8")


def _digest_bytes(data: bytes) -> str:
    return sha256(data).hexdigest()


def _file_digest(path: Path) -> str:
    return _digest_bytes(path.read_bytes())


def _record_ids(document: dict[str, Any], key: str) -> set[str]:
    value = document.get(key, []) or []
    if not isinstance(value, list):
        raise MaterializationError(f"materialization target {key!r} must be a list")
    result: set[str] = set()
    for item in value:
        if not isinstance(item, dict):
            raise MaterializationError(f"materialization target {key!r} contains a non-mapping record")
        entity_id = item.get("id")
        if not isinstance(entity_id, str) or not entity_id:
            raise MaterializationError(f"materialization target {key!r} contains a record without an id")
        if entity_id in result:
            raise MaterializationError(f"duplicate id {entity_id!r} already exists in materialization target {key!r}")
        result.add(entity_id)
    return result


def _assert_safe_output(root: Path, output_dir: Path) -> None:
    root = root.resolve()
    output_dir = output_dir.resolve()
    if output_dir == root or root in output_dir.parents:
        raise MaterializationError(
            "rehearsal output must be outside the source repository; source-tree writes are forbidden"
        )


def _prepare_output_dir(output_dir: Path) -> None:
    if output_dir.exists():
        if not output_dir.is_dir():
            raise MaterializationError(f"output path {output_dir} exists and is not a directory")
        if any(output_dir.iterdir()):
            raise MaterializationError(f"output directory {output_dir} must be empty")
    else:
        output_dir.mkdir(parents=True)


def _write_documents(output_dir: Path, documents: dict[str, dict[str, Any]]) -> dict[str, str]:
    digests: dict[str, str] = {}
    for relative, document in sorted(documents.items()):
        path = output_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = _yaml_bytes(document)
        path.write_bytes(payload)
        digests[relative] = _digest_bytes(payload)
    return digests


def _materialize_documents(root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    source_report = validate_repository(root)
    if not source_report.ok:
        rendered = "; ".join(
            f"{item.code} {item.path}: {item.message}" for item in source_report.errors
        )
        raise MaterializationError(f"source repository does not validate: {rendered}")

    documents = {relative: deepcopy(_load_yaml(root, relative)) for relative in BASE_REGISTRY_PATHS}
    source_manifest = documents["registry/extension-manifest.yaml"]
    manifest_entries = source_manifest.get("extensions", []) or []
    if not isinstance(manifest_entries, list):
        raise MaterializationError("registry/extension-manifest.yaml: extensions must be a list")

    existing_ids: dict[tuple[str, str], set[str]] = {}
    before_counts: dict[str, int] = {}
    for addition_key, (target_path, target_key) in TARGETS.items():
        target_identity = (target_path, target_key)
        if target_identity not in existing_ids:
            ids = _record_ids(documents[target_path], target_key)
            existing_ids[target_identity] = ids
            before_counts[f"{target_path}:{target_key}"] = len(ids)

    applied_extensions: list[dict[str, Any]] = []
    addition_counts: dict[str, int] = {key: 0 for key in TARGETS}
    input_extension_digests: dict[str, str] = {}

    for index, entry in enumerate(manifest_entries):
        if not isinstance(entry, dict):
            raise MaterializationError(f"manifest extension entry {index} is not a mapping")
        extension_id = entry.get("extension_id")
        extension_path = entry.get("path")
        if not isinstance(extension_id, str) or not extension_id:
            raise MaterializationError(f"manifest extension entry {index} has no extension_id")
        if not isinstance(extension_path, str) or not extension_path:
            raise MaterializationError(f"manifest extension {extension_id} has no path")

        extension = _load_yaml(root, extension_path)
        input_extension_digests[extension_id] = _file_digest(root / extension_path)

        per_extension_counts: dict[str, int] = {}
        for addition_key, (target_path, target_key) in TARGETS.items():
            records = extension.get(addition_key, []) or []
            if not isinstance(records, list):
                raise MaterializationError(
                    f"{extension_path}: {addition_key} must be a list"
                )
            if not records:
                continue

            target_records = documents[target_path].setdefault(target_key, [])
            if not isinstance(target_records, list):
                raise MaterializationError(
                    f"{target_path}: {target_key} must be a list"
                )
            ids = existing_ids[(target_path, target_key)]

            for record_index, record in enumerate(records):
                if not isinstance(record, dict):
                    raise MaterializationError(
                        f"{extension_path}:{addition_key}[{record_index}] is not a mapping"
                    )
                entity_id = record.get("id")
                if not isinstance(entity_id, str) or not entity_id:
                    raise MaterializationError(
                        f"{extension_path}:{addition_key}[{record_index}] has no id"
                    )
                if entity_id in ids:
                    raise MaterializationError(
                        f"collision while applying {extension_id}: id {entity_id!r} already exists "
                        f"in {target_path}:{target_key}"
                    )
                target_records.append(deepcopy(record))
                ids.add(entity_id)

            count = len(records)
            addition_counts[addition_key] += count
            per_extension_counts[addition_key] = count

        applied_extensions.append(
            {
                "extension_id": extension_id,
                "path": extension_path,
                "source_sha256": input_extension_digests[extension_id],
                "addition_counts": per_extension_counts,
            }
        )

    source_materialization_state = source_manifest.get("materialization_state", {}) or {}
    already_materialized = (
        not manifest_entries
        and isinstance(source_materialization_state, dict)
        and source_materialization_state.get("rehearsal_materialized") is True
    )

    if not already_materialized:
        witness_document = documents["registry/witnesses.yaml"]
        witness_document["materialization_state"] = "REHEARSAL_MATERIALIZED_NOT_CANONICAL"
        witness_document["pending_extension_records"] = []

        output_manifest = deepcopy(source_manifest)
        output_manifest["status"] = "REHEARSAL_MATERIALIZED_NOT_CANONICAL"
        output_manifest["extensions"] = []
        output_manifest["materialization_state"] = {
            "canonical_materialized": False,
            "rehearsal_materialized": True,
            "source_base_registry_head": source_manifest.get("base_registry_head"),
            "applied_extension_ids": [item["extension_id"] for item in applied_extensions],
            "guard": "This output is a rehearsal artifact and does not authorize or represent canonical promotion.",
        }
        documents["registry/extension-manifest.yaml"] = output_manifest

    after_counts: dict[str, int] = {}
    for target_path, target_key in sorted(set(TARGETS.values())):
        after_counts[f"{target_path}:{target_key}"] = len(
            documents[target_path].get(target_key, []) or []
        )

    source_registry_digests = {
        relative: _file_digest(root / relative) for relative in BASE_REGISTRY_PATHS
    }
    source_manifest_digest = source_registry_digests["registry/extension-manifest.yaml"]
    receipt = {
        "schema_version": "on-theo.materialization-rehearsal-receipt.v1",
        "status": "REHEARSAL_ONLY_NOT_CANONICAL",
        "source_manifest_sha256": source_manifest_digest,
        "source_registry_sha256_before": source_registry_digests,
        "source_base_registry_head": source_manifest.get("base_registry_head"),
        "already_materialized_input": already_materialized,
        "applied_extension_count": len(applied_extensions),
        "applied_extensions": applied_extensions,
        "addition_counts": addition_counts,
        "before_counts": before_counts,
        "after_counts": after_counts,
        "collision_count": 0,
        "unresolved_reference_count": 0,
        "source_validation": {
            "ok": True,
            "errors": 0,
            "warnings": len(source_report.warnings),
        },
        "effect_boundary": {
            "source_tree_modified": False,
            "canonical_materialized": False,
            "merge_authority": False,
        },
    }
    return documents, receipt


def _run_in_output(root: Path, output_dir: Path) -> MaterializationResult:
    documents, receipt = _materialize_documents(root)
    registry_digests = _write_documents(output_dir, documents)

    output_report = validate_repository(output_dir)
    if not output_report.ok:
        rendered = "; ".join(
            f"{item.code} {item.path}: {item.message}" for item in output_report.errors
        )
        raise MaterializationError(f"rehearsal output does not validate: {rendered}")

    source_registry_after = {
        relative: _file_digest(root / relative) for relative in BASE_REGISTRY_PATHS
    }
    source_registry_before = receipt["source_registry_sha256_before"]
    if source_registry_after != source_registry_before:
        raise MaterializationError(
            "source registry bytes changed during rehearsal; refusing to certify source-tree isolation"
        )

    receipt = deepcopy(receipt)
    receipt["source_registry_sha256_after"] = source_registry_after
    receipt["source_tree_readback_unchanged"] = True
    receipt["output_registry_sha256"] = registry_digests
    receipt["output_validation"] = {
        "ok": True,
        "errors": 0,
        "warnings": len(output_report.warnings),
    }

    receipt_path = output_dir / "receipts/MATERIALIZATION_REHEARSAL_V1.yaml"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_bytes(_yaml_bytes(receipt))

    return MaterializationResult(receipt=receipt, output_documents=documents)


def materialize_rehearsal(
    root: Path,
    output_dir: Path | None = None,
) -> MaterializationResult:
    root = Path(root).resolve()
    if output_dir is None:
        with TemporaryDirectory(prefix="on-theo-materialization-rehearsal-") as tmp:
            return _run_in_output(root, Path(tmp))

    output_dir = Path(output_dir)
    _assert_safe_output(root, output_dir)
    _prepare_output_dir(output_dir)
    return _run_in_output(root, output_dir)
