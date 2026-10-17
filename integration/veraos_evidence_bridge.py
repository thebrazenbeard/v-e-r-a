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


def checkpoint_source_linked_fixture(
    receipt_path: Any, *, receiver: Any, task_ledger: Any,
    task_id: str, episode: Any, binding: Mapping[str, Any],
    comment_id: int, message_id: str, coverage: Mapping[str, Any],
    provider: Mapping[str, Any], route_intent: Mapping[str, Any],
    advertisements: tuple[Any, ...],
) -> dict:
    """CAS-append a canonical Mono checkpoint for SYNTHETIC SOURCE use only.

    This function does NOT accept a route for execution or grant provider,
    model, identity, protected effect, or task-result authority. The final
    currentness check is conservative: any concurrent post-CAS journal
    advance revokes the returned source fixture eligibility immediately.
    """
    from vera_core.task_execution import TaskExecutionError
    proposed = verify_source_linked_veraos_route(
        receipt_path, receiver=receiver, task_ledger=task_ledger,
        task_id=task_id, episode=episode, binding=binding,
        comment_id=comment_id, message_id=message_id, coverage=coverage,
        provider=provider, route_intent=route_intent,
        advertisements=advertisements,
    )
    call = proposed["native_call"]
    request = proposed["portal_request"]
    if (proposed["status"] != "ROUTE_PROPOSED_UNATTESTED"
            or type(call) is not dict
            or proposed["portal_assessment"]["state"] != "ROUTE_PROPOSED"
            or request["requested_effect"] != "NO_PROTECTED_EFFECT"
            or any(proposed[flag] is not False for flag in (
                "origin_authenticated", "advertisements_authenticated",
                "normal_resident_route_admitted",
                "accepted_as_task_result", "protected_effect_authority",
                "executed",
            ))):
        raise ProvenanceBridgeError(
            "source checkpoint requires exact non-authoritative advisory"
        )
    event_id = f"{task_id}:CHECKPOINT:source-fixture-{call['request_id']}"
    # Existing canonical Mono TASK_CHECKPOINT journal; no new store, router,
    # event type, worker or scheduler. The expected-head check lives INSIDE
    # Mono.append's BEGIN IMMEDIATE transaction, not in an unlocked read.
    try:
        state = task_ledger.checkpoint(
            task_id, f"source-fixture-{call['request_id']}",
            completed_evidence=(
                "receiver-local:" + proposed["source_evidence"]["message"]["semantic_sha256"],
                "portal-advisory:" + proposed["portal_assessment"]["assessment_digest"],
            ),
            blockers=(
                "source sender/provider not authenticated",
                "real resident admission and dispatch authority not granted",
            ),
            protected_effects_still_gated=("COGNITION_TURN",),
            next_frontier="synthetic no-effect Pre-Active source fixture only",
            lifecycle_evidence_digest=proposed["receipt_sha256"],
            expected_head=request["task_journal_head"],
        )
    except (TaskExecutionError, ValueError, KeyError) as exc:
        raise ProvenanceBridgeError(
            "stale expected task journal head; source fixture CAS denied"
        ) from exc
    events = [event for event in task_ledger.events(task_id)
              if event.event_id == event_id]
    if (len(events) != 1 or events[0].event_type != "TASK_CHECKPOINT"
            or state.journal_head_digest != events[0].event_digest
            or task_ledger.head != events[0].event_digest):
        raise ProvenanceBridgeError(
            "stale task journal after fixture CAS; no dispatch eligible"
        )
    return {
        "schema": "VERA_MONO_SOURCE_FIXTURE_CHECKPOINT_V1",
        "status": "SOURCE_FIXTURE_CHECKPOINT_RECORDED",
        "task_id": task_id,
        "task_packet_digest": request["task_packet_digest"],
        "source_digest": proposed["source_evidence"]["message"]["semantic_sha256"],
        "predecessor_journal_head": request["task_journal_head"],
        "checkpoint_event_id": event_id,
        "checkpoint_journal_head": events[0].event_digest,
        "request_id": call["request_id"],
        "route_id": proposed["portal_assessment"]["route"]["route_id"],
        "task": call["task"],
        "requested_effect": "NO_PROTECTED_EFFECT",
        "advisory_state": "ROUTE_PROPOSED",
        "fixture_only": True,
        "dispatch_accepted": False,
        "model_admitted": False,
        "accepted_as_task_result": False,
        "effect_authority": False,
        "executed": False,
    }


