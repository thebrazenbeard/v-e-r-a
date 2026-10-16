"""Safeguard that historical source inventory does not silently promote old evidence."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class SourceIndexTests(unittest.TestCase):
    def test_all_seed_items_are_non_authoritative(self):
        raw=json.loads((ROOT/"history"/"source_index.json").read_text(encoding="utf-8"))
        self.assertEqual("redworm.source_index.v1",raw["schema"])
        self.assertEqual("CANDIDATE_HISTORY_NOT_INGESTED",raw["status"])
        self.assertGreaterEqual(len(raw["items"]),4)
        for entry in raw["items"]:
            self.assertFalse(entry["current_authority"])
            self.assertEqual("NOT_ADMITTED",entry["admission"])
            self.assertIn(entry["memory_class"],("WORKING_PROJECT","HISTORICAL_AUDIT"))
            self.assertTrue(entry["source_locator"])
            self.assertTrue(entry["verification"])
        self.assertTrue(any(c["status"]=="MISSING" for c in raw["coverage"]))

if __name__=="__main__":
    unittest.main()
