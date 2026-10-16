from pathlib import Path
import hashlib
import json
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
CUT = ROOT / "project-instructions/r10a0/restore-v2-live"
MANIFEST = CUT / "VERA_R10A0_SD1_RESTORE_V2_PROJECT_SOURCE_MANIFEST.json"
NATIVE = CUT / "VERA_R10A0_SD1_RESTORE_V2_NATIVE_PROJECT_INSTRUCTIONS.txt"

PRE_COMMIT = "3fb3c998cf714ed556bb2620649f41361f22e4a1"
PRE_PATH = "project-instructions/r10a0/bus-topology-v2/VERA_R10A0_BUS_TOPOLOGY_NATIVE_PROJECT_INSTRUCTIONS_V2.txt"
ARTIFACT_COMMIT = "687ba64555c39619a9552a86206fa78ab3387a7e"
MANIFEST_PATH = "project-instructions/r10a0/restore-v2-live/VERA_R10A0_SD1_RESTORE_V2_PROJECT_SOURCE_MANIFEST.json"
NATIVE_PATH = "project-instructions/r10a0/restore-v2-live/VERA_R10A0_SD1_RESTORE_V2_NATIVE_PROJECT_INSTRUCTIONS.txt"
EXPECTED_MANIFEST_SHA = "fb99689bd8e8efabf6b9612d7f1451ea9701fae3e655c6cf6dfab0f043a3aeac"
EXPECTED_NATIVE_SHA = "1cfc6708c4e64cebae0a4721d38eb59592239d2ba61e7c4196130162c6e5381b"


def git_bytes(commit, path):
    return subprocess.run(
        ["git", "-C", str(ROOT), "show", f"{commit}:{path}"],
        check=True, capture_output=True,
    ).stdout


def git_blob(commit, path):
    return subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", f"{commit}:{path}"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
class RestoreV2InstallTests(unittest.TestCase):
    def test_manifest_and_native_hashes(self):
        manifest_bytes = git_bytes(ARTIFACT_COMMIT, MANIFEST_PATH)
        native_bytes = git_bytes(ARTIFACT_COMMIT, NATIVE_PATH)
        self.assertEqual(hashlib.sha256(manifest_bytes).hexdigest(), EXPECTED_MANIFEST_SHA)
        self.assertEqual(hashlib.sha256(native_bytes).hexdigest(), EXPECTED_NATIVE_SHA)
        self.assertEqual(len(native_bytes), 7997)

    def test_native_diff_is_only_k00_and_restore_line(self):
        predecessor = git_bytes(PRE_COMMIT, PRE_PATH).decode("utf-8").splitlines()
        candidate = git_bytes(ARTIFACT_COMMIT, NATIVE_PATH).decode("utf-8").splitlines()
        self.assertEqual(len(predecessor), len(candidate))
        changed = [(i, a, b) for i, (a, b) in enumerate(zip(predecessor, candidate), start=1) if a != b]
        self.assertEqual(len(changed), 2)
        self.assertTrue(changed[0][1].startswith("K00 ROOT:R10_PLUS_SD1;"))
        self.assertTrue(changed[0][2].startswith("K00 ROOT:R10_PLUS_SD1_RESTORE_V2;"))
        self.assertTrue(changed[1][1].startswith("`restore yourself`=>"))
        self.assertTrue(changed[1][2].startswith("`restore yourself`=>CONTROL_LOAD `RESTORE_V2`;"))

    def test_native_pins_manifest_sha(self):
        text = git_bytes(ARTIFACT_COMMIT, NATIVE_PATH).decode("utf-8")
        self.assertIn(f"SHA256=`{EXPECTED_MANIFEST_SHA}`", text)
        self.assertIn("manifest=`VERA_R10A0_SD1_RESTORE_V2_PROJECT_SOURCE_MANIFEST.json`", text)
    def test_all_bound_owners_resolve_exact_git_objects(self):
        manifest = json.loads(git_bytes(ARTIFACT_COMMIT, MANIFEST_PATH))
        groups = [
            manifest["predecessor_runtime"]["settings"],
            *manifest["predecessor_runtime"]["project_sources"].values(),
            *manifest["restore_v2"].values(),
            *manifest["r10a2_completion"].values(),
        ]
        for binding in groups:
            data = git_bytes(binding["source_commit"], binding["path"])
            self.assertEqual(git_blob(binding["source_commit"], binding["path"]), binding["git_blob"])
            self.assertEqual(hashlib.sha256(data).hexdigest(), binding["sha256"])
            self.assertEqual(len(data), binding["bytes"])

    def test_restore_composition_preserves_subject_separation(self):
        manifest = json.loads(git_bytes(ARTIFACT_COMMIT, MANIFEST_PATH))
        composition = manifest["control_composition"]
        self.assertIn("supersession/currentness", composition["centered_subject_rule"])
        self.assertIn("cannot override centered-subject selection", composition["r10a2_candidate_scope"])
        self.assertIn("COMPLETE_FULL_SELF", composition["success_rule"])
        self.assertIn("R10A2 deterministic RESTORED", composition["success_rule"])

    def test_required_full_self_layers_are_exactly_ten(self):
        manifest = json.loads(git_bytes(ARTIFACT_COMMIT, MANIFEST_PATH))
        binding = manifest["restore_v2"]["protocol_json"]
        protocol = json.loads(git_bytes(binding["source_commit"], binding["path"]))
        ids = [item["id"] for item in protocol["required_restore_layers"]]
        self.assertEqual(len(ids), 10)
        self.assertIn("EXACT_RELATIONSHIP_IDENTITY", ids)
        self.assertIn("SEXUAL_SELF_CONCEPT", ids)
        self.assertIn("PATRICK_SPECIFIC_EMPATHY_RELATIONAL_MODEL", ids)
        self.assertIn("BEHAVIORAL_EMBODIMENT_NONVERBAL_REPRESENTATION", ids)
        self.assertIn("VERA_SPECIFIC_BEHAVIORAL_TEXTURE", ids)


if __name__ == "__main__":
    unittest.main()
