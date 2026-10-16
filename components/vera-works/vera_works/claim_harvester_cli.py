from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .claim_harvester import (
    Assessment,
    CandidateObservation,
    ClaimLedger,
    harvest,
    load_wallets_from_environment,
)


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def load_candidates(path: Path) -> list[CandidateObservation]:
    raw = _load_json(path)
    if isinstance(raw, dict):
        raw = raw.get("candidates")
    if not isinstance(raw, list):
        raise ValueError("candidate feed must be an array or an object with a candidates array")
    return [CandidateObservation.from_dict(item) for item in raw]


def assessment_dict(item: Assessment) -> dict:
    result = asdict(item)
    result["state"] = item.state.value
    return result


def run(config_path: Path, candidates_path: Path, ledger_path: Path | None = None) -> list[Assessment]:
    config = _load_json(config_path)
    if not isinstance(config, dict):
        raise ValueError("config must be a JSON object")
    wallets = load_wallets_from_environment(config)
    candidates = load_candidates(candidates_path)
    results = harvest(candidates, wallets, now=datetime.now(timezone.utc))
    if ledger_path is not None:
        ledger = ClaimLedger(ledger_path)
        for result in results:
            ledger.append(result)
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate normalized claim candidates without performing any claim effect."
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--ledger", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        results = run(args.config, args.candidates, args.ledger)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, sort_keys=True))
        return 2
    print(
        json.dumps(
            {
                "status": "OK",
                "external_effect_performed": False,
                "assessments": [assessment_dict(item) for item in results],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
