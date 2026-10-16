"""Source-only policy and provenance tests; no imported component execution."""
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

PROJECT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJECT/"scripts"))
import verify_safe_components as v


class SafeComponentExportTests(unittest.TestCase):
    def test_workspace_hooks_are_omitted(self):
        for p in ("repo/.vscode/tasks.json", "repo/.vscode/launch.json",
                  "root/.devcontainer/devcontainer.json", "root/.idea/misc.xml",
                  "test/.husky/pre-commit"):
            self.assertEqual(v.omission_reason(p), "ACTIVE_WORKSPACE_CONFIGURATION")

    def test_ci_workflows_are_omitted(self):
        self.assertEqual(v.omission_reason(".github/workflows/release.yml"),
                         "CI_WORKFLOW_CONFIGURATION")
        self.assertEqual(v.omission_reason("Jenkinsfile"), "AUTOMATIC_EXECUTION_CONFIGURATION")
        self.assertEqual(v.omission_reason("foo.code-workspace"),
                         "AUTOMATIC_EXECUTION_CONFIGURATION")

    def test_unreviewed_font_binary_omitted(self):
        for p in ("public/fonts/brand.woff2", "x/FONT.WOFF", "y/font.TTF", "icon.otf"):
            self.assertEqual(v.omission_reason(p), "UNREVIEWED_EMBEDDED_FONT_BINARY")

    def test_symlink_and_gitlink_omitted(self):
        self.assertEqual(v.omission_reason("README.md", "120000"), "SYMLINK_UNQUALIFIED")
        self.assertEqual(v.omission_reason("submodule", "160000"), "GITLINK_UNQUALIFIED")

    def test_ordinary_source_is_not_claimed_safe(self):
        for p in ("src/main.py","README.md","infra/review.yaml", "program.go"):
            self.assertIsNone(v.omission_reason(p))

    def test_windows_separators_cannot_bypass_policy(self):
        self.assertEqual(v.omission_reason("root\\.vscode\\tasks.json"),
                         "ACTIVE_WORKSPACE_CONFIGURATION")

    def test_exact_source_tree_integrity_with_external_commit(self):
        commit=os.environ.get("VERA_SAFE_EXPORT_TEST_COMMIT")
        repo=os.environ.get("VERA_SAFE_EXPORT_TEST_REPO")
        if not commit or not repo:
            self.skipTest("On-demand exact source commit/root not supplied")
        result=v.inspect(Path(repo),commit,verify_source_objects=True)
        self.assertTrue(result["source_blob_identity_verified"])
        self.assertEqual(result["components"],44)
        self.assertTrue(result["explicit_omissions"]>0)
        self.assertFalse(result["malware_free_proven"])
        self.assertFalse(result["veraos_installed"])

    def test_changed_manifest_tree_must_fail_closed(self):
        commit=os.environ.get("VERA_SAFE_EXPORT_TEST_COMMIT")
        repo=os.environ.get("VERA_SAFE_EXPORT_TEST_REPO")
        if not commit or not repo:self.skipTest("On-demand exact source commit/root not supplied")
        original=v.git
        def corrupted(repo_path,*args):
            value=original(repo_path,*args)
            if args==("show",commit+":component-exports.json"):
                p=json.loads(value)
                p["components"][0]["export_tree"]="0"*40
                return json.dumps(p)
            return value
        with patch.object(v,"git",side_effect=corrupted):
            with self.assertRaisesRegex(ValueError,"tracked component tree mismatch"):
                v.inspect(Path(repo),commit)

    def test_corrupted_omitted_blob_provenance_rejected(self):
        commit=os.environ.get("VERA_SAFE_EXPORT_TEST_COMMIT")
        repo=os.environ.get("VERA_SAFE_EXPORT_TEST_REPO")
        if not commit or not repo:self.skipTest("On-demand original source objects unavailable")
        original=v.git
        def forged(repo_path,*args):
            value=original(repo_path,*args)
            if args==("show",commit+":component-exports.json"):
                doc=json.loads(value)
                item=next(r for r in doc["components"] if r["omitted_paths"])
                item["omitted_paths"][0]["blob_oid"]="0"*40
                return json.dumps(doc)
            return value
        with patch.object(v,"git",side_effect=forged):
            with self.assertRaisesRegex(ValueError,"source blob/omission provenance mismatch"):
                v.inspect(Path(repo),commit,verify_source_objects=True)

if __name__ == "__main__":
    unittest.main()
