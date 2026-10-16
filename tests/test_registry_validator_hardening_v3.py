from pathlib import Path

import yaml

from tools.on_theo_registry.validator import validate_repository


def _write_yaml(root: Path, relative: str, data: dict) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def _repo(root: Path) -> None:
    _write_yaml(root, "registry/sources.yaml", {"sources": [{"id": "SRC-A"}]})
    _write_yaml(
        root,
        "registry/claims.yaml",
        {
            "allowed_evidence_classes": ["PRIMARY_TEXT"],
            "claims": [{"id": "CLM-A", "evidence_class": ["PRIMARY_TEXT"]}],
        },
    )
    _write_yaml(root, "registry/concepts.yaml", {"relation_types": [], "concepts": []})
    _write_yaml(root, "registry/transmissions.yaml", {"relation_types": [], "edges": []})
    _write_yaml(
        root,
        "registry/witnesses.yaml",
        {
            "materialization_state": "EXTENSIONS_PENDING",
            "witnesses": [],
            "pending_extension_records": [],
        },
    )
    _write_yaml(
        root,
        "registry/reviews.yaml",
        {
            "allowed_results": ["PASS_EXACT"],
            "execution_provenance_types": ["INDEPENDENT_RUNTIME"],
            "receipts": [],
        },
    )
    _write_yaml(
        root,
        "registry/source-access.yaml",
        {
            "access_states": {"DIGITAL_EDITION": "digital"},
            "records": [{"source_id": "SRC-A", "state": "DIGITAL_EDITION"}],
        },
    )
    _write_yaml(root, "registry/extension-manifest.yaml", {"extensions": []})


def _codes(root: Path) -> set[str]:
    return {finding.code for finding in validate_repository(root).errors}


def test_review_receipts_reject_non_mapping_records(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/reviews.yaml",
        {
            "allowed_results": ["PASS_EXACT"],
            "execution_provenance_types": ["INDEPENDENT_RUNTIME"],
            "receipts": ["MALFORMED_REVIEW_RECORD"],
        },
    )

    assert "INVALID_RECORD_TYPE" in _codes(tmp_path)


def test_source_access_rejects_non_mapping_records(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/source-access.yaml",
        {
            "access_states": {"DIGITAL_EDITION": "digital"},
            "records": ["MALFORMED_ACCESS_RECORD"],
        },
    )

    assert "INVALID_RECORD_TYPE" in _codes(tmp_path)


def test_pending_witness_index_rejects_non_mapping_records(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/witnesses.yaml",
        {
            "materialization_state": "EXTENSIONS_PENDING",
            "witnesses": [],
            "pending_extension_records": ["MALFORMED_PENDING_WITNESS_RECORD"],
        },
    )

    assert "INVALID_RECORD_TYPE" in _codes(tmp_path)


def test_record_container_must_be_list(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/source-access.yaml",
        {
            "access_states": {"DIGITAL_EDITION": "digital"},
            "records": {"source_id": "SRC-A", "state": "DIGITAL_EDITION"},
        },
    )

    assert "INVALID_RECORD_LIST" in _codes(tmp_path)


def test_extension_additions_reject_non_mapping_records(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/extensions/example.yaml",
        {
            "schema_version": "on-theo.registry-extension.v1",
            "extension_id": "EXT-A",
            "base_registry_head": "abc",
            "status": "PROPOSED",
            "claim_additions": ["MALFORMED_CLAIM_ADDITION"],
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

    assert "INVALID_RECORD_TYPE" in _codes(tmp_path)

def test_claim_evidence_edges_reject_non_mapping_records(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/claims.yaml",
        {
            "allowed_evidence_classes": ["PRIMARY_TEXT"],
            "claims": [
                {
                    "id": "CLM-A",
                    "evidence_class": ["PRIMARY_TEXT"],
                    "supporting_sources": ["MALFORMED_EDGE"],
                }
            ],
        },
    )

    assert "INVALID_RECORD_TYPE" in _codes(tmp_path)


def test_claim_evidence_edge_requires_a_reference(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/claims.yaml",
        {
            "allowed_evidence_classes": ["PRIMARY_TEXT"],
            "claims": [
                {
                    "id": "CLM-A",
                    "evidence_class": ["PRIMARY_TEXT"],
                    "supporting_sources": [{}],
                }
            ],
        },
    )

    assert "MISSING_CLAIM_EVIDENCE_REFERENCE" in _codes(tmp_path)


def test_transmission_requires_from_and_to_sources(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/transmissions.yaml",
        {
            "relation_types": ["PRESERVED_BY"],
            "edges": [
                {
                    "id": "TR-A",
                    "relation": "PRESERVED_BY",
                    "evidence": [{"source_id": "SRC-A"}],
                }
            ],
        },
    )

    codes = _codes(tmp_path)
    assert "MISSING_SOURCE_REFERENCE" in codes


def test_transmission_evidence_requires_source_id(tmp_path: Path) -> None:
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
                    "to_source": "SRC-A",
                    "relation": "PRESERVED_BY",
                    "evidence": [{}],
                }
            ],
        },
    )

    assert "MISSING_SOURCE_REFERENCE" in _codes(tmp_path)


