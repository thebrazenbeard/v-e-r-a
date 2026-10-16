"""Read-only Vera Mono task ↔ Training cognition receipt currentness gate.

This is NOT a cognitive adoption, independent evidence, transport, or effect
authority. The caller must independently qualify imported source modules.
"""
from __future__ import annotations

from hashlib import sha256
import json
import re
from typing import Any, Mapping

TRAINING_HEAD = "a271bf25bdbcd3731ac17588ef475ba1bf74f96f"
TRAINING_SUBJECT = f"git:thebrazenbeard/model-training@{TRAINING_HEAD}"
_SCHEMA = "VERA_COGNITION_TASK_SOURCE_BINDING_V1"
_SHA = re.compile(r"^[0-9a-f]{64}$")
_RECEIPT_KEYS = frozenset({
    "schema", "task_id", "contributions", "dissent", "core_semantic_plan",
    "mosaic_handoff", "cricket_review", "status", "identity_effect",
    "shared_memory_effect", "authority_effect", "executed_effect",
    "model_independence", "cognitive_gain",
})


class CognitionBindingError(ValueError):
    pass


def _canonical(obj: Any) -> bytes:
    try:
        raw = json.dumps(obj, sort_keys=True, ensure_ascii=False,
                         allow_nan=False, separators=(",", ":")).encode("utf8")
        if len(raw) > 32768:
            raise CognitionBindingError("oversized source receipt")
        if json.loads(raw) != obj:
            raise CognitionBindingError("noncanonical object")
        return raw
    except (TypeError, ValueError, OverflowError) as exc:
        raise CognitionBindingError("invalid receipt values") from exc


def _episode_dict(episode: Any) -> dict:
    candidate = episode.as_dict() if hasattr(episode, "as_dict") else episode
    if type(candidate) is not dict or set(candidate) != _RECEIPT_KEYS:
        raise CognitionBindingError("unexpected training receipt shape")
    if candidate["schema"] != "VERA_PARTICIPATING_COGNITION_SOURCE_V1":
        raise CognitionBindingError("unsupported training receipt")
    if not isinstance(candidate["task_id"], str) or not candidate["task_id"]:
        raise CognitionBindingError("missing task identity")
    for k in ("identity_effect", "shared_memory_effect",
              "authority_effect", "executed_effect"):
        if candidate[k] != "NONE":
            raise CognitionBindingError("forbidden cognition effect promotion")
    if (candidate["model_independence"] != "NOT_ESTABLISHED"
            or candidate["cognitive_gain"] != "NOT_ESTABLISHED"):
        raise CognitionBindingError("unverified model/cognitive qualification")
    if candidate["status"] not in {
        "SOURCE_EXPERIMENT_ONLY", "SEMANTIC_TRANSFER_UNREPRESENTABLE",
        "UNRESOLVED_REFERENT_OR_SCOPE",
    }:
        raise CognitionBindingError("unknown training result state")
    contributions = candidate["contributions"]
    if type(contributions) is not list or len(contributions) != 2:
        raise CognitionBindingError("two attributed contributions required")
    seen = set()
    digests = []
    for c in contributions:
        if type(c) is not dict or set(c) != {
            "participant", "claim", "claim_sha256", "task_id"
        } or type(c["participant"]) is not dict or type(c["claim"]) is not dict:
            raise CognitionBindingError("malformed contribution")
        p, claim = c["participant"], c["claim"]
        if c["task_id"] != candidate["task_id"]:
            raise CognitionBindingError("cross-task contribution")
        if any(p.get(pk) != claim.get(ck) for pk, ck in (
            ("identity", "shared_identity"), ("node_id", "node_id"),
            ("agent_id", "agent_id"), ("model_sha256", "model_digest"),
        )):
            raise CognitionBindingError("participant/claim origin mismatch")
        key = (p.get("node_id"), p.get("agent_id"))
        if any(not isinstance(x, str) or not x for x in key) or key in seen:
            raise CognitionBindingError("duplicate or invalid logical participant")
        seen.add(key)
        digest = sha256(_canonical(claim)).hexdigest()
        if c["claim_sha256"] != digest:
            raise CognitionBindingError("attributed claim digest mismatch")
        digests.append(digest)
    dissent = candidate["dissent"]
    if (type(dissent) is not dict
            or dissent.get("source_digests") != digests
            or dissent.get("accepted_as_fact") is not False
            or dissent.get("independence_proven") is not False):
        raise CognitionBindingError("dissent provenance/evidence escalation")
    semantic = candidate["core_semantic_plan"]
    if (type(semantic) is not dict
            or semantic.get("authorization_effect") != "NONE"
            or semantic.get("semantic_equivalence") != "NOT_ESTABLISHED"):
        raise CognitionBindingError("unverified semantic transfer authority")
    cricket = candidate["cricket_review"]
    if type(cricket) is not dict or cricket.get("disposition") not in (
        "PASS", "CHALLENGE", "BLOCK"
    ) or type(cricket.get("findings")) is not list:
        raise CognitionBindingError("malformed Cricket verdict")
    if any(type(f) is not dict or f.get("severity") not in (
        "NOTE", "CHALLENGE", "BLOCK"
    ) for f in cricket["findings"]):
        raise CognitionBindingError("malformed Cricket finding")
    if cricket["disposition"] == "PASS" and any(
        f["severity"] == "BLOCK" for f in cricket["findings"]
    ):
        raise CognitionBindingError("Cricket PASS contradicts BLOCK finding")
    _canonical(candidate)
    return candidate


def bind_episode(ledger: Any, task_id: str, episode: Any, *,
                 training_subject: str = TRAINING_SUBJECT) -> dict:
    """Bind source observations to one current durable task journal head."""
    if training_subject != TRAINING_SUBJECT:
        raise CognitionBindingError("Training exact source binding changed")
    current = _episode_dict(episode)
    if current["task_id"] != task_id:
        raise CognitionBindingError("episode does not belong to current task")
    ledger.verify_chain()
    task = ledger.read(task_id)
    if task.closed:
        raise CognitionBindingError("cannot bind a closed task")
    head = task.journal_head_digest
    if not isinstance(head, str) or _SHA.fullmatch(head) is None:
        raise CognitionBindingError("missing durable journal head")
    digest = sha256(_canonical(current)).hexdigest()
    held = (current["cricket_review"]["disposition"] == "BLOCK"
            or current["status"] == "SEMANTIC_TRANSFER_UNREPRESENTABLE")
    body = {
        "schema": _SCHEMA, "task_id": task_id,
        "packet_digest": task.packet.packet_digest,
        "task_journal_head": head,
        "training_source_subject": TRAINING_SUBJECT,
        "episode_digest": digest,
        "status": "HELD_SOURCE_REVIEW" if held else "OBSERVED_UNATTESTED",
        "independent_source_attestation": False,
        "cognitive_gain": "NOT_ESTABLISHED",
        "accepted_as_task_result": False,
        "effect_authority": False,
        "executed": False,
    }
    return {**body, "binding_digest": sha256(_canonical(body)).hexdigest()}


def verify_episode_binding(ledger: Any, task_id: str, episode: Any,
                           binding: Mapping[str, Any]) -> dict:
    """Read current ledger again: any task-journal advance invalidates binding."""
    fresh = bind_episode(ledger, task_id, episode)
    if type(binding) is not dict or set(binding) != set(fresh) or binding != fresh:
        raise CognitionBindingError("stale, substituted, or modified task/cognition binding")
    return fresh
