from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .calibration_qualification import (
    fit_and_qualify_source_profile,
    qualified_source_profile_from_dict,
    translate_qualified_query,
)
from .translator import reference_translator_model_from_dict
from .unit_registry import LocalUnitEvidence


def _row(obj: dict) -> LocalUnitEvidence:
    return LocalUnitEvidence(
        recording_id=str(obj["recording_id"]),
        source_id=str(obj["source_id"]),
        local_unit_id=str(obj["local_unit_id"]),
        vector=tuple(float(value) for value in obj["vector"]),
    )


def _load_evidence(path: str) -> list[LocalUnitEvidence]:
    rows: list[LocalUnitEvidence] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                rows.append(_row(json.loads(raw)))
            except KeyError as exc:
                raise ValueError(
                    f"line {line_number}: missing field {exc.args[0]!r}"
                ) from exc
    return rows


def _load_model(path: str):
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    if "model" in obj:
        obj = obj["model"]
    return reference_translator_model_from_dict(obj)


def _load_qualified(path: str, model):
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    if "qualified_source_profile" in obj:
        obj = obj["qualified_source_profile"]
    return qualified_source_profile_from_dict(obj, model)


def _load_renderer(path: str | None) -> dict[str, str] | None:
    if path is None:
        return None
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(obj, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in obj.items()
    ):
        raise ValueError(
            "renderer must be a JSON object mapping relation IDs to strings"
        )
    return obj


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Qualify source calibration on held-out acoustic evidence "
            "before translation."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    qualify = subparsers.add_parser(
        "qualify",
        help=(
            "fit source calibration from one evidence file and qualify it "
            "against a separate held-out evidence file"
        ),
    )
    qualify.add_argument("model")
    qualify.add_argument("calibration_evidence")
    qualify.add_argument("qualification_evidence")
    qualify.add_argument("--min-supported-fraction", type=float, default=0.80)
    qualify.add_argument("--min-distinct-global-units", type=int, default=3)

    translate = subparsers.add_parser(
        "translate",
        help="translate query evidence only through a held-out-qualified profile",
    )
    translate.add_argument("model")
    translate.add_argument("qualified_profile")
    translate.add_argument("query_evidence")
    translate.add_argument("--renderer")

    args = parser.parse_args()
    model = _load_model(args.model)

    if args.command == "qualify":
        qualified = fit_and_qualify_source_profile(
            model,
            _load_evidence(args.calibration_evidence),
            _load_evidence(args.qualification_evidence),
            min_supported_fraction=args.min_supported_fraction,
            min_distinct_global_units=args.min_distinct_global_units,
        )
        print(
            json.dumps(
                {"qualified_source_profile": qualified.to_dict()},
                indent=2,
                sort_keys=True,
            )
        )
        return

    qualified = _load_qualified(args.qualified_profile, model)
    result = translate_qualified_query(
        model,
        qualified,
        _load_evidence(args.query_evidence),
        renderer=_load_renderer(args.renderer),
    )
    print(json.dumps(asdict(result), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
