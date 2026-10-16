"""Offline L1 -> L2 -> VeraOS native route SOURCE evidence boundary.

The only positive observation is an exact receiver-local SQLite packet marker
and a bounded current Vera Mono task journal. The VeraOS native route is an
intended API SOURCE REFERENCE, never invoked here. GitHub author, signer, model,
provider qualification, normal-resident route and execution remain unverified.
"""
from __future__ import annotations

from typing import Any, Mapping

from .cognition_task_gate import CognitionBindingError, verify_episode_binding


VERAOS_HEAD = "5ddac1459c3a7b06f251721a14048fc26e60bda0"
NATIVE_ROUTE_BLOB = "4077908524d2f05c4e076019e34fa3b1a9f59adb"
GUEST_PROBE_BLOB = "28e4eccb6e8ae108f4980568c1fa10f9bc019d7b"
_SCHEMA = "VERAOS_SOURCE_PROVENANCE_BRIDGE_V1"
_INTENT = {
    "schema": "VERAOS_NATIVE_ROUTE_INTENT_SOURCE_V1",
    "os_source": f"git:thebrazenbeard/vera-os@{VERAOS_HEAD}",
    "module": "veraos.native_cognition",
    "admit_callable": "admit_local_text_route",
    "execute_callable": "execute_text_request",
    "provider_id": "dev:virtio-qwen4b",
    "model": "qwen3:4b-instruct",
    "port_name": "org.veraos.model.v1",
    "route_class": "COGNITION_ONLY",
}
_MODEL_DIGEST_REPORTED = "0edcdef34593eac1aa2be9c7d06c432dcf81945adca5eca2f27662c18f168ba0"


class ProvenanceBridgeError(ValueError):
    """Evidence cannot be classified even as a safe current local observation."""


def _check_receiver(receiver: Any, comment_id: int, message_id: str) -> dict:
    if type(comment_id) is not int or comment_id <= 0 or type(message_id) is not str or not message_id:
        raise ProvenanceBridgeError("invalid comment/message evidence key")
    try:
        packet = receiver.read_comment_packet_evidence(comment_id, message_id)
    except Exception as exc:
        raise ProvenanceBridgeError("receiver packet local evidence missing or invalid") from exc
    if (type(packet) is not dict or packet.get("local_pair_verified") is not True
            or packet.get("comment_id") != comment_id
            or packet.get("message_id") != message_id
            or packet.get("receiver_target") != "vera:portal"
            or type(packet.get("semantic_sha256")) is not str
            or len(packet["semantic_sha256"]) != 64
            or packet.get("source_ref") !=
            f"github:thebrazenbeard/intranel#9/comment/{comment_id}"):
        raise ProvenanceBridgeError("receiver local pairing and source mismatch")
    # A caller may hand us an object that asserts a sender, delivery, an ACK,
    # or provider consistency. Not even a matching role string authenticates it.
    if any(packet.get(flag) is not False for flag in (
        "origin_authenticated", "provider_snapshot_attested", "delivered",
        "ack_accepted", "executed",
    )):
        raise ProvenanceBridgeError("forged sender, delivery or provider attestation")
    return packet


def _check_provider(provider: Mapping[str, Any], route_intent: Mapping[str, Any]) -> dict:
    if type(route_intent) is not dict or route_intent != _INTENT:
        raise ProvenanceBridgeError("unknown native route intent or source API")
    if type(provider) is not dict or (
            provider.get("schema") != "VERA_OS_COGNITION_PROVIDER_V1"
            or provider.get("provider_id") != _INTENT["provider_id"]
            or provider.get("provider_kind") != "LOCAL_MODEL"
            or provider.get("capabilities") != ["text"]
            or provider.get("transport") != {
                "kind": "OPENAI_COMPATIBLE_HTTP",
                "attachment": "http://127.0.0.1:18766/v1",
            }
            or provider.get("qualification") != {
                "status": "PASS",
                "issuer": "thebrazenbeard/vera-os",
                "subject_sha256": _MODEL_DIGEST_REPORTED,
                "suite_sha256": "0" * 64,
            }
            or provider.get("authority") != {
                "identity_authority": False,
                "canonical_memory_write_authority": False,
                "protected_effect_authority": False,
                "browser_authority": False,
            }
            or provider.get("admission") != {
                "status": "VERAOS_ROUTE_ELIGIBLE",
                "route_class": "COGNITION_ONLY",
                "selector_owner": "thebrazenbeard/portal",
            }):
        raise ProvenanceBridgeError("provider descriptor does not match diagnostic source")
    return {
        "provider_id": provider["provider_id"],
        "claimed_qualification": provider["qualification"]["status"],
        "qualification_provenance": "TEST_ONLY_SELF_DECLARED",
        "reported_model_digest": _MODEL_DIGEST_REPORTED,
        "reported_model_bytes": 2497293803,
        "actual_model_artifact_authenticated": False,
        "independent_issuer_attested": False,
    }


