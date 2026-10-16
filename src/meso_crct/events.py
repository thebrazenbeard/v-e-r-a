"""Distinct runtime event identity for MESO-CRCT.

State/content identity and event identity are separate. Two experiences may
produce identical state transitions while still being distinct events.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib


_EVENT_IDENTITY_TOKEN = object()


@dataclass(frozen=True, slots=True, init=False)
class EventIdentity:
    stream_id: str
    sequence: int
    event_id: str

    def __init__(
        self,
        stream_id: str,
        sequence: int,
        event_id: str,
        *,
        _token: object | None = None,
    ) -> None:
        if _token is not _EVENT_IDENTITY_TOKEN:
            raise TypeError("EventIdentity must be issued by EventSequencer")
        if not stream_id.strip():
            raise ValueError("stream_id must be non-empty")
        if sequence < 1:
            raise ValueError("sequence must be >= 1")
        if not event_id.strip():
            raise ValueError("event_id must be non-empty")
        object.__setattr__(self, "stream_id", stream_id)
        object.__setattr__(self, "sequence", sequence)
        object.__setattr__(self, "event_id", event_id)


@dataclass(frozen=True, slots=True)
class EventSequencer:
    """Immutable reference event sequencer."""

    stream_id: str
    next_sequence: int = 1

    def __post_init__(self) -> None:
        if not self.stream_id.strip():
            raise ValueError("stream_id must be non-empty")
        if self.next_sequence < 1:
            raise ValueError("next_sequence must be >= 1")

    def issue(self) -> tuple["EventSequencer", EventIdentity]:
        sequence = self.next_sequence
        payload = f"{self.stream_id}:{sequence}".encode("utf-8")
        event_id = hashlib.sha256(payload).hexdigest()
        event = EventIdentity(
            stream_id=self.stream_id,
            sequence=sequence,
            event_id=event_id,
            _token=_EVENT_IDENTITY_TOKEN,
        )
        return (
            EventSequencer(
                stream_id=self.stream_id,
                next_sequence=sequence + 1,
            ),
            event,
        )
