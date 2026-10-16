#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.on_theo_registry.validator import validate_repository


def _payload(report):
    findings = [asdict(item) for item in report.findings]
    errors = [item for item in findings if item["level"] == "error"]
    warnings = [item for item in findings if item["level"] == "warning"]
    return {"ok": report.ok, "errors": errors, "warnings": warnings, "findings": findings}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate On-Theo registry contracts.")
    parser.add_argument("--root", default=str(REPO_ROOT), help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args(argv)

    report = validate_repository(Path(args.root))
    payload = _payload(report)

    if args.json:
        print(json.dumps(payload, sort_keys=True))
    else:
        status = "PASS" if report.ok else "FAIL"
        print(f"registry validation: {status} ({len(report.errors)} errors, {len(report.warnings)} warnings)")
        for item in report.findings:
            print(f"{item.level.upper()} {item.code} {item.path}: {item.message}")

    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
