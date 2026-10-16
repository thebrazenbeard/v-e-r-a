import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

from tools.build_native_project_pack_v2 import build

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = (
    ROOT
    / "project-instructions"
    / "native-v2"
    / "VERA_NATIVE_PROJECT_V2_SOURCE_RECEIPT.json"
)


def git_bytes(commit: str, path: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(ROOT), "show", f"{commit}:{path}"],
        check=True,
        capture_output=True,
    ).stdout


def git_blob(commit: str, path: str) -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", f"{commit}:{path}"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def load_receipt() -> dict:
    return json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))


def load_manifest(receipt: dict) -> dict:
    path = (
        receipt["source_directory"]
        + "VERA_NATIVE_PROJECT_PACK_MANIFEST_V2.json"
    )
    return json.loads(git_bytes(receipt["pre_receipt_head"], path))


def test_receipt_files_match_frozen_pre_receipt_git_subject():
    receipt = load_receipt()
    manifest = load_manifest(receipt)
    assert set(receipt["files"]) == set(manifest["files"])

    for name in manifest["files"]:
        path = receipt["source_directory"] + name
        payload = git_bytes(receipt["pre_receipt_head"], path)
        bound = receipt["files"][name]
        assert git_blob(receipt["pre_receipt_head"], path) == bound["git_blob"]
        assert hashlib.sha256(payload).hexdigest() == bound["sha256"]


def test_builder_source_is_exactly_bound():
    receipt = load_receipt()
    builder = receipt["package"]["builder"]
    assert git_blob(builder["source_commit"], builder["path"]) == (
        builder["git_blob"]
    )


def test_rebuilt_package_matches_receipt(tmp_path):
    receipt = load_receipt()
    output = tmp_path / receipt["package"]["filename_hint"]
    digest = build(output)
    assert digest == receipt["package"]["sha256"]
    assert output.stat().st_size == receipt["package"]["bytes"]


def test_archive_entries_are_frozen_git_bytes_in_manifest_order(tmp_path):
    receipt = load_receipt()
    manifest = load_manifest(receipt)
    output = tmp_path / receipt["package"]["filename_hint"]
    build(output)

    with zipfile.ZipFile(output) as archive:
        assert archive.namelist() == manifest["files"]
        for info in archive.infolist():
            expected = git_bytes(
                receipt["pre_receipt_head"],
                receipt["source_directory"] + info.filename,
            )
            assert archive.read(info.filename) == expected
            assert info.date_time == (1980, 1, 1, 0, 0, 0)
            assert info.compress_type == zipfile.ZIP_STORED
            assert info.external_attr >> 16 == 0o100644


def test_receipt_remains_source_custody_only():
    receipt = load_receipt()
    assert receipt["status"] == (
        "SOURCE_CUSTODY_ONLY_NOT_CANONICAL_RELEASE_NOT_INSTALL_EVIDENCE"
    )
    assert receipt["package"]["binary_zip_not_committed"] is True
    assert receipt["package"]["reproducible_from_git"] is True
    assert "not native Project installation evidence" in receipt["non_effects"]
    assert "not current-route evidence" in receipt["non_effects"]
    assert "not runtime-consumption evidence" in receipt["non_effects"]
