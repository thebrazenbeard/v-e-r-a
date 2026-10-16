from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "registry/extension-manifest.yaml"

ADDITION_SECTIONS = {
    "source_additions": "source",
    "scholarly_context_additions": "source",
    "claim_additions": "claim",
    "concept_additions": "concept",
    "witness_additions": "witness",
    "transmission_additions": "transmission",
}


def _load(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), path
    return data


def _records(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    assert isinstance(value, list)
    result: list[dict[str, Any]] = []
    for item in value:
        assert isinstance(item, dict)
        result.append(item)
    return result


def _source_ref(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        source_id = value.get("source_id")
        return source_id if isinstance(source_id, str) else None
    return None


def _references(extension: dict[str, Any]) -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []

    for section in ("source_additions", "scholarly_context_additions"):
        for index, source in enumerate(_records(extension.get(section))):
            for ref_index, source_id in enumerate(source.get("preserved_by", []) or []):
                if isinstance(source_id, str):
                    refs.append(
                        (source_id, f"{section}[{index}].preserved_by[{ref_index}]")
                    )

    for index, witness in enumerate(_records(extension.get("witness_additions"))):
        source_id = witness.get("witness_of")
        if isinstance(source_id, str):
            refs.append((source_id, f"witness_additions[{index}].witness_of"))

    for index, claim in enumerate(_records(extension.get("claim_additions"))):
        for edge_key in ("supporting_sources", "opposing_sources"):
            for edge_index, edge in enumerate(_records(claim.get(edge_key))):
                source_id = edge.get("source_id")
                witness_id = edge.get("witness_id")
                if isinstance(source_id, str):
                    refs.append(
                        (
                            source_id,
                            f"claim_additions[{index}].{edge_key}[{edge_index}].source_id",
                        )
                    )
                if isinstance(witness_id, str):
                    refs.append(
                        (
                            witness_id,
                            f"claim_additions[{index}].{edge_key}[{edge_index}].witness_id",
                        )
                    )

    for index, transmission in enumerate(
        _records(extension.get("transmission_additions"))
    ):
        for key in ("from_source", "to_source"):
            source_id = transmission.get(key)
            if isinstance(source_id, str):
                refs.append(
                    (source_id, f"transmission_additions[{index}].{key}")
                )
        for evidence_index, evidence in enumerate(
            _records(transmission.get("evidence"))
        ):
            source_id = evidence.get("source_id")
            if isinstance(source_id, str):
                refs.append(
                    (
                        source_id,
                        f"transmission_additions[{index}].evidence[{evidence_index}].source_id",
                    )
                )

    for index, concept in enumerate(_records(extension.get("concept_additions"))):
        for claim_index, claim_id in enumerate(concept.get("linked_claims", []) or []):
            if isinstance(claim_id, str):
                refs.append(
                    (
                        claim_id,
                        f"concept_additions[{index}].linked_claims[{claim_index}]",
                    )
                )
        for source_index, source_ref in enumerate(concept.get("source_refs", []) or []):
            source_id = _source_ref(source_ref)
            if source_id is not None:
                refs.append(
                    (
                        source_id,
                        f"concept_additions[{index}].source_refs[{source_index}]",
                    )
                )
        for relation_index, relation in enumerate(
            _records(concept.get("relations"))
        ):
            target = relation.get("target_concept_id")
            if isinstance(target, str):
                refs.append(
                    (
                        target,
                        f"concept_additions[{index}].relations[{relation_index}].target_concept_id",
                    )
                )
            for source_index, source_ref in enumerate(
                relation.get("source_refs", []) or []
            ):
                source_id = _source_ref(source_ref)
                if source_id is not None:
                    refs.append(
                        (
                            source_id,
                            f"concept_additions[{index}].relations[{relation_index}].source_refs[{source_index}]",
                        )
                    )

    return refs


def test_cross_extension_references_are_declared_dependencies() -> None:
    manifest = _load(MANIFEST_PATH)
    entries = manifest["extensions"]
    assert isinstance(entries, list)

    extensions: dict[str, dict[str, Any]] = {}
    declared_dependencies: dict[str, tuple[str, ...]] = {}
    owner_by_id: dict[str, str] = {}

    for entry in entries:
        assert isinstance(entry, dict)
        extension_id = entry["extension_id"]
        assert isinstance(extension_id, str)
        extension_path = entry["path"]
        assert isinstance(extension_path, str)
        extension = _load(ROOT / extension_path)
        extensions[extension_id] = extension
        declared_dependencies[extension_id] = tuple(entry.get("depends_on", []) or [])

        for section in ADDITION_SECTIONS:
            for record in _records(extension.get(section)):
                entity_id = record.get("id")
                assert isinstance(entity_id, str) and entity_id
                prior = owner_by_id.setdefault(entity_id, extension_id)
                assert prior == extension_id, (
                    entity_id,
                    prior,
                    extension_id,
                )

    closure_cache: dict[str, frozenset[str]] = {}

    def dependency_closure(extension_id: str, stack: tuple[str, ...] = ()) -> frozenset[str]:
        cached = closure_cache.get(extension_id)
        if cached is not None:
            return cached
        assert extension_id not in stack, f"dependency cycle: {stack + (extension_id,)}"

        closure: set[str] = set()
        for dependency in declared_dependencies[extension_id]:
            assert dependency in declared_dependencies, (
                extension_id,
                dependency,
                "unknown dependency",
            )
            closure.add(dependency)
            closure.update(
                dependency_closure(dependency, stack + (extension_id,))
            )

        result = frozenset(closure)
        closure_cache[extension_id] = result
        return result

    violations: list[tuple[str, str, str, str]] = []
    for extension_id, extension in extensions.items():
        allowed_owners = dependency_closure(extension_id) | {extension_id}
        for referenced_id, location in _references(extension):
            owner = owner_by_id.get(referenced_id)
            if owner is not None and owner not in allowed_owners:
                violations.append(
                    (extension_id, referenced_id, owner, location)
                )

    assert not violations, (
        "cross-extension references require the referenced ID owner's extension "
        "to appear in the declared dependency closure:\n"
        + "\n".join(
            f"{ext}: {ref} owned by {owner} at {location}"
            for ext, ref, owner, location in sorted(violations)
        )
    )
