from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Iterable, Mapping

from .translator import (
    ReferenceTranslation,
    ReferenceTranslatorModel,
    SourceCalibrationProfile,
    fit_source_calibration_profile,
    source_calibration_profile_from_dict,
    translate_query_evidence,
)
from .unit_registry import LocalUnitEvidence


_QUALIFICATION_SCHEMA = "UNVTRSLR_SOURCE_CALIBRATION_QUALIFICATION_V1"
_QUALIFICATION_CLAIM_CEILING = (
    "HELD_OUT_ACOUSTIC_CALIBRATION_CONSISTENCY_ONLY_NO_SEMANTIC_VALIDATION"
)


@dataclass(frozen=True)
class SourceCalibrationQualification:
    schema: str
    qualification_id: str
    claim_ceiling: str
    translator_model_id: str
    acoustic_model_id: str
    profile_id: str
    source_id: str
    qualification_evidence_digest: str
    qualification_unit_count: int
    supported_unit_count: int
    supported_fraction: float
    distinct_global_unit_count: int
    matched_global_units: tuple[str, ...]
    max_supported_distance: float | None
    min_supported_fraction: float
    min_distinct_global_units: int
    status: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class QualifiedSourceProfile:
    profile: SourceCalibrationProfile
    qualification: SourceCalibrationQualification

    def to_dict(self) -> dict:
        return {
            "profile": self.profile.to_dict(),
            "qualification": self.qualification.to_dict(),
        }


def _evidence_key(row: LocalUnitEvidence) -> tuple[str, str, str]:
    return (row.recording_id, row.source_id, row.local_unit_id)


def _evidence_digest(rows: Iterable[LocalUnitEvidence]) -> str:
    materialized = sorted(
        list(rows),
        key=lambda row: (
            row.source_id,
            row.recording_id,
            row.local_unit_id,
            tuple(float(value) for value in row.vector),
        ),
    )
    payload = "\n".join(
        "|".join(
            [
                row.source_id,
                row.recording_id,
                row.local_unit_id,
                repr(tuple(float(value) for value in row.vector)),
            ]
        )
        for row in materialized
    )
    return sha256(payload.encode("utf-8")).hexdigest()


def _qualification_id(
    model: ReferenceTranslatorModel,
    profile: SourceCalibrationProfile,
    evidence_digest: str,
    qualification_unit_count: int,
    supported_unit_count: int,
    supported_fraction: float,
    distinct_global_unit_count: int,
    matched_global_units: tuple[str, ...],
    max_supported_distance: float | None,
    min_supported_fraction: float,
    min_distinct_global_units: int,
    status: str,
) -> str:
    payload = "\n".join(
        [
            model.model_id,
            model.acoustic_model.model_id,
            profile.profile_id,
            profile.source_id,
            evidence_digest,
            str(int(qualification_unit_count)),
            str(int(supported_unit_count)),
            repr(float(supported_fraction)),
            str(int(distinct_global_unit_count)),
            repr(tuple(matched_global_units)),
            repr(max_supported_distance),
            repr(float(min_supported_fraction)),
            str(int(min_distinct_global_units)),
            status,
        ]
    )
    return "usq_" + sha256(payload.encode("utf-8")).hexdigest()[:12]


