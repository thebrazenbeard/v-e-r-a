from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .bridge import Episode
from .calibration_qualification import qualified_source_profile_from_dict
from .ordered_relations import (
    fit_ordered_relation_model,
    ordered_relation_model_from_dict,
    translate_ordered_sequence,
    translate_qualified_sequence,
)
from .translator import reference_translator_model_from_dict
from .unit_registry import LocalUnitEvidence


def _load_json(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_translator(path: str):
    obj = _load_json(path)
    if "model" in obj:
        obj = obj["model"]
    return reference_translator_model_from_dict(obj)


def _load_ordered_model(path: str):
    obj = _load_json(path)
    if "ordered_model" in obj:
        obj = obj["ordered_model"]
    return ordered_relation_model_from_dict(obj)


def _load_qualified(path: str, translator_model):
    obj = _load_json(path)
    if "qualified_source_profile" in obj:
        obj = obj["qualified_source_profile"]
    return qualified_source_profile_from_dict(obj, translator_model)


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


def _load_episodes(path: str) -> list[Episode]:
    episodes: list[Episode] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            raw = raw.strip()
            if not raw:
                continue
            obj = json.loads(raw)
            try:
                episodes.append(
                    Episode.build(
                        obj["signal"],
                        obj["context"],
                        source=obj.get("source"),
                    )
                )
            except KeyError as exc:
                raise ValueError(
                    f"line {line_number}: missing field {exc.args[0]!r}"
                ) from exc
    return episodes


def _load_renderer(path: str | None) -> dict[str, str] | None:
    if path is None:
        return None
    obj = _load_json(path)
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
        description="Fit and apply order-sensitive UNVTRSLR relations."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    fit = subparsers.add_parser(
        "fit",
        help="fit AB-vs-BA operational relations over frozen global unit IDs",
    )
    fit.add_argument("translator_model")
    fit.add_argument("episodes")
    fit.add_argument("--min-ordered-support", type=int, default=4)
    fit.add_argument("--min-reverse-support", type=int, default=4)
    fit.add_argument("--min-order-source-coverage", type=int, default=2)
    fit.add_argument("--min-positive-sources", type=int, default=2)
    fit.add_argument("--min-positive-per-source", type=int, default=2)

    tokens = subparsers.add_parser(
        "translate-tokens",
        help="translate ordered global-unit IDs with a frozen order model",
    )
    tokens.add_argument("ordered_model")
    tokens.add_argument("signal", nargs="+")
    tokens.add_argument("--renderer")

    qualified = subparsers.add_parser(
        "translate-qualified",
        help=(
            "run held-out-qualified acoustic translation and order-sensitive "
            "translation over the resulting global unit sequence"
        ),
    )
    qualified.add_argument("translator_model")
    qualified.add_argument("qualified_profile")
    qualified.add_argument("ordered_model")
    qualified.add_argument("evidence")
    qualified.add_argument("--renderer")

    args = parser.parse_args()

    if args.command == "fit":
        translator = _load_translator(args.translator_model)
        vocabulary = {
            prototype.global_unit_id
            for prototype in translator.acoustic_model.prototypes
        }
        ordered_model = fit_ordered_relation_model(
            _load_episodes(args.episodes),
            translator_model_id=translator.model_id,
            acoustic_model_id=translator.acoustic_model.model_id,
            valid_token_ids=vocabulary,
            min_ordered_support=args.min_ordered_support,
            min_reverse_support=args.min_reverse_support,
            min_order_source_coverage=args.min_order_source_coverage,
            min_positive_sources=args.min_positive_sources,
            min_positive_per_source=args.min_positive_per_source,
        )
        print(
            json.dumps(
                {"ordered_model": ordered_model.to_dict()},
                indent=2,
                sort_keys=True,
            )
        )
        return

    renderer = _load_renderer(args.renderer)

    if args.command == "translate-tokens":
        ordered_model = _load_ordered_model(args.ordered_model)
        result = translate_ordered_sequence(
            ordered_model,
            args.signal,
            renderer=renderer,
        )
        print(json.dumps(asdict(result), indent=2, sort_keys=True))
        return

    translator = _load_translator(args.translator_model)
    qualified_source = _load_qualified(
        args.qualified_profile,
        translator,
    )
    ordered_model = _load_ordered_model(args.ordered_model)
    result = translate_qualified_sequence(
        translator,
        qualified_source,
        ordered_model,
        _load_evidence(args.evidence),
        renderer=renderer,
    )
    print(json.dumps(asdict(result), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
