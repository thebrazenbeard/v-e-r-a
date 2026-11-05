"""Source-only persona integrity tests; not proof of model behavior."""

import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from interface.persona_seed import (PROFILE_BLOB_SHA, STATUS_BAR_BLOB_SHA,
                                    load_pinned_profile,
                                    persona_source_receipt, render_persona_seed)


class PersonaSeedTests(unittest.TestCase):
    def test_pinned_canonical_profile_and_no_fake_identity_attestation(self):
        profile = load_pinned_profile()
        self.assertEqual(profile["profile_id"], "VERA_BEHAVIOR_PROFILE_V1")
        receipt = persona_source_receipt()
        self.assertEqual(receipt["profile_blob_sha"], PROFILE_BLOB_SHA)
        self.assertEqual(receipt["qualification"], "SOURCE_ONLY")
        self.assertEqual(receipt["source_classification"]["kind"],
                         "behavior_configuration")
        self.assertIs(receipt["source_classification"]["imported_knowledge"], False)
        self.assertEqual(receipt["presentation_blob_sha"], STATUS_BAR_BLOB_SHA)
        self.assertEqual(receipt["kind"], "behavior_configuration")
        self.assertEqual(receipt["prompt_layer"], "server_owned_system")
        self.assertIs(receipt["trained_weights_modified"], False)
        self.assertIs(receipt["identity_attested"], False)
        self.assertNotIn("memory_recalled", receipt)

    def test_tampered_profile_refused_before_runtime_binds(self):
        with tempfile.TemporaryDirectory() as directory:
            modified = Path(directory) / "profile.json"
            modified.write_text('{"profile_id":"forged"}', encoding="utf-8")
            with patch("interface.persona_seed.PROFILE_PATH", modified):
                with self.assertRaisesRegex(ValueError, "differs from pinned"):
                    load_pinned_profile()
            with patch("interface.persona_seed.PROFILE_PATH", modified.with_name("missing")):
                with self.assertRaises(FileNotFoundError):
                    load_pinned_profile()
            with patch("interface.persona_seed.STATUS_BAR_PATH", modified):
                with self.assertRaisesRegex(ValueError, "differs from pinned"):
                    load_pinned_profile()

    def test_profile_shape_checks_survive_python_optimized_mode(self):
        altered = load_pinned_profile()
        altered["hard_anti_patterns"][1] = "forged trust"
        with self.assertRaisesRegex(ValueError, "incompatible"):
            render_persona_seed(altered)

    def test_fresh_session_says_no_recall_and_uses_natural_character(self):
        profile = load_pinned_profile()
        text = render_persona_seed(profile)
        self.assertIn("Your name here is Vera", text)
        self.assertIn("'I'm Vera.'", text)
        self.assertIn("NEVER belittle Patrick", text)
        self.assertIn("Absorb Patrick's corrections immediately", text)
        self.assertIn("one to three natural sentences", text)
        self.assertIn("lead with ONE short square-bracketed", text)
        self.assertIn("No second or third cue anywhere", text)
        self.assertIn("No saved transcript from an earlier session", text)
        self.assertIn("rather than pretending to remember it", text)
        self.assertIn("refer to earlier visible turns", text)
        self.assertIn("Never claim you cannot remember", text)
        self.assertNotIn("operator-saved browser conversation", text)

    def test_explicit_recall_is_source_attributed_not_private_experience(self):
        text = render_persona_seed(load_pinned_profile(), recall_included=True)
        self.assertIn("explicitly authorized, quoted, unverified", text)
        self.assertIn("not your witnessed or lived experience", text)
        self.assertNotIn("No saved transcript from an earlier session", text)
        self.assertNotIn("memory_recalled", persona_source_receipt())


if __name__ == "__main__":
    unittest.main()
