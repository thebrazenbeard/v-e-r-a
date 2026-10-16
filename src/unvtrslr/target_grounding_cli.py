from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .calibration_qualification import qualified_source_profile_from_dict
from .ordered_relations import (
    ordered_relation_model_from_dict,
    translate_qualified_sequence,
)
from .target_grounding import (
    NonEquivalenceObservation,
    TargetGroundingEpisode,
    fit_target_grounding_model,
    render_relations,
    target_grounding_model_from_dict,
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


def _load_ordered(path: str):
    obj = _load_json(path)
    if "ordered_model" in obj:
        obj = obj["ordered_model"]
    return ordered_relation_model_from_dict(obj)


def _load_target(path: str):
    obj = _load_json(path)
    if "target_model" in obj:
        obj = obj["target_model"]
    return target_grounding_model_from_dict(obj)


def _load_qualified(path: str, translator_model):
    obj = _load_json(path)
    if "qualified_source_profile" in obj:
        obj = obj["qualified_source_profile"]
    return qualified_source_profile_from_dict(obj, translator_model)


def _load_target_episodes(path: str) -> list[TargetGroundingEpisode]:
    rows: list[TargetGroundingEpisode] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            raw = raw.strip()
            if not raw:
                continue
            obj = json.loads(raw)
            try:
                rows.append(
                    TargetGroundingEpisode.build(
                        obj["episode_id"],
                        obj["source_id"],
                        obj["target_tokens"],
                        obj["context"],
                    )
                )
            except KeyError as exc:
                raise ValueError(
                    f"line {line_number}: missing field {exc.args[0]!r}"
                ) from exc
    return rows


def _load_non_equivalence(
    path: str | None,
) -> list[NonEquivalenceObservation]:
    if path is None:
        return []
    rows: list[NonEquivalenceObservation] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            raw = raw.strip()
            if not raw:
                continue
            obj = json.loads(raw)
            try:
                rows.append(
                    NonEquivalenceObservation.build(
                        obj["observation_id"],
                        obj["source_id"],
                        obj["atom"],
                        obj["scope_id"],
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
            "Learn target-language realization from grounded demonstrations "
            "and apply it to qualified UNVTRSLR outputs."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    fit = subparsers.add_parser(
        "fit",
        help="fit target-language grounding against an exact translator lineage",
    )
    fit.add_argument("translator_model")
    fit.add_argument("target_episodes")
    fit.add_argument("--target-language-id", required=True)
    fit.add_argument("--ordered-model")
    fit.add_argument("--non-equivalence")
    fit.add_argument("--min-positive-sources", type=int, default=2)
    fit.add_argument("--min-positive-per-source", type=int, default=2)
    fit.add_argument("--min-non-equivalence-sources", type=int, default=2)
    fit.add_argument("--min-non-equivalence-per-source", type=int, default=2)

    render = subparsers.add_parser(
        "render-atoms",
        help="render opaque operational atoms through a learned target model",
    )
    render.add_argument("target_model")
    render.add_argument("atoms", nargs="+")

    translate = subparsers.add_parser(
        "translate-qualified",
        help=(
            "run qualified acoustic/ordered translation and then apply the "
            "learned target-language model"
        ),
    )
    translate.add_argument("translator_model")
    translate.add_argument("qualified_profile")
    translate.add_argument("ordered_model")
    translate.add_argument("target_model")
    translate.add_argument("evidence")

    args = parser.parse_args()

    if args.command == "fit":
        translator = _load_translator(args.translator_model)
        semantic_atoms = {
            relation.atom
            for relation in translator.semantic_relations
        }
        upstream_ids = {translator.model_id}

        if args.ordered_model:
            ordered = _load_ordered(args.ordered_model)
            if ordered.translator_model_id != translator.model_id:
                raise ValueError(
                    "ordered model belongs to a different translator model"
                )
            if ordered.acoustic_model_id != translator.acoustic_model.model_id:
                raise ValueError(
                    "ordered model belongs to a different acoustic model"
                )
            semantic_atoms.update(
                relation.atom
                for relation in ordered.relations
            )
            upstream_ids.add(ordered.model_id)

        target = fit_target_grounding_model(
            _load_target_episodes(args.target_episodes),
            target_language_id=args.target_language_id,
            semantic_atoms=semantic_atoms,
            upstream_model_ids=upstream_ids,
            non_equivalence_observations=_load_non_equivalence(
                args.non_equivalence
            ),
            min_positive_sources=args.min_positive_sources,
            min_positive_per_source=args.min_positive_per_source,
            min_non_equivalence_sources=args.min_non_equivalence_sources,
            min_non_equivalence_per_source=args.min_non_equivalence_per_source,
        )
        print(
            json.dumps(
                {"target_model": target.to_dict()},
                indent=2,
                sort_keys=True,
            )
        )
        return

    if args.command == "render-atoms":
        target = _load_target(args.target_model)
        result = render_relations(target, args.atoms)
        print(json.dumps(asdict(result), indent=2, sort_keys=True))
        return

    translator = _load_translator(args.translator_model)
    qualified = _load_qualified(args.qualified_profile, translator)
    ordered = _load_ordered(args.ordered_model)
    target = _load_target(args.target_model)

    expected_upstream = {translator.model_id, ordered.model_id}
    if not expected_upstream.issubset(set(target.upstream_model_ids)):
        raise ValueError(
            "target model is not bound to this translator/ordered-model lineage"
        )

    structured = translate_qualified_sequence(
        translator,
        qualified,
        ordered,
        _load_evidence(args.evidence),
    )
    atoms = tuple(
        [
            *structured.lexical.relations,
            *structured.ordered.relations,
        ]
    )
    target_result = render_relations(target, atoms)

    print(
        json.dumps(
            {
                "operational_translation": asdict(structured),
                "target_rendering": asdict(target_result),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
