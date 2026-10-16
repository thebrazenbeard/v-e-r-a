#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.on_theo_registry.materializer import MaterializationError, materialize_rehearsal


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Rehearse deterministic On-Theo registry materialization without mutating the source tree."
    )
    parser.add_argument("--root", default=str(REPO_ROOT), help="On-Theo source repository root")
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Optional empty directory outside the source repository for rehearsal output",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = materialize_rehearsal(
            Path(args.root),
            Path(args.output_dir) if args.output_dir else None,
        )
    except MaterializationError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True))
        return 1

    print(json.dumps({"ok": True, "receipt": result.receipt}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
