from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_SUBJECT = "1531eb23cb9c326e9f056a5ce6402fe10a366cf6"


class LocalValidationMigrationTests(unittest.TestCase):
    def test_paid_hosted_workflow_is_removed(self):
        self.assertFalse((ROOT / ".github/workflows/r10a1-validation.yml").exists())

    def test_repo_local_validator_exists_with_required_contract(self):
        script = ROOT / "tools/validate_r10a1.py"
        self.assertTrue(script.is_file())
        text = script.read_text(encoding="utf-8")
        for required in [
            "2d60cd8e87ac0aae89a5a9bd9a44bfb63f48aa64",
            RECEIPT_SUBJECT,
            "VERA_R10A1_SALIENCE_REGRESSION.md",
            "VERA_R10A1_PUBLICATION_RECEIPT.json",
            "R10A1 static/source validation PASS",
            "project-instructions/r10a0/",
        ]:
            self.assertIn(required, text)

    def test_validator_executes_from_descendant_checkout_against_frozen_subject(self):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "tools/validate_r10a1.py")],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(
            proc.returncode,
            0,
            msg=f"validator failed from descendant checkout\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}",
        )
        self.assertIn(f"subject={RECEIPT_SUBJECT}", proc.stdout)

    def test_local_runbook_is_explicit(self):
        doc = ROOT / "docs/R10A1_LOCAL_VALIDATION.md"
        self.assertTrue(doc.is_file())
        text = doc.read_text(encoding="utf-8")
        self.assertIn("python tools/validate_r10a1.py", text)
        self.assertIn("does not require GitHub Actions", text)
        self.assertIn(RECEIPT_SUBJECT, text)
        self.assertIn("descendant checkout", text.lower())


if __name__ == "__main__":
    unittest.main()


class FrozenManifestSchemaRegressionTests(unittest.TestCase):
    def test_validator_uses_actual_nested_freeze_manifest_binding(self):
        script = (ROOT / "tools/validate_r10a1.py").read_text(encoding="utf-8")
        self.assertNotIn('freeze["source_manifest_sha256"]', script)
        self.assertIn('freeze.get("source_manifest")', script)
        self.assertIn('freeze_manifest.get("sha256") == manifest_sha', script)
        self.assertIn('freeze_manifest.get("git_blob") == actual["manifest"]', script)
