from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable, Sequence


_VALID_REGIMES = {
    "HELD_OUT_LANGUAGE",
    "HELD_OUT_SOURCE",
    "HELD_OUT_CONTENT",
    "HELD_OUT_LANGUAGE_AND_CONTENT",
    "HELD_OUT_ALL",
    "PARALLEL_LANGUAGE_TRANSFER",
}

_QUALIFICATION_CLAIM_CEILING = (
    "MULTILINGUAL_HELDOUT_BEHAVIOR_WITHIN_DECLARED_CORPORA_AND_SPLITS"
)


@dataclass(frozen=True)
class TrainingExposure:
    corpus_id: str
    corpus_version: str
    record_id: str
    language_id: str
    source_id: str | None
    content_id: str

    @classmethod
    def build(
        cls,
        corpus_id: str,
        corpus_version: str,
        record_id: str,
        language_id: str,
        content_id: str,
        source_id: str | None = None,
    ) -> "TrainingExposure":
        required = {
            "corpus_id": corpus_id,
            "corpus_version": corpus_version,
            "record_id": record_id,
            "language_id": language_id,
            "content_id": content_id,
        }
        empty = [name for name, value in required.items() if not str(value)]
        if empty:
            raise ValueError(f"training exposure fields must not be empty: {empty}")
        return cls(
            corpus_id=str(corpus_id),
            corpus_version=str(corpus_version),
            record_id=str(record_id),
            language_id=str(language_id),
            source_id=None if source_id is None else str(source_id),
            content_id=str(content_id),
        )


@dataclass(frozen=True)
class EvaluationRecord:
    corpus_id: str
    corpus_version: str
    record_id: str
    language_id: str
    source_id: str | None
    content_id: str
    target_language_id: str
    references: tuple[tuple[str, ...], ...]
    candidates: tuple[tuple[str, ...], ...]
    system_status: str

    @classmethod
    def build(
        cls,
        corpus_id: str,
        corpus_version: str,
        record_id: str,
        language_id: str,
        content_id: str,
        target_language_id: str,
        references: Iterable[Iterable[str]],
        candidates: Iterable[Iterable[str]],
        *,
        source_id: str | None = None,
        system_status: str = "UNSPECIFIED",
    ) -> "EvaluationRecord":
        required = {
            "corpus_id": corpus_id,
            "corpus_version": corpus_version,
            "record_id": record_id,
            "language_id": language_id,
            "content_id": content_id,
            "target_language_id": target_language_id,
            "system_status": system_status,
        }
        empty = [name for name, value in required.items() if not str(value)]
        if empty:
            raise ValueError(f"evaluation fields must not be empty: {empty}")

        refs = tuple(tuple(str(token) for token in row) for row in references)
        cands = tuple(tuple(str(token) for token in row) for row in candidates)
        if not refs or any(not row for row in refs):
            raise ValueError("evaluation record requires nonempty reference sequences")
        if any(any(not token for token in row) for row in refs):
            raise ValueError("reference tokens must not be empty")
        if any(not row for row in cands):
            raise ValueError("candidate sequences must not be empty")
        if any(any(not token for token in row) for row in cands):
            raise ValueError("candidate tokens must not be empty")

        refs = tuple(sorted(set(refs)))
        cands = tuple(sorted(set(cands)))
        return cls(
            corpus_id=str(corpus_id),
            corpus_version=str(corpus_version),
            record_id=str(record_id),
            language_id=str(language_id),
            source_id=None if source_id is None else str(source_id),
            content_id=str(content_id),
            target_language_id=str(target_language_id),
            references=refs,
            candidates=cands,
            system_status=str(system_status),
        )


@dataclass(frozen=True)
class QualificationThresholds:
    min_corpora: int
    min_languages: int
    min_records_per_slice: int
    min_coverage: float
    min_exact_match: float
    min_token_similarity: float
    max_ambiguity_rate: float

    def validate(self) -> None:
        if self.min_corpora < 1:
            raise ValueError("min_corpora must be >= 1")
        if self.min_languages < 1:
            raise ValueError("min_languages must be >= 1")
        if self.min_records_per_slice < 1:
            raise ValueError("min_records_per_slice must be >= 1")
        for name, value in (
            ("min_coverage", self.min_coverage),
            ("min_exact_match", self.min_exact_match),
            ("min_token_similarity", self.min_token_similarity),
            ("max_ambiguity_rate", self.max_ambiguity_rate),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0, 1]")


@dataclass(frozen=True)
class SliceMetrics:
    corpus_id: str
    corpus_version: str
    language_id: str
    record_count: int
    coverage: float
    exact_match: float
    mean_token_similarity: float
    ambiguity_rate: float


