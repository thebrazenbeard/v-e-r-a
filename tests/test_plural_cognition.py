"""Unity without erasure: read-only projection of genuine Mosaic V1 receipts."""
from __future__ import annotations

from dataclasses import asdict
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from copy import deepcopy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from integration.plural_cognition import (
    Participant, PluralityProtocolError,
    compose_mosaic_plurality, verify_mosaic_plurality,
)

FIXTURE = Path(__file__).parent / "fixtures" / "mosaic_plurality_v1.json"
MOSAIC_ROOT = os.environ.get("MOSAIC_SOURCE_ROOT")
if MOSAIC_ROOT:
    sys.path.insert(0, MOSAIC_ROOT)


def load_fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def participants(fixture):
    return {key: Participant(**value) for key, value in fixture["participants"].items()}


class PluralityTests(unittest.TestCase):
    def test_disagreement_preserved_across_serialized_restart(self):
        fixture = load_fixture()
        projection = compose_mosaic_plurality(fixture["receipt"], participants(fixture))
        self.assertEqual(projection["alignment"], "DISSENT_RETAINED")
        self.assertEqual(projection["disagreeing_specialists"], ["critic"])
        self.assertEqual(len(projection["contributions"]), 3)
        self.assertEqual(projection["contributions"][0]["position"]["reasoning"], "Initial conservative Core answer")
        self.assertEqual(projection["contributions"][1]["position"]["rationale"], "Counterexample challenges the Core")
        self.assertEqual(projection["contributions"][-1]["position"]["reasoning"], "Core retained its view while acknowledging the challenge")
        self.assertEqual(projection["source_receipt"]["receipt_sha256"], fixture["receipt"]["receipt_sha256"])
        self.assertFalse(projection["effect_executed"])
        self.assertEqual(projection["authorization_effect"], "NONE")
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "projection.json"
            file.write_text(json.dumps(projection, sort_keys=True), encoding="utf-8")
            verify_mosaic_plurality(json.loads(file.read_text(encoding="utf-8")))
        self.assertEqual(fixture["participants"]["critic"]["local_state_ref"],
                         projection["participants"]["critic"]["local_state_ref"])

    def test_original_core_revision_survives_change_of_conclusion(self):
        fixture = load_fixture()
        # Actual Mosaic source is not executed here: frozen fixture is reused
        # to show tamper rejection; altered fixture must never be re-signed.
        tampered = deepcopy(fixture["receipt"])
        tampered["core_final"]["supports"] = not tampered["core_final"]["supports"]
        with self.assertRaisesRegex(PluralityProtocolError, "digest"):
            compose_mosaic_plurality(tampered, participants(fixture))

    def test_eliminating_or_rewriting_dissent_fails(self):
        fixture = load_fixture()
        projection = compose_mosaic_plurality(fixture["receipt"], participants(fixture))
        for operation in (
            lambda p: p["contributions"].pop(1),
            lambda p: p["disagreeing_specialists"].clear(),
            lambda p: p["contributions"][1]["position"].update({"supports": True}),
            lambda p: p["final_core_position"].update({"reasoning": "silenced"}),
            lambda p: p["participants"]["critic"].update({"local_state_ref": "rewritten"}),
            lambda p: p.update({"effect_executed": True}),
        ):
            altered = deepcopy(projection)
            operation(altered)
            with self.assertRaises(PluralityProtocolError):
                verify_mosaic_plurality(altered)

    def test_core_and_specialist_ownership_cannot_be_reassigned(self):
        f = load_fixture()
        p = participants(f)
        p.pop("critic")
        with self.assertRaisesRegex(PluralityProtocolError, "directory"):
            compose_mosaic_plurality(f["receipt"], p)
        p = participants(f)
        p["critic"] = Participant("critic", "CORE", p["critic"].source_ref,
                                  p["critic"].source_sha256, p["critic"].local_state_ref)
        with self.assertRaisesRegex(PluralityProtocolError, "role"):
            compose_mosaic_plurality(f["receipt"], p)
        p = participants(f)
        p["core"] = Participant("critic", "CORE", p["core"].source_ref,
                                p["core"].source_sha256, p["core"].local_state_ref)
        with self.assertRaisesRegex(PluralityProtocolError, "identity"):
            compose_mosaic_plurality(f["receipt"], p)

    @unittest.skipUnless(MOSAIC_ROOT, "exact Mosaic source required")
    def test_changed_core_stance_preserves_original_and_independent_evidence(self):
        from runtime.thinking_core import (
            CoreDeliberationEngine, CorePosition, DeliberationTask,
            SpecialistObjection, EvidenceVerdict,
        )
        class Core:
            def think(self, task):
                return CorePosition(task.proposition_id, True, "Initial view before challenge")
            def reconsider(self, task, prior, objections, evidence):
                return CorePosition(task.proposition_id, False,
                                    "Corrected Core reasoning under evidence", ("critic",))
        class Critic:
            specialist_id = "critic"
            def review(self, task, core_position):
                return SpecialistObjection("critic", task.proposition_id, False,
                                           "Specialist found a contradiction")
        class Verifier:
            def examine(self, task, proposal, objections):
                return EvidenceVerdict(task.proposition_id, False, "independent",
                                       "audit:case-proof", "Independent falsifying observation")

        task = DeliberationTask("case-revised-2", "claim-B", "Does B hold?", consequential=True)
        receipt = CoreDeliberationEngine().deliberate(task, Core(), (Critic(),), Verifier())
        declarations = participants(load_fixture())
        declarations["independent"] = Participant(
            "independent", "INDEPENDENT_VERIFIER", "fixture:verifier:1",
            "d" * 64, "participant:verifier:private-local-state",
        )
        combined = compose_mosaic_plurality(receipt, declarations)
        self.assertTrue(combined["contributions"][0]["position"]["supports"])
        self.assertFalse(combined["contributions"][-1]["position"]["supports"])
        self.assertEqual([x["phase"] for x in combined["contributions"]],
                         ["INITIAL", "REVIEW", "INDEPENDENT_EVIDENCE", "FINAL"])
        self.assertEqual(combined["alignment"], "REVIEWERS_ALIGNED_WITH_FINAL")
        self.assertEqual(combined["mosaic_decision_status"], "EVIDENCE_SUPPORTED_ADVISORY")
        self.assertEqual(combined["contributions"][2]["position"]["evidence_ref"], "audit:case-proof")
        self.assertFalse(combined["effect_executed"])
        verify_mosaic_plurality(json.loads(json.dumps(combined)))

    @unittest.skipUnless(MOSAIC_ROOT, "exact Mosaic source required")
    def test_consequential_unverified_disagreement_remains_on_hold(self):
        from runtime.thinking_core import (
            CoreDeliberationEngine, CorePosition, DeliberationTask, SpecialistObjection,
        )
        class Core:
            def think(self, task):
                return CorePosition(task.proposition_id, True, "An uncertain view")
            def reconsider(self, task, prior, objections, evidence):
                return CorePosition(task.proposition_id, True,
                                    "Dispute acknowledged but still unresolved", ("critic",))
        class Critic:
            specialist_id = "critic"
            def review(self, task, prior):
                return SpecialistObjection("critic", task.proposition_id, False,
                                           "Unresolved credible alternative")

        task = DeliberationTask("case-high-stakes-3", "claim-C", "Act on C?",
                                consequential=True, protected_effect=True)
        receipt = CoreDeliberationEngine().deliberate(task, Core(), (Critic(),))
        record = compose_mosaic_plurality(receipt, participants(load_fixture()))
        self.assertEqual(record["mosaic_decision_status"], "HOLD_UNVERIFIED_DISPUTE")
        self.assertEqual(record["alignment"], "DISSENT_RETAINED")
        self.assertFalse(record["effect_executed"])
        self.assertEqual(record["authorization_effect"], "NONE")
        verify_mosaic_plurality(json.loads(json.dumps(record)))

    def test_supplied_authentication_or_cognition_claim_is_never_created(self):
        f = load_fixture()
        projection = compose_mosaic_plurality(f["receipt"], participants(f))
        self.assertEqual(projection["identity_or_consciousness_claim"], "NONE")
        self.assertIn("not authentication", projection["claim_ceiling"])
        self.assertNotIn("permit", projection)
        self.assertNotIn("execute", projection)
        self.assertNotIn("QUALIFIED", projection["alignment"])

    @unittest.skipUnless(MOSAIC_ROOT, "set MOSAIC_SOURCE_ROOT to the exact Mosaic Thinking Core PR10 checkout")
    def test_real_mosaic_deliberation_engine_composes_instead_of_mock(self):
        from runtime.thinking_core import (
            CoreDeliberationEngine, CorePosition, DeliberationTask, SpecialistObjection
        )

        class Core:
            def think(self, task):
                return CorePosition(task.proposition_id, True, "Initial conservative Core answer")
            def reconsider(self, task, prior, objections, evidence):
                return CorePosition(task.proposition_id, True,
                    "Core retained its view while acknowledging the challenge", ("critic",))
        class Critic:
            specialist_id = "critic"
            def review(self, task, core_position):
                return SpecialistObjection("critic", task.proposition_id, False,
                    "Counterexample challenges the Core")

        task = DeliberationTask("case-independent-1", "claim-A",
                                "Does evidence justify claim A?", consequential=False)
        actual = CoreDeliberationEngine().deliberate(task, Core(), (Critic(),))
        fixture = load_fixture()
        self.assertEqual(asdict(actual)["receipt_sha256"], fixture["receipt"]["receipt_sha256"])
        projection = compose_mosaic_plurality(actual, participants(fixture))
        self.assertEqual(projection["alignment"], "DISSENT_RETAINED")
        verify_mosaic_plurality(json.loads(json.dumps(projection)))
        self.assertEqual(projection["mosaic_decision_status"], "CONTESTED_ADVISORY")


if __name__ == "__main__":
    unittest.main()
