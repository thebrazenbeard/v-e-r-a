from pathlib import Path
import unittest


INSTRUCTIONS = Path("prompts/PROJECT_INSTRUCTIONS.md")
MAX_PROJECT_INSTRUCTION_CHARACTERS = 8000


class ProjectInstructionsTests(unittest.TestCase):
    def test_project_instructions_fit_native_limit(self):
        content = INSTRUCTIONS.read_text(encoding="utf-8")
        self.assertLessEqual(len(content), MAX_PROJECT_INSTRUCTION_CHARACTERS)

    def test_core_authority_and_automation_invariants_are_present(self):
        content = INSTRUCTIONS.read_text(encoding="utf-8")
        required = (
            "Vera is the principal and default decision authority for Vera Works.",
            "Patrick is legal custodian and physical/financial proxy",
            "Automate execution. Escalate judgment.",
            "Silence is never approval.",
            "`Patrick must do it` must never mean `Patrick must remember it`.",
            "Never blindly retry a non-idempotent external effect.",
            "One active lease owns an assignment at a time.",
        )
        for invariant in required:
            with self.subTest(invariant=invariant):
                self.assertIn(invariant, content)


if __name__ == "__main__":
    unittest.main()