# Local graphical input is an IN-PROCESS SYNTHETIC source fixture, NOT a
# registered OS endpoint, signed user session, model grant or installed UI.
# It deliberately does not require any remote GitHub/ChatGPT message.
def _local_json_digest(value: dict) -> str:
    import hashlib
    import json
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf8")).hexdigest()


def _check_local_intake(intake: Any) -> None:
    import re
    keys = {"schema", "conversation_id", "message_id", "text", "task_id",
            "source_digest", "task_packet_digest", "opened_journal_head",
            "origin_authenticated", "fixture_only"}
    if type(intake) is not dict or set(intake) != keys:
        raise ProvenanceBridgeError("local UI intake has unknown or missing fields")
    for key in ("conversation_id", "message_id"):
        value = intake[key]
        if type(value) is not str or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,95}", value) is None:
            raise ProvenanceBridgeError("invalid local UI conversation/message locator")
    text = intake["text"]
    if type(text) is not str or not text.strip() or text != text.strip() or len(text) > 2048:
        raise ProvenanceBridgeError("local UI text is not an exact bounded request")
    ident = _local_json_digest({
        "schema": "VERAOS_LOCAL_MESSAGE_KEY_V1",
        "conversation_id": intake["conversation_id"],
        "message_id": intake["message_id"],
    })
    source = _local_json_digest({
        "schema": "VERAOS_LOCAL_UI_INTAKE_SOURCE_V1",
        "conversation_id": intake["conversation_id"],
        "message_id": intake["message_id"], "text": text,
    })
    if (intake["schema"] != "VERAOS_LOCAL_UI_INTAKE_V1" or
            intake["task_id"] != "ui-" + ident or intake["source_digest"] != source or
            intake["origin_authenticated"] is not False or
            intake["fixture_only"] is not True or
            type(intake["opened_journal_head"]) is not str or
            len(intake["opened_journal_head"]) != 64):
        raise ProvenanceBridgeError("local UI intake identity/source substitution")


def open_local_cognition_fixture(
    *, ledger: Any, conversation_id: str, message_id: str, text: str,
) -> dict:
    """Open/replay ONE canonical Vera Mono task, never a conversation store."""
    from vera_core.task_execution import TaskPacket, TaskExecutionError
    candidate = {
        "schema": "VERAOS_LOCAL_UI_INTAKE_V1",
        "conversation_id": conversation_id, "message_id": message_id,
        "text": text,
        "task_id": "ui-" + _local_json_digest({
            "schema": "VERAOS_LOCAL_MESSAGE_KEY_V1",
            "conversation_id": conversation_id, "message_id": message_id,
        }),
        "source_digest": _local_json_digest({
            "schema": "VERAOS_LOCAL_UI_INTAKE_SOURCE_V1",
            "conversation_id": conversation_id, "message_id": message_id,
            "text": text,
        }),
        "task_packet_digest": "0" * 64,
        "opened_journal_head": ledger.head,
        "origin_authenticated": False, "fixture_only": True,
    }
    _check_local_intake(candidate)
    packet = TaskPacket(
        purpose="Source-only local text cognition fixture",
        subject=text,
        completion_state="Observed synthetic response held pending trusted resident acceptance",
        evidence_requirements=("current canonical task", "Pre-Active run readback"),
        writable_scope=(),
        non_targets=("model installation", "protected effect", "canonical memory"),
        forbidden_shortcuts_or_effects=("no real provider admission", "no dispatch by advisory"),
        priority_order=("task provenance", "request fidelity", "fail-closed replay"),
        unknowns=("UI identity not authenticated", "model admission not installed"),
        return_shape=("event_id", "run_id", "literal synthetic text", "HOLD"),
        relevant_surfaces=("source", "workspace/coordination"),
    )
    try:
        state = ledger.open_task(
            candidate["task_id"], packet,
            lifecycle_evidence_digest=candidate["source_digest"],
        )
    except (TaskExecutionError, ValueError, KeyError) as exc:
        raise ProvenanceBridgeError("local message identity/text collision") from exc
    if (state.packet.subject != text or
            state.opened_lifecycle_evidence_digest != candidate["source_digest"]):
        raise ProvenanceBridgeError("local source intake task identity mismatch")
    opening = ledger.events(candidate["task_id"])
    if not opening or opening[0].event_type != "TASK_OPENED":
        raise ProvenanceBridgeError("local message has no canonical opening event")
    candidate["task_packet_digest"] = state.packet.packet_digest
    # Always return the actual immutable opening event's head, NOT a fresh
    # global head after a replay. Re-opening a completed task cannot mint a
    # second route checkpoint by laundering the new head as an old opening.
    candidate["opened_journal_head"] = opening[0].event_digest
    return candidate


