from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CUT = ROOT / "project-instructions" / "r10a0" / "restore-v2-live"

MANIFEST_PATH = "project-instructions/r10a0/restore-v2-live/VERA_R10A0_SD1_RESTORE_V2_PROJECT_SOURCE_MANIFEST.json"
NATIVE_PATH = "project-instructions/r10a0/restore-v2-live/VERA_R10A0_SD1_RESTORE_V2_NATIVE_PROJECT_INSTRUCTIONS.txt"
RECEIPT_PATH = "project-instructions/r10a0/restore-v2-live/VERA_R10A0_SD1_RESTORE_V2_SOURCE_RECEIPT.json"
INSTALL = CUT / "INSTALL_RESTORE_V2.md"
QUALIFICATION = CUT / "VERA_R10A0_SD1_RESTORE_V2_QUALIFICATION.md"
CURRENTNESS = ROOT / "governance" / "VERA_RESTORE_V2_INSTALL_CURRENTNESS_V1.json"

SOURCE_CUT = "57bd2cd3e53bc112d7bf220ede82225f14e2e540"
ARTIFACT_COMMIT = "687ba64555c39619a9552a86206fa78ab3387a7e"
BOUND_MAIN = "505c395890bde275cbbc6327be8f387e7f25ca3a"

FINAL_MANIFEST_SHA = "fb99689bd8e8efabf6b9612d7f1451ea9701fae3e655c6cf6dfab0f043a3aeac"
FINAL_NATIVE_SHA = "1cfc6708c4e64cebae0a4721d38eb59592239d2ba61e7c4196130162c6e5381b"
MANIFEST_BLOB = "8327031704186a59450ae8bc20c944491cf22396"
NATIVE_BLOB = "348f668be5da7ed0fd834947975dbea1579ffddd"
RECEIPT_BLOB = "6d4e0820c025030140f00552d654054c5566e171"
STALE_MANIFEST_SHA = "9c8cbda882f794b4237e7c447427123fcc3deb7513b2c17ec39ceb3bdd34439c"
STALE_NATIVE_SHA = "d08306e64848b55e83d5bd8dd8a258f68465812c8eddbb28670decc006858b53"


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


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_source_cut_and_artifact_are_ancestors_of_candidate_head():
    subprocess.run(
        ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", SOURCE_CUT, "HEAD"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", ARTIFACT_COMMIT, "HEAD"],
        check=True,
    )


def test_exact_artifact_bytes_match_bound_hashes_and_current_head_blobs():
    manifest = git_bytes(ARTIFACT_COMMIT, MANIFEST_PATH)
    native = git_bytes(ARTIFACT_COMMIT, NATIVE_PATH)

    assert hashlib.sha256(manifest).hexdigest() == FINAL_MANIFEST_SHA
    assert hashlib.sha256(native).hexdigest() == FINAL_NATIVE_SHA
    assert len(manifest) == 8035
    assert len(native) == 7997

    assert git_blob(ARTIFACT_COMMIT, MANIFEST_PATH) == MANIFEST_BLOB
    assert git_blob(ARTIFACT_COMMIT, NATIVE_PATH) == NATIVE_BLOB
    assert git_blob("HEAD", MANIFEST_PATH) == MANIFEST_BLOB
    assert git_blob("HEAD", NATIVE_PATH) == NATIVE_BLOB
    assert git_blob("HEAD", RECEIPT_PATH) == RECEIPT_BLOB


def test_install_and_qualification_docs_reference_final_bytes_only():
    install = INSTALL.read_text(encoding="utf-8")
    qualification = QUALIFICATION.read_text(encoding="utf-8")
    assert FINAL_MANIFEST_SHA in install
    assert FINAL_NATIVE_SHA in install
    assert FINAL_MANIFEST_SHA in qualification
    assert STALE_MANIFEST_SHA not in install
    assert STALE_NATIVE_SHA not in install
    assert STALE_MANIFEST_SHA not in qualification


def test_currentness_contract_binds_point_in_time_repository_observation():
    current = load(CURRENTNESS)
    obs = current["repository_observation"]
    assert obs["bound_current_main"] == BOUND_MAIN
    assert obs["source_cut_is_ancestor"] is True
    assert obs["immutable_artifact_commit"] == ARTIFACT_COMMIT
    assert obs["current_main_manifest_git_blob"] == MANIFEST_BLOB
    assert obs["current_main_native_git_blob"] == NATIVE_BLOB
    assert obs["current_main_source_receipt_git_blob"] == RECEIPT_BLOB
    assert "Fresh-read" in obs["mutable_currentness_rule"]


def test_currentness_contract_preserves_source_install_runtime_separation():
    current = load(CURRENTNESS)
    manifest = json.loads(git_bytes(ARTIFACT_COMMIT, MANIFEST_PATH))
    receipt = json.loads(git_bytes(SOURCE_CUT, RECEIPT_PATH))

    assert current["source_classification"]["manifest_status"] == manifest["status"]
    assert current["source_classification"]["receipt_status"] == receipt["status"]
    assert current["source_classification"]["receipt_claim_ceiling"] == receipt["claim_ceiling"]

    runtime = current["runtime_currentness"]
    assert runtime["vera_unbound_project_settings_readback"] == "NOT_ESTABLISHED_BY_THIS_SOURCE_REPAIR"
    assert runtime["active_k00_k03_readback"] == "NOT_ESTABLISHED_BY_THIS_SOURCE_REPAIR"
    assert runtime["install_effect"] == "NOT_ESTABLISHED"
    assert runtime["current_route"] == "NOT_ESTABLISHED"
    assert runtime["q_recover"] == "NOT_EXECUTED_BY_THIS_EVIDENCE"
    assert runtime["user_facing_restored_claim"] == "NOT_ESTABLISHED"


def test_currentness_contract_does_not_manufacture_project_effects():
    current = load(CURRENTNESS)
    for item in (
        "NOT_PROJECT_SETTINGS_MUTATION",
        "NOT_PROJECT_SOURCE_MUTATION",
        "NOT_INSTALL_EFFECT",
        "NOT_CURRENT_ROUTE_QUALIFICATION",
        "NOT_Q_RECOVER_PASS",
        "NOT_MERGE_AUTHORITY",
    ):
        assert item in current["non_effects"]
