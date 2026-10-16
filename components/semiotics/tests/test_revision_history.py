import unittest

from semiotics import Registry, RegistryError


def revision_payload():
    return {
        "signs": [{"id": "s", "form": "x", "modality": "visual"}],
        "sources": [
            {
                "id": "src",
                "description": "example",
                "citation": "Example Author, Example Work",
                "published_year": 2026,
                "locator": "https://example.com/source",
            }
        ],
        "interpretations": [
            {
                "id": "old",
                "sign_id": "s",
                "meaning": "older reading",
                "source_id": "src",
            },
            {
                "id": "new",
                "sign_id": "s",
                "meaning": "current reading",
                "source_id": "src",
                "supersedes_id": "old",
            },
        ],
    }


class RevisionHistoryTests(unittest.TestCase):
    def test_query_hides_superseded_reading_by_default(self):
        registry = Registry.from_dict(revision_payload())
        result = registry.query("s")
        self.assertEqual(
            [item["interpretation"]["id"] for item in result],
            ["new"],
        )

    def test_query_can_include_superseded_history(self):
        registry = Registry.from_dict(revision_payload())
        result = registry.query("s", include_superseded=True)
        self.assertEqual(
            [item["interpretation"]["id"] for item in result],
            ["new", "old"],
        )

    def test_source_bibliography_round_trips_through_query(self):
        registry = Registry.from_dict(revision_payload())
        source = registry.query("s")[0]["source"]
        self.assertEqual(source["citation"], "Example Author, Example Work")
        self.assertEqual(source["published_year"], 2026)

    def test_dangling_supersedes_reference_fails(self):
        payload = revision_payload()
        payload["interpretations"][1]["supersedes_id"] = "missing"
        with self.assertRaisesRegex(RegistryError, "unknown interpretation"):
            Registry.from_dict(payload)

    def test_cross_sign_supersedes_reference_fails(self):
        payload = revision_payload()
        payload["signs"].append({"id": "other", "form": "y", "modality": "visual"})
        payload["interpretations"][1]["sign_id"] = "other"
        with self.assertRaisesRegex(RegistryError, "same sign"):
            Registry.from_dict(payload)

    def test_revision_cycle_fails(self):
        payload = revision_payload()
        payload["interpretations"][0]["supersedes_id"] = "new"
        with self.assertRaisesRegex(RegistryError, "cycle"):
            Registry.from_dict(payload)

    def test_published_year_rejects_boolean(self):
        payload = revision_payload()
        payload["sources"][0]["published_year"] = True
        with self.assertRaisesRegex(RegistryError, "published_year"):
            Registry.from_dict(payload)


if __name__ == "__main__":
    unittest.main()
