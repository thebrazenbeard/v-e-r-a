import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from semiotics import load_registry


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schema/registry.schema.json").read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA)


class SchemaTests(unittest.TestCase):
    def test_published_schema_is_valid_draft_2020_12(self):
        Draft202012Validator.check_schema(SCHEMA)

    def test_shipped_registries_validate(self):
        for relative in ["examples/registry.json", "corpus/foundations.json"]:
            with self.subTest(relative=relative):
                payload = json.loads((ROOT / relative).read_text(encoding="utf-8"))
                VALIDATOR.validate(payload)

    def test_schema_rejects_unknown_fields(self):
        payload = json.loads((ROOT / "examples/registry.json").read_text(encoding="utf-8"))
        payload["signs"][0]["unexpected"] = True
        with self.assertRaises(ValidationError):
            VALIDATOR.validate(payload)

    def test_schema_rejects_whitespace_only_text(self):
        payload = json.loads((ROOT / "examples/registry.json").read_text(encoding="utf-8"))
        payload["signs"][0]["form"] = "   "
        with self.assertRaises(ValidationError):
            VALIDATOR.validate(payload)

    def test_schema_rejects_duplicate_tags(self):
        payload = json.loads((ROOT / "examples/registry.json").read_text(encoding="utf-8"))
        payload["interpretations"][0]["required_tags"] = ["studio", "studio"]
        with self.assertRaises(ValidationError):
            VALIDATOR.validate(payload)


    def test_canonical_export_validates_against_published_schema(self):
        registry = load_registry(ROOT / "corpus/foundations.json")
        VALIDATOR.validate(registry.to_dict())


if __name__ == "__main__":
    unittest.main()