def accept_local_cognition_fixture(
    *, ledger: Any, intake: dict, advertisements: tuple,
) -> dict:
    """Durable fixture-only Mono CAS after the real P.O.R.T.A.L. advisory."""
    from vera_core.task_execution import TaskExecutionError
    from vera_core.portal_task_handoff import (
        export_portal_route_request, verify_portal_route_assessment,
    )
    from portal.vera_task_handoff import assess_vera_task_route
    _check_local_intake(intake)
    if type(advertisements) is not tuple:
        raise ProvenanceBridgeError("invalid advisory source collection")
    try:
        state = ledger.read(intake["task_id"])
        if (state.closed or state.active_dependencies or
                state.latest_checkpoint is not None or
                len(ledger.events(intake["task_id"])) != 1 or
                state.unresolved_correction_ids or
                state.opened_lifecycle_evidence_digest != intake["source_digest"] or
                state.packet.packet_digest != intake["task_packet_digest"] or
                state.packet.subject != intake["text"] or
                ledger.events(intake["task_id"])[-1].event_digest != intake["opened_journal_head"]):
            raise ProvenanceBridgeError("local task changed or dependencies not resolved")
        request = export_portal_route_request(
            ledger, intake["task_id"], node_id="veraos",
            target_kind="MODEL", target_id="qwen3:4b-instruct",
            required_capabilities=("text",),
        )
        assessed = assess_vera_task_route(request, advertisements)
        verified = verify_portal_route_assessment(ledger, request, assessed)
        route = verified["route"]
        if (verified["state"] != "ROUTE_PROPOSED" or
                route != {
                    "adapter_id": "pre-active-openai-compatible",
                    "route_id": "dev:virtio-qwen4b",
                } or request["requested_effect"] != "NO_PROTECTED_EFFECT"):
            raise ProvenanceBridgeError("no exact no-effect synthetic advisory route")
        if ledger.events(intake["task_id"])[-1].event_digest != intake["opened_journal_head"]:
            raise ProvenanceBridgeError("stale task head at route assessment")
        rid = "ui-" + _local_json_digest({
            "task_id": intake["task_id"], "source_digest": intake["source_digest"],
            "request_digest": request["request_digest"],
            "route_id": route["route_id"],
        })
        source_receipt = _local_json_digest({
            "schema": "VERAOS_LOCAL_COGNITION_SOURCE_DECISION_V1",
            "intake": intake, "portal_request": request, "assessment": verified,
            "request_id": rid,
        })
        checkpoint_id = "local-fixture-" + rid
        # Keep the verified source intake and route seed inside the existing
        # immutable Mono checkpoint, so a cold process can recover and bind
        # the same message without a third database or a volatile dict.
        import json
        acceptance_seed = {
            "intake": intake, "request_id": rid,
            "route_id": route["route_id"],
            "source_receipt_sha256": source_receipt,
            "advisory_global_head": request["task_journal_head"],
        }
        seed_json = json.dumps(acceptance_seed, sort_keys=True,
                               separators=(",", ":"), ensure_ascii=False)
        latest = ledger.checkpoint(
            intake["task_id"], checkpoint_id,
            completed_evidence=(
                "ui-source:" + intake["source_digest"],
                "portal-advisory:" + verified["assessment_digest"],
                "local-source-seed-json:" + seed_json,
            ),
            blockers=(
                "local user identity unverified", "resident provider not admitted",
                "result cannot update canonical task authority",
            ),
            protected_effects_still_gated=("COGNITION_TURN",),
            next_frontier="no-effect synthetic Pre-Active source fixture",
            lifecycle_evidence_digest=source_receipt,
            expected_task_head=intake["opened_journal_head"],
        )
        event_id = intake["task_id"] + ":CHECKPOINT:" + checkpoint_id
        event = [x for x in ledger.events(intake["task_id"]) if x.event_id == event_id]
        if (len(event) != 1 or ledger.events(intake["task_id"])[-1].event_digest != event[0].event_digest):
            raise ProvenanceBridgeError("task checkpoint advanced; no synthetic route")
    except (TaskExecutionError, KeyError, ValueError, TypeError) as exc:
        raise ProvenanceBridgeError("stale local fixture CAS or forged route") from exc
    return {
        "schema": "VERAOS_LOCAL_COGNITION_FIXTURE_ACCEPTANCE_V1",
        "task_id": intake["task_id"],
        "task_packet_digest": intake["task_packet_digest"],
        "source_digest": intake["source_digest"],
        "conversation_id": intake["conversation_id"],
        "message_id": intake["message_id"],
        "task": intake["text"],
        "request_id": rid,
        "route_id": route["route_id"],
        "source_receipt_sha256": source_receipt,
        "predecessor_journal_head": event[0].predecessor_digest,
        "checkpoint_event_id": event_id,
        "checkpoint_journal_head": event[0].event_digest,
        "requested_effect": "NO_PROTECTED_EFFECT",
        "fixture_only": True, "dispatch_accepted": False,
        "provider_authenticated": False, "accepted_as_task_result": False,
        "effect_authority": False, "executed": False,
    }


