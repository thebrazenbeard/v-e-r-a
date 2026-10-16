from pathlib import Path

import yaml

from tools.on_theo_registry.validator import validate_repository


def _write_yaml(root: Path, relative: str, data: dict) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _repo(root: Path) -> None:
    _write_yaml(root, "registry/sources.yaml", {"sources": [{"id": "SRC-A"}, {"id": "SRC-B"}]})
    _write_yaml(
        root,
        "registry/claims.yaml",
        {
            "allowed_evidence_classes": ["PRIMARY_TEXT", "UNKNOWN"],
            "claims": [
                {
                    "id": "CLM-A",
                    "evidence_class": ["PRIMARY_TEXT"],
                    "supporting_sources": [{"source_id": "SRC-A"}],
                    "opposing_sources": [],
                }
            ],
        },
    )
    _write_yaml(
        root,
        "registry/concepts.yaml",
        {
            "relation_types": ["RELATED_BUT_NOT_EQUIVALENT"],
            "concepts": [],
        },
    )
    _write_yaml(
        root,
        "registry/transmissions.yaml",
        {
            "relation_types": ["PRESERVED_BY"],
            "edges": [
                {
                    "id": "TR-A",
                    "from_source": "SRC-A",
                    "to_source": "SRC-B",
                    "relation": "PRESERVED_BY",
                    "evidence": [{"source_id": "SRC-A"}],
                }
            ],
        },
    )
    _write_yaml(root, "registry/witnesses.yaml", {"witnesses": []})
    _write_yaml(
        root,
        "registry/reviews.yaml",
        {
            "allowed_results": ["PASS_EXACT"],
            "execution_provenance_types": ["INDEPENDENT_RUNTIME"],
            "required_fields": [
                "id",
                "repository",
                "subject_sha",
                "review_type",
                "reviewer_role",
                "execution_provenance",
                "result",
                "reviewed_artifacts",
                "findings",
            ],
            "receipts": [],
        },
    )
    _write_yaml(
        root,
        "registry/source-access.yaml",
        {
            "access_states": {
                "DIGITAL_EDITION": "digital edition",
                "INDIRECT_PRESERVATION": "indirect preservation",
            },
            "records": [
                {
                    "source_id": "SRC-A",
                    "direct_access": True,
                    "state": "DIGITAL_EDITION",
                }
            ],
        },
    )
    _write_yaml(root, "registry/extension-manifest.yaml", {"extensions": []})


def _codes(root: Path) -> set[str]:
    return {finding.code for finding in validate_repository(root).errors}


def test_unlisted_extension_file_fails(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/extensions/orphan.yaml",
        {"extension_id": "EXT-ORPHAN", "base_registry_head": "abc", "source_additions": []},
    )

    assert "ORPHAN_EXTENSION_FILE" in _codes(tmp_path)


def test_duplicate_manifest_extension_path_fails(tmp_path: Path) -> None:
    _repo(tmp_path)
    extension = {
        "extension_id": "EXT-A",
        "base_registry_head": "abc",
        "source_additions": [],
    }
    _write_yaml(tmp_path, "registry/extensions/shared.yaml", extension)
    _write_yaml(
        tmp_path,
        "registry/extension-manifest.yaml",
        {
            "extensions": [
                {
                    "extension_id": "EXT-A",
                    "path": "registry/extensions/shared.yaml",
                    "declared_base": "abc",
                    "depends_on": [],
                },
                {
                    "extension_id": "EXT-B",
                    "path": "registry/extensions/shared.yaml",
                    "declared_base": "abc",
                    "depends_on": [],
                },
            ]
        },
    )

    codes = _codes(tmp_path)
    assert "DUPLICATE_EXTENSION_PATH" in codes
    assert "MANIFEST_EXTENSION_ID_MISMATCH" in codes


def test_invalid_claim_evidence_class_fails(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/claims.yaml",
        {
            "allowed_evidence_classes": ["PRIMARY_TEXT"],
            "claims": [
                {
                    "id": "CLM-A",
                    "evidence_class": ["NOT_A_CLASS"],
                    "supporting_sources": [{"source_id": "SRC-A"}],
                    "opposing_sources": [],
                }
            ],
        },
    )

    assert "INVALID_EVIDENCE_CLASS" in _codes(tmp_path)


def test_invalid_transmission_relation_fails(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/transmissions.yaml",
        {
            "relation_types": ["PRESERVED_BY"],
            "edges": [
                {
                    "id": "TR-A",
                    "from_source": "SRC-A",
                    "to_source": "SRC-B",
                    "relation": "INVENTED_RELATION",
                    "evidence": [],
                }
            ],
        },
    )

    assert "INVALID_TRANSMISSION_RELATION" in _codes(tmp_path)


