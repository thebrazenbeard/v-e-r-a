from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import yaml


BASE_REGISTRY_SECTIONS: tuple[tuple[str, str], ...] = (
    ("registry/sources.yaml", "sources"),
    ("registry/claims.yaml", "claims"),
    ("registry/concepts.yaml", "concepts"),
    ("registry/witnesses.yaml", "witnesses"),
    ("registry/transmissions.yaml", "edges"),
)

ADDITION_SECTIONS: tuple[str, ...] = (
    "source_additions",
    "scholarly_context_additions",
    "claim_additions",
    "concept_additions",
    "witness_additions",
    "transmission_additions",
)


class RebaseAuditError(RuntimeError):
    pass


def _git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        encoding="utf-8",
        errors="strict",
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise RebaseAuditError(
            f"git {' '.join(args)} failed ({result.returncode}): {result.stderr.strip()}"
        )
    return result


def _show_yaml(root: Path, ref: str, relative: str) -> dict[str, Any]:
    result = _git(root, "show", f"{ref}:{relative}")
    try:
        data = yaml.safe_load(result.stdout)
    except yaml.YAMLError as exc:
        raise RebaseAuditError(f"cannot parse {ref}:{relative}: {exc}") from exc
    if not isinstance(data, dict):
        raise RebaseAuditError(f"{ref}:{relative} must contain a YAML mapping")
    return data


def _show_yaml_if_present(
    root: Path,
    ref: str,
    relative: str,
) -> dict[str, Any] | None:
    probe = _git(
        root,
        "ls-tree",
        "--name-only",
        ref,
        "--",
        relative,
        check=False,
    )
    if probe.returncode != 0:
        raise RebaseAuditError(
            f"git ls-tree {ref} -- {relative} failed ({probe.returncode}): "
            f"{probe.stderr.strip()}"
        )
    paths = {line.strip() for line in probe.stdout.splitlines() if line.strip()}
    if relative not in paths:
        return None
    return _show_yaml(root, ref, relative)