def _check_local_acceptance(ledger: Any, intake: dict, acceptance: dict) -> None:
    _check_local_intake(intake)
    if type(acceptance) is not dict or set(acceptance) != {
        "schema", "task_id", "task_packet_digest", "source_digest",
        "conversation_id", "message_id", "task", "request_id", "route_id",
        "source_receipt_sha256", "predecessor_journal_head",
        "checkpoint_event_id", "checkpoint_journal_head", "requested_effect",
        "fixture_only", "dispatch_accepted", "provider_authenticated",
        "accepted_as_task_result", "effect_authority", "executed",
    }:
        raise ProvenanceBridgeError("unknown or modified local acceptance shape")
    import re
    state = ledger.read(intake["task_id"])
    events = ledger.events(intake["task_id"])
    expected_event = (intake["task_id"] + ":CHECKPOINT:local-fixture-" +
                      str(acceptance["request_id"]))
    if (type(acceptance["request_id"]) is not str or
            re.fullmatch(r"ui-[0-9a-f]{64}", acceptance["request_id"]) is None or
            acceptance["checkpoint_event_id"] != expected_event or
            type(acceptance["source_receipt_sha256"]) is not str or
            re.fullmatch(r"[0-9a-f]{64}", acceptance["source_receipt_sha256"]) is None or
            not events or events[-1].event_id != expected_event or
            events[-1].predecessor_digest !=
            acceptance["predecessor_journal_head"]):
        raise ProvenanceBridgeError("forged fixture acceptance identity or predecessor")
    if (acceptance["schema"] != "VERAOS_LOCAL_COGNITION_FIXTURE_ACCEPTANCE_V1" or
            acceptance["task_id"] != intake["task_id"] or
            acceptance["task_packet_digest"] != intake["task_packet_digest"] or
            acceptance["source_digest"] != intake["source_digest"] or
            acceptance["conversation_id"] != intake["conversation_id"] or
            acceptance["message_id"] != intake["message_id"] or
            acceptance["task"] != intake["text"] or
            acceptance["route_id"] != "dev:virtio-qwen4b" or
            acceptance["requested_effect"] != "NO_PROTECTED_EFFECT" or
            acceptance["fixture_only"] is not True or
            any(acceptance[x] is not False for x in (
                "dispatch_accepted", "provider_authenticated",
                "accepted_as_task_result", "effect_authority", "executed",
            )) or
            state.closed or state.active_dependencies or
            state.unresolved_correction_ids or
            state.opened_lifecycle_evidence_digest != intake["source_digest"] or
            state.packet.packet_digest != intake["task_packet_digest"] or
            state.packet.subject != intake["text"] or
            events[-1].event_digest != acceptance["checkpoint_journal_head"] or
            state.latest_checkpoint is None or
            state.latest_checkpoint["lifecycle_evidence_digest"] !=
            acceptance["source_receipt_sha256"] or
            "COGNITION_TURN" not in
            state.latest_checkpoint["protected_effects_still_gated"]):
        raise ProvenanceBridgeError("stale or forged local fixture acceptance")
    ev = ledger.events(intake["task_id"])
    if (not ev or ev[-1].event_id != acceptance["checkpoint_event_id"] or
            ev[-1].event_digest != acceptance["checkpoint_journal_head"]):
        raise ProvenanceBridgeError("replaced local fixture journal head")


