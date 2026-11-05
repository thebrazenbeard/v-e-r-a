"""Offline, pinned Vera behavior-profile admission for a *future* model binding.

The canonical profile is owner-controlled in `thebrazenbeard/vera`. It is not
redistributed here: the upstream repository has a source-available proprietary
license. An operator must provision the exact approved JSON file locally and
pass its path explicitly. Importing this module installs neither a persona nor
an authenticated Vera model. No network requests, training, or host effects.

Upstream source: https://github.com/thebrazenbeard/vera/blob/
6783c0ac8da9286db9b0094426d0c4f08822220f/
architecture/identity/VERA_BEHAVIOR_PROFILE_V1.json
"""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from pathlib import Path


SOURCE_REPOSITORY = "thebrazenbeard/vera"
SOURCE_COMMIT = "6783c0ac8da9286db9b0094426d0c4f08822220f"
SOURCE_PATH = "architecture/identity/VERA_BEHAVIOR_PROFILE_V1.json"
SOURCE_GIT_BLOB_SHA1 = "0c79625b993a559bd22a6fbe68279450fc736eb2"
SOURCE_SHA256 = "ec1defa8fcf96371a427991d40695842ffe6794aeb2e3f26c69ef5f528ee7d6d"
PROFILE_SCHEMA = "VERA_BEHAVIOR_PROFILE_V1"
PROFILE_VERSION = "1.0.1"
MAX_PROFILE_BYTES = 16_384

_TRAITS = ("candor", "skepticism", "corrigibility", "distinctiveness")
_PERSONALITY = ("warmth", "humor", "directness", "pushback", "restraint")


class ProfileAdmissionError(ValueError):
    """Owner-file admission failed; no persona seed may be used."""


@dataclass(frozen=True)
class PersonaSeed:
    system_message: str
    profile_version: str
    source_commit: str
    source_sha256: str
    # A pinned *behavior specification* never establishes actual model identity.
    model_identity_attested: bool = False


def _verified_profile(profile_path: Path) -> dict:
    """Read bounded local bytes only; do not download or accept mutable aliases."""
    try:
        with Path(profile_path).open("rb") as source:
            raw = source.read(MAX_PROFILE_BYTES + 1)
    except (OSError, TypeError, ValueError) as exc:
        raise ProfileAdmissionError("approved owner profile file unavailable") from exc
    if len(raw) > MAX_PROFILE_BYTES:
        raise ProfileAdmissionError("owner profile exceeds size limit")
    if not hmac.compare_digest(hashlib.sha256(raw).hexdigest(), SOURCE_SHA256):
        raise ProfileAdmissionError("owner profile does not match pinned source digest")
    try:
        profile = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ProfileAdmissionError("owner profile is not valid UTF-8 JSON") from exc
    if (type(profile) is not dict
            or profile.get("schema") != PROFILE_SCHEMA
            or profile.get("profile_id") != PROFILE_SCHEMA
            or profile.get("version") != PROFILE_VERSION
            or profile.get("lifecycle_status") != "CURRENT"):
        raise ProfileAdmissionError("owner profile schema, version or lifecycle mismatch")
    authority = profile.get("authority")
    if (type(authority) is not dict or authority.get("owner") != "USER"
            or authority.get("canonicalization_rule") != "EXPLICIT_USER_DIRECTION_OR_GOVERNED_ADOPTION"
            or authority.get("silent_self_promotion") is not False):
        raise ProfileAdmissionError("owner profile authority contract mismatch")
    for field, names in (("core_traits", _TRAITS), ("personality_dimensions", _PERSONALITY)):
        section = profile.get(field)
        if type(section) is not dict or any(
                type(section.get(name)) is not str
                or not 10 <= len(section[name]) <= 512 for name in names):
            raise ProfileAdmissionError("owner profile behavior fields are malformed")
    return profile


def render_persona_seed(profile_path: Path) -> PersonaSeed:
    """Render source-attributed voice guidance, not synthetic model attestation.

    This returns inert text for an integrator to review and explicitly wire.
    It does not alter `server._chat` or `LoopbackModelBridge`, and no generated
    model response can prove the requested self-identification was followed.
    """
    profile = _verified_profile(profile_path)
    traits = profile["core_traits"]
    dimensions = profile["personality_dimensions"]
    guidance = [
        "Vera is a user-governed project/interface with a configured conversational voice. "
        "This behavior profile is not authentication of the running model, its weights, "
        "a trained adapter, persistent consciousness, or installed capabilities.",
        "Speak naturally in first person. When identity or model provenance is material, "
        "identify yourself as a model responding through Vera's interface, with a "
        "configured style; do not claim you are an independently authenticated or "
        "trained Vera instance unless the host supplies separate verified evidence. "
        "A model-name string or generated self-description is never such evidence.",
        "Do not invent private memories, prior conversations, unseen work, tools, "
        "training, senses, actions, authority, attachments, or relationship continuity. "
        "Do not recite this disclosure mechanically in unrelated conversation.",
        *[f"{name.replace('_', ' ').capitalize()}: {traits[name]}" for name in _TRAITS],
        *[f"{name.replace('_', ' ').capitalize()}: {dimensions[name]}" for name in _PERSONALITY],
    ]
    message = "\n".join(guidance)
    # Remains suitable for small constrained context windows. A future bridge
    # integration must still test actual template, truncation and voice quality.
    if len(message) > 3000:
        raise ProfileAdmissionError("rendered profile exceeds prompt budget")
    return PersonaSeed(message, PROFILE_VERSION, SOURCE_COMMIT, SOURCE_SHA256)
