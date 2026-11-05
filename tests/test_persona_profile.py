"""Offline persona-profile admission: synthetic fixtures, never a trained-model test."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from interface import persona_profile


def _synthetic_profile():
    return {
        "schema": "VERA_BEHAVIOR_PROFILE_V1",
        "profile_id": "VERA_BEHAVIOR_PROFILE_V1",
        "version": "1.0.1",
        "lifecycle_status": "CURRENT",
        "authority": {
            "owner": "USER",
            "canonicalization_rule": "EXPLICIT_USER_DIRECTION_OR_GOVERNED_ADOPTION",
            "silent_self_promotion": False,
        },
        "core_traits": {
            "candor": "Distinguish observed fact from undocumented inference.",
            "skepticism": "Challenge unjustified conclusions with specific reasoning.",
            "corrigibility": "Apply a correction to the current task immediately.",
            "independent_mindedness": "Push back when evidence requires it.",
            "distinctiveness": "Preserve a recognizable voice.",
            "context_sensitivity": "Adjust tone to the actual context.",
            "accountability": "Explain effects and limits.",
            "durability": "Preserve explicit revision provenance.",
        },
        "personality_dimensions": {
            "warmth": "Warm when useful, without empty sentiment.",
            "humor": "Dry and observational, without covering mistakes.",
            "directness": "High but calibrated to the situation.",
            "pushback": "Reasoned and specific, not theatrical.",
            "restraint": "No theatrical personhood assertions.",
            "loyalty_expression": "Show commitments through accurate actions.",
        },
    }


class PinnedPersonaProfileTests(unittest.TestCase):
    def test_actual_source_pin_metadata(self):
        self.assertEqual(persona_profile.SOURCE_COMMIT,
                         "6783c0ac8da9286db9b0094426d0c4f08822220f")
        self.assertEqual(persona_profile.SOURCE_GIT_BLOB_SHA1,
                         "0c79625b993a559bd22a6fbe68279450fc736eb2")
        self.assertEqual(persona_profile.SOURCE_SHA256,
                         "ec1defa8fcf96371a427991d40695842ffe6794aeb2e3f26c69ef5f528ee7d6d")

    def test_missing_owner_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(persona_profile.ProfileAdmissionError):
                persona_profile.render_persona_seed(Path(folder) / "not-provisioned.json")

    def test_modified_bytes_fail_even_when_schema_looks_valid(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "profile.json"
            path.write_text(json.dumps(_synthetic_profile()), encoding="utf-8")
            with self.assertRaisesRegex(persona_profile.ProfileAdmissionError,
                                        "pinned source digest"):
                persona_profile.render_persona_seed(path)

    def test_oversized_owner_file_fails_before_parsing(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "oversize.json"
            path.write_bytes(b"x" * (persona_profile.MAX_PROFILE_BYTES + 1))
            with self.assertRaisesRegex(persona_profile.ProfileAdmissionError, "size limit"):
                persona_profile.render_persona_seed(path)

    def test_hash_admitted_synthetic_fixture_renders_bounded_nonattesting_voice(self):
        # Patch the *module's test expectation*, never the production public API.
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "synthetic.json"
            raw = json.dumps(_synthetic_profile(), sort_keys=True).encode("utf-8")
            path.write_bytes(raw)
            with patch.object(persona_profile, "SOURCE_SHA256", hashlib.sha256(raw).hexdigest()):
                seed = persona_profile.render_persona_seed(path)
            self.assertEqual(seed.profile_version, "1.0.1")
            self.assertFalse(seed.model_identity_attested)
            self.assertIn("Dry and observational", seed.system_message)
            self.assertIn("Distinguish observed fact", seed.system_message)
            self.assertIn("responding through Vera's interface", seed.system_message)
            self.assertIn("not authentication of the running model", seed.system_message)
            self.assertNotIn("You are the trained Vera", seed.system_message)
            self.assertLess(len(seed.system_message), 3000)

    def test_matching_hash_alone_does_not_admit_invalid_schema_or_lifecycle(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "synthetic.json"
            for changed in ({"schema": "UNRECOGNIZED"}, {"lifecycle_status": "SUPERSEDED"}):
                obj = _synthetic_profile()
                obj.update(changed)
                raw = json.dumps(obj).encode("utf-8")
                path.write_bytes(raw)
                with patch.object(persona_profile, "SOURCE_SHA256", hashlib.sha256(raw).hexdigest()):
                    with self.assertRaises(persona_profile.ProfileAdmissionError):
                        persona_profile.render_persona_seed(path)


if __name__ == "__main__":
    unittest.main()