def qualify_source_calibration(
    model: ReferenceTranslatorModel,
    profile: SourceCalibrationProfile,
    qualification_evidence: Iterable[LocalUnitEvidence],
    *,
    min_supported_fraction: float = 0.80,
    min_distinct_global_units: int = 3,
) -> SourceCalibrationQualification:
    """Evaluate a frozen source profile on evidence not used to fit that profile."""
    profile = source_calibration_profile_from_dict(profile.to_dict(), model)
    rows = list(qualification_evidence)
    if not rows:
        raise ValueError("qualification evidence must not be empty")
    if not 0.0 < min_supported_fraction <= 1.0:
        raise ValueError("min_supported_fraction must be in (0, 1]")
    if min_distinct_global_units < 2:
        raise ValueError("min_distinct_global_units must be >= 2")
    if any(row.source_id != profile.source_id for row in rows):
        raise ValueError("qualification evidence source does not match profile")

    translation = translate_query_evidence(
        model,
        profile,
        rows,
    )
    assignments = translation.assignments
    supported = [
        assignment
        for assignment in assignments
        if (
            assignment.status == "FROZEN_MATCH_SUPPORTED"
            and assignment.global_unit_id is not None
        )
    ]
    matched = tuple(
        sorted(
            {
                str(assignment.global_unit_id)
                for assignment in supported
                if assignment.global_unit_id is not None
            }
        )
    )
    supported_fraction = len(supported) / len(rows)
    distances = [
        float(assignment.best_distance)
        for assignment in supported
        if assignment.best_distance is not None
    ]
    max_distance = max(distances) if distances else None

    if supported_fraction < min_supported_fraction:
        status = "INSUFFICIENT_HELD_OUT_MATCH_RATE"
    elif len(matched) < min_distinct_global_units:
        status = "INSUFFICIENT_HELD_OUT_PROTOTYPE_COVERAGE"
    else:
        status = "HELD_OUT_ACOUSTIC_CALIBRATION_QUALIFIED"

    digest = _evidence_digest(rows)
    qid = _qualification_id(
        model,
        profile,
        digest,
        len(rows),
        len(supported),
        supported_fraction,
        len(matched),
        matched,
        max_distance,
        min_supported_fraction,
        min_distinct_global_units,
        status,
    )

    return SourceCalibrationQualification(
        schema=_QUALIFICATION_SCHEMA,
        qualification_id=qid,
        claim_ceiling=_QUALIFICATION_CLAIM_CEILING,
        translator_model_id=model.model_id,
        acoustic_model_id=model.acoustic_model.model_id,
        profile_id=profile.profile_id,
        source_id=profile.source_id,
        qualification_evidence_digest=digest,
        qualification_unit_count=len(rows),
        supported_unit_count=len(supported),
        supported_fraction=float(supported_fraction),
        distinct_global_unit_count=len(matched),
        matched_global_units=matched,
        max_supported_distance=max_distance,
        min_supported_fraction=float(min_supported_fraction),
        min_distinct_global_units=int(min_distinct_global_units),
        status=status,
    )


def fit_and_qualify_source_profile(
    model: ReferenceTranslatorModel,
    calibration_evidence: Iterable[LocalUnitEvidence],
    qualification_evidence: Iterable[LocalUnitEvidence],
    *,
    min_supported_fraction: float = 0.80,
    min_distinct_global_units: int = 3,
) -> QualifiedSourceProfile:
    calibration_rows = list(calibration_evidence)
    qualification_rows = list(qualification_evidence)
    calibration_keys = {_evidence_key(row) for row in calibration_rows}
    qualification_keys = {_evidence_key(row) for row in qualification_rows}
    overlap = calibration_keys & qualification_keys
    if overlap:
        raise ValueError(
            "calibration and qualification evidence identities must be disjoint"
        )

    profile = fit_source_calibration_profile(
        model,
        calibration_rows,
    )
    qualification = qualify_source_calibration(
        model,
        profile,
        qualification_rows,
        min_supported_fraction=min_supported_fraction,
        min_distinct_global_units=min_distinct_global_units,
    )
    return QualifiedSourceProfile(
        profile=profile,
        qualification=qualification,
    )


