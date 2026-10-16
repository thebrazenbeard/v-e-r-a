#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import platform
import re
import sys
import tarfile
import unicodedata
from collections import Counter
from dataclasses import asdict
from pathlib import Path

from unvtrslr.multilingual_qualification import (
    EvaluationRecord,
    QualificationThresholds,
    TrainingExposure,
    evaluate_multilingual_holdout,
)
from unvtrslr.target_constructions import (
    TargetConstructionEpisode,
    fit_target_construction_model,
    render_semantic_sequence,
)


RUN_ID = "MASSIVE_V1_FIRST_REAL_CORPUS_20260922"
DATASET_URL = (
    "https://amazon-massive-nlu-dataset.s3.amazonaws.com/"
    "amazon-massive-dataset-1.0.tar.gz"
)
DATASET_VERSION = "1.0"
LOCALES = ("en-US", "fr-FR", "de-DE", "sw-KE", "tr-TR")
HOLDOUT_PER_LOCALE = 200
MODEL_LINEAGE = {
    "target_grounding_pr17_head":
        "897362fea8c8ccf6483e8594f581019e4b47a90d",
    "target_construction_pr18_head":
        "3a378d02e534d739bfeb3be64fed76dd4976b1b0",
    "multilingual_qualification_pr19_head":
        "cc72e50dced024a33731a690ca1225e6d9a5fe76",
}
ADAPTER_ID = "massive-v1-intent-ordered-slot-types-to-utterance-v1"
_SLOT_RE = re.compile(r"\[\s*([^:\]\[]+)\s*:")


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_tokens(text: str) -> tuple[str, ...]:
    normalized = unicodedata.normalize("NFC", str(text))
    return tuple(normalized.split())


def semantic_pattern(row: dict) -> tuple[str, ...]:
    atoms = [f"intent:{row['intent']}"]
    annot = str(row.get("annot_utt", ""))
    for slot in _SLOT_RE.findall(annot):
        atoms.append("slot:" + " ".join(slot.split()))
    return tuple(atoms)


def stable_holdout_key(locale: str, row_id: str) -> str:
    return hashlib.sha256(f"{locale}:{row_id}".encode("utf-8")).hexdigest()


def locate_member(tar: tarfile.TarFile, locale: str) -> tarfile.TarInfo:
    suffix = f"/data/{locale}.jsonl"
    matches = [
        member
        for member in tar.getmembers()
        if member.isfile()
        and (
            member.name.endswith(suffix)
            or member.name == f"data/{locale}.jsonl"
        )
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"expected one archive member for {locale}, found "
            f"{[member.name for member in matches]!r}"
        )
    return matches[0]


def read_locale_rows(tar: tarfile.TarFile, locale: str) -> list[dict]:
    member = locate_member(tar, locale)
    stream = tar.extractfile(member)
    if stream is None:
        raise RuntimeError(f"could not read {member.name}")
    rows = []
    for line_number, raw in enumerate(stream, 1):
        if not raw.strip():
            continue
        try:
            row = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            raise RuntimeError(
                f"{locale}:{line_number}: invalid JSON"
            ) from exc
        if row.get("locale") != locale:
            raise RuntimeError(
                f"{locale}:{line_number}: locale mismatch "
                f"{row.get('locale')!r}"
            )
        rows.append(row)
    return rows