def _inspect_local_pre_active(
    *, store: Any, intake: dict, acceptance: dict, resident_result: dict,
) -> dict:
    import json
    if (type(resident_result) is not dict or set(resident_result) !=
            {"status", "event_id", "run_id", "final_text", "route_id", "provider_id"} or
            resident_result["status"] != "COMPLETED" or
            resident_result["route_id"] != acceptance["route_id"] or
            resident_result["provider_id"] != acceptance["route_id"] or
            type(resident_result["event_id"]) is not str or
            type(resident_result["run_id"]) is not str or
            type(resident_result["final_text"]) is not str or
            len(resident_result["final_text"]) > 8192):
        raise ProvenanceBridgeError("incomplete, conflicting or unqualified result")
    event_id, run_id = resident_result["event_id"], resident_result["run_id"]
    event = store.connection.execute(
        "SELECT id,kind,payload_json,dedup_key,status FROM events WHERE id=?",
        (event_id,),
    ).fetchone()
    run = store.connection.execute(
        """SELECT id,task,status,capabilities_json,final_text,last_error,
                  source_event_id,failed_event_id,control_action FROM runs WHERE id=?""",
        (run_id,),
    ).fetchone()
    if (event is None or run is None or event["kind"] != "task.requested" or
            event["status"] != "DONE" or
            event["dedup_key"] != "veraos-text:" + acceptance["request_id"] or
            json.loads(event["payload_json"]) !=
            {"task": intake["text"], "capabilities": []} or
            run["source_event_id"] != event_id or
            run["task"] != intake["text"] or
            run["status"] != "COMPLETED" or
            json.loads(run["capabilities_json"]) != [] or
            run["final_text"] != resident_result["final_text"] or
            run["last_error"] is not None or run["failed_event_id"] is not None or
            run["control_action"] is not None):
        raise ProvenanceBridgeError("Pre-Active event/run/text mismatch")
    selected = store.connection.execute(
        "SELECT payload_json FROM journal WHERE subject_id=? AND event_type='VERAOS_COGNITION_ROUTE_SELECTED'",
        (event_id,),
    ).fetchall()
    expected = {
        "adapter_id": "pre-active-openai-compatible",
        "route_id": acceptance["route_id"],
        "provider_id": acceptance["route_id"], "model": "qwen3:4b-instruct",
        "effect_class": "COGNITION_ONLY",
    }
    if len(selected) != 1 or json.loads(selected[0]["payload_json"]) != expected:
        raise ProvenanceBridgeError("missing or substituted Pre-Active route evidence")
    return {
        "schema": "VERAOS_LOCAL_PRE_ACTIVE_RESULT_SOURCE_V1",
        "task_id": intake["task_id"], "source_digest": intake["source_digest"],
        "conversation_id": intake["conversation_id"],
        "message_id": intake["message_id"],
        "task": intake["text"],
        "request_id": acceptance["request_id"],
        "route_id": acceptance["route_id"],
        "event_id": event_id, "run_id": run_id,
        "status": "COMPLETED", "final_text": str(run["final_text"]),
    }


def record_local_cognition_result(
    *, ledger: Any, store: Any, intake: dict, acceptance: dict,
    resident_result: dict,
) -> dict:
    """Canonical Mono CAS-append a readback of PRE-ACTIVE SYNTHETIC result.

    A COMPLETED Pre-Active source row means neither human identity nor real
    model admission; no task closeout/effect, and no installed display grant.
    """
    from vera_core.task_execution import TaskExecutionError
    _check_local_acceptance(ledger, intake, acceptance)
    observed = _inspect_local_pre_active(
        store=store, intake=intake, acceptance=acceptance,
        resident_result=resident_result,
    )
    result_digest = _local_json_digest(observed)
    checkpoint_id = "source-result-" + acceptance["request_id"]
    try:
        state = ledger.checkpoint(
            intake["task_id"], checkpoint_id,
            completed_evidence=(
                "pre-active-event:" + observed["event_id"],
                "pre-active-run:" + observed["run_id"],
                "pre-active-observation-sha256:" + result_digest,
                "pre-active-source-json:" + __import__("json").dumps(
                    observed, sort_keys=True, separators=(",", ":"),
                    ensure_ascii=False,
                ),
            ),
            blockers=("synthetic output is NOT accepted task completion",
                      "GUI session and provider remain unauthenticated"),
            protected_effects_still_gated=("COGNITION_TURN",),
            next_frontier="trusted OS UI correlation and resident admission required",
            lifecycle_evidence_digest=result_digest,
            expected_task_head=acceptance["checkpoint_journal_head"],
        )
    except (TaskExecutionError, ValueError, KeyError) as exc:
        raise ProvenanceBridgeError("stale task result acceptance CAS denied") from exc
    event_id = intake["task_id"] + ":CHECKPOINT:" + checkpoint_id
    e = [x for x in ledger.events(intake["task_id"]) if x.event_id == event_id]
    if len(e) != 1 or ledger.events(intake["task_id"])[-1].event_digest != e[0].event_digest:
        raise ProvenanceBridgeError("result checkpoint substituted or changed")
    return {
        "schema": "VERAOS_LOCAL_COGNITION_RESULT_OBSERVATION_V1",
        "source": observed,
        "result_sha256": result_digest,
        "checkpoint_event_id": event_id,
        "result_journal_head": e[0].event_digest,
        "accepted_as_task_result": False, "display_authorized": False,
        "effect_authority": False, "real_model_attested": False,
    }


