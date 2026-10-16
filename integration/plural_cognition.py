"""Mosaic -> V-E-R-A plurality projection: unity without erasing original voices.

This is a read-only derived view of a Mosaic Thinking Core decision receipt.
The Core reasons; specialists retain attributed positions (including dissent);
the collective receives a traceable view, not collective execution authority.

No participant is authenticated by its declared label or hash. No claim is
made about consciousness, subjective experience or actual model competence.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
from hashlib import sha256
import json
import re
from typing import Any, Mapping

_SCHEMA = "VERA_MOSAIC_PLURALITY_PROJECTION_V1"
_RECEIPT_SCHEMA = "MOSAIC_THINKING_CORE_DELIBERATION_V1"
_SHA = re.compile(r"^[0-9a-f]{64}$")
_ID = re.compile(r"^[A-Za-z][A-Za-z0-9._-]{0,127}$")
_RECEIPT_FIELDS = {
    "task", "core_initial", "core_final", "objections", "evidence",
    "status", "claim_verified", "verified_proposition_is_false",
    "effect_executed", "claim_ceiling",
}
_STATUSES = {
    "UNVERIFIED_ADVISORY", "CONTESTED_ADVISORY",
    "HOLD_UNACKNOWLEDGED_OBJECTION", "HOLD_UNVERIFIED_DISPUTE",
    "BLOCKED_BY_EVIDENCE", "EVIDENCE_SUPPORTED_ADVISORY",
    "PROPOSED_EFFECT_REQUIRES_AUTHORIZATION",
}


class PluralityProtocolError(ValueError):
    """Mismatched, stale or authority-promoting composition input."""


@dataclass(frozen=True, slots=True)
class Participant:
    participant_id: str
    role: str
    source_ref: str
    source_sha256: str
    local_state_ref: str

    def validate(self) -> None:
        if type(self.participant_id) is not str or not _ID.fullmatch(self.participant_id):
            raise PluralityProtocolError("invalid participant identity")
        if self.role not in ("CORE", "SPECIALIST", "INDEPENDENT_VERIFIER"):
            raise PluralityProtocolError("unknown participant role")
        if (type(self.source_ref) is not str or not self.source_ref.strip()
            or type(self.local_state_ref) is not str or not self.local_state_ref.strip()):
            raise PluralityProtocolError("participant requires exact source and local state references")
        if type(self.source_sha256) is not str or not _SHA.fullmatch(self.source_sha256):
            raise PluralityProtocolError("participant source digest invalid")


def _json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _digest(value: Any) -> str:
    return sha256(_json(value)).hexdigest()


def _assert(value: bool, detail: str) -> None:
    if not value:
        raise PluralityProtocolError(detail)


def _read_receipt(receipt: Any) -> dict[str, Any]:
    if is_dataclass(receipt) and not isinstance(receipt, type):
        # dataclasses.asdict preserves tuples; JSON wire format uses arrays.
        receipt = json.loads(_json(asdict(receipt)).decode("utf-8"))
    _assert(type(receipt) is dict, "Mosaic receipt must be an exact dict/dataclass")
    _assert(set(receipt) == _RECEIPT_FIELDS | {"receipt_sha256"},
            "Mosaic receipt fields do not match the exact contract")
    receipt = dict(receipt)
    if isinstance(receipt["status"], Enum):
        receipt["status"] = receipt["status"].value
    _assert(type(receipt["status"]) is str and receipt["status"] in _STATUSES,
            "unknown Mosaic status")
    _assert(type(receipt["receipt_sha256"]) is str and bool(_SHA.fullmatch(receipt["receipt_sha256"])),
            "Mosaic digest invalid")
    body = {k: receipt[k] for k in _RECEIPT_FIELDS}
    _assert(_digest({"schema": _RECEIPT_SCHEMA, **body}) == receipt["receipt_sha256"],
            "Mosaic receipt bytes or digest do not match")
    task = receipt["task"]
    _assert(type(task) is dict and set(task) == {
        "case_id", "proposition_id", "question", "consequential", "protected_effect",
    }, "Mosaic task shape mismatch")
    _assert(type(task["case_id"]) is str and bool(task["case_id"].strip())
            and type(task["proposition_id"]) is str and bool(task["proposition_id"].strip()),
            "Mosaic task identity invalid")
    _assert(type(task["question"]) is str and bool(task["question"].strip())
            and all(type(task[k]) is bool for k in ("consequential", "protected_effect")),
            "Mosaic task content invalid")
    for name in ("core_initial", "core_final"):
        p = receipt[name]
        _assert(type(p) is dict and set(p) == {
            "proposition_id", "supports", "reasoning", "acknowledged_objections",
        }, "Core position shape invalid")
        _assert(p["proposition_id"] == task["proposition_id"] and type(p["supports"]) is bool
                and type(p["reasoning"]) is str and bool(p["reasoning"].strip())
                and type(p["acknowledged_objections"]) is (list),
                "Core position invalid")
        _assert(all(type(x) is str and bool(x.strip()) for x in p["acknowledged_objections"]),
                "Invalid Core objection acknowledgments")
    _assert(type(receipt["objections"]) is list, "specialist objections must be a list")
    seen = set()
    for obj in receipt["objections"]:
        _assert(type(obj) is dict and set(obj) == {
            "specialist_id", "proposition_id", "supports", "rationale",
        }, "specialist position shape invalid")
        pid = obj["specialist_id"]
        _assert(type(pid) is str and bool(_ID.fullmatch(pid))
                and pid.casefold() != "core" and pid.casefold() not in seen,
                "duplicate or impersonated specialist")
        seen.add(pid.casefold())
        _assert(obj["proposition_id"] == task["proposition_id"]
                and type(obj["supports"]) is bool and type(obj["rationale"]) is str
                and bool(obj["rationale"].strip()), "specialist position invalid")
    evidence = receipt["evidence"]
    if evidence is not None:
        _assert(type(evidence) is dict and set(evidence) == {
            "proposition_id", "supports", "verifier_id", "evidence_ref", "rationale",
        }, "independent evidence shape invalid")
        _assert(evidence["proposition_id"] == task["proposition_id"]
                and (type(evidence["supports"]) is bool or evidence["supports"] is None)
                and type(evidence["verifier_id"]) is str
                and bool(_ID.fullmatch(evidence["verifier_id"]))
                and evidence["verifier_id"].casefold() not in seen
                and evidence["verifier_id"].casefold() != "core",
                "invalid independent verifier identity")
        _assert(type(evidence["rationale"]) is str and bool(evidence["rationale"].strip())
                and type(evidence["evidence_ref"]) is str,
                "invalid evidence rationale or reference")
    _assert(receipt["effect_executed"] is False, "source receipt claims an executed effect")
    _assert(all(type(receipt[k]) is bool for k in (
        "claim_verified", "verified_proposition_is_false",
    )), "invalid source verification flags")
    _assert(type(receipt["claim_ceiling"]) is str and bool(receipt["claim_ceiling"].strip()),
            "source qualification ceiling missing")
    return receipt


def compose_mosaic_plurality(
    receipt: Any,
    participants: Mapping[str, Participant],
) -> dict[str, Any]:
    """Project all original positions without overwriting a dissenting voice."""
    r = _read_receipt(receipt)
    _assert(type(participants) is dict, "participants must be an explicit directory")
    expected = {"core": "CORE"}
    expected.update({x["specialist_id"]: "SPECIALIST" for x in r["objections"]})
    if r["evidence"] is not None:
        expected[r["evidence"]["verifier_id"]] = "INDEPENDENT_VERIFIER"
    _assert(set(participants) == set(expected),
            "participant directory does not exactly match source contributors")
    _assert(len({key.casefold() for key in participants}) == len(participants),
            "participant identities collide under case-folding")
    directory: dict[str, dict[str, str]] = {}
    for pid, role in expected.items():
        participant = participants[pid]
        _assert(type(participant) is Participant and participant.participant_id == pid,
                "participant declared identity mismatch")
        participant.validate()
        _assert(participant.role == role, "participant role cannot be rewritten")
        directory[pid] = asdict(participant)
    initial = r["core_initial"]
    final = r["core_final"]
    contributions = [
        {"participant_id": "core", "phase": "INITIAL", "position": initial},
    ]
    contributions.extend({
        "participant_id": obj["specialist_id"], "phase": "REVIEW",
        "position": obj,
    } for obj in r["objections"])
    if r["evidence"] is not None:
        contributions.append({
            "participant_id": r["evidence"]["verifier_id"],
            "phase": "INDEPENDENT_EVIDENCE",
            "position": r["evidence"],
        })
    contributions.append({"participant_id": "core", "phase": "FINAL", "position": final})
    dissent = sorted(obj["specialist_id"] for obj in r["objections"]
                    if obj["supports"] != final["supports"])
    if not r["objections"]:
        alignment = "UNREVIEWED_CORE_POSITION"
    elif dissent:
        alignment = "DISSENT_RETAINED"
    else:
        alignment = "REVIEWERS_ALIGNED_WITH_FINAL"
    body = {
        "schema": _SCHEMA,
        "mosaic_receipt_sha256": r["receipt_sha256"],
        "case_id": r["task"]["case_id"],
        "proposition_id": r["task"]["proposition_id"],
        "participants": {key: directory[key] for key in sorted(directory)},
        "contributions": contributions,
        "final_core_position": final,
        "disagreeing_specialists": dissent,
        "alignment": alignment,
        "mosaic_decision_status": r["status"],
        "mosaic_claim_verified": r["claim_verified"],
        "source_receipt": r,
        "effect_executed": False,
        "authorization_effect": "NONE",
        "identity_or_consciousness_claim": "NONE",
        "claim_ceiling": (
            "PRESERVATION_OF_DECLARED_POSITIONS_ONLY: Participant labels and "
            "source hashes are not authentication; independent reasoning, "
            "model quality, agency, subjective experience, and integrated "
            "intelligence are not established by this projection."
        ),
    }
    return {**body, "projection_sha256": _digest(body)}


def verify_mosaic_plurality(projection: dict[str, Any]) -> None:
    """Readback against the original source receipt and participant directory."""
    _assert(type(projection) is dict and "projection_sha256" in projection,
            "projection record missing")
    directory = projection.get("participants")
    _assert(type(directory) is dict, "projection participants missing")
    try:
        participants = {key: Participant(**value) for key, value in directory.items()}
    except (TypeError, ValueError) as exc:
        raise PluralityProtocolError("invalid participant declarations") from exc
    recomputed = compose_mosaic_plurality(projection.get("source_receipt"), participants)
    _assert(_json(recomputed) == _json(projection),
            "plurality projection was altered or is incomplete")
