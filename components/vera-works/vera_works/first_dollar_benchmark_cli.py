from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from vera_works.first_dollar_benchmark import (
    BenchmarkObservation,
    assess_observation,
    rank_first_dollar,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare first-dollar revenue experiments without starting a workload."
    )
    parser.add_argument("--input", required=True, help="JSON file containing observations")
    parser.add_argument("--now", help="Optional deterministic ISO-8601 evaluation timestamp")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    now = None
    if args.now:
        now = datetime.fromisoformat(args.now.replace("Z", "+00:00"))

    try:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        observations = [
            BenchmarkObservation.from_dict(item)
            for item in payload.get("observations", [])
        ]
        assessments = [assess_observation(item, now=now) for item in observations]
        ranking = rank_first_dollar(assessments)
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, indent=2, sort_keys=True))
        return 2

    print(json.dumps({
        "status": "OK",
        "external_effect_performed": False,
        "authorization_state": "NOT_AUTHORIZED",
        "assessments": [item.to_dict() for item in assessments],
        "first_dollar_ranking": [item.to_dict() for item in ranking],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
