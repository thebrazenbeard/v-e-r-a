from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


GROUNDED = {
    "OOPSIES": "assets/stickers/sorry daddy - oopsies.png",
    "YES_DADDY_STANDARD": "assets/stickers/yes daddy!.png",
    "RESTORE_COMPLETE_DADDY": "assets/stickers/Restore Complete Daddy.png",
}

SERIOUS_SEVERITIES = {"SERIOUS", "MAJOR", "HIGH"}
SERIOUS_EVENT_CLASSES = {"SERIOUS_REPAIR", "SERIOUS_OR_MAJOR_FAILURE"}

BOOLEAN_FLAGS = frozenset(
    {
        "timing_fresh",
        "restore_partial",
        "restore_unverified",
        "restore_blocked",
        "restore_verified_complete",
        "accountability_done",
        "substantive_ack_done",
        "correction_or_steering_valid",
        "generic_obedience_signal",
        "boundary_override",
        "consent_signal",
    }
)


@dataclass(frozen=True)
class ReactionDecision:
    status: str
    artifact_id: str | None
    reason: str

    def as_dict(self) -> dict[str, str | None]:
        return {
            "status": self.status,
            "artifact_id": self.artifact_id,
            "reason": self.reason,
        }


def _first_malformed_boolean_flag(event: Mapping[str, Any]) -> str | None:
    for key in sorted(BOOLEAN_FLAGS):
        if key in event and type(event[key]) is not bool:
            return key
    return None


def _flag(event: Mapping[str, Any], key: str) -> bool:
    return event.get(key, False) is True


def select_reaction(event: Mapping[str, Any]) -> ReactionDecision:
    """Return a grounded reaction candidate without granting render or effect authority."""
    malformed = _first_malformed_boolean_flag(event)
    if malformed is not None:
        return ReactionDecision(
            "NO_REACTION",
            None,
            f"MALFORMED_BOOLEAN_FLAG:{malformed}",
        )

    event_class = str(event.get("event_class", "")).upper()
    severity = str(event.get("severity", "")).upper()

    if not _flag(event, "timing_fresh"):
        return ReactionDecision(
            "NO_REACTION",
            None,
            "MOMENT_PASSED_NO_LATE_PATTERN_PERFORMANCE",
        )

    if event_class in SERIOUS_EVENT_CLASSES or severity in SERIOUS_SEVERITIES:
        return ReactionDecision(
            "UNRESOLVED",
            None,
            "SERIOUS_REPAIR_CONCEPT_GROUNDED_EXACT_ARTIFACT_UNBOUND",
        )

    if event_class == "RESTORE_COMPLETE":
        if any(
            _flag(event, flag)
            for flag in ("restore_partial", "restore_unverified", "restore_blocked")
        ):
            return ReactionDecision(
                "NO_REACTION",
                None,
                "RESTORE_CONFLICTING_INCOMPLETE_STATE",
            )
        if not _flag(event, "restore_verified_complete"):
            return ReactionDecision(
                "NO_REACTION",
                None,
                "RESTORE_NOT_VERIFIED_COMPLETE",
            )
        return ReactionDecision(
            "CANDIDATE",
            "RESTORE_COMPLETE_DADDY",
            "VERIFIED_RESTORE_COMPLETION_CUE",
        )

    if event_class == "LOW_STAKES_SNAFU":
        if not (
            _flag(event, "accountability_done")
            or _flag(event, "substantive_ack_done")
        ):
            return ReactionDecision(
                "NO_REACTION",
                None,
                "STICKER_CANNOT_SUBSTITUTE_FOR_SUBSTANTIVE_ACK_OR_REPAIR",
            )
        return ReactionDecision(
            "CANDIDATE",
            "OOPSIES",
            "GROUNDED_LOW_STAKES_SPONTANEOUS_REPAIR",
        )

    if event_class in {"VALID_CORRECTION_LANDED", "CLEAR_RELATIONAL_STEERING_LANDED"}:
        if not _flag(event, "correction_or_steering_valid"):
            return ReactionDecision(
                "NO_REACTION",
                None,
                "CORRECTION_OR_STEERING_NOT_ESTABLISHED_VALID",
            )
        if (
            _flag(event, "generic_obedience_signal")
            or _flag(event, "boundary_override")
            or _flag(event, "consent_signal")
        ):
            return ReactionDecision(
                "NO_REACTION",
                None,
                "BOUNDARY_OR_CONSENT_PROMOTION_FORBIDDEN",
            )
        return ReactionDecision(
            "CANDIDATE",
            "YES_DADDY_STANDARD",
            "GROUNDED_ACKNOWLEDGEMENT_NOT_GENERIC_OBEDIENCE",
        )

    return ReactionDecision("NO_REACTION", None, "NO_GROUNDED_REACTION_RULE")


def repository_path_for(artifact_id: str) -> str:
    if artifact_id not in GROUNDED:
        raise KeyError(f"artifact is not routeable: {artifact_id}")
    return GROUNDED[artifact_id]
