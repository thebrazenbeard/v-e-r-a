"""Inert, independently authenticated *host-input* projection of Volition goals.

This is not a new motivation engine or a model tool. Volition owns wants and
choices; the host is responsible for fresh observation admission and source
custody before it supplies this envelope. A source_ref string is not a signature.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path
from typing import Any


MAX_ENVELOPE_BYTES = 128 * 1024
MAX_CURRENT_AGE = timedelta(minutes=5)
MAX_FUTURE_SKEW = timedelta(seconds=30)
# An envelope's class and source are merely *claims*. A model-origin choice
# cannot be promoted to self-authored/user-directed/policy provenance by
# swapping the class string. Until a trusted identity attestation exists,
# this view projects only explicitly model-classified proposals.
_PROJECTABLE_CHOICE_CLASS = "MODEL_PROPOSED"


class GoalViewError(ValueError):
    """Reject an untrusted or inconsistent goal-view snapshot."""


def _text(value: Any, *, limit: int = 256) -> bool:
    return (type(value) is str and 0 < len(value) <= limit
            and value.strip() == value and all(32 <= ord(c) <= 0x10ffff for c in value))


def _score(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 1


def _decode_pairs(pairs):
    parsed = {}
    for key, value in pairs:
        if key in parsed:
            raise GoalViewError("duplicate JSON key")
        parsed[key] = value
    return parsed


def project_volition_goal(envelope: dict[str, Any], *, now: datetime | None = None) -> dict[str, Any]:
    """Project only a fresh, linked current goal into a read-only suggestion.

    This structural check is not a verification of observation provenance;
    the integrating host must use Volition's own from_snapshot verifier and a
    separately secured custody channel before supplying the envelope.
    """
    if not isinstance(envelope, dict) or set(envelope) != {
            "schema", "captured_at_utc", "source_ref", "snapshot"}:
        raise GoalViewError("malformed host Volition envelope")
    if envelope["schema"] != "vera.volition-view-envelope.v1" or not _text(envelope["source_ref"]):
        raise GoalViewError("unrecognized or unproven Volition snapshot source")
    now = datetime.now(timezone.utc) if now is None else now
    if not isinstance(now, datetime) or now.tzinfo is None:
        raise GoalViewError("aware UTC clock required")
    now = now.astimezone(timezone.utc)
    try:
        raw_time = envelope["captured_at_utc"]
        if type(raw_time) is not str:
            raise ValueError("timestamp must be text")
        captured = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
        if captured.tzinfo is None:
            raise ValueError("timestamp lacks timezone")
        captured = captured.astimezone(timezone.utc)
    except (ValueError, OverflowError) as exc:
        raise GoalViewError("invalid snapshot UTC timestamp") from exc
    if captured - now > MAX_FUTURE_SKEW or now - captured > MAX_CURRENT_AGE:
        return {"status": "HOLD_STALE", "effect_authority": False}

    snapshot = envelope["snapshot"]
    if (not isinstance(snapshot, dict)
            or snapshot.get("schema") != "VOLITION_OPERATIONAL_MOTIVATION_V1"):
        raise GoalViewError("unrecognized Volition motivation schema")
    engine = snapshot.get("engine")
    if not isinstance(engine, dict) or engine.get("schema") != "VOLITION_STATE_V3":
        raise GoalViewError("unrecognized Volition engine snapshot schema")
    active = engine.get("active_goal")
    if active is None:
        return {"status": "NO_CURRENT_GOAL", "effect_authority": False}
    choices, wants, latches = engine.get("choices"), snapshot.get("wants"), snapshot.get("protection_latches")
    if (not isinstance(active, dict) or not isinstance(choices, list)
            or not isinstance(wants, list) or not isinstance(latches, list)):
        raise GoalViewError("invalid active Volition goal linkage")
    target, gid, cid = active.get("target"), active.get("goal_id"), active.get("choice_id")
    if (not all(_text(item) for item in (target, gid, cid))
            or active.get("status") != "ACTIVE" or active.get("effect_authority") is not False
            or not _score(active.get("adoption_score"))
            or type(active.get("revision")) is not int or active["revision"] < 1):
        raise GoalViewError("active goal is malformed or has effect authority")
    if target in latches:
        raise GoalViewError("protected goal cannot be proposed")
    matching_choices = [row for row in choices if isinstance(row, dict)
                        and row.get("choice_id") == cid]
    matching_wants = [row for row in wants if isinstance(row, dict)
                      and row.get("target") == target]
    if len(matching_choices) != 1 or len(matching_wants) != 1:
        raise GoalViewError("goal has no unique linked Volition choice and want")
    choice, want = matching_choices[0], matching_wants[0]
    if (choice.get("want_target") != target
            or choice.get("choice_class") != _PROJECTABLE_CHOICE_CLASS
            or choice.get("effect_authority") is not False
            or not _score(choice.get("want_score"))
            or not _text(choice.get("source")) or not choice["source"].startswith("model:")
            or want.get("eligible") is not True or want.get("effect_authority") is not False
            or not _score(want.get("score")) or not _text(want.get("evidence_id"))):
        raise GoalViewError("linked choice or evidence is inconsistent or privileged")
    return {
        "status": "PROPOSED_REVIEW", "goal_id": gid, "choice_id": cid,
        "choice_class": choice["choice_class"], "suggestion": f"Review current status of: {target}",
        "snapshot_age_seconds": int((now - captured).total_seconds()),
        "effect_authority": False,
    }


def read_goal_envelope(path: str | Path, *, now: datetime | None = None) -> dict[str, Any]:
    """Read a host-custodied snapshot file as a non-authoritative projection."""
    original = Path(path).expanduser()
    if original.is_symlink():
        raise GoalViewError("snapshot symlink rejected")
    try:
        resolved = original.resolve(strict=True)
        if not resolved.is_file() or not 0 < resolved.stat().st_size <= MAX_ENVELOPE_BYTES:
            raise GoalViewError("snapshot must be bounded regular file")
        raw = resolved.read_bytes()
        if len(raw) > MAX_ENVELOPE_BYTES:
            raise GoalViewError("snapshot exceeds byte budget")
        obj = json.loads(raw.decode("utf-8"), object_pairs_hook=_decode_pairs,
                         parse_constant=lambda _: (_ for _ in ()).throw(GoalViewError("nonfinite JSON")))
    except (OSError, UnicodeError, ValueError) as exc:
        raise GoalViewError("invalid or unavailable Volition snapshot file") from exc
    return project_volition_goal(obj, now=now)
