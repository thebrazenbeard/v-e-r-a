"""Bounded local CLI for Mosaic -> Vera plurality projection and readback.

Examples:
  python -m integration.plural_cognition_cli compose --receipt input.json \
    --participants participants.json --output projection.json
  python -m integration.plural_cognition_cli verify --projection projection.json
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from .plural_cognition import (
    Participant, PluralityProtocolError,
    compose_mosaic_plurality, verify_mosaic_plurality,
)

_MAX_BYTES = 1024 * 1024


def _load(path: Path) -> object:
    if not path.is_file() or path.is_symlink() or path.stat().st_size > _MAX_BYTES:
        raise PluralityProtocolError("input file missing, symlinked or oversized")
    return json.loads(path.read_text(encoding="utf-8"))


def _save_new(path: Path, value: dict) -> None:
    if path.exists() or path.is_symlink() or not path.parent.is_dir():
        raise PluralityProtocolError("output destination already exists or lacks a directory")
    payload = (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False)
               + "\n").encode("utf-8")
    if len(payload) > _MAX_BYTES:
        raise PluralityProtocolError("output too large")
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def run(argv: list[str] | None = None) -> dict:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    build = sub.add_parser("compose")
    build.add_argument("--receipt", required=True, type=Path)
    build.add_argument("--participants", required=True, type=Path)
    build.add_argument("--output", required=True, type=Path)
    verify = sub.add_parser("verify")
    verify.add_argument("--projection", required=True, type=Path)
    args = parser.parse_args(argv)
    if args.action == "verify":
        record = _load(args.projection)
        verify_mosaic_plurality(record)
        return {"status": "PROJECTION_READBACK_VALID",
                "projection_sha256": record["projection_sha256"],
                "source_mosaic_receipt_sha256": record["mosaic_receipt_sha256"],
                "identity_authenticated": False, "effects_executed": False}
    receipt = _load(args.receipt)
    directory = _load(args.participants)
    if type(directory) is not dict or len(directory) > 64:
        raise PluralityProtocolError("invalid participant directory")
    if any(type(item) is not dict for item in directory.values()):
        raise PluralityProtocolError("invalid participant structure")
    try:
        members = {key: Participant(**value) for key, value in directory.items()}
    except (ValueError, TypeError) as exc:
        raise PluralityProtocolError("invalid participant declarations") from exc
    result = compose_mosaic_plurality(receipt, members)
    _save_new(args.output, result)
    return {"status": "ADVISORY_PLURALITY_RECORDED",
            "projection_sha256": result["projection_sha256"],
            "alignment": result["alignment"],
            "mosaic_decision_status": result["mosaic_decision_status"],
            "identity_authenticated": False, "effects_executed": False}


def main() -> int:
    try:
        print(json.dumps(run(), sort_keys=True))
        return 0
    except (PluralityProtocolError, OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"status": "HELD", "reason": str(exc)[:300],
                          "effects_executed": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
