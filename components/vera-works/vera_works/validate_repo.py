from __future__ import annotations

import json
import sys
from pathlib import Path

from .contracts import validate_event
from .projections import available_balance, decision_queues
from .state_machine import validate_history


def load_events(path: Path) -> tuple[list[dict], list[str]]:
    events: list[dict] = []
    errors: list[str] = []
    for file_path in sorted(path.rglob("*.json")):
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{file_path}: unreadable JSON: {exc}")
            continue
        if not isinstance(data, dict):
            errors.append(f"{file_path}: event must be an object")
            continue
        event_errors = validate_event(data)
        if event_errors:
            errors.extend(f"{file_path}: {error}" for error in event_errors)
        events.append(data)
    return events, errors


def validate_path(path: Path) -> dict:
    events, errors = load_events(path)
    if not errors:
        errors.extend(validate_history(events))
    queues = decision_queues(events)
    try:
        balance = available_balance(events)
        balance_text = f"{balance:.2f}"
    except (ValueError, ArithmeticError) as exc:
        errors.append(str(exc))
        balance_text = "UNRESOLVED"
    resolved_holds = sum(1 for event in events if event.get("subject_type") == "hold" and event.get("to_state") == "RESOLVED")
    return {
        "errors": errors,
        "event_count": len(events),
        "available_balance": balance_text,
        "resolved_holds": resolved_holds,
        "queues": {name: [item["event_id"] for item in items] for name, items in queues.items()},
    }


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    target = Path(args[0] if args else "ops/events")
    report = validate_path(target)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
