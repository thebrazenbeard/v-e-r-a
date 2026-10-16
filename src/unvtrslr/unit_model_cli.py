from __future__ import annotations

import argparse
import json
from pathlib import Path

from .unit_model import (
    assign_source_units,
    fit_frozen_unit_model,
    frozen_unit_model_from_dict,
)
from .unit_registry import (
    LocalUnitEvidence,
)


def _load_evidence(
    path: str,
) -> list[LocalUnitEvidence]:
    rows: list[
        LocalUnitEvidence
    ] = []

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
                rows.append(
                    LocalUnitEvidence(
                        recording_id=str(
                            obj[
                                "recording_id"
                            ]
                        ),
                        source_id=str(
                            obj["source_id"]
                        ),
                        local_unit_id=str(
                            obj[
                                "local_unit_id"
                            ]
                        ),
                        vector=tuple(
                            float(v)
                            for v in obj[
                                "vector"
                            ]
                        ),
                    )
                )

            except KeyError as exc:
                raise ValueError(
                    f"line {line_number}: "
                    f"missing field "
                    f"{exc.args[0]!r}"
                ) from exc

    return rows


def _load_model(
    path: str,
):
    payload = json.loads(
        Path(path).read_text(
            encoding="utf-8",
        )
    )
    return frozen_unit_model_from_dict(
        payload
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Fit or apply a frozen "
            "cross-source acoustic unit model."
        )
    )
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    fit = subparsers.add_parser(
        "fit",
        help=(
            "fit a frozen model from "
            "cross-source local-unit evidence"
        ),
    )
    fit.add_argument("evidence")
    fit.add_argument(
        "--min-sources",
        type=int,
        default=2,
    )
    fit.add_argument(
        "--min-units-per-source",
        type=int,
        default=2,
    )
    fit.add_argument(
        "--cluster-distance",
        type=float,
        default=0.65,
    )
    fit.add_argument(
        "--scale-floor",
        type=float,
        default=0.25,
    )
    fit.add_argument(
        "--match-threshold",
        type=float,
        default=None,
    )
    fit.add_argument(
        "--ambiguity-margin",
        type=float,
        default=0.15,
    )

    assign = subparsers.add_parser(
        "assign",
        help=(
            "assign one new source's local "
            "units against a frozen model"
        ),
    )
    assign.add_argument("model")
    assign.add_argument("evidence")

    args = parser.parse_args()

    if args.command == "fit":
        model, registry = (
            fit_frozen_unit_model(
                _load_evidence(
                    args.evidence
                ),
                min_sources=(
                    args.min_sources
                ),
                min_units_per_source=(
                    args.min_units_per_source
                ),
                cluster_distance=(
                    args.cluster_distance
                ),
                scale_floor=(
                    args.scale_floor
                ),
                match_threshold=(
                    args.match_threshold
                ),
                ambiguity_margin=(
                    args.ambiguity_margin
                ),
            )
        )
        print(
            json.dumps(
                {
                    "model": (
                        model.to_dict()
                    ),
                    "training_registry": (
                        registry.to_dict()
                    ),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return

    model = _load_model(
        args.model
    )
    assignments = (
        assign_source_units(
            model,
            _load_evidence(
                args.evidence
            ),
        )
    )
    print(
        json.dumps(
            [
                assignment.__dict__
                for assignment
                in assignments
            ],
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
