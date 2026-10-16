from __future__ import annotations

import argparse
import json
from pathlib import Path

from .multilingual_qualification import (
    EvaluationRecord,
    QualificationThresholds,
    TrainingExposure,
    audit_holdout_split,
    evaluate_multilingual_holdout,
)


def _load_training(path: str) -> list[TrainingExposure]:
    rows: list[TrainingExposure] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            raw = raw.strip()
            if not raw:
                continue
            obj = json.loads(raw)
            try:
                rows.append(
                    TrainingExposure.build(
                        obj["corpus_id"],
                        obj["corpus_version"],
                        obj["record_id"],
                        obj["language_id"],
                        obj["content_id"],
                        obj.get("source_id"),
                    )
                )
            except KeyError as exc:
                raise ValueError(
                    f"training line {line_number}: missing field {exc.args[0]!r}"
                ) from exc
    return rows


def _load_evaluation(path: str) -> list[EvaluationRecord]:
    rows: list[EvaluationRecord] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, 1):
            raw = raw.strip()
            if not raw:
                continue
            obj = json.loads(raw)
            try:
                rows.append(
                    EvaluationRecord.build(
                        obj["corpus_id"],
                        obj["corpus_version"],
                        obj["record_id"],
                        obj["language_id"],
                        obj["content_id"],
                        obj["target_language_id"],
                        obj["references"],
                        obj.get("candidates", []),
                        source_id=obj.get("source_id"),
                        system_status=obj.get("system_status", "UNSPECIFIED"),
                    )
                )
            except KeyError as exc:
                raise ValueError(
                    f"evaluation line {line_number}: missing field {exc.args[0]!r}"
                ) from exc
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Audit and evaluate multilingual held-out corpora without allowing "
            "training-language/source/content leakage to masquerade as transfer."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit = subparsers.add_parser(
        "audit",
        help="audit a proposed train/holdout split before scoring predictions",
    )
    audit.add_argument("training_exposure")
    audit.add_argument("evaluation")
    audit.add_argument("--regime", required=True)

    evaluate = subparsers.add_parser(
        "evaluate",
        help="score a leakage-audited multilingual holdout with explicit thresholds",
    )
    evaluate.add_argument("training_exposure")
    evaluate.add_argument("evaluation")
    evaluate.add_argument("--regime", required=True)
    evaluate.add_argument("--min-corpora", type=int, required=True)
    evaluate.add_argument("--min-languages", type=int, required=True)
    evaluate.add_argument("--min-records-per-slice", type=int, required=True)
    evaluate.add_argument("--min-coverage", type=float, required=True)
    evaluate.add_argument("--min-exact-match", type=float, required=True)
    evaluate.add_argument("--min-token-similarity", type=float, required=True)
    evaluate.add_argument("--max-ambiguity-rate", type=float, required=True)

    args = parser.parse_args()
    training = _load_training(args.training_exposure)
    evaluation = _load_evaluation(args.evaluation)

    if args.command == "audit":
        violations = audit_holdout_split(
            training,
            evaluation,
            regime=args.regime,
        )
        print(
            json.dumps(
                {
                    "regime": args.regime,
                    "status": (
                        "LEAKAGE_DETECTED"
                        if violations
                        else "HOLDOUT_SPLIT_AUDIT_PASS"
                    ),
                    "violations": violations,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return

    thresholds = QualificationThresholds(
        min_corpora=args.min_corpora,
        min_languages=args.min_languages,
        min_records_per_slice=args.min_records_per_slice,
        min_coverage=args.min_coverage,
        min_exact_match=args.min_exact_match,
        min_token_similarity=args.min_token_similarity,
        max_ambiguity_rate=args.max_ambiguity_rate,
    )
    report = evaluate_multilingual_holdout(
        training,
        evaluation,
        regime=args.regime,
        thresholds=thresholds,
    )
    print(
        json.dumps(
            report.to_dict(),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
