from __future__ import annotations

import argparse
import json
from pathlib import Path

from .unit_registry import (
    LocalUnitEvidence,
    build_unit_registry,
)


def _load(path: str) -> list[LocalUnitEvidence]:
    rows: list[LocalUnitEvidence] = []
    with Path(path).open(
        "r",
        encoding="utf-8",
    ) as handle:
        for line_number, raw in enumerate(
            handle,
            1,
        ):
            raw = raw.strip()
            if not raw:
                continue

            obj = json.loads(raw)
            try:
                vector = tuple(
                    float(v)
                    for v in obj["vector"]
                )
                rows.append(
                    LocalUnitEvidence(
                        recording_id=str(
                            obj["recording_id"]
                        ),
                        source_id=str(
                            obj["source_id"]
                        ),
                        local_unit_id=str(
                            obj["local_unit_id"]
                        ),
                        vector=vector,
                    )
                )
            except KeyError as exc:
                raise ValueError(
                    f"line {line_number}: "
                    f"missing field {exc.args[0]!r}"
                ) from exc

    return rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Promote recording-local acoustic "
            "unit hypotheses only when recurrence "
            "survives cross-source contrast."
        )
    )
    parser.add_argument(
        "evidence",
        help=(
            "JSONL rows with recording_id, "
            "source_id, local_unit_id and vector"
        ),
    )
    parser.add_argument(
        "--min-sources",
        type=int,
        default=2,
    )
    parser.add_argument(
        "--min-units-per-source",
        type=int,
        default=2,
    )
    parser.add_argument(
        "--cluster-distance",
        type=float,
        default=0.65,
    )
    parser.add_argument(
        "--scale-floor",
        type=float,
        default=0.25,
    )
    args = parser.parse_args()

    result = build_unit_registry(
        _load(args.evidence),
        min_sources=args.min_sources,
        min_units_per_source=(
            args.min_units_per_source
        ),
        cluster_distance=args.cluster_distance,
        scale_floor=args.scale_floor,
    )
    print(
        json.dumps(
            result.to_dict(),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
