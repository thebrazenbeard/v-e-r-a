import unittest

from semiotics import Registry, RegistryError


def relation_payload():
    return {
        "signs": [{"id": "s", "form": "sign", "modality": "conceptual-term"}],
        "sources": [{"id": "src", "description": "comparison source"}],
        "interpretations": [
            {
                "id": "a",
                "sign_id": "s",
                "meaning": "reading a",
                "source_id": "src",
                "required_tags": ["framework:a"],
            },
            {
                "id": "b",
                "sign_id": "s",
                "meaning": "reading b",
                "source_id": "src",
                "required_tags": ["framework:b"],
            },
        ],
        "relations": [
            {
                "id": "a-b-contrast",
                "left_id": "a",
                "right_id": "b",
                "kind": "contrasts_with",
                "source_id": "src",
            }
        ],
    }


class RelationTests(unittest.TestCase):
    def test_query_exposes_explicit_relations_without_affecting_matching(self):
        registry = Registry.from_dict(relation_payload())
        result = registry.query("s", {"framework:a"})
        self.assertEqual([item["interpretation"]["id"] for item in result], ["a"])
        self.assertEqual(result[0]["relations"][0]["id"], "a-b-contrast")
        self.assertEqual(result[0]["relations"][0]["kind"], "contrasts_with")

    def test_registry_without_relations_preserves_old_output_shape(self):
        payload = relation_payload()
        payload.pop("relations")
        registry = Registry.from_dict(payload)
        result = registry.query("s", {"framework:a"})
        self.assertNotIn("relations", result[0])

    def test_unknown_relation_endpoint_fails(self):
        payload = relation_payload()
        payload["relations"][0]["right_id"] = "missing"
        with self.assertRaisesRegex(RegistryError, "unknown interpretation"):
            Registry.from_dict(payload)

    def test_relation_self_edge_fails(self):
        payload = relation_payload()
        payload["relations"][0]["right_id"] = "a"
        with self.assertRaisesRegex(RegistryError, "distinct interpretations"):
            Registry.from_dict(payload)

    def test_unknown_relation_source_fails(self):
        payload = relation_payload()
        payload["relations"][0]["source_id"] = "missing"
        with self.assertRaisesRegex(RegistryError, "unknown source"):
            Registry.from_dict(payload)

    def test_unknown_relation_kind_fails(self):
        payload = relation_payload()
        payload["relations"][0]["kind"] = "wins_over"
        with self.assertRaisesRegex(RegistryError, "relation kind"):
            Registry.from_dict(payload)

    def test_duplicate_relation_id_fails(self):
        payload = relation_payload()
        payload["relations"].append(dict(payload["relations"][0]))
        with self.assertRaisesRegex(RegistryError, "duplicate relation"):
            Registry.from_dict(payload)


if __name__ == "__main__":
    unittest.main()
