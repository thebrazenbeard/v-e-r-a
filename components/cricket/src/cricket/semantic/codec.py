from __future__ import annotations

from typing import Any

from .model import (
    Force,
    Polarity,
    ProvenanceKind,
    SemanticFrame,
    SemanticProposition,
    SemanticScope,
    SpeechAct,
    TemporalStatus,
)


def frame_from_dict(raw: dict[str, Any]) -> SemanticFrame:
    if not isinstance(raw, dict):
        raise ValueError("semantic frame must be an object")
    allowed = {"propositions", "unresolved_interpretations"}
    unknown = set(raw) - allowed
    if unknown:
        raise ValueError("unknown semantic frame fields: " + ", ".join(sorted(unknown)))

    propositions_raw = raw.get("propositions", [])
    unresolved = raw.get("unresolved_interpretations", [])

    if not isinstance(propositions_raw, list) or not all(isinstance(x, dict) for x in propositions_raw):
        raise ValueError("semantic propositions must be a list of objects")
    if not isinstance(unresolved, list) or not all(isinstance(x, str) and x.strip() for x in unresolved):
        raise ValueError("unresolved_interpretations must be a list of non-empty strings")
    return SemanticFrame(
        propositions=tuple(_proposition_from_dict(item) for item in propositions_raw),
        unresolved_interpretations=tuple(unresolved),
    )


def _proposition_from_dict(raw: dict[str, Any]) -> SemanticProposition:
    allowed = {
        "anchor_id",
        "referent",
        "predicate",
        "force",
        "polarity",
        "scope",
        "speech_act",
        "temporal_status",
        "provenance",
    }
    unknown = set(raw) - allowed
    if unknown:
        raise ValueError("unknown semantic proposition fields: " + ", ".join(sorted(unknown)))
    missing = [key for key in ("anchor_id", "referent", "predicate") if key not in raw]
    if missing:
        raise ValueError("required semantic proposition fields missing: " + ", ".join(missing))

    scope_raw = raw.get("scope")
    scope = None
    if scope_raw is not None:
        if not isinstance(scope_raw, list) or not all(isinstance(x, str) and x.strip() for x in scope_raw):
            raise ValueError("semantic proposition scope must be a list of non-empty strings")
        scope = SemanticScope(members=frozenset(scope_raw))

    try:
        return SemanticProposition(
            anchor_id=raw["anchor_id"],
            referent=raw["referent"],
            predicate=raw["predicate"],
            force=Force(raw.get("force", "ASSERTED")),
            polarity=Polarity(raw.get("polarity", "AFFIRMED")),
            scope=scope,
            speech_act=SpeechAct(raw.get("speech_act", "DESCRIPTION")),
            temporal_status=TemporalStatus(raw.get("temporal_status", "CURRENT")),
            provenance=ProvenanceKind(raw.get("provenance", "UNKNOWN")),
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid semantic proposition: {exc}") from exc


