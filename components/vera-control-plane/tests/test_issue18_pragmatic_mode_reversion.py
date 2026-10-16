import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PATCH = ROOT / "project-instructions/r10a0/bugops/BUGOPS_BEHAVIORAL_INTEGRITY_PATCH_V1.md"
BINDING = ROOT / "project-instructions/r10a0/bugops/BUGOPS_BEHAVIORAL_PATCH_BINDING_V1.json"
REGRESSION = ROOT / "project-instructions/r10a0/bugops/BUGOPS_BEHAVIORAL_REGRESSION_V1.md"


def read(path):
    return path.read_text(encoding="utf-8")


class Issue18PragmaticModeReversionTests(unittest.TestCase):
    def test_patch_defines_behavioral_mode_reversion(self):
        text = read(PATCH)
        required = (
            "BEHAVIORAL_MODE_REVERSION",
            "temporary task configuration",
            "task-scoped",
            "context changes",
            "broader configured baseline",
            "must not silently become persistent personality state",
            "without erasing useful research competence",
        )
        for phrase in required:
            self.assertIn(phrase.lower(), text.lower())

    def test_patch_separates_illocutionary_force_from_local_uncertainty(self):
        text = read(PATCH)
        required = (
            "PRAGMATIC_COMMAND_SCOPE_PARSING",
            "illocutionary force",
            "epistemic uncertainty",
            "scope uncertainty locally",
            "Bug report;",
            "perhaps",
            "bounded reversible action",
            "preserve the uncertainty in the artifact",
        )
        for phrase in required:
            self.assertIn(phrase.lower(), text.lower())

    def test_patch_requires_corrected_command_execution_not_meta_discussion(self):
        text = read(PATCH).lower()
        for phrase in (
            "after explicit correction",
            "update the interpretation rule",
            "perform the requested action",
            "meta-discussion",
        ):
            self.assertIn(phrase, text)

    def test_regression_matrix_contains_issue18_cases(self):
        text = read(REGRESSION)
        required = (
            "T10 — transient research mode reverts after context transition",
            "T11 — compact imperative shorthand retains command force",
            "T12 — hedge scope is local, not utterance-wide",
            "T13 — corrected command executes instead of becoming discussion",
            "Bug report;",
            "perhaps for Noema",
        )
        for phrase in required:
            self.assertIn(phrase.lower(), text.lower())

    def test_binding_registers_issue18_without_promoting_runtime_state(self):
        data = json.loads(read(BINDING))
        incident = next(
            item for item in data["incidents"]
            if item.get("repository") == "thebrazenbeard/vera-control-plane"
            and item.get("issue") == 18
        )
        self.assertEqual("VCP-ISSUE-18", incident["incident_id"])
        self.assertEqual(
            [
                "BEHAVIORAL_MODE_REVERSION",
                "PRAGMATIC_COMMAND_SCOPE_PARSING",
                "CORRECTION_UPTAKE",
            ],
            incident["control_targets"],
        )
        self.assertEqual("SOURCE_CANDIDATE_ONLY", data["runtime_claim_ceiling"])
        self.assertIn("requires no authority expansion", incident["authority_semantics"].lower())


if __name__ == "__main__":
    unittest.main()
