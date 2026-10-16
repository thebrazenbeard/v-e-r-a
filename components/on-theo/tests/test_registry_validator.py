from pathlib import Path

import yaml

from tools.on_theo_registry.validator import validate_repository


def _write_yaml(root: Path, relative: str, data: dict) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _minimal_repo(root: Path) -> None:
    _write_yaml(root, "registry/sources.yaml", {"sources": [{"id": "SRC-A"}]})
    _write_yaml(
        root,
        "registry/claims.yaml",
        {
            "claims": [
                {
                    "id": "CLM-A",
                    "supporting_sources": [{"source_id": "SRC-A"}],
                    "opposing_sources": [],
                }
            ]
        },
    )
    _write_yaml(root, "registry/concepts.yaml", {"concepts": []})
    _write_yaml(root, "registry/transmissions.yaml", {"edges": []})
    _write_yaml(root, "registry/witnesses.yaml", {"witnesses": []})
    _write_yaml(
        root,
        "registry/reviews.yaml",
        {
            "allowed_results": ["PASS_EXACT", "PASS_WITH_LIMITATIONS", "CHANGES_REQUIRED", "FAIL", "UNRESOLVED", "NOT_REVIEWED"],
            "execution_provenance_types": ["SAME_RUNTIME_ROLE_PASS", "INDEPENDENT_RUNTIME", "EXTERNAL_HUMAN_REVIEW", "UNKNOWN"],
            "receipts": [],
        },
    )
    _write_yaml(root, "registry/source-access.yaml", {"records": [{"source_id": "SRC-A"}]})
    _write_yaml(root, "registry/extension-manifest.yaml", {"extensions": []})


def _error_codes(report) -> set[str]:
    return {finding.code for finding in report.errors}


def test_minimal_valid_repository_passes(tmp_path: Path) -> None:
    _minimal_repo(tmp_path)

    report = validate_repository(tmp_path)

    assert report.ok
    assert report.errors == ()


def test_duplicate_stable_ids_fail(tmp_path: Path) -> None:
    _minimal_repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/sources.yaml",
        {"sources": [{"id": "SRC-DUP"}, {"id": "SRC-DUP"}]},
    )

    report = validate_repository(tmp_path)

    assert "DUPLICATE_ID" in _error_codes(report)


def test_unknown_claim_source_reference_fails(tmp_path: Path) -> None:
    _minimal_repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/claims.yaml",
        {
            "claims": [
                {
                    "id": "CLM-A",
                    "supporting_sources": [{"source_id": "SRC-MISSING"}],
                    "opposing_sources": [],
                }
            ]
        },
    )

    report = validate_repository(tmp_path)

    assert "UNKNOWN_SOURCE_REFERENCE" in _error_codes(report)


def test_manifest_extension_identity_must_match_file(tmp_path: Path) -> None:
    _minimal_repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/extension-manifest.yaml",
        {
            "extensions": [
                {
                    "extension_id": "EXT-DECLARED",
                    "path": "registry/extensions/example.yaml",
                    "declared_base": "abc123",
                    "depends_on": [],
                }
            ]
        },
    )
    _write_yaml(
        tmp_path,
        "registry/extensions/example.yaml",
        {
            "extension_id": "EXT-ACTUAL",
            "base_registry_head": "abc123",
            "source_additions": [],
        },
    )

    report = validate_repository(tmp_path)

    assert "MANIFEST_EXTENSION_ID_MISMATCH" in _error_codes(report)


def test_witness_must_resolve_its_source(tmp_path: Path) -> None:
    _minimal_repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/witnesses.yaml",
        {
            "witnesses": [
                {
                    "id": "WIT-A",
                    "witness_of": "SRC-MISSING",
                }
            ]
        },
    )

    report = validate_repository(tmp_path)

    assert "UNKNOWN_WITNESS_SOURCE" in _error_codes(report)


def test_review_result_and_execution_provenance_use_declared_vocabularies(tmp_path: Path) -> None:
    _minimal_repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/reviews.yaml",
        {
            "allowed_results": ["PASS_EXACT"],
            "execution_provenance_types": ["SAME_RUNTIME_ROLE_PASS"],
            "receipts": [
                {
                    "id": "REV-A",
                    "repository": "example/repo",
                    "subject_sha": "abc123",
                    "review_type": "HOSTILE_ALTERNATIVES",
                    "reviewer_role": "Masa",
                    "execution_provenance": "MAGIC_INDEPENDENCE",
                    "result": "PERFECT",
                    "reviewed_artifacts": ["registry/claims.yaml"],
                    "findings": [],
                }
            ],
        },
    )

    report = validate_repository(tmp_path)

    assert "INVALID_REVIEW_RESULT" in _error_codes(report)
    assert "INVALID_EXECUTION_PROVENANCE" in _error_codes(report)


def test_manifest_dependency_must_precede_dependent(tmp_path: Path) -> None:
    _minimal_repo(tmp_path)
    _write_yaml(
        tmp_path,
        "registry/extension-manifest.yaml",
        {
            "extensions": [
                {
                    "extension_id": "EXT-B",
                    "path": "registry/extensions/b.yaml",
                    "declared_base": "base-b",
                    "depends_on": ["EXT-A"],
                },
                {
                    "extension_id": "EXT-A",
                    "path": "registry/extensions/a.yaml",
                    "declared_base": "base-a",
                    "depends_on": [],
                },
            ]
        },
    )
    _write_yaml(
        tmp_path,
        "registry/extensions/a.yaml",
        {"extension_id": "EXT-A", "base_registry_head": "base-a"},
    )
    _write_yaml(
        tmp_path,
        "registry/extensions/b.yaml",
        {"extension_id": "EXT-B", "base_registry_head": "base-b"},
    )

    report = validate_repository(tmp_path)

    assert "MANIFEST_DEPENDENCY_ORDER" in _error_codes(report)


def test_current_repository_stack_validates() -> None:
    root = Path(__file__).resolve().parents[1]
    report = validate_repository(root)
    assert report.errors == (), "\n".join(
        f"{item.code} {item.path}: {item.message}" for item in report.errors
    )
