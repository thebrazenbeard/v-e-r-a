from pathlib import Path
import unittest


WORKFLOW = Path(".github/workflows/ops-spine.yml")
CHECKOUT_SHA = "3d3c42e5aac5ba805825da76410c181273ba90b1"  # actions/checkout v7.0.1
SETUP_PYTHON_SHA = "5fda3b95a4ea91299a34e894583c3862153e4b97"  # actions/setup-python v7.0.0


class WorkflowConfigTests(unittest.TestCase):
    def test_actions_are_pinned_to_current_node24_releases(self):
        content = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(f"actions/checkout@{CHECKOUT_SHA}", content)
        self.assertIn(f"actions/setup-python@{SETUP_PYTHON_SHA}", content)
        self.assertNotIn("actions/checkout@v4", content)
        self.assertNotIn("actions/setup-python@v5", content)

    def test_operating_contract_changes_trigger_validation(self):
        content = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('      - "prompts/**"', content)
        self.assertIn('      - "governance/**"', content)
        self.assertIn('      - "docs/AUTOMATION_SPINE.md"', content)
        self.assertIn('      - "docs/INFRASTRUCTURE_TRIGGERS.md"', content)
        self.assertIn('      - "docs/superpowers/specs/**"', content)

    def test_validator_checks_entire_event_store(self):
        content = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("run: python -m vera_works.validate_repo ops/events", content)
        self.assertNotIn("run: python -m vera_works.validate_repo ops/events/examples", content)


if __name__ == "__main__":
    unittest.main()
