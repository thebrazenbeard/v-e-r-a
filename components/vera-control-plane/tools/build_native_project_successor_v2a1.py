"""Build the NV2A1 Project-source repair ZIP from the current checkout.

The source filenames in Git remain stable. Install-facing filenames come from
VERA_NATIVE_PROJECT_PACK_MANIFEST_V2.json::delivery_filename_map and must be
fresh release-scoped names.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "project-instructions" / "native-v2"
MANIFEST = NATIVE / "VERA_NATIVE_PROJECT_PACK_MANIFEST_V2.json"
FIXED_ZIP_DATETIME = (1980, 1, 1, 0, 0, 0)


def build(output: Path) -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source_names = manifest["files"]
    mapping = manifest["delivery_filename_map"]

    if set(mapping) != set(source_names):
        raise ValueError("delivery map must bind every and only manifest source file")
    delivery_names = [mapping[name] for name in source_names]
    if len(delivery_names) != len(set(delivery_names)):
        raise ValueError("delivery filenames must be unique")
    if not all(name.startswith("VERA_NV2A1_20260922_") for name in delivery_names):
        raise ValueError("delivery filename escaped the fresh NV2A1 namespace")
    if any(source == mapping[source] for source in source_names):
        raise ValueError("install-facing successor reused a source basename")

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
        for source in source_names:
            payload = (NATIVE / source).read_bytes()
            info = zipfile.ZipInfo(mapping[source], FIXED_ZIP_DATETIME)
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, payload)

    with zipfile.ZipFile(output, "r") as archive:
        if archive.namelist() != delivery_names:
            raise ValueError("ZIP member order/name mismatch")
        members = {
            name: hashlib.sha256(archive.read(name)).hexdigest()
            for name in delivery_names
        }

    return {
        "package": output.name,
        "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "bytes": output.stat().st_size,
        "members": members,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.output), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
