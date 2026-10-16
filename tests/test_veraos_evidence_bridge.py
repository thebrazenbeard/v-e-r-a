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
    VERAOS_HEAD, NATIVE_ROUTE_BLOB, GUEST_PROBE_BLOB,
)

ROOT = Path(__file__).resolve().parents[1]
MONO = os.environ.get("VERA_MONO_SOURCE_ROOT")
TRAINING = os.environ.get("VERA_TRAINING_SOURCE_ROOT")
INTRANEL = os.environ.get("INTRANEL_SOURCE_ROOT")
VERAOS = os.environ.get("VERAOS_SOURCE_ROOT")


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
            (cls.mono, "dec5c029e51c4fd436435cbda7e02e501822ee85"),
            (cls.training, "1390fbebbc5d1685a80610796e7ad8c2b955dac1"),
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
