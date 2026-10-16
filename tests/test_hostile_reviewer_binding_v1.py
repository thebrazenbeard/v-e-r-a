import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
BINDING = ROOT / "governance" / "VERA_HOSTILE_REVIEWER_BINDING_V1.json"


class HostileReviewerBindingTests(unittest.TestCase):
    def test_binding_pins_repaired_runtime_exactly(self):
        data = json.loads(BINDING.read_text(encoding="utf-8"))
        runtime = data["runtime"]
        self.assertEqual("44bd82b07ced00cabf800c6ee36bf096a363b797", runtime["source_commit"])
        self.assertEqual("ecdf279a231e2469aa202098250fe30981aa900e", runtime["architecture_contract"]["blob"])
        self.assertEqual("da14b1f4fbfa587157dce1a7ce409313c7bda9a1", runtime["runtime_module"]["blob"])
        self.assertEqual("23b93c30a89bcd8002847a7a53d89eb145ef4e22", runtime["package_init"]["blob"])
        self.assertEqual("381d71150561b4fb28e6eec6cc454a335bef24cc", runtime["focused_test"]["blob"])

    def test_binding_pins_current_main_control_cut(self):
        data = json.loads(BINDING.read_text(encoding="utf-8"))
        control = data["control_plane"]
        self.assertEqual("98d0755c68d0c86f977ba31f3a1bbf757e78bcd0", control["control_core_commit"])
        self.assertEqual("8f3ffe26dbcfe9132138210ab1a1fe4a6b355ab9", control["control_contract"]["blob"])
        self.assertEqual("8b59faac8985c1bd237ee3f72a9ff466df80a097", control["source_state"]["blob"])
        self.assertEqual("fbb0eb93751dfb856d55ae92c047d30c48d5d807", control["toggle_tool"]["blob"])
        self.assertEqual("792de993db7dc122a06890112dcb61887803a514", control["focused_test"]["blob"])
        self.assertEqual("governance/VERA_HOSTILE_REVIEWER_BINDING_V1.json", control["binding_identity"]["path"])
        self.assertIn("does not self-hash", control["binding_identity"]["rule"])
        self.assertEqual("ATOMIC_O_EXCL_LOCKFILE", control["mutation_semantics"]["single_writer_lock"])
        self.assertEqual("FAIL_CLOSED_RECONCILE", control["mutation_semantics"]["lock_collision"])
        self.assertTrue(control["mutation_semantics"]["exact_readback"])

    def test_typed_contract_and_lifecycle_ceiling_are_explicit(self):
        data = json.loads(BINDING.read_text(encoding="utf-8"))
        typed = data["runtime"]["typed_contract"]
        self.assertEqual("LiteralProposition", typed["input"])
        self.assertEqual("HostileReviewDecision", typed["output"])
        self.assertTrue(typed["proposition_digest_bound"])
        self.assertTrue(typed["primary_answer_digest_bound"])
        self.assertTrue(typed["zero_objection_survival_allowed"])
        self.assertTrue(typed["stronger_route_guarded"])
        self.assertEqual("NOT_ESTABLISHED", data["lifecycle"]["install"])
        self.assertEqual("NOT_ESTABLISHED", data["lifecycle"]["runtime_consumption"])
        self.assertEqual("NOT_ESTABLISHED", data["lifecycle"]["behavioral_qualification"])


if __name__ == "__main__":
    unittest.main()