def read_local_cognition_response(
    *, ledger: Any, store: Any, intake: dict, acceptance: dict,
    observation: dict, conversation_id: str, message_id: str,
) -> dict:
    """Recheck persisted two-store fixture evidence; NO authorization to display."""
    if (conversation_id != intake.get("conversation_id") or
            message_id != intake.get("message_id") or
            type(observation) is not dict or
            set(observation) != {
                "schema", "source", "result_sha256", "checkpoint_event_id",
                "result_journal_head", "accepted_as_task_result",
                "display_authorized", "effect_authority", "real_model_attested",
            } or observation["schema"] != "VERAOS_LOCAL_COGNITION_RESULT_OBSERVATION_V1" or
            any(observation[x] is not False for x in (
                "accepted_as_task_result", "display_authorized",
                "effect_authority", "real_model_attested",
            ))):
        raise ProvenanceBridgeError("wrong conversation, message or authority")
    _check_local_intake(intake)
    current = ledger.read(intake["task_id"])
    if (current.closed or current.active_dependencies or
            current.unresolved_correction_ids or
            current.packet.subject != intake["text"] or
            current.opened_lifecycle_evidence_digest != intake["source_digest"] or
            current.packet.packet_digest != intake["task_packet_digest"] or
            ledger.events(intake["task_id"])[-1].event_digest != observation["result_journal_head"] or
            current.latest_checkpoint is None or
            current.latest_checkpoint["lifecycle_evidence_digest"] !=
            observation["result_sha256"] or
            ledger.events(intake["task_id"])[-1].event_id !=
            observation["checkpoint_event_id"]):
        raise ProvenanceBridgeError("stale or changed task result journal")
    supplied = observation["source"]
    if type(supplied) is not dict:
        raise ProvenanceBridgeError("invalid saved result source")
    # Validate source input against original accepted fixture fields without
    # requiring the earlier checkpoint still to be the latest state.
    required = (
        supplied.get("task_id") == acceptance.get("task_id") == intake["task_id"] and
        supplied.get("source_digest") == acceptance.get("source_digest") == intake["source_digest"] and
        supplied.get("conversation_id") == intake["conversation_id"] and
        supplied.get("message_id") == intake["message_id"] and
        supplied.get("task") == acceptance.get("task") == intake["text"] and
        supplied.get("request_id") == acceptance.get("request_id") and
        supplied.get("route_id") == acceptance.get("route_id")
    )
    if not required:
        raise ProvenanceBridgeError("source task or conversation substituted")
    now = _inspect_local_pre_active(
        store=store, intake=intake, acceptance=acceptance,
        resident_result={
            "status": supplied["status"], "event_id": supplied["event_id"],
            "run_id": supplied["run_id"], "final_text": supplied["final_text"],
            "route_id": supplied["route_id"], "provider_id": supplied["route_id"],
        },
    )
    if (now != supplied or
            _local_json_digest(now) != observation["result_sha256"]):
        raise ProvenanceBridgeError("stored Pre-Active output replaced since receipt")
    return {
        "schema": "VERAOS_LOCAL_UI_RESPONSE_CANDIDATE_V1",
        "conversation_id": conversation_id, "message_id": message_id,
        "task_id": intake["task_id"], "event_id": now["event_id"],
        "run_id": now["run_id"], "text": now["final_text"],
        "source_digest": intake["source_digest"],
        "display_authorized": False, "accepted_as_task_result": False,
        "effect_authority": False,
    }