def test_source_access_requires_source_id(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/source-access.yaml",
        {
            "access_states": {"DIGITAL_EDITION": "digital"},
            "records": [{"state": "DIGITAL_EDITION"}],
        },
    )

    assert "MISSING_SOURCE_REFERENCE" in _codes(tmp_path)


def test_concept_source_ref_mapping_requires_source_id(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/concepts.yaml",
        {
            "relation_types": [],
            "concepts": [{"id": "CON-A", "source_refs": [{}], "relations": []}],
        },
    )

    assert "MISSING_SOURCE_REFERENCE" in _codes(tmp_path)


def test_manifest_dependencies_must_be_a_list(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/extensions/example.yaml",
        {
            "schema_version": "on-theo.registry-extension.v1",
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
                    "depends_on": "EXT-OTHER",
                    "status": "PROPOSED",
                    "adds_entity_types": [],
                }
            ],
        },
    )

    assert "INVALID_EXTENSION_DEPENDENCY_LIST" in _codes(tmp_path)


def test_manifest_extension_path_cannot_escape_repository(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/extension-manifest.yaml",
        {
            "extensions": [
                {
                    "extension_id": "EXT-A",
                    "path": "../outside.yaml",
                    "declared_base": "abc",
                    "depends_on": [],
                    "status": "PROPOSED",
                    "adds_entity_types": [],
                }
            ],
        },
    )

    assert "INVALID_EXTENSION_PATH" in _codes(tmp_path)

def test_review_receipt_requires_exact_subject_sha(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
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
            "receipts": [
                {
                    "id": "REV-A",
                    "repository": "example/repo",
                    "subject_sha": None,
                    "review_type": "HOSTILE",
                    "reviewer_role": "Masa",
                    "execution_provenance": "INDEPENDENT_RUNTIME",
                    "result": "PASS_EXACT",
                    "reviewed_artifacts": ["registry/claims.yaml"],
                    "findings": [],
                }
            ],
        },
    )

    assert "INVALID_REVIEW_SUBJECT_SHA" in _codes(tmp_path)


def test_review_receipt_requires_nonempty_reviewed_artifacts(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
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
            "receipts": [
                {
                    "id": "REV-A",
                    "repository": "example/repo",
                    "subject_sha": "0" * 40,
                    "review_type": "HOSTILE",
                    "reviewer_role": "Masa",
                    "execution_provenance": "INDEPENDENT_RUNTIME",
                    "result": "PASS_EXACT",
                    "reviewed_artifacts": [],
                    "findings": [],
                }
            ],
        },
    )

    assert "INVALID_REVIEWED_ARTIFACTS" in _codes(tmp_path)


def test_review_findings_reject_non_mapping_entries(tmp_path: Path) -> None:
    _repo(tmp_path)
    _write_yaml(
        tmp_path,
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
            "receipts": [
                {
                    "id": "REV-A",
                    "repository": "example/repo",
                    "subject_sha": "0" * 40,
                    "review_type": "HOSTILE",
                    "reviewer_role": "Masa",
                    "execution_provenance": "INDEPENDENT_RUNTIME",
                    "result": "PASS_EXACT",
                    "reviewed_artifacts": ["registry/claims.yaml"],
                    "findings": ["MALFORMED_FINDING"],
                }
            ],
        },
    )

    assert "INVALID_REVIEW_FINDING" in _codes(tmp_path)
