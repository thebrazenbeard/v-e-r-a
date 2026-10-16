import copy
import importlib.util
import json
import pathlib
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "hostile_reviewer_toggle.py"
CONTROL = ROOT / "governance" / "VERA_HOSTILE_REVIEWER_CONTROL_V1.json"
SOURCE_STATE = ROOT / "state" / "features" / "hostile-reviewer-v1.json"

spec = importlib.util.spec_from_file_location("hostile_reviewer_toggle", TOOL)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class HostileReviewerToggleTests(unittest.TestCase):
    def test_control_contract_binds_current_typed_runtime(self):
        data = json.loads(CONTROL.read_text(encoding="utf-8"))
        runtime = data["runtime_source"]
        self.assertEqual("44bd82b07ced00cabf800c6ee36bf096a363b797", runtime["head"])
        self.assertEqual("da14b1f4fbfa587157dce1a7ce409313c7bda9a1", runtime["runtime_module_blob"])
        self.assertEqual("ecdf279a231e2469aa202098250fe30981aa900e", runtime["architecture_contract_blob"])
        self.assertEqual("23b93c30a89bcd8002847a7a53d89eb145ef4e22", runtime["runtime_package_init_blob"])
        self.assertEqual("381d71150561b4fb28e6eec6cc454a335bef24cc", runtime["runtime_test_blob"])
        self.assertEqual("LiteralProposition", runtime["typed_input"])
        self.assertEqual("HostileReviewDecision", runtime["typed_output"])
        self.assertEqual(["LITERAL_SURVIVES", "LITERAL_FAILS", "UNRESOLVED"], runtime["literal_verdicts"])

    def test_source_state_defaults_off_without_false_install_claim(self):
        data = json.loads(SOURCE_STATE.read_text(encoding="utf-8"))
        self.assertEqual(0, data["generation"])
        self.assertEqual("OFF", data["mode"])
        self.assertEqual("VERA_PROJECT_ALL_CHATS", data["scope"])
        self.assertEqual("SOURCE_CANDIDATE_NOT_INSTALLED", data["source_status"])
        module._validate_state(data)

    def test_cas_toggle_on_and_exact_readback(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "state.json"
            path.write_text(SOURCE_STATE.read_text(encoding="utf-8"), encoding="utf-8")
            result = module.set_mode(path, mode="ON", expected_generation=0, note="test")
            self.assertEqual(1, result["generation"])
            self.assertEqual("ON", result["mode"])
            self.assertEqual(result, module.load_state(path))
            self.assertFalse(path.with_name(f".{path.name}.lock").exists())

    def test_stale_generation_is_rejected_without_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "state.json"
            path.write_text(SOURCE_STATE.read_text(encoding="utf-8"), encoding="utf-8")
            first = module.set_mode(path, mode="ON", expected_generation=0)
            before = path.read_text(encoding="utf-8")
            with self.assertRaises(module.HostileReviewerControlError):
                module.set_mode(path, mode="OFF", expected_generation=0)
            self.assertEqual(before, path.read_text(encoding="utf-8"))
            self.assertEqual(first, module.load_state(path))

    def test_existing_mutation_lock_fails_closed_without_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "state.json"
            path.write_text(SOURCE_STATE.read_text(encoding="utf-8"), encoding="utf-8")
            lock_path = path.with_name(f".{path.name}.lock")
            lock_path.write_text("held\n", encoding="utf-8")
            before = path.read_text(encoding="utf-8")
            with self.assertRaisesRegex(module.HostileReviewerControlError, "concurrent mutation lock"):
                module.set_mode(path, mode="ON", expected_generation=0)
            self.assertEqual(before, path.read_text(encoding="utf-8"))
            self.assertEqual("held\n", lock_path.read_text(encoding="utf-8"))

    def test_boolean_generation_is_rejected(self):
        data = json.loads(SOURCE_STATE.read_text(encoding="utf-8"))
        data["generation"] = True
        with self.assertRaisesRegex(module.HostileReviewerControlError, "exact non-negative integer"):
            module._validate_state(data)
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "state.json"
            path.write_text(SOURCE_STATE.read_text(encoding="utf-8"), encoding="utf-8")
            with self.assertRaisesRegex(module.HostileReviewerControlError, "expected_generation"):
                module.set_mode(path, mode="ON", expected_generation=True)

    def test_unknown_state_field_is_rejected(self):
        data = json.loads(SOURCE_STATE.read_text(encoding="utf-8"))
        data["authority"] = "MINTED"
        with self.assertRaisesRegex(module.HostileReviewerControlError, "closed control schema"):
            module._validate_state(data)

    def test_install_ceiling_cannot_be_mutated_in_state(self):
        data = json.loads(SOURCE_STATE.read_text(encoding="utf-8"))
        data["source_status"] = "INSTALLED"
        with self.assertRaisesRegex(module.HostileReviewerControlError, "not-installed ceiling"):
            module._validate_state(data)

    def test_last_change_shape_and_mutation_kind_fail_closed(self):
        data = json.loads(SOURCE_STATE.read_text(encoding="utf-8"))
        bad = copy.deepcopy(data)
        bad["last_change"]["authority"] = "YES"
        with self.assertRaisesRegex(module.HostileReviewerControlError, "closed schema"):
            module._validate_state(bad)

        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "state.json"
            path.write_text(SOURCE_STATE.read_text(encoding="utf-8"), encoding="utf-8")
            with self.assertRaisesRegex(module.HostileReviewerControlError, "EXPLICIT_CONTROL_CHANGE"):
                module.set_mode(path, mode="ON", expected_generation=0, change_kind="RESTORE")
            with self.assertRaisesRegex(module.HostileReviewerControlError, "note must be a string"):
                module.set_mode(path, mode="ON", expected_generation=0, note=7)


if __name__ == "__main__":
    unittest.main()