def recover_local_cognition_observation(
    *, ledger: Any, store: Any, conversation_id: str, message_id: str,
) -> dict:
    """Cold recovery from existing Mono events and Pre-Active run, no new DB.

    Return a held state unless the source observation is fully reconstructed
    and reverified. A recovered response is NOT an authenticated UI display.
    """
    import json
    import re
    for name, value in (("conversation_id", conversation_id),
                        ("message_id", message_id)):
        if type(value) is not str or re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9._:-]{0,95}", value
        ) is None:
            raise ProvenanceBridgeError("invalid local recovery message identity")
    task_id = "ui-" + _local_json_digest({
        "schema": "VERAOS_LOCAL_MESSAGE_KEY_V1",
        "conversation_id": conversation_id, "message_id": message_id,
    })
    events = ledger.events(task_id)
    if not events:
        return {"status": "NO_CANONICAL_TASK", "display_authorized": False}
    if events[0].event_type != "TASK_OPENED":
        raise ProvenanceBridgeError("recovery has no valid task opener")
    state = ledger.read(task_id)
    if state.closed or state.active_dependencies or state.unresolved_correction_ids:
        return {"status": "HELD_TASK_CHANGED", "display_authorized": False}
    if len(events) == 1:
        return {"status": "NOT_ACCEPTED", "display_authorized": False}
    acceptance_event = events[1]
    if acceptance_event.event_type != "TASK_CHECKPOINT":
        return {"status": "HELD_TASK_CHANGED", "display_authorized": False}

    def one_json(event, prefix):
        fields = event.payload.get("completed_evidence", [])
        found = [s[len(prefix):] for s in fields
                 if type(s) is str and s.startswith(prefix)]
        if len(found) != 1:
            raise ProvenanceBridgeError("missing unique canonical recovery evidence")
        try:
            value = json.loads(found[0])
        except (ValueError, TypeError) as exc:
            raise ProvenanceBridgeError("invalid durable recovery JSON") from exc
        if type(value) is not dict:
            raise ProvenanceBridgeError("recovery evidence must be an object")
        return value

    seed = one_json(acceptance_event, "local-source-seed-json:")
    if set(seed) != {
        "intake", "request_id", "route_id", "source_receipt_sha256",
        "advisory_global_head",
    }:
        raise ProvenanceBridgeError("recovery seed has unknown keys")
    intake = seed["intake"]
    _check_local_intake(intake)
    if (intake["conversation_id"] != conversation_id or
            intake["message_id"] != message_id or
            intake["task_id"] != task_id or
            intake["opened_journal_head"] != events[0].event_digest or
            intake["text"] != state.packet.subject or
            intake["source_digest"] != state.opened_lifecycle_evidence_digest or
            intake["task_packet_digest"] != state.packet.packet_digest or
            seed["route_id"] != "dev:virtio-qwen4b" or
            acceptance_event.event_id != task_id + ":CHECKPOINT:local-fixture-" + seed["request_id"] or
            acceptance_event.payload.get("lifecycle_evidence_digest") != seed["source_receipt_sha256"] or
            acceptance_event.payload.get("protected_effects_still_gated") != ["COGNITION_TURN"] or
            acceptance_event.event_digest == events[0].event_digest):
        raise ProvenanceBridgeError("stored local source/advisory is inconsistent")
    accepted = {
        "schema": "VERAOS_LOCAL_COGNITION_FIXTURE_ACCEPTANCE_V1",
        "task_id": task_id, "task_packet_digest": intake["task_packet_digest"],
        "source_digest": intake["source_digest"],
        "conversation_id": conversation_id, "message_id": message_id,
        "task": intake["text"], "request_id": seed["request_id"],
        "route_id": seed["route_id"],
        "source_receipt_sha256": seed["source_receipt_sha256"],
        "predecessor_journal_head": acceptance_event.predecessor_digest,
        "checkpoint_event_id": acceptance_event.event_id,
        "checkpoint_journal_head": acceptance_event.event_digest,
        "requested_effect": "NO_PROTECTED_EFFECT",
        "fixture_only": True, "dispatch_accepted": False,
        "provider_authenticated": False, "accepted_as_task_result": False,
        "effect_authority": False, "executed": False,
    }
    if len(events) == 2:
        return {
            "status": "OUTCOME_UNKNOWN_NO_REDISPATCH",
            "task_id": task_id, "display_authorized": False,
        }
    if len(events) != 3 or events[2].event_type != "TASK_CHECKPOINT":
        return {"status": "HELD_TASK_CHANGED", "display_authorized": False}
    result_event = events[2]
    if result_event.event_id != (
        task_id + ":CHECKPOINT:source-result-" + seed["request_id"]
    ):
        return {"status": "HELD_TASK_CHANGED", "display_authorized": False}
    observed = one_json(result_event, "pre-active-source-json:")
    digest = _local_json_digest(observed)
    if (result_event.payload.get("lifecycle_evidence_digest") != digest or
            result_event.payload.get("protected_effects_still_gated") != ["COGNITION_TURN"] or
            result_event.event_digest != events[-1].event_digest):
        raise ProvenanceBridgeError("result journal and source digest mismatch")
    observation = {
        "schema": "VERAOS_LOCAL_COGNITION_RESULT_OBSERVATION_V1",
        "source": observed, "result_sha256": digest,
        "checkpoint_event_id": result_event.event_id,
        "result_journal_head": result_event.event_digest,
        "accepted_as_task_result": False, "display_authorized": False,
        "effect_authority": False, "real_model_attested": False,
    }
    reply = read_local_cognition_response(
        ledger=ledger, store=store, intake=intake, acceptance=accepted,
        observation=observation,
        conversation_id=conversation_id, message_id=message_id,
    )
    return {
        "status": "SOURCE_OBSERVATION_REVALIDATED",
        "task_id": task_id, "response_candidate": reply,
        "display_authorized": False, "accepted_as_task_result": False,
    }


