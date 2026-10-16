from __future__ import annotations

from typing import Any

from .model import (
    BehavioralAssessment,
    BehavioralHypothesis,
    BehavioralObservation,
    BehavioralPattern,
    HypothesisState,
)


def assessment_from_dict(raw: dict[str, Any]) -> BehavioralAssessment:
    if not isinstance(raw, dict):
        raise ValueError("behavioral assessment must be an object")
    allowed = {"observations", "hypotheses"}
    unknown = set(raw) - allowed
    if unknown:
        raise ValueError("unknown behavioral assessment fields: " + ", ".join(sorted(unknown)))

    observations_raw = raw.get("observations", [])
    hypotheses_raw = raw.get("hypotheses", [])
    if not isinstance(observations_raw, list) or not all(isinstance(x, dict) for x in observations_raw):
        raise ValueError("observations must be a list of objects")
    if not isinstance(hypotheses_raw, list) or not all(isinstance(x, dict) for x in hypotheses_raw):
        raise ValueError("hypotheses must be a list of objects")

    return BehavioralAssessment(
        observations=tuple(_observation_from_dict(item) for item in observations_raw),
        hypotheses=tuple(_hypothesis_from_dict(item) for item in hypotheses_raw),
    )


def _observation_from_dict(raw: dict[str, Any]) -> BehavioralObservation:
    allowed = {"observation_id", "subject", "description", "source_ref"}
    unknown = set(raw) - allowed
    if unknown:
        raise ValueError("unknown behavioral observation fields: " + ", ".join(sorted(unknown)))
    missing = [key for key in allowed if key not in raw]
    if missing:
        raise ValueError("required behavioral observation fields missing: " + ", ".join(sorted(missing)))
    return BehavioralObservation(
        observation_id=raw["observation_id"],
        subject=raw["subject"],
        description=raw["description"],
        source_ref=raw["source_ref"],
    )


def _hypothesis_from_dict(raw: dict[str, Any]) -> BehavioralHypothesis:
    allowed = {
        "hypothesis_id",
        "pattern",
        "subject",
        "evidence_refs",
        "rationale",
        "alternative_explanations",
        "state",
    }
    unknown = set(raw) - allowed
    if unknown:
        raise ValueError("unknown behavioral hypothesis fields: " + ", ".join(sorted(unknown)))
    required = {"hypothesis_id", "pattern", "subject", "evidence_refs", "rationale"}
    missing = [key for key in required if key not in raw]
    if missing:
        raise ValueError("required behavioral hypothesis fields missing: " + ", ".join(sorted(missing)))

    evidence = raw["evidence_refs"]
    alternatives = raw.get("alternative_explanations", [])
    if not isinstance(evidence, list):
        raise ValueError("evidence_refs must be a list")
    if not isinstance(alternatives, list):
        raise ValueError("alternative_explanations must be a list")

    try:
        return BehavioralHypothesis(
            hypothesis_id=raw["hypothesis_id"],
            pattern=BehavioralPattern(raw["pattern"]),
            subject=raw["subject"],
            evidence_refs=tuple(evidence),
            rationale=raw["rationale"],
            alternative_explanations=tuple(alternatives),
            state=HypothesisState(raw.get("state", "PROPOSED")),
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid behavioral hypothesis: {exc}") from exc