def test_invalid_concept_relation_fails(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/concepts.yaml",
        {
            "relation_types": ["RELATED_BUT_NOT_EQUIVALENT"],
            "concepts": [
                {
                    "id": "CON-A",
                    "relations": [
                        {
                            "target_concept_id": "CON-B",
                            "relation": "INVENTED_RELATION",
                        }
                    ],
                },
                {"id": "CON-B", "relations": []},
            ],
        },
    )

    assert "INVALID_CONCEPT_RELATION" in _codes(tmp_path)


def test_source_access_state_and_preservation_refs_are_validated(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/source-access.yaml",
        {
            "access_states": {"DIGITAL_EDITION": "digital edition"},
            "records": [
                {
                    "source_id": "SRC-A",
                    "direct_access": "yes",
                    "state": "UNKNOWN_STATE",
                    "preserved_by": ["SRC-MISSING"],
                }
            ],
        },
    )

    codes = _codes(tmp_path)
    assert "INVALID_SOURCE_ACCESS_STATE" in codes
    assert "INVALID_DIRECT_ACCESS_FLAG" in codes
    assert "UNKNOWN_SOURCE_REFERENCE" in codes


def test_review_contract_required_fields_are_enforced(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/reviews.yaml",
        {
            "allowed_results": ["PASS_EXACT"],
            "execution_provenance_types": ["INDEPENDENT_RUNTIME"],
            "required_fields": ["id", "repository", "subject_sha", "result"],
            "receipts": [
                {
                    "id": "REV-A",
                    "repository": "example/repo",
                    "result": "PASS_EXACT",
                    "execution_provenance": "INDEPENDENT_RUNTIME",
                }
            ],
        },
    )

    assert "MISSING_REVIEW_REQUIRED_FIELD" in _codes(tmp_path)

def test_witness_required_fields_are_enforced(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/witnesses.yaml",
        {
            "required_fields": ["id", "witness_of", "witness_kind"],
            "witnesses": [{"id": "WIT-A", "witness_of": "SRC-A"}],
        },
    )

    assert "MISSING_WITNESS_REQUIRED_FIELD" in _codes(tmp_path)


def test_concept_required_fields_are_enforced(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/concepts.yaml",
        {
            "relation_types": ["RELATED_BUT_NOT_EQUIVALENT"],
            "concept_record_contract": {
                "required_fields": ["id", "canonical_label", "kind", "forms", "semantic_guard"]
            },
            "concepts": [{"id": "CON-A", "relations": []}],
        },
    )

    assert "MISSING_CONCEPT_REQUIRED_FIELD" in _codes(tmp_path)


def test_pending_witness_must_resolve_to_manifest_extension_and_witness(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/witnesses.yaml",
        {
            "witnesses": [],
            "pending_extension_records": [
                {"id": "WIT-MISSING", "declared_in": "EXT-MISSING"}
            ],
        },
    )

    codes = _codes(tmp_path)
    assert "UNKNOWN_PENDING_WITNESS" in codes
    assert "UNKNOWN_PENDING_WITNESS_EXTENSION" in codes

def test_concept_relation_requires_target_id(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/concepts.yaml",
        {
            "relation_types": ["RELATED_BUT_NOT_EQUIVALENT"],
            "concepts": [
                {
                    "id": "CON-A",
                    "relations": [{"relation": "RELATED_BUT_NOT_EQUIVALENT"}],
                }
            ],
        },
    )

    assert "MISSING_CONCEPT_TARGET" in _codes(tmp_path)

def test_manifest_entity_types_must_match_extension_contents(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/extensions/example.yaml",
        {
            "extension_id": "EXT-A",
            "base_registry_head": "abc",
            "source_additions": [{"id": "SRC-C"}],
        },
    )
    _write_yaml(
        tmp_path,
        "registry/extension-manifest.yaml",
        {
            "extensions": [
                {
                    "extension_id": "EXT-A",
                    "path": "registry/extensions/example.yaml",
                    "declared_base": "abc",
                    "depends_on": [],
                    "adds_entity_types": ["claim"],
                }
            ]
        },
    )

    assert "MANIFEST_ENTITY_TYPES_MISMATCH" in _codes(tmp_path)


def test_concept_source_refs_must_resolve(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/concepts.yaml",
        {
            "relation_types": ["RELATED_BUT_NOT_EQUIVALENT"],
            "concepts": [
                {
                    "id": "CON-A",
                    "source_refs": ["SRC-MISSING"],
                    "relations": [],
                }
            ],
        },
    )

    assert "UNKNOWN_SOURCE_REFERENCE" in _codes(tmp_path)


