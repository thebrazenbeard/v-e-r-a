import json
import subprocess
import sys
from pathlib import Path

import yaml


def _write_yaml(root: Path, relative: str, data: dict) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _minimal_repo(root: Path, *, missing_source: bool = False) -> None:
    _write_yaml(root, "registry/sources.yaml", {"sources": [{"id": "SRC-A"}]})
    source_id = "SRC-MISSING" if missing_source else "SRC-A"
    _write_yaml(root, "registry/claims.yaml", {"claims": [{"id": "CLM-A", "supporting_sources": [{"source_id": source_id}], "opposing_sources": []}]})
    _write_yaml(root, "registry/concepts.yaml", {"concepts": []})
    _write_yaml(root, "registry/transmissions.yaml", {"edges": []})
    _write_yaml(root, "registry/witnesses.yaml", {"witnesses": []})
    _write_yaml(root, "registry/reviews.yaml", {"allowed_results": ["PASS_EXACT"], "execution_provenance_types": ["SAME_RUNTIME_ROLE_PASS"], "receipts": []})
    _write_yaml(root, "registry/source-access.yaml", {"records": [{"source_id": "SRC-A"}]})
    _write_yaml(root, "registry/extension-manifest.yaml", {"extensions": []})


def _run_cli(repo_root: Path, target_root: Path):
    return subprocess.run(
        [sys.executable, str(repo_root / "scripts/validate_registry.py"), "--root", str(target_root), "--json"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )


def test_cli_json_success(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    _minimal_repo(tmp_path)
    result = _run_cli(repo_root, tmp_path)
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["errors"] == []


def test_cli_json_failure_has_stable_code(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    _minimal_repo(tmp_path, missing_source=True)
    result = _run_cli(repo_root, tmp_path)
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert "UNKNOWN_SOURCE_REFERENCE" in [item["code"] for item in payload["errors"]]