def _records(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise RebaseAuditError("expected list-valued registry section")
    output: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            raise RebaseAuditError("registry section contains a non-mapping record")
        output.append(item)
    return output


def _base_index(root: Path, ref: str) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for relative, section in BASE_REGISTRY_SECTIONS:
        document = _show_yaml_if_present(root, ref, relative)
        if document is None:
            continue
        for record in _records(document.get(section)):
            entity_id = record.get("id")
            if not isinstance(entity_id, str) or not entity_id:
                raise RebaseAuditError(f"{ref}:{relative}:{section} record has no id")
            if entity_id in index:
                raise RebaseAuditError(f"{ref} duplicates stable id {entity_id!r}")
            index[entity_id] = record
    return index


def _source_ref(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        source_id = value.get("source_id")
        return source_id if isinstance(source_id, str) else None
    return None


def _references(extension: dict[str, Any]) -> set[str]:
    refs: set[str] = set()

    for section in ("source_additions", "scholarly_context_additions"):
        for source in _records(extension.get(section)):
            for source_id in source.get("preserved_by", []) or []:
                if isinstance(source_id, str):
                    refs.add(source_id)

    for witness in _records(extension.get("witness_additions")):
        source_id = witness.get("witness_of")
        if isinstance(source_id, str):
            refs.add(source_id)

    for claim in _records(extension.get("claim_additions")):
        for edge_key in ("supporting_sources", "opposing_sources"):
            for edge in _records(claim.get(edge_key)):
                source_id = edge.get("source_id")
                witness_id = edge.get("witness_id")
                if isinstance(source_id, str):
                    refs.add(source_id)
                if isinstance(witness_id, str):
                    refs.add(witness_id)

    for transmission in _records(extension.get("transmission_additions")):
        for key in ("from_source", "to_source"):
            source_id = transmission.get(key)
            if isinstance(source_id, str):
                refs.add(source_id)
        for evidence in _records(transmission.get("evidence")):
            source_id = evidence.get("source_id")
            if isinstance(source_id, str):
                refs.add(source_id)

    for concept in _records(extension.get("concept_additions")):
        for claim_id in concept.get("linked_claims", []) or []:
            if isinstance(claim_id, str):
                refs.add(claim_id)
        for source_ref in concept.get("source_refs", []) or []:
            source_id = _source_ref(source_ref)
            if source_id is not None:
                refs.add(source_id)
        for relation in _records(concept.get("relations")):
            target = relation.get("target_concept_id")
            if isinstance(target, str):
                refs.add(target)
            for source_ref in relation.get("source_refs", []) or []:
                source_id = _source_ref(source_ref)
                if source_id is not None:
                    refs.add(source_id)

    return refs


def _canonical_record(record: dict[str, Any]) -> str:
    return json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _is_ancestor(root: Path, base: str, subject: str) -> bool:
    result = _git(root, "merge-base", "--is-ancestor", base, subject, check=False)
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    raise RebaseAuditError(
        f"git merge-base --is-ancestor {base} {subject} failed: {result.stderr.strip()}"
    )


def audit_rebase_preconditions(root: Path, subject: str) -> dict[str, Any]:
    root = Path(root).resolve()
    manifest = _show_yaml(root, subject, "registry/extension-manifest.yaml")
    entries = manifest.get("extensions", [])
    if not isinstance(entries, list):
        raise RebaseAuditError("manifest extensions must be a list")

    extension_by_id: dict[str, dict[str, Any]] = {}
    owner_by_id: dict[str, str] = {}
    entry_by_id: dict[str, dict[str, Any]] = {}

    for entry in entries:
        if not isinstance(entry, dict):
            raise RebaseAuditError("manifest extension entry is not a mapping")
        extension_id = entry.get("extension_id")
        extension_path = entry.get("path")
        if not isinstance(extension_id, str) or not extension_id:
            raise RebaseAuditError("manifest extension entry has no extension_id")
        if not isinstance(extension_path, str) or not extension_path:
            raise RebaseAuditError(f"{extension_id} has no path")
        extension = _show_yaml(root, subject, extension_path)
        extension_by_id[extension_id] = extension
        entry_by_id[extension_id] = entry

        for section in ADDITION_SECTIONS:
            for record in _records(extension.get(section)):
                entity_id = record.get("id")
                if not isinstance(entity_id, str) or not entity_id:
                    raise RebaseAuditError(f"{extension_id}:{section} record has no id")
                prior = owner_by_id.setdefault(entity_id, extension_id)
                if prior != extension_id:
                    raise RebaseAuditError(
                        f"stable id {entity_id!r} is owned by both {prior} and {extension_id}"
                    )

    current_base = _base_index(root, subject)
    base_index_cache: dict[str, dict[str, dict[str, Any]]] = {}
    results: list[dict[str, Any]] = []
    all_mismatches: list[dict[str, Any]] = []

    for extension_id, extension in extension_by_id.items():
        entry = entry_by_id[extension_id]
        declared_base = entry.get("declared_base")
        if not isinstance(declared_base, str) or not declared_base:
            raise RebaseAuditError(f"{extension_id} has no declared_base")

        if _is_ancestor(root, declared_base, subject):
            results.append(
                {
                    "extension_id": extension_id,
                    "declared_base": declared_base,
                    "relation": "ANCESTOR",
                    "external_reference_count": 0,
                    "mismatch_count": 0,
                }
            )
            continue

        historical_base = base_index_cache.get(declared_base)
        if historical_base is None:
            historical_base = _base_index(root, declared_base)
            base_index_cache[declared_base] = historical_base

        external_refs = sorted(
            reference
            for reference in _references(extension)
            if reference not in owner_by_id
        )
        mismatches: list[dict[str, Any]] = []

        for reference in external_refs:
            historical = historical_base.get(reference)
            current = current_base.get(reference)
            if historical is None or current is None:
                mismatches.append(
                    {
                        "stable_id": reference,
                        "kind": "MISSING_PRECONDITION_RECORD",
                        "declared_base_present": historical is not None,
                        "subject_present": current is not None,
                    }
                )
                continue
            if _canonical_record(historical) != _canonical_record(current):
                mismatches.append(
                    {
                        "stable_id": reference,
                        "kind": "PRECONDITION_RECORD_CHANGED",
                        "declared_base_record": historical,
                        "subject_record": current,
                    }
                )

        extension_result = {
            "extension_id": extension_id,
            "declared_base": declared_base,
            "relation": "DIVERGED_REBASE_EXCEPTION_REQUIRED",
            "external_reference_count": len(external_refs),
            "external_reference_ids": external_refs,
            "mismatch_count": len(mismatches),
            "mismatches": mismatches,
        }
        results.append(extension_result)
        for mismatch in mismatches:
            all_mismatches.append({"extension_id": extension_id, **mismatch})

    divergent = [item for item in results if item["relation"] != "ANCESTOR"]
    return {
        "schema_version": "on-theo.rebase-precondition-audit.v1",
        "subject": subject,
        "extension_count": len(results),
        "ancestor_extension_count": len(results) - len(divergent),
        "divergent_extension_count": len(divergent),
        "divergent_unique_base_count": len({item["declared_base"] for item in divergent}),
        "referential_precondition_mismatch_count": len(all_mismatches),
        "referential_preconditions_equivalent": not all_mismatches,
        "extensions": results,
        "mismatches": all_mismatches,
        "semantic_scope_guard": (
            "PASS means only that every referenced stable ID not owned by an extension has "
            "an identical canonical record at the declared base and frozen subject. It is "
            "referential-precondition equivalence, not a complete proof of historical or "
            "philosophical semantic equivalence."
        ),
    }