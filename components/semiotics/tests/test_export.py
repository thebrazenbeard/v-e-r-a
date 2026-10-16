import json
import tempfile
import unittest
from pathlib import Path

from semiotics import Registry, dump_registry


def export_payload():
    return {
        "signs": [
            {"id": "z", "form": "z", "modality": "visual"},
            {"id": "a", "form": "a", "modality": "visual"},
        ],
        "sources": [
            {
                "id": "src",
                "description": "example",
                "citation": "Example Citation",
                "published_year": 2026,
            }
        ],
        "interpretations": [
            {
                "id": "old",
                "sign_id": "a",
                "meaning": "old",
                "source_id": "src",
            },
            {
                "id": "new",
                "sign_id": "a",
                "meaning": "new",
                "source_id": "src",
                "supersedes_id": "old",
                "required_tags": ["x"],
            },
        ],
        "relations": [
            {
                "id": "revision-contrast",
                "left_id": "old",
                "right_id": "new",
                "kind": "contrasts_with",
                "source_id": "src",
            }
        ],
    }


class ExportTests(unittest.TestCase):
    def test_to_dict_preserves_revision_relation_and_bibliography(self):
        registry = Registry.from_dict(export_payload())
        exported = registry.to_dict()
        self.assertEqual(exported["sources"][0]["citation"], "Example Citation")
        interpretations = {item["id"]: item for item in exported["interpretations"]}
        self.assertEqual(interpretations["new"]["supersedes_id"], "old")
        self.assertEqual(exported["relations"][0]["id"], "revision-contrast")

    def test_to_dict_is_deterministically_sorted_by_id(self):
        registry = Registry.from_dict(export_payload())
        exported = registry.to_dict()
        self.assertEqual([item["id"] for item in exported["signs"]], ["a", "z"])
        self.assertEqual(
            [item["id"] for item in exported["interpretations"]],
            ["new", "old"],
        )

    def test_dump_registry_round_trips_through_loader(self):
        registry = Registry.from_dict(export_payload())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "registry.json"
            dump_registry(registry, path)
            written = json.loads(path.read_text(encoding="utf-8"))
            loaded = Registry.from_dict(written)
        self.assertEqual(loaded.to_dict(), registry.to_dict())

    def test_empty_relations_are_omitted_for_backward_compatible_shape(self):
        payload = export_payload()
        payload.pop("relations")
        registry = Registry.from_dict(payload)
        self.assertNotIn("relations", registry.to_dict())


if __name__ == "__main__":
    unittest.main()