@dataclass(frozen=True)
class MultilingualQualificationReport:
    regime: str
    status: str
    claim_ceiling: str
    training_record_count: int
    evaluation_record_count: int
    corpus_count: int
    language_count: int
    leakage_violations: tuple[str, ...]
    threshold_failures: tuple[str, ...]
    macro_coverage: float
    macro_exact_match: float
    macro_token_similarity: float
    macro_ambiguity_rate: float
    slices: tuple[SliceMetrics, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def _levenshtein(a: Sequence[str], b: Sequence[str]) -> int:
    if len(a) < len(b):
        a, b = b, a
    previous = list(range(len(b) + 1))
    for i, token_a in enumerate(a, 1):
        current = [i]
        for j, token_b in enumerate(b, 1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[j] + 1,
                    previous[j - 1] + (token_a != token_b),
                )
            )
        previous = current
    return previous[-1]


def _best_similarity(record: EvaluationRecord) -> float:
    if not record.candidates:
        return 0.0
    best = 0.0
    for reference in record.references:
        for candidate in record.candidates:
            denominator = max(len(reference), len(candidate), 1)
            similarity = 1.0 - (_levenshtein(reference, candidate) / denominator)
            best = max(best, similarity)
    return best


def _exact_match(record: EvaluationRecord) -> bool:
    refs = set(record.references)
    return any(candidate in refs for candidate in record.candidates)


def _validate_unique_records(
    training: Sequence[TrainingExposure],
    evaluation: Sequence[EvaluationRecord],
) -> None:
    train_ids = [(row.corpus_id, row.corpus_version, row.record_id) for row in training]
    eval_ids = [(row.corpus_id, row.corpus_version, row.record_id) for row in evaluation]
    if len(train_ids) != len(set(train_ids)):
        raise ValueError("training exposure contains duplicate record IDs")
    if len(eval_ids) != len(set(eval_ids)):
        raise ValueError("evaluation set contains duplicate record IDs")


def audit_holdout_split(
    training: Iterable[TrainingExposure],
    evaluation: Iterable[EvaluationRecord],
    *,
    regime: str,
) -> tuple[str, ...]:
    train = list(training)
    eval_rows = list(evaluation)
    if regime not in _VALID_REGIMES:
        raise ValueError(f"unsupported multilingual qualification regime: {regime}")
    if not train:
        raise ValueError("training exposure must not be empty")
    if not eval_rows:
        raise ValueError("evaluation set must not be empty")
    _validate_unique_records(train, eval_rows)

    violations: list[str] = []

    train_record_keys = {
        (row.corpus_id, row.corpus_version, row.record_id)
        for row in train
    }
    overlap_records = sorted(
        {
            (row.corpus_id, row.corpus_version, row.record_id)
            for row in eval_rows
        }
        & train_record_keys
    )
    if overlap_records:
        violations.append(
            f"record leakage: {len(overlap_records)} evaluation records were exposed"
        )

    train_languages = {row.language_id for row in train}
    eval_languages = {row.language_id for row in eval_rows}

    train_sources = {
        (row.corpus_id, row.source_id)
        for row in train
        if row.source_id is not None
    }
    eval_sources = {
        (row.corpus_id, row.source_id)
        for row in eval_rows
        if row.source_id is not None
    }

    train_contents = {
        (row.corpus_id, row.content_id)
        for row in train
    }
    eval_contents = {
        (row.corpus_id, row.content_id)
        for row in eval_rows
    }

    if regime in {
        "HELD_OUT_LANGUAGE",
        "HELD_OUT_LANGUAGE_AND_CONTENT",
        "HELD_OUT_ALL",
        "PARALLEL_LANGUAGE_TRANSFER",
    }:
        overlap = sorted(train_languages & eval_languages)
        if overlap:
            violations.append(
                "language leakage: " + ",".join(overlap)
            )

    if regime in {"HELD_OUT_SOURCE", "HELD_OUT_ALL"}:
        overlap = sorted(train_sources & eval_sources)
        if overlap:
            violations.append(
                f"source leakage: {len(overlap)} corpus/source IDs overlap"
            )
        if any(row.source_id is None for row in eval_rows):
            violations.append(
                "source holdout requested but evaluation contains missing source IDs"
            )

    if regime in {
        "HELD_OUT_CONTENT",
        "HELD_OUT_LANGUAGE_AND_CONTENT",
        "HELD_OUT_ALL",
    }:
        overlap = sorted(train_contents & eval_contents)
        if overlap:
            violations.append(
                f"content leakage: {len(overlap)} corpus/content IDs overlap"
            )

    if regime == "PARALLEL_LANGUAGE_TRANSFER":
        missing_parallel = sorted(eval_contents - train_contents)
        if missing_parallel:
            violations.append(
                "parallel-transfer control missing: "
                f"{len(missing_parallel)} evaluation content IDs were not exposed "
                "in another training language"
            )

    return tuple(violations)


