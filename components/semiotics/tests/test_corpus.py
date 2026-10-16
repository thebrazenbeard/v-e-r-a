import unittest
from pathlib import Path

from semiotics import load_registry


ROOT = Path(__file__).resolve().parents[1]


class CorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = load_registry(ROOT / "corpus/foundations.json")

    def test_sign_keeps_peirce_and_saussure_readings_separate(self):
        peirce = self.registry.query("sign", {"framework:peirce"})
        saussure = self.registry.query("sign", {"framework:saussure"})
        self.assertEqual(peirce[0]["interpretation"]["id"], "sign-peirce-triadic")
        self.assertEqual(
            saussure[0]["interpretation"]["id"],
            "sign-saussure-differential",
        )

    def test_peirce_classification_is_queryable(self):
        result = self.registry.query("index", {"framework:peirce"})
        self.assertEqual(result[0]["interpretation"]["id"], "index-peirce")
        self.assertEqual(result[0]["source"]["published_year"], 2022)

    def test_morris_dimensions_are_queryable(self):
        result = self.registry.query("pragmatics", {"framework:morris"})
        self.assertEqual(result[0]["interpretation"]["id"], "pragmatics-morris")
        self.assertEqual(result[0]["source"]["published_year"], 1938)

    def test_framework_specific_readings_do_not_match_without_context(self):
        self.assertEqual(self.registry.query("sign"), [])


    def test_augustine_historical_sign_reading_is_queryable(self):
        result = self.registry.query("sign", {"framework:augustine"})
        self.assertEqual(result[0]["interpretation"]["id"], "sign-augustine")
        self.assertIn("Augustine", result[0]["source"]["citation"])

    def test_peirce_and_saussure_contrast_is_explicit_and_sourced(self):
        result = self.registry.query("sign", {"framework:peirce"})
        relations = result[0]["relations"]
        self.assertEqual(relations[0]["id"], "peirce-saussure-contrast")
        self.assertEqual(relations[0]["kind"], "contrasts_with")
        self.assertEqual(relations[0]["source_id"], "sep-peirce-2012")


if __name__ == "__main__":
    unittest.main()
