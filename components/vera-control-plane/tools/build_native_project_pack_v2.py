"""Build the Vera Native Project V2 package deterministically from frozen Git bytes."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = (
    ROOT
    / "project-instructions"
    / "native-v2"
    / "VERA_NATIVE_PROJECT_V2_SOURCE_RECEIPT.json"
)
FIXED_ZIP_DATETIME = (1980, 1, 1, 0, 0, 0)


def git_bytes(commit: str, path: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(ROOT), "show", f"{commit}:{path}"],
        check=True,
        capture_output=True,
    ).stdout


def load_receipt() -> dict:
    return json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))


def manifest_from_receipt(receipt: dict) -> dict:
    source_dir = receipt["source_directory"]
    manifest_name = "VERA_NATIVE_PROJECT_PACK_MANIFEST_V2.json"
    raw = git_bytes(
        receipt["pre_receipt_head"],
        f"{source_dir}{manifest_name}",
    )
    return json.loads(raw)


def package_subject(receipt: dict) -> list[tuple[str, bytes]]:
    manifest = manifest_from_receipt(receipt)
    source_dir = receipt["source_directory"]
    names = manifest["files"]
    return [
        (
            name,
            git_bytes(
                receipt["pre_receipt_head"],
                f"{source_dir}{name}",
            ),
        )
        for name in names
    ]


def write_deterministic_zip(output: Path, entries: list[tuple[str, bytes]]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, payload in entries:
            info = zipfile.ZipInfo(name, FIXED_ZIP_DATETIME)
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, payload)


def build(output: Path) -> str:
    receipt = load_receipt()
    entries = package_subject(receipt)
    write_deterministic_zip(output, entries)
    return hashlib.sha256(output.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    digest = build(args.output)
    print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