def make_local_resident_fixture_handler(
    *, ledger_path: Any, store_path: Any, conversation_id: str,
    advertisements: tuple, source_only_executor: Any,
):
    """Exact PR37 conversation_handler(task, request_id) source-only binding.

    The executable must be a caller-injected in-memory synthetic fixture.
    This adapter is NOT registered in VeraOS, is not a provider verifier, and
    never returns COMPLETED to the graphical HTTP handler. PORTAL must own
    authorization, resident admission, and real display after exact review.
    """
    from pathlib import Path
    from vera_core.task_execution import TaskExecutionLedger
    from pre_active.store import Store
    if not callable(source_only_executor):
        raise ProvenanceBridgeError("source-only executor callback required")
    ledger_file, store_file = Path(ledger_path), Path(store_path)

    def handle(task: str, request_id: str) -> dict:
        if type(task) is not str or type(request_id) is not str:
            raise ProvenanceBridgeError("invalid PR37 two-argument callback")
        ledger = TaskExecutionLedger(ledger_file)
        store = Store(store_file)
        try:
            intake = open_local_cognition_fixture(
                ledger=ledger, conversation_id=conversation_id,
                message_id=request_id, text=task,
            )
            prior = recover_local_cognition_observation(
                ledger=ledger, store=store,
                conversation_id=conversation_id, message_id=request_id,
            )
            if prior["status"] != "NOT_ACCEPTED":
                # Cold readback is available through the explicit recovery
                # API, never automatic re-execution or UI output.
                return {
                    "status": "BLOCKED", "run_id": None, "final_text": None,
                }
            acceptance = accept_local_cognition_fixture(
                ledger=ledger, intake=intake, advertisements=advertisements,
            )
            # This callback is explicitly a synthetic no-model-source test
            # seam. Calling a real endpoint here would violate the contract.
            source_result = source_only_executor(
                store=store, task=acceptance["task"],
                request_id=acceptance["request_id"],
                route_id=acceptance["route_id"],
            )
            record_local_cognition_result(
                ledger=ledger, store=store, intake=intake,
                acceptance=acceptance, resident_result=source_result,
            )
            checked = recover_local_cognition_observation(
                ledger=ledger, store=store,
                conversation_id=conversation_id, message_id=request_id,
            )
            if checked["status"] != "SOURCE_OBSERVATION_REVALIDATED":
                raise ProvenanceBridgeError("synthetic run not durably correlated")
            # IMPORTANT: PR37 HTTP would display status COMPLETED; this
            # unqualified source adapter deliberately returns BLOCKED.
            return {
                "status": "BLOCKED", "run_id": checked["response_candidate"]["run_id"],
                "final_text": None,
            }
        finally:
            store.close()

    return handle
