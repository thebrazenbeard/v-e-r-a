#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.on_theo_registry.rebase_preconditions import RebaseAuditError, audit_rebase_preconditions


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit divergent extension bases for referential precondition equivalence."
    )
    parser.add_argument("--root", default=str(REPO_ROOT))
    parser.add_argument("--subject", required=True)
    args = parser.parse_args()

    try:
        report = audit_rebase_preconditions(Path(args.root), args.subject)
    except RebaseAuditError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True))
        return 1

    ok = report["referential_preconditions_equivalent"]
    print(json.dumps({"ok": ok, "report": report}, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
