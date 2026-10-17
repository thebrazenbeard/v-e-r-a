"""Real pinned source: receiver packet -> Vera Mono task -> VeraOS PR32 route intent.

All tests are offline. No network, QEMU, model inference or route admission.
"""
from __future__ import annotations
from copy import deepcopy
import ast
import gc
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from integration.cognition_task_gate import bind_episode
from integration.veraos_evidence_bridge import (
    evaluate_source_route_evidence, ProvenanceBridgeError,
    prepare_source_linked_veraos_route, verify_source_linked_veraos_route,
    checkpoint_source_linked_fixture,
    VERAOS_HEAD, NATIVE_ROUTE_BLOB, GUEST_PROBE_BLOB,
)

ROOT = Path(__file__).resolve().parents[1]
MONO = os.environ.get("VERA_MONO_SOURCE_ROOT")
TRAINING = os.environ.get("VERA_TRAINING_SOURCE_ROOT")
INTRANEL = os.environ.get("INTRANEL_SOURCE_ROOT")
VERAOS = os.environ.get("VERAOS_SOURCE_ROOT")
PORTAL = os.environ.get("PORTAL_SOURCE_ROOT")
PRE_ACTIVE = os.environ.get("PRE_ACTIVE_SOURCE_ROOT")


def git(root, *args):
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True,
        timeout=15, check=True,
    ).stdout.strip()


@unittest.skipUnless(all((MONO, TRAINING, INTRANEL)),
                     "Requires three exact public source checkouts")
class VeraOSProvenanceBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mono, cls.training = Path(MONO), Path(TRAINING)
        cls.intranel = Path(INTRANEL)
        cls.veraos = Path(VERAOS) if VERAOS else None
        expected = (
            (cls.mono, "36ae11802808bc1b1392a361716109d1022ee6af"),
            (cls.training, "a242df78155ca20b36dbde8cbb7448dad43a5e55"),
            (cls.intranel, "58714f5f6561b5e44e42dcdbca67e2cb59bfb87b"),
        )
        for root, commit in expected:
            if git(root, "rev-parse", "HEAD") != commit:
                raise AssertionError("wrong exact dependency Git subject")
        sys.path.insert(0, str(cls.intranel / "src"))
        sys.path.insert(0, str(cls.intranel / "tests"))
        sys.path.insert(0, str(cls.training))
        sys.path.insert(0, str(cls.training / "tests"))
        sys.path[:0] = [str(p) for p in (cls.mono / "packages").glob("*/src")]
        from intranel.four_role_receiver import AtomicRoleReceiver
        from intranel.coordination import wrap
        from intranel.message import parse_message
        from test_four_role_ledger import request, reply
        from test_participating_cognition_v1 import compose
        from vera_core.task_execution import TaskExecutionLedger, TaskPacket
        cls.Receiver, cls.wrap, cls.parse = AtomicRoleReceiver, staticmethod(wrap), staticmethod(parse_message)
        cls.request, cls.reply = staticmethod(request), staticmethod(reply)
        cls.Ledger, cls.Packet, cls.compose = TaskExecutionLedger, TaskPacket, staticmethod(compose)

    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(gc.collect)
        self.task_id = "task:one"
        self.ledger = self.Ledger(Path(self.temp.name) / "tasks.sqlite3")
        packet_data = json.loads((ROOT / "integration" / "example_readonly_task_packet.json").read_text("utf8"))
        task_packet = self.Packet(**{
            k: tuple(v) if isinstance(v, list) else v for k, v in packet_data.items()
        })
        self.ledger.open_task(self.task_id, task_packet, lifecycle_evidence_digest="a" * 64)
        self.episode = self.compose().as_dict()
        self.binding = bind_episode(self.ledger, self.task_id, self.episode)
        self.receiver = self.Receiver(Path(self.temp.name) / "receiver.sqlite3", expected_target="vera:portal")
        req = self.request()
        child = self.reply(req)
        self.receiver.observe_outbound_request(req, "local:outbound")
        self.receiver.receive(
            self.wrap(self.parse(child)),
            "github:thebrazenbeard/intranel#9/comment/81",
            comment_id=81,
        )
        self.intent = {
            "schema": "VERAOS_NATIVE_ROUTE_INTENT_SOURCE_V1",
            "os_source": "git:thebrazenbeard/vera-os@" + VERAOS_HEAD,
            "module": "veraos.native_cognition",
            "admit_callable": "admit_local_text_route",
            "execute_callable": "execute_text_request",
            "provider_id": "dev:virtio-qwen4b",
            "model": "qwen3:4b-instruct",
            "port_name": "org.veraos.model.v1",
            "route_class": "COGNITION_ONLY",
        }
        self.provider = {
            "schema": "VERA_OS_COGNITION_PROVIDER_V1",
            "provider_id": "dev:virtio-qwen4b",
            "provider_kind": "LOCAL_MODEL",
            "capabilities": ["text"],
            "transport": {"kind": "OPENAI_COMPATIBLE_HTTP",
                          "attachment": "http://127.0.0.1:18766/v1"},
            "qualification": {
                "status": "PASS", "issuer": "thebrazenbeard/vera-os",
                "subject_sha256": "0edcdef34593eac1aa2be9c7d06c432dcf81945adca5eca2f27662c18f168ba0",
                "suite_sha256": "0" * 64,
            },
            "authority": {
                "identity_authority": False, "canonical_memory_write_authority": False,
                "protected_effect_authority": False, "browser_authority": False,
            },
            "admission": {
                "status": "VERAOS_ROUTE_ELIGIBLE", "route_class": "COGNITION_ONLY",
                "selector_owner": "thebrazenbeard/portal",
            },
        }
        self.coverage = {
            "coverage_complete": False,
            "coverage_status": "HOLD_PRECEDING_PAGES_UNVERIFIED",
        }

    def evaluate(self, **changes):
        args = dict(
            receiver=self.receiver, task_ledger=self.ledger, task_id=self.task_id,
            episode=self.episode, binding=self.binding, comment_id=81,
            message_id="reply-1", coverage=self.coverage,
            provider=self.provider, route_intent=self.intent,
        )
        args.update(changes)
        return evaluate_source_route_evidence(**args)

    def test_real_local_packet_and_task_produce_only_explicit_hold(self):
        result = self.evaluate()
        self.assertEqual(result["schema"], "VERAOS_SOURCE_PROVENANCE_BRIDGE_V1")
        self.assertEqual(result["verdict"], "HOLD_INCOMPLETE_COMMENT_COVERAGE")
        self.assertEqual(result["message"]["comment_id"], 81)
        self.assertEqual(result["message"]["local_pair_verified"], True)
        self.assertEqual(result["task"]["task_journal_head"], self.binding["task_journal_head"])
        self.assertEqual(result["native_route"]["module"], "veraos.native_cognition")
        for field in ("origin_authenticated", "provider_authenticated", "normal_resident_route_admitted",
                      "accepted_as_task_result", "executed", "protected_effect_authority"):
            self.assertIs(result[field], False)

    def test_forged_sender_attestation_is_rejected_not_promoted(self):
        class ForgedReceiver:
            def __init__(self, real):
                self.real = real
            def read_comment_packet_evidence(self, comment_id, message_id):
                row = self.real.read_comment_packet_evidence(comment_id, message_id)
                return {**row, "origin_authenticated": True}
        with self.assertRaisesRegex(ProvenanceBridgeError, "sender"):
            self.evaluate(receiver=ForgedReceiver(self.receiver))

    def test_unknown_comment_and_partial_coverage_cannot_claim_delivery(self):
        with self.assertRaises(ProvenanceBridgeError):
            self.evaluate(comment_id=999)
        completed = {"coverage_complete": True, "coverage_status": "COMPLETE_SCANNED_WINDOW"}
        result = self.evaluate(coverage=completed)
        self.assertEqual(result["verdict"], "HOLD_UNATTESTED_SENDER_AND_PROVIDER")
        self.assertFalse(result["normal_resident_route_admitted"])
        self.assertFalse(result["origin_authenticated"])
        self.assertFalse(result["message_task_causal_link_attested"])

    def test_stale_task_journal_head_must_fail(self):
        self.ledger.bind_dependency(self.task_id, "dependency:changed",
                                    kind="COORDINATION_COMMAND", target_id="command:changed")
        with self.assertRaisesRegex(ProvenanceBridgeError, "task"):
            self.evaluate()

    def test_mid_binding_task_journal_advance_must_fail(self):
        class RacingLedger:
            def __init__(self, real):
                self.real = real
                self.changed = False
            def verify_chain(self):
                return self.real.verify_chain()
            def read(self, task_id):
                state = self.real.read(task_id)
                if not self.changed:
                    self.real.bind_dependency(task_id, "dependency:raced",
                                              kind="COORDINATION_COMMAND", target_id="command:raced")
                    self.changed = True
                return state
        racing = RacingLedger(self.ledger)
        with self.assertRaisesRegex(ProvenanceBridgeError, "task"):
            self.evaluate(task_ledger=racing)
        self.assertTrue(racing.changed)

    def test_diagnostic_provider_pass_is_not_normal_resident_admission(self):
        result = self.evaluate(coverage={
            "coverage_complete": True, "coverage_status": "COMPLETE_SCANNED_WINDOW"})
        self.assertEqual(result["provider"]["claimed_qualification"], "PASS")
        self.assertEqual(result["provider"]["qualification_provenance"], "TEST_ONLY_SELF_DECLARED")
        self.assertEqual(result["native_route"]["execute_callable"], "execute_text_request")
        self.assertFalse(result["provider_authenticated"])
        self.assertFalse(result["normal_resident_route_admitted"])
        corrupted = deepcopy(self.provider)
        corrupted["authority"]["protected_effect_authority"] = True
        with self.assertRaisesRegex(ProvenanceBridgeError, "provider"):
            self.evaluate(provider=corrupted)
        wrong = deepcopy(self.intent)
        wrong["module"] = "veraos.resident"
        with self.assertRaisesRegex(ProvenanceBridgeError, "native route"):
            self.evaluate(route_intent=wrong)

    def test_exact_private_veraos_source_api_when_authorized_checkout_available(self):
        # Public CI cannot fetch private VeraOS PR32. Never vendor its source
        # into public v-e-r-a or treat absence as a production PASS.
        if self.veraos is None:
            self.skipTest("Private VeraOS exact source requires separate authorized readback")
        self.assertEqual(git(self.veraos, "rev-parse", "HEAD"), VERAOS_HEAD)
        for file, blob in (
            ("src/veraos/native_cognition.py", NATIVE_ROUTE_BLOB),
            ("src/veraos/virtio_guest_probe.py", GUEST_PROBE_BLOB),
        ):
            self.assertEqual(git(self.veraos, "rev-parse", "HEAD:" + file), blob)
            self.assertEqual(git(self.veraos, "hash-object", str(self.veraos / file)), blob)
        module = ast.parse((self.veraos / "src/veraos/native_cognition.py").read_text("utf8"))
        functions = {x.name for x in module.body if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef))}
        self.assertTrue({"admit_local_text_route", "execute_text_request"} <= functions)
        guest = (self.veraos / "src/veraos/virtio_guest_probe.py").read_text("utf8")
        self.assertIn("TEST-ONLY record", guest)



    def test_edited_comment_collision_invalidates_cross_system_source(self):
        edited = self.reply(self.request())
        edited["payload"]["finding"] = "conflicting source edit"
        outcome = self.receiver.receive(
            self.wrap(self.parse(edited)),
            "github:thebrazenbeard/intranel#9/comment/82", comment_id=82,
        )
        self.assertEqual(outcome["ingest"], "CONFLICT")
        self.assertEqual(outcome["classification"], "IDENTITY_COLLISION")
        with self.assertRaisesRegex(ProvenanceBridgeError, "receiver"):
            self.evaluate()


    def test_current_training_development_cut_cannot_admit_diagnostic_model(self):
        from dataclasses import replace
        from veraos_development_evidence_v1 import (
            DevelopmentInventory, DevelopmentCut, evaluate_development_cut,
            bind_participation_development_cut, DEV_OS_HEAD, DEV_MODEL,
            DEV_OLLAMA_REPORTED_DIGEST, DEV_MODEL_BYTES,
            SourceObservationStamp,
        )
        inventory = DevelopmentInventory(
            source_head=DEV_OS_HEAD, model=DEV_MODEL,
            reported_ollama_digest=DEV_OLLAMA_REPORTED_DIGEST,
            reported_ollama_size_bytes=DEV_MODEL_BYTES,
            quantization="Q4_K_M",
        )
        common = dict(node_id="Lappy", generation=6,
                      session="session:6", nonce="a"*32)
        cut = DevelopmentCut(**{
            **{prefix+"_"+key: value
               for prefix in ("registry", "telemetry", "inventory", "artifact")
               for key, value in common.items()},
            "observed_at_epoch_s": 1800000000,
            "cpu_threads": 8, "ram_available_mib": 8192,
            "gpu_free_vram_mib": None, "artifact_bytes_sha256": None,
            "descriptor_status": "PASS", "route": "DIAGNOSTIC_QEMU_ONLY",
            "registry_stamp": SourceObservationStamp(1800000000, "sample:registry"),
            "telemetry_stamp": SourceObservationStamp(1800000000, "sample:telemetry"),
            "inventory_stamp": SourceObservationStamp(1800000000, "sample:inventory"),
            "artifact_stamp": SourceObservationStamp(1800000000, "sample:artifact"),
        })
        opts = dict(expected_node_id="Lappy", expected_generation=6,
                    expected_session="session:6", expected_nonce="a"*32,
                    now_epoch_s=1800000001)
        reviewed = evaluate_development_cut(cut, inventory, **opts)
        self.assertEqual(reviewed.status, "DEVELOPMENT_METADATA_ONLY")
        self.assertIn("DIAGNOSTIC_PASS_IS_SELF_DECLARED", reviewed.holds)
        joined = bind_participation_development_cut(
            self.episode, reviewed, expected_task_id=self.task_id,
        )
        self.assertEqual(joined["status"], "HELD_NORMAL_RESIDENT")
        self.assertFalse(joined["model_identity_authenticated"])
        self.assertFalse(joined["accepted_as_task_result"])
        self.assertFalse(joined["effect_authority"])
        source = self.evaluate(coverage={
            "coverage_complete": True,
            "coverage_status": "COMPLETE_SCANNED_WINDOW",
        })
        self.assertEqual(source["verdict"], "HOLD_UNATTESTED_SENDER_AND_PROVIDER")
        self.assertFalse(source["normal_resident_route_admitted"])
        conflicted = evaluate_development_cut(
            replace(cut, telemetry_nonce="b"*32), inventory, **opts,
        )
        self.assertEqual(conflicted.status, "HELD_SOURCE_PROVENANCE")
        self.assertIn("JOINT_SESSION_PROVENANCE_MISMATCH", conflicted.holds)
        missing_stamp = evaluate_development_cut(
            replace(cut, artifact_stamp=None), inventory, **opts,
        )
        self.assertEqual(missing_stamp.status, "HELD_SOURCE_PROVENANCE")
        self.assertIn("COMPONENT_OBSERVATION_MISSING", missing_stamp.holds)
        stale_stamp = evaluate_development_cut(
            replace(cut, telemetry_stamp=SourceObservationStamp(
                1799999600, "sample:telemetry",
            )), inventory, **opts,
        )
        self.assertIn("COMPONENT_OBSERVATION_OUTSIDE_WINDOW", stale_stamp.holds)
        reused_sample = evaluate_development_cut(
            replace(cut, artifact_stamp=SourceObservationStamp(
                1800000000, "sample:registry",
            )), inventory, **opts,
        )
        self.assertIn("REUSED_SOURCE_OBSERVATION_ID", reused_sample.holds)

    def test_mutated_receiver_stage_bytes_cannot_cross_bridge(self):
        import sqlite3
        # The exact local source remains hash-stamped, but the staged
        # envelope bytes are corrupted after the SQLite transaction.
        with sqlite3.connect(Path(self.temp.name) / "receiver.sqlite3") as db:
            db.execute(
                "UPDATE receiver_staged SET envelope=? WHERE message_id='reply-1'",
                ('{"rewritten":"packet"}',),
            )
        with self.assertRaisesRegex(ProvenanceBridgeError, "receiver"):
            self.evaluate()


    def test_forged_task_acceptance_or_effect_claim_never_becomes_route_evidence(self):
        # A caller may edit a source-only task binding after it was built.
        # Matching task ID and journal head do not authorize result adoption.
        for authority in (
            "accepted_as_task_result", "effect_authority",
            "executed", "independent_source_attestation",
        ):
            with self.subTest(authority=authority):
                forged = deepcopy(self.binding)
                forged[authority] = True
                with self.assertRaisesRegex(ProvenanceBridgeError, "task"):
                    self.evaluate(binding=forged)


    def linked(self):
        # An actual durable Mono TASK_OPENED event records the same local
        # receiver packet digest. This is declared causality, not identity.
        from integration.cognition_task_gate import bind_episode
        source = self.receiver.read_comment_packet_evidence(81, "reply-1")
        ledger = self.Ledger(Path(self.temp.name) / "linked-tasks.sqlite3")
        ledger.open_task(
            self.task_id, self.ledger.read(self.task_id).packet,
            lifecycle_evidence_digest=source["semantic_sha256"],
        )
        return ledger, bind_episode(ledger, self.task_id, self.episode)

    def advisory_ad(self, route_id="dev:virtio-qwen4b"):
        from portal.route_resolver import PortalRouteAdvertisement
        return PortalRouteAdvertisement(
            adapter_id="pre-active-openai-compatible", route_id=route_id,
            node_id="veraos", target_kind="MODEL", target_id="qwen3:4b-instruct",
            capabilities=("text",),
            effect_capabilities=("NO_PROTECTED_EFFECT",),
            authorized_effects=("NO_PROTECTED_EFFECT",),
            available=True, attached=True, current=True,
        )

    def proposal(self, ledger, binding, **changes):
        props = dict(
            receiver=self.receiver, task_ledger=ledger, task_id=self.task_id,
            episode=self.episode, binding=binding, comment_id=81,
            message_id="reply-1", coverage=self.coverage,
            provider=self.provider, route_intent=self.intent,
            advertisements=(self.advisory_ad(),),
        )
        props.update(changes)
        return prepare_source_linked_veraos_route(**props)

    def test_real_mono_open_digest_to_portal_to_veraos_intent_is_durable_and_reverified(self):
        if not PORTAL:
            self.skipTest("requires actual pinned PORTAL source checkout")
        sys.path.insert(0, str(Path(PORTAL)))
        ledger, binding = self.linked()
        proposal = self.proposal(ledger, binding)
        self.assertEqual(proposal["status"], "ROUTE_PROPOSED_UNATTESTED")
        self.assertEqual(proposal["portal_request"]["requested_effect"], "NO_PROTECTED_EFFECT")
        self.assertEqual(proposal["portal_assessment"]["state"], "ROUTE_PROPOSED")
        self.assertEqual(proposal["native_call"]["module"], "veraos.native_cognition")
        self.assertEqual(proposal["native_call"]["callable"], "execute_text_request")
        self.assertEqual(proposal["native_call"]["task"], ledger.read(self.task_id).packet.subject)
        self.assertLessEqual(len(proposal["native_call"]["request_id"]), 96)
        for denied in ("accepted_as_task_result", "normal_resident_route_admitted",
                       "executed", "protected_effect_authority", "origin_authenticated"):
            self.assertIs(proposal[denied], False)
        # Actual durable receipt, cold reread and idempotent exact proposal
        receipt_file = Path(self.temp.name) / "portal-veraos-proposal.json"
        self.proposal(ledger, binding, receipt_path=receipt_file)
        self.assertTrue(receipt_file.is_file())
        self.assertEqual(verify_source_linked_veraos_route(
            receipt_file, receiver=self.receiver, task_ledger=ledger,
            task_id=self.task_id, episode=self.episode, binding=binding,
            comment_id=81, message_id="reply-1", coverage=self.coverage,
            provider=self.provider, route_intent=self.intent,
            advertisements=(self.advisory_ad(),),
        ), proposal)
        self.assertEqual(self.proposal(ledger, binding), proposal)
        with self.assertRaisesRegex(ProvenanceBridgeError, "receipt"):
            self.proposal(ledger, binding, receipt_path=receipt_file)

    def test_unlinked_task_and_stale_post_receipt_journal_fail_closed(self):
        if not PORTAL:
            self.skipTest("requires pinned PORTAL")
        sys.path.insert(0, str(Path(PORTAL)))
        with self.assertRaisesRegex(ProvenanceBridgeError, "opening"):
            self.proposal(self.ledger, self.binding)
        ledger, binding = self.linked()
        path = Path(self.temp.name) / "durable-source-proposal.json"
        self.proposal(ledger, binding, receipt_path=path)
        ledger.bind_dependency(self.task_id, "dependency:other-writer",
                               kind="COORDINATION_COMMAND", target_id="command:advance")
        with self.assertRaisesRegex(ProvenanceBridgeError, "task"):
            verify_source_linked_veraos_route(
                path, receiver=self.receiver, task_ledger=ledger,
                task_id=self.task_id, episode=self.episode, binding=binding,
                comment_id=81, message_id="reply-1", coverage=self.coverage,
                provider=self.provider, route_intent=self.intent,
                advertisements=(self.advisory_ad(),),
            )

    def test_forged_model_route_and_incomplete_provider_keep_advisory_untrusted(self):
        if not PORTAL:
            self.skipTest("requires pinned PORTAL")
        sys.path.insert(0, str(Path(PORTAL)))
        ledger, binding = self.linked()
        unmatched = self.proposal(ledger, binding, advertisements=(self.advisory_ad("forged:route"),))
        self.assertEqual(unmatched["status"], "HELD_UNQUALIFIED_ROUTE")
        self.assertIsNone(unmatched["native_call"])
        unqualified = self.proposal(ledger, binding, advertisements=())
        self.assertEqual(unqualified["status"], "HELD_UNQUALIFIED_ROUTE")
        proposed = self.proposal(ledger, binding)
        self.assertFalse(proposed["coverage"]["coverage_complete"])
        self.assertFalse(proposed["normal_resident_route_admitted"])


    def test_latest_training_trial_is_synthetic_only_not_a_route_permit(self):
        # Latest sibling Training PR106 adds a supervised trial SOURCE preflight,
        # NOT authenticated artifact or installed resident model admission.
        from test_controlled_resident_trial_v1 import ControlledResidentTrialTests
        trial = ControlledResidentTrialTests()
        trial.setUp()
        accepted = trial.evaluate()
        self.assertEqual(accepted.status, "ACCEPT_SYNTHETIC_DEV_PREFLIGHT")
        self.assertFalse(accepted.model_identity_authenticated)
        self.assertFalse(accepted.normal_resident_admitted)
        self.assertFalse(accepted.effect_authority)
        from controlled_resident_trial_v1 import evaluate_controlled_trial
        live = evaluate_controlled_trial(
            trial.target, trial.session, trial.sample, trial.session,
            trial.bytes, trial.development, trial.cognition,
            episode=trial.episode, now_epoch_s=1800000001,
            evidence_scope="REAL_HOST_UNATTESTED",
        )
        self.assertEqual(live.status, "HOLD_SOURCE_PREFLIGHT")
        self.assertIn("HOST_CAPTURE_NOT_RECEIVER_AUTHENTICATED", live.holds)
        # Even a separately coherent synthetic development cut cannot
        # turn our real Mono/PORTAL route proposal into model admission.
        if PORTAL:
            sys.path.insert(0, str(Path(PORTAL)))
            ledger, binding = self.linked()
            offered = self.proposal(ledger, binding)
            self.assertFalse(offered["normal_resident_route_admitted"])
            self.assertFalse(offered["accepted_as_task_result"])

    def test_actual_other_writer_waits_until_advisory_sqlite_source_cut_releases(self):
        # The writer is the REAL Mono bind_dependency() append writer.
        # During the no-effect advisory construction the SQLite writer
        # cannot alter the journal; immediately AFTER release it can, and
        # the advisory receipt must then be rejected before any dispatch.
        if not PORTAL:
            self.skipTest("requires pinned PORTAL")
        import threading
        from unittest.mock import patch
        sys.path.insert(0, str(Path(PORTAL)))
        import portal.vera_task_handoff as handoff
        ledger, binding = self.linked()
        receipt = Path(self.temp.name) / "writer-race-advisory.json"
        started = threading.Event()
        finished = threading.Event()
        failures = []
        writer = None
        real_assess = handoff.assess_vera_task_route
        def concurrent_writer():
            started.set()
            try:
                ledger.bind_dependency(
                    self.task_id, "dependency:concurrent-writer",
                    kind="COORDINATION_COMMAND", target_id="command:concurrent",
                )
            except Exception as exc:
                failures.append(exc)
            finally:
                finished.set()
        def assess_while_writer_attempts(request, routes):
            nonlocal writer
            writer = threading.Thread(target=concurrent_writer, daemon=True)
            writer.start()
            self.assertTrue(started.wait(5))
            self.assertFalse(
                finished.wait(0.15),
                "journal writer slipped through SQLite BEGIN IMMEDIATE reservation",
            )
            return real_assess(request, routes)
        try:
            with patch.object(handoff, "assess_vera_task_route",
                              side_effect=assess_while_writer_attempts):
                proposed = self.proposal(ledger, binding, receipt_path=receipt)
        finally:
            if writer is not None:
                writer.join(timeout=15)
        self.assertFalse(failures, failures)
        self.assertTrue(finished.is_set())
        self.assertTrue(receipt.is_file())
        self.assertNotEqual(
            ledger.read(self.task_id).journal_head_digest,
            proposed["portal_request"]["task_journal_head"],
        )
        with self.assertRaisesRegex(ProvenanceBridgeError, "task"):
            verify_source_linked_veraos_route(
                receipt, receiver=self.receiver, task_ledger=ledger,
                task_id=self.task_id, episode=self.episode, binding=binding,
                comment_id=81, message_id="reply-1", coverage=self.coverage,
                provider=self.provider, route_intent=self.intent,
                advertisements=(self.advisory_ad(),),
            )


    def test_real_pre_active_durable_run_from_mono_proposal_synthetic_only(self):
        # Real Pre-Active event/run SQLite with deterministic stub response.
        # No model, endpoint, QEMU, native route admission or resident is called.
        if not PORTAL or not PRE_ACTIVE:
            self.skipTest("requires exact pinned PORTAL and Pre-Active test sources")
        pre = Path(PRE_ACTIVE)
        self.assertEqual(git(pre, "rev-parse", "HEAD"),
                         "1f23a809d7274df506e03e2d9052525538c3bcf6")
        self.assertEqual(git(pre, "rev-parse", "HEAD:src/pre_active/store.py"),
                         "4612d4c621e01ce4ee69ad5702c4ca37fa7e3402")
        sys.path.insert(0, str(Path(PORTAL)))
        sys.path.insert(0, str(pre / "src"))
        from pre_active.store import Store
        from pre_active.engine import Engine, ModelResponse
        from pre_active.context import ContextAssembler
        from pre_active.tools import ToolRegistry

        ledger, binding = self.linked()
        proposal = self.proposal(ledger, binding)
        self.assertEqual(proposal["status"], "ROUTE_PROPOSED_UNATTESTED")
        self.assertFalse(proposal["normal_resident_route_admitted"])
        call = proposal["native_call"]
        self.assertEqual(call["callable"], "execute_text_request")

        class Stub:
            calls = 0
            def respond(inner, *, messages, tools):
                inner.calls += 1
                assert tools == [], "no effect tools allowed in fixture"
                assert any(m["role"] == "user" and call["task"] in m["content"]
                           for m in messages)
                return ModelResponse(final_text="SYNTHETIC PRE-ACTIVE RESPONSE ONLY")

        path = Path(self.temp.name) / "preactive-fixture.sqlite3"
        store = Store(path)
        stub = Stub()
        engine = Engine(
            store=store, model=stub, tools=ToolRegistry(store),
            context=ContextAssembler(store, max_chars=4096),
            system_prompt="Synthetic fixture only; no inference.",
            worker_id="synthetic-no-effect", max_steps=2,
            max_autonomous_turns_per_run=0,
            max_consecutive_endogenous_turns=0,
        )
        try:
            event = store.enqueue_event(
                kind="task.requested",
                payload={"task": call["task"], "capabilities": []},
                priority=0, dedup_key="veraos-text:" + call["request_id"],
                now=1.0,
            )
            store.append_journal(
                event_type="VERAOS_COGNITION_ROUTE_SELECTED",
                subject_id=event,
                payload={
                    "adapter_id": "pre-active-openai-compatible",
                    "route_id": "dev:virtio-qwen4b",
                    "provider_id": "dev:virtio-qwen4b",
                    "model": "qwen3:4b-instruct",
                    "effect_class": "COGNITION_ONLY",
                },
                now=1.0,
            )
            for i in range(4):
                engine.run_once(now=2.0 + i * 0.02)
            row = store.connection.execute(
                "SELECT id FROM runs WHERE source_event_id=?", (event,),
            ).fetchone()
            self.assertIsNotNone(row)
            run_id = str(row["id"])
            run = store.get_run(run_id)
            self.assertEqual(run["status"], "COMPLETED")
            self.assertEqual(run["final_text"],
                             "SYNTHETIC PRE-ACTIVE RESPONSE ONLY")
            self.assertEqual(stub.calls, 1)
            self.assertTrue(any(
                j["event_type"] == "VERAOS_COGNITION_ROUTE_SELECTED"
                for j in store.list_journal(limit=50)
            ))
            duplicate = store.enqueue_event(
                kind="task.requested",
                payload={"task": call["task"], "capabilities": []},
                priority=0, dedup_key="veraos-text:" + call["request_id"],
                now=9.0,
            )
            self.assertEqual(duplicate, event)
            self.assertEqual(stub.calls, 1)
            with self.assertRaises((RuntimeError, ValueError)):
                store.enqueue_event(
                    kind="task.requested",
                    payload={"task": "FORGED TASK", "capabilities": []},
                    priority=0, dedup_key="veraos-text:" + call["request_id"],
                    now=10.0,
                )
        finally:
            store.close()
        cold = Store(path)
        try:
            persistent = cold.get_run(run_id)
            stored_event = cold.connection.execute(
                "SELECT source_event_id FROM runs WHERE id=?", (run_id,),
            ).fetchone()
            self.assertEqual(stored_event["source_event_id"], event)
            self.assertEqual(persistent["status"], "COMPLETED")
            self.assertEqual(persistent["final_text"],
                             "SYNTHETIC PRE-ACTIVE RESPONSE ONLY")
        finally:
            cold.close()
        ledger.bind_dependency(
            self.task_id, "dependency:after-synthetic-result",
            kind="COORDINATION_COMMAND", target_id="command:advanced",
        )
        with self.assertRaisesRegex(ProvenanceBridgeError, "task"):
            self.proposal(ledger, binding)


    def fixture_checkpoint(self, ledger, binding, receipt):
        return checkpoint_source_linked_fixture(
            receipt, receiver=self.receiver, task_ledger=ledger,
            task_id=self.task_id, episode=self.episode, binding=binding,
            comment_id=81, message_id="reply-1", coverage=self.coverage,
            provider=self.provider, route_intent=self.intent,
            advertisements=(self.advisory_ad(),),
        )

    def test_real_mono_expected_head_cas_records_only_no_effect_fixture(self):
        if not PORTAL:
            self.skipTest("requires exact PORTAL source")
        sys.path.insert(0, str(Path(PORTAL)))
        ledger, binding = self.linked()
        path = Path(self.temp.name) / "cas-source-proposal.json"
        proposed = self.proposal(ledger, binding, receipt_path=path)
        before = proposed["portal_request"]["task_journal_head"]
        decision = self.fixture_checkpoint(ledger, binding, path)
        self.assertEqual(decision["status"], "SOURCE_FIXTURE_CHECKPOINT_RECORDED")
        self.assertEqual(decision["predecessor_journal_head"], before)
        self.assertNotEqual(decision["checkpoint_journal_head"], before)
        self.assertEqual(decision["task_id"], self.task_id)
        self.assertEqual(decision["source_digest"],
                         proposed["source_evidence"]["message"]["semantic_sha256"])
        self.assertEqual(decision["request_id"], proposed["native_call"]["request_id"])
        self.assertEqual(decision["route_id"], "dev:virtio-qwen4b")
        self.assertEqual(decision["requested_effect"], "NO_PROTECTED_EFFECT")
        for forbidden in ("dispatch_accepted", "model_admitted",
                          "accepted_as_task_result", "effect_authority", "executed"):
            self.assertIs(decision[forbidden], False)
        reopened = self.Ledger(ledger.path)
        current = reopened.read(self.task_id)
        self.assertEqual(current.journal_head_digest,
                         decision["checkpoint_journal_head"])
        self.assertEqual(current.latest_checkpoint["lifecycle_evidence_digest"],
                         proposed["receipt_sha256"])
        self.assertIn("COGNITION_TURN",
                      current.latest_checkpoint["protected_effects_still_gated"])
        # Duplicate no-effect request ID must not append another checkpoint.
        count = len(reopened.events(self.task_id))
        with self.assertRaisesRegex(ProvenanceBridgeError, "stale|expected|task"):
            self.fixture_checkpoint(reopened, binding, path)
        self.assertEqual(len(reopened.events(self.task_id)), count)

    def test_cas_rejects_interleaved_task_mutation_after_source_verification(self):
        if not PORTAL:
            self.skipTest("requires exact PORTAL source")
        from unittest.mock import patch
        sys.path.insert(0, str(Path(PORTAL)))
        ledger, binding = self.linked()
        path = Path(self.temp.name) / "interleaved-proposal.json"
        self.proposal(ledger, binding, receipt_path=path)
        checkpoint = ledger.checkpoint
        def concurrent_checkpoint(*args, **kwargs):
            ledger.bind_dependency(
                self.task_id, "dependency:cas-contender",
                kind="COORDINATION_COMMAND", target_id="command:other-writer",
            )
            return checkpoint(*args, **kwargs)
        with patch.object(ledger, "checkpoint", side_effect=concurrent_checkpoint):
            with self.assertRaisesRegex(ProvenanceBridgeError, "stale|expected"):
                self.fixture_checkpoint(ledger, binding, path)
        self.assertIsNone(ledger.read(self.task_id).latest_checkpoint)
