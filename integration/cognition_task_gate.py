"""Read-only Vera Mono task ↔ Training cognition receipt currentness gate.

This is NOT a cognitive adoption, independent evidence, transport, or effect
authority. The caller must independently qualify imported source modules.
"""
from __future__ import annotations

from hashlib import sha256
import json
import re
from typing import Any, Mapping

TRAINING_HEAD = "06995fd7c43230e1ccc33cab196dcd55ffc363d9"
TRAINING_SUBJECT = f"git:thebrazenbeard/model-training@{TRAINING_HEAD}"
_SCHEMA = "VERA_COGNITION_TASK_SOURCE_BINDING_V1"
_SHA = re.compile(r"^[0-9a-f]{64}$")
_DISSENT_CLASSES = frozenset({
    "EVIDENCE_CONFLICT_FOR_REVIEW", "SAME_CLAIM",
    "DIFFERENT_PROPOSITION", "DIFFERENT_SCOPE", "DIFFERENT_REVISION",
    "UNVERIFIED_DISSENT", "MIXED_CLAIM_TYPES",
    "SELF_OR_CORRELATED_CLAIMS",
})
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
        "UNRESOLVED_REFERENT_OR_SCOPE", "CRICKET_BLOCKED",
        "CRICKET_CHALLENGED",
    }:
        raise CognitionBindingError("unknown training result state")
    contributions = candidate["contributions"]
    if type(contributions) is not list or len(contributions) != 2:
        raise CognitionBindingError("two attributed contributions required")
    seen = set()
    runtimes = set()
    correlated_runtime = False
    evidence_groups = set()
    correlated_evidence_group = False
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
        key = p.get("agent_id")
        if type(key) is not str or not key or key in seen:
            raise CognitionBindingError("duplicate or invalid logical participant")
        seen.add(key)
        runtime_id = p.get("runtime_instance_id")
        if type(runtime_id) is not str or not runtime_id:
            raise CognitionBindingError("invalid participant runtime identity")
        if runtime_id in runtimes:
            correlated_runtime = True
        runtimes.add(runtime_id)
        evidence_group = claim.get("evidence_group")
        if type(evidence_group) is not str or not evidence_group:
            raise CognitionBindingError("missing attributed evidence group")
        if evidence_group in evidence_groups:
            correlated_evidence_group = True
        evidence_groups.add(evidence_group)
        digest = sha256(_canonical(claim)).hexdigest()
        if c["claim_sha256"] != digest:
            raise CognitionBindingError("attributed claim digest mismatch")
        digests.append(digest)
    dissent = candidate["dissent"]
    if (type(dissent) is not dict
            or set(dissent) != {
                "classification", "source_digests", "challenge_for_review",
                "accepted_as_fact", "independence_proven",
            }
            or dissent.get("source_digests") != digests
            or dissent.get("accepted_as_fact") is not False
            or dissent.get("independence_proven") is not False):
        raise CognitionBindingError("dissent provenance/evidence escalation")
    dissent_class = dissent.get("classification")
    if (dissent_class not in _DISSENT_CLASSES
            or type(dissent.get("challenge_for_review")) is not bool
            or dissent["challenge_for_review"] != (
                dissent_class == "EVIDENCE_CONFLICT_FOR_REVIEW"
            )):
        raise CognitionBindingError("dissent review classification/flag contradiction")
    if dissent_class == "EVIDENCE_CONFLICT_FOR_REVIEW" and (
            correlated_runtime or correlated_evidence_group):
        raise CognitionBindingError(
            "correlated evidence group or runtime cannot supply independent review"
        )
    semantic = candidate["core_semantic_plan"]
    if (type(semantic) is not dict
            or semantic.get("authorization_effect") != "NONE"
            or semantic.get("semantic_equivalence") != "NOT_ESTABLISHED"):
        raise CognitionBindingError("unverified semantic transfer authority")
    # Independent source-receipt consistency guard: caller-supplied JSON
    # must not relabel missing capabilities as an EXACT transfer.
    required = semantic.get("required_capabilities")
    missing = semantic.get("missing_capabilities")
    unresolved = semantic.get("unresolved_capabilities")
    native = semantic.get("native_capabilities")
    rewrites = semantic.get("rewrites")
    arrays = (required, missing, unresolved, native)
    if any(type(arr) is not list or
           any(type(x) is not str or not x for x in arr) or
           len(arr) != len(set(arr)) for arr in arrays):
        raise CognitionBindingError("invalid semantic capability inventory")
    if (not set(missing) <= set(required)
            or not set(native) <= set(required)
            or set(missing) & set(native)
            or not set(unresolved) <= set(missing)):
        raise CognitionBindingError("semantic capability inventory mismatch")
    labels = {"EXACT": 0, "CONSTRUCTIVE": 1,
              "LOSSY": 2, "UNREPRESENTABLE": 3}
    keys = {"source_capability", "rule_name", "fidelity", "description"}
    if type(rewrites) is not list or any(
        type(r) is not dict or set(r) != keys or
        any(type(r[k]) is not str or not r[k] for k in keys) or
        r["fidelity"] not in labels for r in rewrites
    ):
        raise CognitionBindingError("invalid semantic rewrite entries")
    rewritten = [r["source_capability"] for r in rewrites]
    if (len(rewritten) != len(set(rewritten))
            or set(rewritten) | set(unresolved) != set(missing)
            or set(rewritten) & set(unresolved)):
        raise CognitionBindingError("semantic rewrite coverage mismatch")
    severity = ("UNREPRESENTABLE" if unresolved else
                max(("EXACT", *(r["fidelity"] for r in rewrites)),
                    key=labels.__getitem__))
    if semantic.get("fidelity") != severity:
        raise CognitionBindingError("semantic rewrite fidelity contradicts plan")
    cricket = candidate["cricket_review"]
    if type(cricket) is not dict or cricket.get("disposition") not in (
        "PASS", "CHALLENGE", "BLOCK"
    ) or type(cricket.get("findings")) is not list:
        raise CognitionBindingError("malformed Cricket verdict")
    if any(type(f) is not dict or f.get("severity") not in (
        "NOTE", "CHALLENGE", "BLOCK"
    ) for f in cricket["findings"]):
        raise CognitionBindingError("malformed Cricket finding")
    # Full real Cricket precedence: BLOCK > CHALLENGE > PASS.
    severities = {f["severity"] for f in cricket["findings"]}
    expected_disposition = ("BLOCK" if "BLOCK" in severities else
                            "CHALLENGE" if "CHALLENGE" in severities else "PASS")
    if cricket["disposition"] != expected_disposition:
        raise CognitionBindingError("Cricket disposition contradicts finding precedence")
    fidelity = semantic.get("fidelity")
    expected_status = ("CRICKET_BLOCKED" if expected_disposition == "BLOCK" else
                       "SEMANTIC_TRANSFER_UNREPRESENTABLE"
                       if fidelity == "UNREPRESENTABLE" else
                       "CRICKET_CHALLENGED" if expected_disposition == "CHALLENGE" else
                       "UNRESOLVED_REFERENT_OR_SCOPE"
                       if dissent_class in ("DIFFERENT_PROPOSITION",
                                           "DIFFERENT_SCOPE", "DIFFERENT_REVISION") else
                       "SOURCE_EXPERIMENT_ONLY")
    if candidate["status"] != expected_status:
        raise CognitionBindingError("Training episode status contradicts source receipts")
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
    # Two independent journal reads provide a bounded race detector, not
    # an atomic snapshot or authority to accept a task result.
    first_chain = ledger.verify_chain()
    first_task = ledger.read(task_id)
    second_chain = ledger.verify_chain()
    task = ledger.read(task_id)
    if (first_chain != second_chain
            or first_task.journal_head_digest != task.journal_head_digest
            or first_task.packet.packet_digest != task.packet.packet_digest
            or first_task.closed != task.closed):
        raise CognitionBindingError("task journal advanced during binding")
    if task.closed:
        raise CognitionBindingError("cannot bind a closed task")
    head = task.journal_head_digest
    if not isinstance(head, str) or _SHA.fullmatch(head) is None:
        raise CognitionBindingError("missing durable journal head")
    digest = sha256(_canonical(current)).hexdigest()
    runtimes = [x["participant"]["runtime_instance_id"] for x in current["contributions"]]
    held = (current["status"] != "SOURCE_EXPERIMENT_ONLY"
            or current["dissent"]["classification"] in {
                "EVIDENCE_CONFLICT_FOR_REVIEW",
                "MIXED_CLAIM_TYPES", "SELF_OR_CORRELATED_CLAIMS",
            }
            or len(set(runtimes)) != len(runtimes))
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