def write_json(path: Path, obj) -> None:
    path.write_text(
        json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_jsonl(path: Path, rows) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(
                json.dumps(
                    row,
                    sort_keys=True,
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
                + "\n"
            )


def gzip_copy(path: Path) -> Path:
    output = path.with_suffix(path.suffix + ".gz")
    with path.open("rb") as source, output.open("wb") as raw_target:
        with gzip.GzipFile(
            filename="",
            mode="wb",
            fileobj=raw_target,
            compresslevel=9,
            mtime=0,
        ) as target:
            while True:
                chunk = source.read(1024 * 1024)
                if not chunk:
                    break
                target.write(chunk)
    return output


def record_file_hashes(outdir: Path) -> dict[str, dict]:
    result = {}
    for path in sorted(outdir.iterdir()):
        if path.is_file() and path.name != "artifact_hashes.json":
            result[path.name] = {
                "sha256": sha256_path(path),
                "bytes": path.stat().st_size,
            }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-tar", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--thresholds", required=True)
    args = parser.parse_args()

    dataset_tar = Path(args.dataset_tar).resolve()
    outdir = Path(args.out).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    thresholds_obj = json.loads(
        Path(args.thresholds).read_text(encoding="utf-8")
    )
    thresholds = QualificationThresholds(
        min_corpora=int(thresholds_obj["min_corpora"]),
        min_languages=int(thresholds_obj["min_languages"]),
        min_records_per_slice=int(
            thresholds_obj["min_records_per_slice"]
        ),
        min_coverage=float(thresholds_obj["min_coverage"]),
        min_exact_match=float(thresholds_obj["min_exact_match"]),
        min_token_similarity=float(
            thresholds_obj["min_token_similarity"]
        ),
        max_ambiguity_rate=float(
            thresholds_obj["max_ambiguity_rate"]
        ),
    )

    provenance = {
        "run_id": RUN_ID,
        "dataset_name": "MASSIVE",
        "dataset_version": DATASET_VERSION,
        "canonical_url": DATASET_URL,
        "dataset_sha256": sha256_path(dataset_tar),
        "dataset_bytes": dataset_tar.stat().st_size,
        "locales": list(LOCALES),
    }
    write_json(outdir / "dataset_provenance.json", provenance)

    training_exposures: list[TrainingExposure] = []
    evaluation_records: list[EvaluationRecord] = []
    construction_stats = {}
    dataset_counts = {}

    with tarfile.open(dataset_tar, "r:gz") as tar:
        for locale in LOCALES:
            rows = read_locale_rows(tar, locale)
            partitions = Counter(str(row["partition"]) for row in rows)
            dataset_counts[locale] = dict(sorted(partitions.items()))

            expected = {"train": 11514, "dev": 2033, "test": 2974}
            for partition, count in expected.items():
                if partitions.get(partition) != count:
                    raise RuntimeError(
                        f"{locale}: expected {count} {partition} rows, "
                        f"observed {partitions.get(partition)}"
                    )

            train_rows = [
                row for row in rows if row["partition"] == "train"
            ]
            test_rows = [
                row for row in rows if row["partition"] == "test"
            ]
            selected_test = sorted(
                test_rows,
                key=lambda row: stable_holdout_key(
                    locale,
                    str(row["id"]),
                ),
            )[:HOLDOUT_PER_LOCALE]

            namespace = sorted(
                {
                    atom
                    for row in train_rows
                    for atom in semantic_pattern(row)
                }
            )
            episodes = [
                TargetConstructionEpisode.build(
                    episode_id=f"{locale}:train:{row['id']}",
                    source_id=f"{locale}:worker:{row['worker_id']}",
                    semantic_atoms=semantic_pattern(row),
                    target_tokens=canonical_tokens(row["utt"]),
                )
                for row in train_rows
            ]

            model = None
            model_error = None
            try:
                model = fit_target_construction_model(
                    episodes,
                    target_language_id=locale,
                    semantic_atoms=namespace,
                    upstream_model_ids={
                        MODEL_LINEAGE["target_construction_pr18_head"],
                        ADAPTER_ID,
                    },
                    min_sources=2,
                    min_positive_per_source=1,
                )
            except ValueError as exc:
                model_error = str(exc)

            if model is None:
                frozen_count = 0
                semantic_pattern_count = 0
            else:
                frozen_count = len(model.constructions)
                semantic_pattern_count = len(
                    {row.semantic_atoms for row in model.constructions}
                )

            status_counts = Counter()
            candidate_count_hist = Counter()
            exact_candidate_hits = 0

            for row in train_rows:
                training_exposures.append(
                    TrainingExposure.build(
                        "massive",
                        DATASET_VERSION,
                        f"{locale}:train:{row['id']}",
                        locale,
                        str(row["id"]),
                        f"{locale}:worker:{row['worker_id']}",
                    )
                )

            for row in selected_test:
                pattern = semantic_pattern(row)
                references = [canonical_tokens(row["utt"])]
                if model is None:
                    candidates = []
                    system_status = "NO_CONSTRUCTION_MODEL_SURVIVED"
                else:
                    rendered = render_semantic_sequence(
                        model,
                        pattern,
                    )
                    candidates = list(rendered.realizations)
                    system_status = rendered.status

                status_counts[system_status] += 1
                candidate_count_hist[len(candidates)] += 1
                if any(candidate in references for candidate in candidates):
                    exact_candidate_hits += 1

                evaluation_records.append(
                    EvaluationRecord.build(
                        "massive",
                        DATASET_VERSION,
                        f"{locale}:test:{row['id']}",
                        locale,
                        str(row["id"]),
                        locale,
                        references,
                        candidates,
                        source_id=(
                            f"{locale}:worker:{row['worker_id']}"
                        ),
                        system_status=system_status,
                    )
                )

            construction_stats[locale] = {
                "train_rows": len(train_rows),
                "test_rows_total": len(test_rows),
                "test_rows_selected": len(selected_test),
                "semantic_namespace_size": len(namespace),
                "frozen_construction_count": frozen_count,
                "frozen_semantic_pattern_count": semantic_pattern_count,
                "model_fit_error": model_error,
                "prediction_status_counts": dict(
                    sorted(status_counts.items())
                ),
                "candidate_count_histogram": {
                    str(key): value
                    for key, value in sorted(
                        candidate_count_hist.items()
                    )
                },
                "exact_candidate_hits_pre_evaluator":
                    exact_candidate_hits,
            }

    training_path = outdir / "training_exposure.jsonl"
    predictions_path = outdir / "holdout_predictions.jsonl"

    write_jsonl(
        training_path,
        (asdict(row) for row in training_exposures),
    )
    write_jsonl(
        predictions_path,
        (asdict(row) for row in evaluation_records),
    )
    gzip_copy(training_path)
    gzip_copy(predictions_path)

    report = evaluate_multilingual_holdout(
        training_exposures,
        evaluation_records,
        regime="HELD_OUT_CONTENT",
        thresholds=thresholds,
    )
    write_json(outdir / "multilingual_report.json", report.to_dict())
    write_json(outdir / "construction_stats.json", construction_stats)
    write_json(outdir / "dataset_counts.json", dataset_counts)

    model_manifest = {
        "run_id": RUN_ID,
        "pr_head_sha": os.environ.get("UNVTRSLR_HEAD_SHA", "UNKNOWN"),
        "checked_out_sha": os.environ.get("GITHUB_SHA", "UNKNOWN"),
        "github_ref": os.environ.get("GITHUB_REF", "UNKNOWN"),
        "github_event_name": os.environ.get(
            "GITHUB_EVENT_NAME",
            "UNKNOWN",
        ),
        "lineage": MODEL_LINEAGE,
        "adapter_id": ADAPTER_ID,
        "construction_gate": {
            "min_sources": 2,
            "min_positive_per_source": 1,
        },
        "holdout_selection": {
            "records_per_locale": HOLDOUT_PER_LOCALE,
            "algorithm": "lowest SHA256(locale + ':' + id)",
        },
        "qualification_thresholds": thresholds_obj,
    }
    write_json(outdir / "model_manifest.json", model_manifest)

    environment = "\n".join(
        [
            f"python={sys.version.replace(chr(10), ' ')}",
            f"platform={platform.platform()}",
            f"executable={sys.executable}",
        ]
    )
    (outdir / "environment.txt").write_text(
        environment + "\n",
        encoding="utf-8",
    )

    receipt = {
        "run_id": RUN_ID,
        "status": report.status,
        "claim_ceiling": (
            "MASSIVE_V1_TARGET_CONSTRUCTION_GENERALIZATION_"
            "WITHIN_DECLARED_OPERATIONAL_ADAPTER"
        ),
        "dataset_sha256": provenance["dataset_sha256"],
        "pr_head_sha": model_manifest["pr_head_sha"],
        "checked_out_sha": model_manifest["checked_out_sha"],
        "evaluation_record_count": len(evaluation_records),
        "training_record_count": len(training_exposures),
        "languages": list(LOCALES),
        "multilingual_report_status": report.status,
        "leakage_violations": list(report.leakage_violations),
        "threshold_failure_count": len(report.threshold_failures),
    }
    write_json(outdir / "run_receipt.json", receipt)

    write_json(
        outdir / "artifact_hashes.json",
        record_file_hashes(outdir),
    )

    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