def test_concept_relation_source_refs_must_resolve(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/concepts.yaml",
        {
            "relation_types": ["RELATED_BUT_NOT_EQUIVALENT"],
            "concepts": [
                {
                    "id": "CON-A",
                    "relations": [
                        {
                            "relation": "RELATED_BUT_NOT_EQUIVALENT",
                            "target_concept_id": "CON-B",
                            "source_refs": ["SRC-MISSING"],
                        }
                    ],
                },
                {"id": "CON-B", "relations": []},
            ],
        },
    )

    assert "UNKNOWN_SOURCE_REFERENCE" in _codes(tmp_path)

def test_pending_witness_owner_must_match_extension(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/extensions/witness.yaml",
        {
            "extension_id": "EXT-WIT",
            "base_registry_head": "abc",
            "witness_additions": [
                {
                    "id": "WIT-A",
                    "witness_of": "SRC-A",
                    "witness_kind": "manuscript",
                }
            ],
        },
    )
    _write_yaml(
        tmp_path,
        "registry/extension-manifest.yaml",
        {
            "extensions": [
                {
                    "extension_id": "EXT-WIT",
                    "path": "registry/extensions/witness.yaml",
                    "declared_base": "abc",
                    "depends_on": [],
                    "adds_entity_types": ["witness"],
                }
            ]
        },
    )
    _write_yaml(
        tmp_path,
        "registry/witnesses.yaml",
        {
            "witnesses": [],
            "pending_extension_records": [
                {"id": "WIT-A", "declared_in": "EXT-WRONG"}
            ],
        },
    )

    codes = _codes(tmp_path)
    assert "PENDING_WITNESS_OWNER_MISMATCH" in codes
    assert "UNKNOWN_PENDING_WITNESS_EXTENSION" in codes


def test_extensions_pending_requires_complete_witness_index(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/extensions/witness.yaml",
        {
            "extension_id": "EXT-WIT",
            "base_registry_head": "abc",
            "witness_additions": [
                {
                    "id": "WIT-A",
                    "witness_of": "SRC-A",
                    "witness_kind": "manuscript",
                }
            ],
        },
    )
    _write_yaml(
        tmp_path,
        "registry/extension-manifest.yaml",
        {
            "extensions": [
                {
                    "extension_id": "EXT-WIT",
                    "path": "registry/extensions/witness.yaml",
                    "declared_base": "abc",
                    "depends_on": [],
                    "adds_entity_types": ["witness"],
                }
            ]
        },
    )
    _write_yaml(
        tmp_path,
        "registry/witnesses.yaml",
        {
            "materialization_state": "EXTENSIONS_PENDING",
            "witnesses": [],
            "pending_extension_records": [],
        },
    )

    assert "MISSING_PENDING_WITNESS_INDEX" in _codes(tmp_path)

def test_extension_schema_version_must_match_manifest_contract(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/extensions/example.yaml",
        {
            "schema_version": "wrong.schema",
            "extension_id": "EXT-A",
            "base_registry_head": "abc",
            "status": "PROPOSED",
        },
    )
    _write_yaml(
        tmp_path,
        "registry/extension-manifest.yaml",
        {
            "extension_schema_version": "on-theo.registry-extension.v1",
            "extensions": [
                {
                    "extension_id": "EXT-A",
                    "path": "registry/extensions/example.yaml",
                    "declared_base": "abc",
                    "depends_on": [],
                    "status": "PROPOSED",
                    "adds_entity_types": [],
                }
            ],
        },
    )

    assert "EXTENSION_SCHEMA_VERSION_MISMATCH" in _codes(tmp_path)


def test_extension_status_must_match_manifest_entry(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/extensions/example.yaml",
        {
            "schema_version": "on-theo.registry-extension.v1",
            "extension_id": "EXT-A",
            "base_registry_head": "abc",
            "status": "FILE_STATUS",
        },
    )
    _write_yaml(
        tmp_path,
        "registry/extension-manifest.yaml",
        {
            "extension_schema_version": "on-theo.registry-extension.v1",
            "extensions": [
                {
                    "extension_id": "EXT-A",
                    "path": "registry/extensions/example.yaml",
                    "declared_base": "abc",
                    "depends_on": [],
                    "status": "MANIFEST_STATUS",
                    "adds_entity_types": [],
                }
            ],
        },
    )

    assert "MANIFEST_EXTENSION_STATUS_MISMATCH" in _codes(tmp_path)
