from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .calibration_qualification import qualified_source_profile_from_dict
from .ordered_relations import ordered_relation_model_from_dict
from .target_constructions import (
    TargetConstructionEpisode,
    fit_target_construction_model,
    render_semantic_sequence,
    target_construction_model_from_dict,
    translate_qualified_construction,
)
from .target_grounding import target_grounding_model_from_dict
from .translator import reference_translator_model_from_dict
from .unit_registry import LocalUnitEvidence


def _load_json(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_translator(path: str):
    obj = _load_json(path)
    if "model" in obj:
        obj = obj["model"]
    return reference_translator_model_from_dict(obj)


def _load_target(path: str):
    obj = _load_json(path)
    if "target_model" in obj:
        obj = obj["target_model"]
    return target_grounding_model_from_dict(obj)


def _load_construction(path: str):
    obj = _load_json(path)
    if "construction_model" in obj:
        obj = obj["construction_model"]
    return target_construction_model_from_dict(obj)


def _load_ordered(path: str | None):
    if path is None:
        return None
    obj = _load_json(path)
    if "ordered_model" in obj:
        obj = obj["ordered_model"]
    return ordered_relation_model_from_dict(obj)


def _load_qualified(path: str, translator_model):
    obj = _load_json(path)
    if "qualified_source_profile" in obj:
        obj = obj["qualified_source_profile"]
    return qualified_source_profile_from_dict(obj, translator_model)


def _load_episodes(path: str) -> list[TargetConstructionEpisode]:
    rows: list[TargetConstructionEpisode] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            raw = raw.strip()
            if not raw:
                continue
            obj = json.loads(raw)
            try:
                rows.append(
                    TargetConstructionEpisode.build(
                        obj["episode_id"],
                        obj["source_id"],
                        obj["semantic_atoms"],
                        obj["target_tokens"],
                    )
                )
            except KeyError as exc:
                raise ValueError(
                    f"line {line_number}: missing field {exc.args[0]!r}"
                ) from exc
    return rows


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


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Learn multiword target constructions and target-side ordering "
            "from grounded demonstrations."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    fit = subparsers.add_parser(
        "fit",
        help="fit multiword constructions against an exact learned target model",
    )
    fit.add_argument("translator_model")
    fit.add_argument("target_model")
    fit.add_argument("episodes")
    fit.add_argument("--ordered-model")
    fit.add_argument("--min-sources", type=int, default=2)
    fit.add_argument("--min-positive-per-source", type=int, default=2)

    render = subparsers.add_parser(
        "render",
        help="render one ordered operational semantic sequence",
    )
    render.add_argument("construction_model")
    render.add_argument("semantic_atoms", nargs="+")

    translate = subparsers.add_parser(
        "translate-qualified",
        help=(
            "derive an ordered operational sequence from qualified acoustic "
            "evidence and realize it through a learned multiword construction"
        ),
    )
    translate.add_argument("translator_model")
    translate.add_argument("qualified_profile")
    translate.add_argument("target_model")
    translate.add_argument("construction_model")
    translate.add_argument("evidence")

    args = parser.parse_args()

    if args.command == "fit":
        translator = _load_translator(args.translator_model)
        target = _load_target(args.target_model)

        if translator.model_id not in set(target.upstream_model_ids):
            raise ValueError(
                "target grounding model is not bound to this translator model"
            )

        upstream_ids = {
            translator.model_id,
            target.model_id,
        }

        ordered = _load_ordered(args.ordered_model)
        if ordered is not None:
            if ordered.translator_model_id != translator.model_id:
                raise ValueError(
                    "ordered model belongs to a different translator model"
                )
            if ordered.acoustic_model_id != translator.acoustic_model.model_id:
                raise ValueError(
                    "ordered model belongs to a different acoustic model"
                )
            upstream_ids.add(ordered.model_id)

        construction = fit_target_construction_model(
            _load_episodes(args.episodes),
            target_language_id=target.target_language_id,
            semantic_atoms=target.semantic_atoms,
            upstream_model_ids=upstream_ids,
            min_sources=args.min_sources,
            min_positive_per_source=args.min_positive_per_source,
        )
        print(
            json.dumps(
                {"construction_model": construction.to_dict()},
                indent=2,
                sort_keys=True,
            )
        )
        return

    if args.command == "render":
        construction = _load_construction(args.construction_model)
        result = render_semantic_sequence(
            construction,
            args.semantic_atoms,
        )
        print(json.dumps(asdict(result), indent=2, sort_keys=True))
        return

    translator = _load_translator(args.translator_model)
    qualified = _load_qualified(args.qualified_profile, translator)
    target = _load_target(args.target_model)
    construction = _load_construction(args.construction_model)

    required = {translator.model_id, target.model_id}
    if not required.issubset(set(construction.upstream_model_ids)):
        raise ValueError(
            "construction model is not bound to this translator/target lineage"
        )
    if construction.target_language_id != target.target_language_id:
        raise ValueError(
            "construction and target grounding models use different target languages"
        )

    result = translate_qualified_construction(
        translator,
        qualified,
        construction,
        _load_evidence(args.evidence),
    )
    print(json.dumps(asdict(result), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
