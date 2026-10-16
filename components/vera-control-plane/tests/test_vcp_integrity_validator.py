from __future__ import annotations

import json
from pathlib import Path
import tempfile

from tools.validate_vcp_integrity import (
    MANIFEST_PATH,
    RECEIPT_PATH,
    verify_kernel,
    verify_package,
)

ROOT = Path(__file__).resolve().parents[1]


def test_validator_kernel_contract() -> None:
    report = verify_kernel()
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert report["kernel_characters"] == manifest["native_kernel_chars"]
    assert report["kernel_characters"] <= 8000


def test_validator_reproduces_frozen_nv2a1_package() -> None:
    with tempfile.TemporaryDirectory(prefix="vcp-validator-test-") as tmp:
        output = Path(tmp) / "VERA_NV2A1_20260922_INSTALL.zip"
        report = verify_package(output)
    receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert report["package_sha256"] == receipt["package"]["sha256"]
    assert report["package_bytes"] == receipt["package"]["bytes"]
    assert report["package_members"] == receipt["package"]["member_count"]


def test_workflow_calls_executable_validator() -> None:
    workflow = (
        ROOT / ".github" / "workflows" / "vcp-integrity.yml"
    ).read_text(encoding="utf-8")
    assert 'python tools/validate_vcp_integrity.py --base-sha "$BASE_SHA"' in workflow
