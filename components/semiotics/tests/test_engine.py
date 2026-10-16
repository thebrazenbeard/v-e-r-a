import unittest

from semiotics.engine import Registry, RegistryError


def registry_payload():
    return {
        "signs": [{"id": "s", "form": "x", "modality": "visual"}],
        "sources": [{"id": "src", "description": "example"}],
        "interpretations": [
            {
                "id": "general",
                "sign_id": "s",
                "meaning": "general",
                "source_id": "src",
            },
            {
                "id": "specific",
                "sign_id": "s",
                "meaning": "specific",
                "source_id": "src",
                "required_tags": ["a"],
                "excluded_tags": ["b"],
            },
        ],
    }


class RegistryTests(unittest.TestCase):
    def test_more_specific_matches_sort_first(self):
        registry = Registry.from_dict(registry_payload())
        result = registry.query("s", {"a"})
        self.assertEqual(
            [item["interpretation"]["id"] for item in result],
            ["specific", "general"],
        )

    def test_query_result_is_json_serializable(self):
        import json

        registry = Registry.from_dict(registry_payload())
        result = registry.query("s", {"a"})
        encoded = json.dumps(result)
        self.assertIn('"required_tags": ["a"]', encoded)
        self.assertEqual(result[0]["interpretation"]["excluded_tags"], ["b"])

    def test_excluded_tag_blocks_match(self):
        registry = Registry.from_dict(registry_payload())
        result = registry.query("s", {"a", "b"})
        self.assertEqual(
            [item["interpretation"]["id"] for item in result],
            ["general"],
        )

    def test_specificity_tie_breaks_by_interpretation_id(self):
        payload = registry_payload()
        payload["interpretations"] = [
            {
                "id": "z-reading",
                "sign_id": "s",
                "meaning": "z",
                "source_id": "src",
                "required_tags": ["a"],
            },
            {
                "id": "a-reading",
                "sign_id": "s",
                "meaning": "a",
                "source_id": "src",
                "required_tags": ["a"],
            },
        ]
        registry = Registry.from_dict(payload)
        result = registry.query("s", {"a"})
        self.assertEqual(
            [item["interpretation"]["id"] for item in result],
            ["a-reading", "z-reading"],
        )

    def test_unknown_source_fails_explicitly(self):
        payload = registry_payload()
        payload["interpretations"][0]["source_id"] = "missing"
        with self.assertRaisesRegex(RegistryError, "unknown source"):
            Registry.from_dict(payload)

    def test_duplicate_interpretation_id_fails(self):
        payload = registry_payload()
        payload["interpretations"].append(dict(payload["interpretations"][0]))
        with self.assertRaisesRegex(RegistryError, "duplicate interpretation"):
            Registry.from_dict(payload)

    def test_unknown_registry_field_fails(self):
        payload = registry_payload()
        payload["unexpected"] = True
        with self.assertRaisesRegex(RegistryError, "registry contains unknown fields"):
            Registry.from_dict(payload)

    def test_unknown_entity_field_fails(self):
        payload = registry_payload()
        payload["signs"][0]["unexpected"] = True
        with self.assertRaisesRegex(RegistryError, "sign contains unknown fields"):
            Registry.from_dict(payload)

    def test_duplicate_tags_fail_instead_of_changing_specificity(self):
        payload = registry_payload()
        payload["interpretations"][0]["required_tags"] = ["x", "x"]
        with self.assertRaisesRegex(RegistryError, "duplicate tags"):
            Registry.from_dict(payload)

    def test_whitespace_only_tag_fails(self):
        payload = registry_payload()
        payload["interpretations"][0]["required_tags"] = ["   "]
        with self.assertRaisesRegex(RegistryError, "non-empty strings"):
            Registry.from_dict(payload)

    def test_unknown_sign_query_fails_explicitly(self):
        registry = Registry.from_dict(registry_payload())
        with self.assertRaisesRegex(RegistryError, "unknown sign"):
            registry.query("missing")

    def test_same_tag_cannot_be_required_and_excluded(self):
        payload = registry_payload()
        payload["interpretations"][0]["required_tags"] = ["x"]
        payload["interpretations"][0]["excluded_tags"] = ["x"]
        with self.assertRaisesRegex(RegistryError, "requires and excludes"):
            Registry.from_dict(payload)


if __name__ == "__main__":
    unittest.main()