def evaluate_source_route_evidence(
    *, receiver: Any, task_ledger: Any, task_id: str, episode: Any,
    binding: Mapping[str, Any], comment_id: int, message_id: str,
    coverage: Mapping[str, Any], provider: Mapping[str, Any],
    route_intent: Mapping[str, Any],
) -> dict:
    """Return local SOURCE lineage with explicit HOLD, without admitting a route.

    This is not an atomic cross-database snapshot, provider cursor, signer
    verifier, model identity, accepted task or Pre-Active run.
    """
    packet = _check_receiver(receiver, comment_id, message_id)
    try:
        bound = verify_episode_binding(task_ledger, task_id, episode, binding)
    except (CognitionBindingError, KeyError, ValueError) as exc:
        raise ProvenanceBridgeError("stale, raced or substituted task journal") from exc
    provider_source = _check_provider(provider, route_intent)
    if (type(coverage) is not dict
            or type(coverage.get("coverage_complete")) is not bool
            or coverage.get("coverage_status") not in {
                "HOLD_PRECEDING_PAGES_UNVERIFIED",
                "HOLD_COMMENT_PAGINATION_LIMIT",
                "HOLD_COMMENT_PAGE_CEILING",
                "COMPLETE_SCANNED_WINDOW",
            }
            or (coverage["coverage_complete"] is True
                and coverage["coverage_status"] != "COMPLETE_SCANNED_WINDOW")
            or (coverage["coverage_complete"] is False
                and coverage["coverage_status"] == "COMPLETE_SCANNED_WINDOW")):
        raise ProvenanceBridgeError("inconsistent or unsupported comment coverage")
    # Second bound-read can reject races within this procedure; it is NOT CAS
    # and says nothing about a task write AFTER the final read.
    try:
        second = verify_episode_binding(task_ledger, task_id, episode, binding)
    except (CognitionBindingError, KeyError, ValueError) as exc:
        raise ProvenanceBridgeError("stale or raced task journal after route assessment") from exc
    if second != bound or bound.get("effect_authority") is not False or (
            bound.get("accepted_as_task_result") is not False
            or bound.get("executed") is not False
            or bound.get("independent_source_attestation") is not False):
        raise ProvenanceBridgeError("task binding changed or falsely asserts authority")
    return {
        "schema": _SCHEMA,
        "verdict": ("HOLD_INCOMPLETE_COMMENT_COVERAGE"
                    if not coverage["coverage_complete"]
                    else "HOLD_UNATTESTED_SENDER_AND_PROVIDER"),
        "message": {
            "comment_id": comment_id,
            "message_id": message_id,
            "conversation_id": packet["conversation_id"],
            "semantic_sha256": packet["semantic_sha256"],
            "receiver_target": packet["receiver_target"],
            "local_pair_verified": True,
        },
        "task": {
            "task_id": task_id,
            "task_journal_head": bound["task_journal_head"],
            "task_packet_digest": bound["packet_digest"],
            "cognition_binding_digest": bound["binding_digest"],
            "cognition_source_status": bound["status"],
        },
        "native_route": dict(route_intent),
        "provider": provider_source,
        "coverage": dict(coverage),
        "origin_authenticated": False,
        "message_task_causal_link_attested": False,
        "provider_authenticated": False,
        "normal_resident_route_admitted": False,
        "accepted_as_task_result": False,
        "executed": False,
        "protected_effect_authority": False,
    }


