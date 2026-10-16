"""Actual-source Integration ↔ Training ↔ Vera Mono journal negative tests.

No external transport or model runtime; requires exact sibling source roots.
"""
from __future__ import annotations

from copy import deepcopy
import gc
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from integration.cognition_task_gate import (
    CognitionBindingError, TRAINING_HEAD, TRAINING_SUBJECT,
    bind_episode, verify_episode_binding,
)

MONO = os.environ.get("VERA_MONO_SOURCE_ROOT")
TRAINING = os.environ.get("VERA_TRAINING_SOURCE_ROOT")
ROOT = Path(__file__).resolve().parents[1]


def git(root, *argv):
    outcome = subprocess.run(
        ["git", "-C", str(root), *argv],
        capture_output=True, text=True, timeout=15, check=True,
    )
    return outcome.stdout.strip()


@unittest.skipUnless(MONO and TRAINING,
                     "Needs exact separate Vera Mono and Training sources")
class RealCognitionTaskGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mono = Path(MONO)
        cls.training = Path(TRAINING)
        cls.mono_head = "dec5c029e51c4fd436435cbda7e02e501822ee85"
        if git(cls.training, "rev-parse", "HEAD") != TRAINING_HEAD:
            raise AssertionError("wrong Training source HEAD")
        if git(cls.mono, "rev-parse", "HEAD") != cls.mono_head:
            raise AssertionError("wrong Vera Mono source HEAD")
        for root, path in (
            (cls.training, "participating_cognition_v1.py"),
            (cls.training, "independent_challenge_eval_v1.py"),
            (cls.mono, "packages/vera_core/src/vera_core/task_execution.py"),
        ):
            if git(root, "rev-parse", "HEAD:" + path) != git(root, "hash-object", str(root / path)):
                raise AssertionError("source file not pinned to exact Git blob")
        if git(cls.training, "status", "--porcelain", "--untracked-files=all",
               "--", "participating_cognition_v1.py", "independent_challenge_eval_v1.py"):
            raise AssertionError("untrusted Training source changes")
        sys.path[:0] = [str(cls.training), str(cls.training / "tests")]
        sys.path[:0] = [str(p) for p in (cls.mono / "packages").glob("*/src")]
        from vera_core.task_execution import TaskExecutionLedger, TaskPacket
        from test_participating_cognition_v1 import compose, cricket
        cls.Ledger, cls.Packet = TaskExecutionLedger, TaskPacket
        cls.compose, cls.cricket = staticmethod(compose), staticmethod(cricket)

    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.addCleanup(gc.collect)
        self.file = Path(self.tmp.name) / "vera-tasks.sqlite"
        self.task_id = "task:one"
        self.ledger = self.Ledger(self.file)
        raw = json.loads((ROOT / "integration" /
                          "example_readonly_task_packet.json").read_text("utf8"))
        packet = self.Packet(**{
            k: tuple(v) if isinstance(v, list) else v for k, v in raw.items()
        })
        self.ledger.open_task(
            self.task_id, packet, lifecycle_evidence_digest="a" * 64
        )
        self.episode = self.compose().as_dict()

    def test_cold_reopen_binds_current_task_and_preserves_untrusted_status(self):
        bound = bind_episode(self.ledger, self.task_id, self.episode)
        observed = verify_episode_binding(self.Ledger(self.file), self.task_id,
                                           self.episode, deepcopy(bound))
        self.assertEqual(observed["binding_digest"], bound["binding_digest"])
        self.assertEqual(observed["training_source_subject"], TRAINING_SUBJECT)
        for key in ("effect_authority", "executed", "accepted_as_task_result",
                    "independent_source_attestation"):
            self.assertIs(observed[key], False)
        self.assertEqual(observed["status"], "OBSERVED_UNATTESTED")

    def test_real_task_journal_advance_invalidates_previous_cognition_receipt(self):
        original = bind_episode(self.ledger, self.task_id, self.episode)
        self.ledger.bind_dependency(
            self.task_id, "dependency:changed", kind="COORDINATION_COMMAND",
            target_id="command:changed",
        )
        with self.assertRaisesRegex(CognitionBindingError, "stale"):
            verify_episode_binding(self.Ledger(self.file),
                                   self.task_id, self.episode, original)

    def test_claim_mutation_and_disguised_new_task_fail_closed(self):
        original = bind_episode(self.ledger, self.task_id, self.episode)
        tampered = deepcopy(self.episode)
        tampered["contributions"][0]["claim"]["value"] = "INJECTED"
        with self.assertRaisesRegex(CognitionBindingError, "digest"):
            verify_episode_binding(self.ledger, self.task_id, tampered, original)
        tampered = deepcopy(self.episode)
        tampered["task_id"] = "task:other"
        with self.assertRaises(CognitionBindingError):
            bind_episode(self.ledger, self.task_id, tampered)

    def test_training_cricket_block_remains_held_and_forged_pass_block_rejected(self):
        block = deepcopy(self.episode)
        block["cricket_review"]["disposition"] = "BLOCK"
        block["cricket_review"]["findings"] = [dict(
            rule_id="effect", severity="BLOCK", title="No authorization",
            rationale="No grant", evidence="fixture",
            recommendation="Hold", source="Cricket",
        )]
        block["status"] = "CRICKET_BLOCKED"
        held = bind_episode(self.ledger, self.task_id, block)
        self.assertEqual(held["status"], "HELD_SOURCE_REVIEW")
        self.assertFalse(held["effect_authority"])
        conflicting = deepcopy(self.episode)
        conflicting["cricket_review"] = {
            "disposition": "PASS",
            "findings": [dict(
                rule_id="effect", severity="BLOCK", title="No authorization",
                rationale="No grant", evidence="synthetic fixture",
                recommendation="Hold", source="Cricket",
            )],
        }
        # A self-declared PASS cannot contradict stronger nested findings.
        with self.assertRaisesRegex(CognitionBindingError, "contradicts"):
            bind_episode(self.ledger, self.task_id, conflicting)

    def test_source_head_substitution_and_binding_mutation_fail_closed(self):
        with self.assertRaisesRegex(CognitionBindingError, "source"):
            bind_episode(self.ledger, self.task_id, self.episode,
                         training_subject="git:thebrazenbeard/model-training@" + "b"*40)
        bound = bind_episode(self.ledger, self.task_id, self.episode)
        bound["effect_authority"] = True
        with self.assertRaises(CognitionBindingError):
            verify_episode_binding(self.ledger, self.task_id, self.episode, bound)


    def test_migrated_agent_and_cricket_challenge_fences(self):
        migrated = deepcopy(self.episode)
        migrated["contributions"][1]["participant"]["agent_id"] = (
            migrated["contributions"][0]["participant"]["agent_id"]
        )
        migrated["contributions"][1]["claim"]["agent_id"] = (
            migrated["contributions"][0]["participant"]["agent_id"]
        )
        with self.assertRaisesRegex(CognitionBindingError, "duplicate"):
            bind_episode(self.ledger, self.task_id, migrated)
        challenged = deepcopy(self.episode)
        challenged["cricket_review"] = {
            "disposition": "CHALLENGE",
            "findings": [dict(
                rule_id="challenge", severity="CHALLENGE", title="Review",
                rationale="Unresolved", evidence="fixture",
                recommendation="Check", source="Cricket",
            )],
        }
        challenged["status"] = "CRICKET_CHALLENGED"
        self.assertEqual(
            bind_episode(self.ledger, self.task_id, challenged)["status"],
            "HELD_SOURCE_REVIEW",
        )
        challenged["cricket_review"]["disposition"] = "PASS"
        with self.assertRaisesRegex(CognitionBindingError, "contradicts"):
            bind_episode(self.ledger, self.task_id, challenged)

    def test_runtime_correlation_is_not_independent_evidence(self):
        correlated = deepcopy(self.episode)
        correlated["contributions"][1]["participant"]["runtime_instance_id"] = (
            correlated["contributions"][0]["participant"]["runtime_instance_id"]
        )
        correlated["dissent"]["classification"] = "SELF_OR_CORRELATED_CLAIMS"
        self.assertEqual(
            bind_episode(self.ledger, self.task_id, correlated)["status"],
            "HELD_SOURCE_REVIEW",
        )
        forged = deepcopy(correlated)
        forged["dissent"]["classification"] = "EVIDENCE_CONFLICT_FOR_REVIEW"
        forged["dissent"]["challenge_for_review"] = True
        with self.assertRaisesRegex(CognitionBindingError, "correlated"):
            bind_episode(self.ledger, self.task_id, forged)

    def test_cricket_block_dominates_semantic_unrepresentable(self):
        blocked = deepcopy(self.episode)
        plan = blocked["core_semantic_plan"]
        plan["fidelity"] = "UNREPRESENTABLE"
        plan["required_capabilities"].append("latent:unresolved")
        plan["missing_capabilities"].append("latent:unresolved")
        plan["unresolved_capabilities"].append("latent:unresolved")
        blocked["cricket_review"] = {
            "disposition": "BLOCK",
            "findings": [dict(
                rule_id="block", severity="BLOCK", title="Blocked",
                rationale="Source holds", evidence="fixture",
                recommendation="Review", source="Cricket",
            )],
        }
        blocked["status"] = "CRICKET_BLOCKED"
        self.assertEqual(
            bind_episode(self.ledger, self.task_id, blocked)["status"],
            "HELD_SOURCE_REVIEW",
        )


    def test_dissent_review_flag_is_consistent_with_training_classification(self):
        forged = deepcopy(self.episode)
        forged["dissent"]["classification"] = "EVIDENCE_CONFLICT_FOR_REVIEW"
        forged["dissent"]["challenge_for_review"] = False
        with self.assertRaisesRegex(CognitionBindingError, "review classification"):
            bind_episode(self.ledger, self.task_id, forged)
        forged["dissent"]["challenge_for_review"] = True
        self.assertEqual(
            bind_episode(self.ledger, self.task_id, forged)["status"],
            "HELD_SOURCE_REVIEW",
        )
        forged["dissent"]["classification"] = "invented-proof"
        with self.assertRaisesRegex(CognitionBindingError, "review classification"):
            bind_episode(self.ledger, self.task_id, forged)
        forged = deepcopy(self.episode)
        forged["dissent"]["unexpected_claim"] = "adopted"
        with self.assertRaisesRegex(CognitionBindingError, "provenance"):
            bind_episode(self.ledger, self.task_id, forged)

    def test_shared_evidence_group_is_correlated_even_with_separate_runtimes(self):
        shared = deepcopy(self.episode)
        self.assertNotEqual(
            shared["contributions"][0]["participant"]["runtime_instance_id"],
            shared["contributions"][1]["participant"]["runtime_instance_id"],
        )
        shared["dissent"]["classification"] = "SELF_OR_CORRELATED_CLAIMS"
        shared["dissent"]["challenge_for_review"] = False
        result = bind_episode(self.ledger, self.task_id, shared)
        self.assertEqual(result["status"], "HELD_SOURCE_REVIEW")
        self.assertFalse(result["accepted_as_task_result"])
        self.assertFalse(result["effect_authority"])
        for classification in ("MIXED_CLAIM_TYPES", "EVIDENCE_CONFLICT_FOR_REVIEW"):
            changed = deepcopy(self.episode)
            changed["dissent"]["classification"] = classification
            changed["dissent"]["challenge_for_review"] = (
                classification == "EVIDENCE_CONFLICT_FOR_REVIEW"
            )
            self.assertEqual(
                bind_episode(self.ledger, self.task_id, changed)["status"],
                "HELD_SOURCE_REVIEW",
            )



    def test_task_journal_advance_during_binding_fails_closed(self):
        # Inject a REAL Vera Mono journal advancement just after the first
        # read returns a stable old snapshot, not a forged packet.
        class AdvanceAfterRead:
            def __init__(self, delegate):
                self.delegate = delegate
                self.advanced = False
            def verify_chain(self):
                return self.delegate.verify_chain()
            def read(self, task_id):
                snapshot = self.delegate.read(task_id)
                if not self.advanced:
                    self.delegate.bind_dependency(
                        task_id, "dependency:mid-binding",
                        kind="COORDINATION_COMMAND",
                        target_id="command:mid-binding",
                    )
                    self.advanced = True
                return snapshot
        racing = AdvanceAfterRead(self.ledger)
        with self.assertRaisesRegex(
            CognitionBindingError, "journal advanced during binding"
        ):
            bind_episode(racing, self.task_id, self.episode)
        self.assertTrue(racing.advanced)
        self.assertNotEqual(
            self.ledger.read(self.task_id).journal_head_digest,
            self.ledger.events(self.task_id)[0].event_digest,
        )


    def test_missing_semantic_capability_cannot_be_hidden_by_exact_status(self):
        forged = deepcopy(self.episode)
        plan = forged["core_semantic_plan"]
        plan["required_capabilities"].append("latent:unmapped")
        plan["missing_capabilities"].append("latent:unmapped")
        plan["fidelity"] = "EXACT"
        with self.assertRaisesRegex(CognitionBindingError, "rewrite coverage"):
            bind_episode(self.ledger, self.task_id, forged)

    def test_well_formed_lossy_semantic_plan_stays_no_effect_observation(self):
        source = deepcopy(self.episode)
        plan = source["core_semantic_plan"]
        plan["required_capabilities"].append("latent:lossy")
        plan["missing_capabilities"].append("latent:lossy")
        plan["rewrites"] = [{
            "source_capability": "latent:lossy",
            "rule_name": "fixture-rewrite",
            "fidelity": "LOSSY",
            "description": "Typed source-only lossy transformation",
        }]
        plan["fidelity"] = "LOSSY"
        bound = bind_episode(self.ledger, self.task_id, source)
        self.assertEqual(bound["status"], "OBSERVED_UNATTESTED")
        self.assertFalse(bound["effect_authority"])
        self.assertFalse(bound["accepted_as_task_result"])
