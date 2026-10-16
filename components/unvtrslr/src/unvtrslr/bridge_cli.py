from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .bridge import BridgeLearner, Episode


def _load_episodes(path: str) -> list[Episode]:
    rows: list[Episode] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            raw = raw.strip()
            if not raw:
                continue
            obj = json.loads(raw)
            try:
                rows.append(
                    Episode.build(
                        obj["signal"],
                        obj["context"],
                        source=obj.get("source"),
                    )
                )
            except KeyError as exc:
                raise ValueError(f"line {line_number}: missing required field {exc.args[0]!r}") from exc
    return rows


def _load_renderer(path: str | None) -> dict[str, str] | None:
    if path is None:
        return None
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(obj, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in obj.items()):
        raise ValueError("renderer must be a JSON object mapping context atom IDs to strings")
    return obj


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Learn an operational bridge from ambiguous JSONL interaction episodes."
    )
    parser.add_argument("episodes", help="JSONL file with signal/context arrays and optional source")
    parser.add_argument("signal", nargs="+", help="opaque signal unit(s) to interpret")
    parser.add_argument("--renderer", help="optional JSON mapping from opaque context atoms to target strings")
    parser.add_argument("--probe", action="store_true", help="also emit a discriminating-probe suggestion per token")
    args = parser.parse_args()

    learner = BridgeLearner().fit(_load_episodes(args.episodes))
    renderer = _load_renderer(args.renderer)
    result = asdict(learner.translate(args.signal, renderer=renderer))
    if args.probe:
        result["probe_suggestions"] = [asdict(learner.suggest_probe(token)) for token in args.signal]
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
