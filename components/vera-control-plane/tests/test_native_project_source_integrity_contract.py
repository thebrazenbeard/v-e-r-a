from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "project-instructions" / "native-v2"


def read(name: str) -> str:
    return (NATIVE / name).read_text(encoding="utf-8")


def test_kernel_preserves_live_inventory_and_filename_boundaries() -> None:
    kernel = read("VERA_NATIVE_PROJECT_KERNEL_V2.txt")
    assert len(kernel) <= 8000
    assert "NO_RESULT != ABSENT" in kernel
    assert "inspect the live Project source surface" in kernel
    assert "Patrick's upload claim requires live verification before contradiction" in kernel
    assert "typed source-separation filename/ZIP rule" in kernel
    assert "suffixes alone never trigger rename/repackage" in kernel


def test_source_separation_distinguishes_identity_from_successor_naming() -> None:
    control = read("VERA_CONTROL_SOURCE_SEPARATION_V2.md")
    assert "CACHED_INVENTORY != LIVE_INVENTORY" in control
    assert "must not reuse a basename previously exposed" in control
    assert "release-scoped, never-before-used filename namespace" in control
    assert "only inside one verified ZIP" in control
    assert "Do not rename or repackage an existing live Project set merely because the UI displays suffixes" in control


def test_repeated_correction_changes_method_instead_of_repeating_it() -> None:
    task = read("VERA_TASK_EXECUTION_AND_CLOSEOUT_V2.md")
    assert "Correction recurrence gate" in task
    assert "Do not re-offer the obsolete route under a new label" in task
    assert "inspection/verification request stays inspection/verification" in task
    assert "another apology plus the same route is not a repair" in task


def test_currentness_requires_fresh_live_check_after_upload_claim() -> None:
    currentness = read("VERA_CURRENTNESS_AND_RECOVERY_V2.md")
    assert "Project-source absence is a live-state claim" in currentness
    assert "PRESENT_UPLOAD_CLAIM => FRESH_LIVE_CHECK" in currentness
    assert "FILENAME_VARIANT != CONTENT_VARIANT" in currentness


def test_interface_requires_live_project_source_check_before_absence_claim() -> None:
    interface = read("VERA_NATIVE_PROJECT_INTERFACE_V2.yaml")
    assert "before any missing/stale/duplicate Project-source claim" in interface
    assert "fresh-check the live Project source surface" in interface


def test_manifest_binds_kernel_length_and_install_naming_policy() -> None:
    kernel = read("VERA_NATIVE_PROJECT_KERNEL_V2.txt")
    manifest = json.loads(read("VERA_NATIVE_PROJECT_PACK_MANIFEST_V2.json"))
    assert manifest["native_kernel_chars"] == len(kernel)
    naming = manifest["install_artifact_naming"]
    assert naming["successor_basename_policy"] == "NEW_RELEASE_SCOPED_UNUSED_NAMESPACE"
    assert naming["loose_installable_chat_artifacts"] == "FORBIDDEN"
    assert naming["handoff"] == "ONE_VERIFIED_ZIP"
    assert naming["existing_upload_suffix_semantics"] == "NON_AUTHORITATIVE"
    assert manifest["delivery_release_id"] == "VERA_NATIVE_V2A1_20260922_PROJECT_SOURCE_FIX"
    mapping = manifest["delivery_filename_map"]
    assert set(mapping) == set(manifest["files"])
    assert len(set(mapping.values())) == len(mapping)
    assert all(name.startswith("VERA_NV2A1_20260922_") for name in mapping.values())
    assert all(source != delivered for source, delivered in mapping.items())
