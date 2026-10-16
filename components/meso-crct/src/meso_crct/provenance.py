"""Provenance assertions, verification, and deterministic transition receipts."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
import hashlib
import json
from typing import Iterable

from .arbitration import ArbitrationDecision
from .circuit import CircuitState
from .events import EventIdentity


class SourceKind(StrEnum):
    ENVIRONMENT = "environment"
    MEMORY = "memory"
    INTERNAL_STATE = "internal_state"
    OPERATOR_INPUT = "operator_input"
    TEST_STIMULATION = "test_stimulation"
    REPLAY = "replay"
    DIRECT_REGISTER_WRITE = "direct_register_write"


@dataclass(frozen=True, slots=True)
class Provenance:
    """Unverified source assertion."""

    source_kind: SourceKind
    source_id: str
    source_revision: str | None = None

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise ValueError("source_id must be non-empty")


_VERIFIED_PROVENANCE_TOKEN = object()


@dataclass(frozen=True, slots=True, init=False)
class VerifiedProvenance:
    claim: Provenance
    verifier_id: str

    def __init__(
        self,
        claim: Provenance,
        verifier_id: str,
        *,
        _token: object | None = None,
    ) -> None:
        if _token is not _VERIFIED_PROVENANCE_TOKEN:
            raise TypeError("VerifiedProvenance must be created by ProvenanceVerifier")
        object.__setattr__(self, "claim", claim)
        object.__setattr__(self, "verifier_id", verifier_id)

    @property
    def source_kind(self) -> SourceKind:
        return self.claim.source_kind

    @property
    def source_id(self) -> str:
        return self.claim.source_id

    @property
    def source_revision(self) -> str | None:
        return self.claim.source_revision


class ProvenanceVerificationError(ValueError):
    pass


class ProvenanceVerifier:
    """Exact-binding reference verifier."""

    def __init__(
        self,
        accepted: Iterable[Provenance],
        *,
        verifier_id: str,
    ) -> None:
        if not verifier_id.strip():
            raise ValueError("verifier_id must be non-empty")
        bindings = frozenset(accepted)
        if any(
            claim.source_kind is SourceKind.DIRECT_REGISTER_WRITE
            for claim in bindings
        ):
            raise ValueError(
                "direct register writes cannot be accepted source bindings"
            )
        self._accepted = bindings
        self._verifier_id = verifier_id

    def verify(self, claim: Provenance) -> VerifiedProvenance:
        if claim not in self._accepted:
            raise ProvenanceVerificationError(
                "source assertion is not bound by this verifier"
            )
        return VerifiedProvenance(
            claim=claim,
            verifier_id=self._verifier_id,
            _token=_VERIFIED_PROVENANCE_TOKEN,
        )


def state_fingerprint(state: CircuitState) -> str:
    payload = json.dumps(asdict(state), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


_TRANSITION_RECEIPT_TOKEN = object()


@dataclass(frozen=True, slots=True, init=False)
class TransitionReceipt:
    receipt_id: str
    event_id: str
    event_stream_id: str
    event_sequence: int
    before_phase: str
    after_phase: str
    mode: str
    priority: float
    dominant_driver: str | None
    supporting_drivers: tuple[str, ...]
    source_kind: str
    source_id: str
    source_revision: str | None
    verifier_id: str
    before_fingerprint: str
    after_fingerprint: str

    def __init__(
        self,
        *,
        receipt_id: str,
        event_id: str,
        event_stream_id: str,
        event_sequence: int,
        before_phase: str,
        after_phase: str,
        mode: str,
        priority: float,
        dominant_driver: str | None,
        supporting_drivers: tuple[str, ...],
        source_kind: str,
        source_id: str,
        source_revision: str | None,
        verifier_id: str,
        before_fingerprint: str,
        after_fingerprint: str,
        _token: object | None = None,
    ) -> None:
        if _token is not _TRANSITION_RECEIPT_TOKEN:
            raise TypeError(
                "TransitionReceipt must be created by the evaluated transition path"
            )
        for name, value in (
            ("receipt_id", receipt_id),
            ("event_id", event_id),
            ("event_stream_id", event_stream_id),
            ("before_phase", before_phase),
            ("after_phase", after_phase),
            ("mode", mode),
            ("source_kind", source_kind),
            ("source_id", source_id),
            ("verifier_id", verifier_id),
            ("before_fingerprint", before_fingerprint),
            ("after_fingerprint", after_fingerprint),
        ):
            if not value.strip():
                raise ValueError(f"{name} must be non-empty")
        if event_sequence < 1:
            raise ValueError("event_sequence must be >= 1")
        object.__setattr__(self, "receipt_id", receipt_id)
        object.__setattr__(self, "event_id", event_id)
        object.__setattr__(self, "event_stream_id", event_stream_id)
        object.__setattr__(self, "event_sequence", event_sequence)
        object.__setattr__(self, "before_phase", before_phase)
        object.__setattr__(self, "after_phase", after_phase)
        object.__setattr__(self, "mode", mode)
        object.__setattr__(self, "priority", float(priority))
        object.__setattr__(self, "dominant_driver", dominant_driver)
        object.__setattr__(self, "supporting_drivers", tuple(supporting_drivers))
        object.__setattr__(self, "source_kind", source_kind)
        object.__setattr__(self, "source_id", source_id)
        object.__setattr__(self, "source_revision", source_revision)
        object.__setattr__(self, "verifier_id", verifier_id)
        object.__setattr__(self, "before_fingerprint", before_fingerprint)
        object.__setattr__(self, "after_fingerprint", after_fingerprint)

    @classmethod
    def build(
        cls,
        *,
        before: CircuitState,
        after: CircuitState,
        before_phase: str,
        after_phase: str,
        decision: ArbitrationDecision,
        provenance: VerifiedProvenance,
        event: EventIdentity,
    ) -> "TransitionReceipt":
        data = {
            "event_id": event.event_id,
            "event_stream_id": event.stream_id,
            "event_sequence": event.sequence,
            "before_phase": before_phase,
            "after_phase": after_phase,
            "mode": decision.mode.value,
            "priority": decision.priority,
            "dominant_driver": decision.dominant_driver,
            "supporting_drivers": list(decision.supporting_drivers),
            "source_kind": provenance.source_kind.value,
            "source_id": provenance.source_id,
            "source_revision": provenance.source_revision,
            "verifier_id": provenance.verifier_id,
            "before_fingerprint": state_fingerprint(before),
            "after_fingerprint": state_fingerprint(after),
        }
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
        receipt_id = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return cls(
            receipt_id=receipt_id,
            event_id=event.event_id,
            event_stream_id=event.stream_id,
            event_sequence=event.sequence,
            before_phase=before_phase,
            after_phase=after_phase,
            mode=decision.mode.value,
            priority=decision.priority,
            dominant_driver=decision.dominant_driver,
            supporting_drivers=decision.supporting_drivers,
            source_kind=provenance.source_kind.value,
            source_id=provenance.source_id,
            source_revision=provenance.source_revision,
            verifier_id=provenance.verifier_id,
            before_fingerprint=data["before_fingerprint"],
            after_fingerprint=data["after_fingerprint"],
            _token=_TRANSITION_RECEIPT_TOKEN,
        )