def _slice_metrics(
    rows: Sequence[EvaluationRecord],
) -> SliceMetrics:
    count = len(rows)
    covered = sum(bool(row.candidates) for row in rows)
    exact = sum(_exact_match(row) for row in rows)
    similarity = sum(_best_similarity(row) for row in rows)
    ambiguous = sum(len(row.candidates) > 1 for row in rows)
    first = rows[0]
    return SliceMetrics(
        corpus_id=first.corpus_id,
        corpus_version=first.corpus_version,
        language_id=first.language_id,
        record_count=count,
        coverage=covered / count,
        exact_match=exact / count,
        mean_token_similarity=similarity / count,
        ambiguity_rate=ambiguous / count,
    )


def evaluate_multilingual_holdout(
    training: Iterable[TrainingExposure],
    evaluation: Iterable[EvaluationRecord],
    *,
    regime: str,
    thresholds: QualificationThresholds,
) -> MultilingualQualificationReport:
    thresholds.validate()
    train = list(training)
    eval_rows = list(evaluation)
    leakage = audit_holdout_split(
        train,
        eval_rows,
        regime=regime,
    )

    grouped: dict[tuple[str, str, str], list[EvaluationRecord]] = {}
    for row in eval_rows:
        grouped.setdefault(
            (row.corpus_id, row.corpus_version, row.language_id),
            [],
        ).append(row)

    slices = tuple(
        _slice_metrics(rows)
        for _, rows in sorted(grouped.items())
    )
    corpus_count = len({row.corpus_id for row in eval_rows})
    language_count = len({row.language_id for row in eval_rows})

    failures: list[str] = []
    if corpus_count < thresholds.min_corpora:
        failures.append(
            f"corpus_count={corpus_count} < min_corpora={thresholds.min_corpora}"
        )
    if language_count < thresholds.min_languages:
        failures.append(
            f"language_count={language_count} < min_languages={thresholds.min_languages}"
        )

    for metrics in slices:
        prefix = (
            f"{metrics.corpus_id}@{metrics.corpus_version}/"
            f"{metrics.language_id}"
        )
        if metrics.record_count < thresholds.min_records_per_slice:
            failures.append(
                f"{prefix}: records={metrics.record_count} "
                f"< {thresholds.min_records_per_slice}"
            )
        if metrics.coverage < thresholds.min_coverage:
            failures.append(
                f"{prefix}: coverage={metrics.coverage:.6f} "
                f"< {thresholds.min_coverage:.6f}"
            )
        if metrics.exact_match < thresholds.min_exact_match:
            failures.append(
                f"{prefix}: exact_match={metrics.exact_match:.6f} "
                f"< {thresholds.min_exact_match:.6f}"
            )
        if metrics.mean_token_similarity < thresholds.min_token_similarity:
            failures.append(
                f"{prefix}: token_similarity={metrics.mean_token_similarity:.6f} "
                f"< {thresholds.min_token_similarity:.6f}"
            )
        if metrics.ambiguity_rate > thresholds.max_ambiguity_rate:
            failures.append(
                f"{prefix}: ambiguity_rate={metrics.ambiguity_rate:.6f} "
                f"> {thresholds.max_ambiguity_rate:.6f}"
            )

    if slices:
        macro_coverage = sum(row.coverage for row in slices) / len(slices)
        macro_exact = sum(row.exact_match for row in slices) / len(slices)
        macro_similarity = (
            sum(row.mean_token_similarity for row in slices) / len(slices)
        )
        macro_ambiguity = (
            sum(row.ambiguity_rate for row in slices) / len(slices)
        )
    else:
        macro_coverage = macro_exact = macro_similarity = macro_ambiguity = 0.0

    if leakage:
        status = "LEAKAGE_DETECTED"
    elif failures:
        status = "MULTILINGUAL_HOLDOUT_THRESHOLD_NOT_MET"
    else:
        status = "QUALIFIED_WITHIN_DECLARED_MULTILINGUAL_HOLDOUT"

    return MultilingualQualificationReport(
        regime=regime,
        status=status,
        claim_ceiling=_QUALIFICATION_CLAIM_CEILING,
        training_record_count=len(train),
        evaluation_record_count=len(eval_rows),
        corpus_count=corpus_count,
        language_count=language_count,
        leakage_violations=leakage,
        threshold_failures=tuple(failures),
        macro_coverage=macro_coverage,
        macro_exact_match=macro_exact,
        macro_token_similarity=macro_similarity,
        macro_ambiguity_rate=macro_ambiguity,
        slices=slices,
    )
