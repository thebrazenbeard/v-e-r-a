"""Run the VCP integrity gate from any checkout.

This is the executable source of truth used by both local validation and
GitHub Actions. It does not mutate repository state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build_native_project_successor_v2a1 import build as build_nv2a1
NATIVE = ROOT / "project-instructions" / "native-v2"
MANIFEST_PATH = NATIVE / "VERA_NATIVE_PROJECT_PACK_MANIFEST_V2.json"
RECEIPT_PATH = NATIVE / "delivery" / "VERA_NV2A1_20260922_DELIVERY_RECEIPT.json"
KERNEL_PATH = NATIVE / "VERA_NATIVE_PROJECT_KERNEL_V2.txt"
ZERO_SHA = "0" * 40


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def verify_kernel() -> dict[str, int]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    kernel = KERNEL_PATH.read_text(encoding="utf-8")
    actual = len(kernel)
    assert actual <= 8000, f"native kernel exceeds 8000 characters: {actual}"
    assert actual == manifest["native_kernel_chars"], (
        f"kernel character count {actual} != manifest {manifest['native_kernel_chars']}"
    )
    return {"kernel_characters": actual}


def verify_package(output: Path) -> dict[str, object]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    build = build_nv2a1(output)

    payload = output.read_bytes()
    actual_sha = hashlib.sha256(payload).hexdigest()
    expected = receipt["package"]

    assert actual_sha == build["sha256"]
    assert actual_sha == expected["sha256"]
    assert len(payload) == expected["bytes"]

    expected_names = [
        manifest["delivery_filename_map"][name]
        for name in manifest["files"]
    ]
    with zipfile.ZipFile(output, "r") as archive:
        names = archive.namelist()
        assert names == expected_names
        assert len(names) == expected["member_count"]
        assert len(names) == len(set(names))

    return {
        "package_sha256": actual_sha,
        "package_bytes": len(payload),
        "package_members": len(expected_names),
    }


def verify_whitespace(base_sha: str | None) -> None:
    if base_sha and base_sha != ZERO_SHA:
        probe = subprocess.run(
            ["git", "cat-file", "-e", f"{base_sha}^{{commit}}"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if probe.returncode == 0:
            run(["git", "diff", "--check", f"{base_sha}...HEAD"])
            return

    parent = subprocess.run(
        ["git", "rev-parse", "HEAD^"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if parent.returncode == 0:
        run(["git", "diff", "--check", "HEAD^", "HEAD"])
    else:
        run(["git", "diff", "--check"])


def run_repository_tests() -> None:
    run([sys.executable, "-m", "compileall", "-q", "tools", "tests"])
    run([sys.executable, "-m", "pytest", "-q", "tests"])


def validate(base_sha: str | None = None, run_tests: bool = True) -> dict[str, object]:
    report: dict[str, object] = {}
    report.update(verify_kernel())

    with tempfile.TemporaryDirectory(prefix="vcp-integrity-") as tmp:
        package = Path(tmp) / "VERA_NV2A1_20260922_INSTALL.zip"
        report.update(verify_package(package))

    verify_whitespace(base_sha)

    if run_tests:
        run_repository_tests()
        report["repository_tests"] = "PASS"
    else:
        report["repository_tests"] = "SKIPPED"

    report["status"] = "PASS"
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-sha", default=None)
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args()
    print(json.dumps(validate(args.base_sha, not args.skip_tests), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
