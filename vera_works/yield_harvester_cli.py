from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .yield_harvester import (
    YieldAssessment,
    YieldCandidate,
    YieldLedger,
    YieldPolicy,
    broker_plan,
    harvest,
    load_resources_from_environment,
)


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def load_candidates(path: Path) -> list[YieldCandidate]:
    raw = _load_json(path)
    if isinstance(raw, dict):
        raw = raw.get("candidates")
    if not isinstance(raw, list):
        raise ValueError("candidate feed must be an array or an object with a candidates array")
    return [YieldCandidate.from_dict(item) for item in raw]


def assessment_dict(item: YieldAssessment) -> dict:
    result = asdict(item)
    result["reward_model"] = item.reward_model.value
    result["state"] = item.state.value
    return result


def run(
    config_path: Path,
    candidates_path: Path,
    ledger_path: Path | None = None,
) -> tuple[list[YieldAssessment], list[dict]]:
    config = _load_json(config_path)
    if not isinstance(config, dict):
        raise ValueError("config must be a JSON object")
    resources = load_resources_from_environment(config)
    policy_raw = config.get("policy")
    if policy_raw is not None and not isinstance(policy_raw, dict):
        raise ValueError("policy must be a JSON object")
    policy = YieldPolicy.from_dict(policy_raw)
    candidates = load_candidates(candidates_path)
    results = harvest(candidates, resources, policy, now=datetime.now(timezone.utc))
    if ledger_path is not None:
        ledger = YieldLedger(ledger_path)
        for result in results:
            ledger.append(result)
    plan = [asdict(item) | {"reward_model": item.reward_model.value} for item in broker_plan(results)]
    return results, plan


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Rank customerless yield mechanisms without starting any workload."
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--ledger", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        results, plan = run(args.config, args.candidates, args.ledger)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, sort_keys=True))
        return 2
    print(
        json.dumps(
            {
                "status": "OK",
                "external_effect_performed": False,
                "assessments": [assessment_dict(item) for item in results],
                "broker_plan": plan,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