# This is deliberately in the existing integration bridge, NOT a new
# task ledger, API service, scheduler, resident route, or effect dispatcher.
def prepare_source_linked_veraos_route(
    *, receiver: Any, task_ledger: Any, task_id: str, episode: Any,
    binding: Mapping[str, Any], comment_id: int, message_id: str,
    coverage: Mapping[str, Any], provider: Mapping[str, Any],
    route_intent: Mapping[str, Any], advertisements: tuple[Any, ...],
    receipt_path: Any = None,
) -> dict:
    """Make a durable no-effect *proposal* from real Mono/PORTAL source.

    A short SQLite BEGIN IMMEDIATE serializes proposal construction with
    ALL TaskExecutionLedger.append() writers to the SAME ledger file. The
    transaction does not commit acceptance, atomically bind another database,
    attest GitHub authorship, or protect a future dispatch after release.
    """
    import hashlib
    import json
    import sqlite3
    from .vera_portal_runtime import save_receipt
    from vera_core.portal_task_handoff import (
        export_portal_route_request, verify_portal_route_assessment,
    )
    from portal.vera_task_handoff import assess_vera_task_route
    from .cognition_task_gate import CognitionBindingError

    if type(advertisements) is not tuple:
        raise ProvenanceBridgeError("caller advertisements must be a typed tuple")
    try:
        # Uses Mono's existing SQLite journal, not a sibling state store.
        # BEGIN IMMEDIATE is a bounded SOURCE cut, NOT a write-CAS or permit.
        with sqlite3.connect(task_ledger.path, timeout=10) as transaction:
            transaction.execute("BEGIN IMMEDIATE")
            evidence = evaluate_source_route_evidence(
                receiver=receiver, task_ledger=task_ledger,
                task_id=task_id, episode=episode, binding=binding,
                comment_id=comment_id, message_id=message_id,
                coverage=coverage, provider=provider, route_intent=route_intent,
            )
            current = task_ledger.read(task_id)
            if current.closed or (
                current.opened_lifecycle_evidence_digest !=
                evidence["message"]["semantic_sha256"]
            ):
                raise ProvenanceBridgeError(
                    "task opening did not declare this local source packet digest"
                )
            if current.journal_head_digest != binding["task_journal_head"]:
                raise ProvenanceBridgeError("task journal advanced during route proposal")

            # Reuse Mono and PORTAL's actual exact-source contract. The
            # NO_PROTECTED_EFFECT resolver is advisory, not the VeraOS
            # COGNITION_TURN route admission and NOT a model permit.
            request = export_portal_route_request(
                task_ledger, task_id, node_id="veraos",
                target_kind="MODEL", target_id="qwen3:4b-instruct",
                required_capabilities=("text",),
            )
            assessment = assess_vera_task_route(request, advertisements)
            checked = verify_portal_route_assessment(
                task_ledger, request, assessment,
            )
            selected = checked["state"] == "ROUTE_PROPOSED" and checked["route"] == {
                "adapter_id": "pre-active-openai-compatible",
                "route_id": "dev:virtio-qwen4b",
            }
            task_text = current.packet.subject
            if type(task_text) is not str or not task_text.strip() or len(task_text) > 2048:
                raise ProvenanceBridgeError("task text violates VeraOS native request size")
            stable_seed = json.dumps(
                {
                    "request_digest": request["request_digest"],
                    "packet_sha256": evidence["message"]["semantic_sha256"],
                    "task_id": task_id,
                    "model": route_intent["model"],
                }, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
            )
            request_id = "mono-" + hashlib.sha256(stable_seed.encode("utf-8")).hexdigest()
            native_call = ({
                "module": "veraos.native_cognition",
                "callable": "execute_text_request",
                "task": task_text.strip(),
                "request_id": request_id,
                "admitted_route_required": True,
                "called": False,
            } if selected else None)
            status = ("ROUTE_PROPOSED_UNATTESTED"
                      if selected else "HELD_UNQUALIFIED_ROUTE")
            body = {
                "schema": "VERAOS_MONO_PORTAL_SOURCE_PROPOSAL_V1",
                "status": status,
                "source_evidence": evidence,
                "portal_request": request,
                "portal_assessment": checked,
                "native_call": native_call,
                "task_opening_digest_matches_local_packet": True,
                "causal_origin_authenticated": False,
                "advertisements_authenticated": False,
                "coverage": dict(coverage),
                "origin_authenticated": False,
                "normal_resident_route_admitted": False,
                "accepted_as_task_result": False,
                "protected_effect_authority": False,
                "executed": False,
            }
            canonical = json.dumps(
                body, ensure_ascii=False, sort_keys=True,
                separators=(",", ":"), allow_nan=False,
            )
            result = {
                **body,
                "receipt_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
            }
            if receipt_path is not None:
                try:
                    save_receipt(receipt_path, result)
                except (OSError, ValueError) as exc:
                    raise ProvenanceBridgeError(
                        "receipt cannot be durably created without overwrite"
                    ) from exc
            # Releasing the reservation leaves the proposal revocable by ANY
            # later task append. An execution call would require a new,
            # authorized, atomic head-CAS inside Mono's ownership boundary.
            return result
    except (sqlite3.Error, CognitionBindingError, KeyError) as exc:
        raise ProvenanceBridgeError("task journal source proposal unavailable") from exc


def verify_source_linked_veraos_route(
    receipt_path: Any, *, receiver: Any, task_ledger: Any,
    task_id: str, episode: Any, binding: Mapping[str, Any],
    comment_id: int, message_id: str, coverage: Mapping[str, Any],
    provider: Mapping[str, Any], route_intent: Mapping[str, Any],
    advertisements: tuple[Any, ...],
) -> dict:
    """Revalidate an existing local proposal; NEVER approve actual dispatch."""
    from .vera_portal_runtime import load_json
    try:
        stored = load_json(receipt_path, 32768)
    except (OSError, ValueError) as exc:
        raise ProvenanceBridgeError("receipt absent, invalid or oversized") from exc
    if type(stored) is not dict:
        raise ProvenanceBridgeError("receipt payload must be object")
    current = prepare_source_linked_veraos_route(
        receiver=receiver, task_ledger=task_ledger,
        task_id=task_id, episode=episode, binding=binding,
        comment_id=comment_id, message_id=message_id,
        coverage=coverage, provider=provider, route_intent=route_intent,
        advertisements=advertisements,
    )
    if stored != current:
        raise ProvenanceBridgeError("receipt tampered, stale or substituted")
    return current