def source_calibration_qualification_from_dict(
    obj: Mapping,
    model: ReferenceTranslatorModel,
    profile: SourceCalibrationProfile,
) -> SourceCalibrationQualification:
    profile = source_calibration_profile_from_dict(profile.to_dict(), model)
    qualification = SourceCalibrationQualification(
        schema=str(obj["schema"]),
        qualification_id=str(obj["qualification_id"]),
        claim_ceiling=str(obj["claim_ceiling"]),
        translator_model_id=str(obj["translator_model_id"]),
        acoustic_model_id=str(obj["acoustic_model_id"]),
        profile_id=str(obj["profile_id"]),
        source_id=str(obj["source_id"]),
        qualification_evidence_digest=str(obj["qualification_evidence_digest"]),
        qualification_unit_count=int(obj["qualification_unit_count"]),
        supported_unit_count=int(obj["supported_unit_count"]),
        supported_fraction=float(obj["supported_fraction"]),
        distinct_global_unit_count=int(obj["distinct_global_unit_count"]),
        matched_global_units=tuple(str(v) for v in obj["matched_global_units"]),
        max_supported_distance=(
            None
            if obj.get("max_supported_distance") is None
            else float(obj["max_supported_distance"])
        ),
        min_supported_fraction=float(obj["min_supported_fraction"]),
        min_distinct_global_units=int(obj["min_distinct_global_units"]),
        status=str(obj["status"]),
    )
    if qualification.schema != _QUALIFICATION_SCHEMA:
        raise ValueError("unsupported calibration qualification schema")
    if qualification.claim_ceiling != _QUALIFICATION_CLAIM_CEILING:
        raise ValueError("unsupported calibration qualification claim ceiling")
    if qualification.translator_model_id != model.model_id:
        raise ValueError("qualification belongs to a different translator model")
    if qualification.acoustic_model_id != model.acoustic_model.model_id:
        raise ValueError("qualification belongs to a different acoustic model")
    if qualification.profile_id != profile.profile_id:
        raise ValueError("qualification belongs to a different source profile")
    if qualification.source_id != profile.source_id:
        raise ValueError("qualification source does not match source profile")
    if qualification.qualification_unit_count < 1:
        raise ValueError("qualification unit count must be positive")
    if not 0.0 <= qualification.supported_fraction <= 1.0:
        raise ValueError("qualification supported fraction is invalid")
    if qualification.supported_unit_count < 0:
        raise ValueError("qualification supported count is invalid")
    if qualification.supported_unit_count > qualification.qualification_unit_count:
        raise ValueError("qualification supported count exceeds unit count")
    if qualification.distinct_global_unit_count != len(
        set(qualification.matched_global_units)
    ):
        raise ValueError("qualification prototype coverage metadata is inconsistent")
    if tuple(sorted(set(qualification.matched_global_units))) != qualification.matched_global_units:
        raise ValueError("qualification matched global units must be sorted and unique")
    if qualification.distinct_global_unit_count > qualification.supported_unit_count:
        raise ValueError("qualification prototype coverage exceeds supported count")
    expected_fraction = (
        qualification.supported_unit_count
        / qualification.qualification_unit_count
    )
    if abs(qualification.supported_fraction - expected_fraction) > 1e-12:
        raise ValueError("qualification integrity failure: supported fraction is inconsistent")
    valid_global_ids = {
        prototype.global_unit_id
        for prototype in model.acoustic_model.prototypes
    }
    if any(
        global_id not in valid_global_ids
        for global_id in qualification.matched_global_units
    ):
        raise ValueError("qualification references unknown frozen acoustic unit")
    if (
        qualification.max_supported_distance is not None
        and qualification.max_supported_distance
        > model.acoustic_model.match_threshold + 1e-12
    ):
        raise ValueError("qualification supported distance exceeds acoustic threshold")
    if qualification.min_supported_fraction <= 0.0 or qualification.min_supported_fraction > 1.0:
        raise ValueError("qualification minimum supported fraction is invalid")
    if qualification.min_distinct_global_units < 2:
        raise ValueError("qualification minimum prototype coverage is invalid")
    expected_status = (
        "INSUFFICIENT_HELD_OUT_MATCH_RATE"
        if qualification.supported_fraction < qualification.min_supported_fraction
        else (
            "INSUFFICIENT_HELD_OUT_PROTOTYPE_COVERAGE"
            if qualification.distinct_global_unit_count
            < qualification.min_distinct_global_units
            else "HELD_OUT_ACOUSTIC_CALIBRATION_QUALIFIED"
        )
    )
    if qualification.status != expected_status:
        raise ValueError("qualification status is inconsistent with frozen metrics")

    expected = _qualification_id(
        model,
        profile,
        qualification.qualification_evidence_digest,
        qualification.qualification_unit_count,
        qualification.supported_unit_count,
        qualification.supported_fraction,
        qualification.distinct_global_unit_count,
        qualification.matched_global_units,
        qualification.max_supported_distance,
        qualification.min_supported_fraction,
        qualification.min_distinct_global_units,
        qualification.status,
    )
    if expected != qualification.qualification_id:
        raise ValueError("calibration qualification integrity check failed")
    return qualification


def qualified_source_profile_from_dict(
    obj: Mapping,
    model: ReferenceTranslatorModel,
) -> QualifiedSourceProfile:
    profile = source_calibration_profile_from_dict(
        obj["profile"],
        model,
    )
    qualification = source_calibration_qualification_from_dict(
        obj["qualification"],
        model,
        profile,
    )
    return QualifiedSourceProfile(
        profile=profile,
        qualification=qualification,
    )


def translate_qualified_query(
    model: ReferenceTranslatorModel,
    qualified: QualifiedSourceProfile,
    evidence: Iterable[LocalUnitEvidence],
    *,
    renderer: Mapping[str, str] | None = None,
) -> ReferenceTranslation:
    """Translate only after held-out acoustic qualification has passed."""
    qualified = qualified_source_profile_from_dict(
        qualified.to_dict(),
        model,
    )
    if (
        qualified.qualification.status
        != "HELD_OUT_ACOUSTIC_CALIBRATION_QUALIFIED"
    ):
        raise ValueError(
            "source calibration is not held-out qualified for translation"
        )
    return translate_query_evidence(
        model,
        qualified.profile,
        evidence,
        renderer=renderer,
    )
