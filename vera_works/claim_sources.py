from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Mapping


class DiscoveryMode(str, Enum):
    DIRECT_FETCH = "DIRECT_FETCH"
    PUBLIC_API = "PUBLIC_API"
    SEARCH_FORM = "SEARCH_FORM"
    INTERACTIVE_SEARCH = "INTERACTIVE_SEARCH"
    MANUAL_ONLY = "MANUAL_ONLY"


class SourceReadState(str, Enum):
    READY = "READY"
    INTERACTIVE_GATE = "INTERACTIVE_GATE"
    BOT_BLOCKED = "BOT_BLOCKED"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ClaimSource:
    source_id: str
    title: str
    jurisdiction: str
    source_class: str
    discovery_mode: DiscoveryMode
    read_state: SourceReadState
    entrypoint: str
    authoritative: bool
    person_to_person_communication_required: bool
    claim_effect_requires_identity: bool
    notes: str = ""

    @classmethod
    def from_dict(cls, value: Mapping[str, object]) -> "ClaimSource":
        data = dict(value)
        data["discovery_mode"] = DiscoveryMode(str(data["discovery_mode"]))
        data["read_state"] = SourceReadState(str(data["read_state"]))
        return cls(**data)  # type: ignore[arg-type]


def load_source_registry(path: Path) -> list[ClaimSource]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("sources"), list):
        raise ValueError("source registry must be an object with a sources array")
    sources = [ClaimSource.from_dict(item) for item in raw["sources"]]
    identifiers = [item.source_id for item in sources]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("source registry contains duplicate source_id values")
    return sources


def automatic_read_queue(sources: list[ClaimSource]) -> list[ClaimSource]:
    """Return sources safe for unattended read-only acquisition.

    This function intentionally excludes interactive gates, bot blocks,
    authenticated surfaces, and person-to-person communication.
    """
    allowed_modes = {DiscoveryMode.DIRECT_FETCH, DiscoveryMode.PUBLIC_API}
    return [
        item
        for item in sources
        if item.authoritative
        and item.read_state == SourceReadState.READY
        and item.discovery_mode in allowed_modes
        and not item.person_to_person_communication_required
    ]


def deferred_sources(sources: list[ClaimSource]) -> list[ClaimSource]:
    automatic = {item.source_id for item in automatic_read_queue(sources)}
    return [item for item in sources if item.source_id not in automatic]
