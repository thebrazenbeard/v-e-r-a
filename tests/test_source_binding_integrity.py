"""Fail-closed import-source provenance tests for PR #1.

A matching Git HEAD with a clean tracked tree can still import attacker-created
untracked or ignored Python packages from the candidate import roots.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import types
from unittest.mock import patch
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from integration import vera_portal_runtime as runner


def git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args], text=True,
                       capture_output=True, timeout=15)
    if p.returncode:
        raise AssertionError(p.stderr)
    return p.stdout.strip()


class ImportSourceBindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="vera-source-bound-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        git(self.root, "init")
        git(self.root, "config", "user.name", "Vera Integration Test")
        git(self.root, "config", "user.email", "integration@example.test")
        original = self.root / "packages" / "vera_core" / "src" / "vera_core"
        original.mkdir(parents=True)
        (original / "__init__.py").write_text("ORIGINAL=True\n", encoding="utf-8")
        (self.root / ".gitignore").write_text("**/__pycache__/\n**/zz_hidden/\n", encoding="utf-8")
        git(self.root, "add", ".")
        git(self.root, "commit", "-m", "Reference tracked source")
        self.head = git(self.root, "rev-parse", "HEAD")

    def test_clean_reference_passes(self):
        runner.source_check(self.root, self.head, "Vera Mono")

    def test_untracked_python_package_cannot_shadow_pinned_code(self):
        path = self.root / "packages" / "zz_training_probe" / "src" / "vera_core"
        path.mkdir(parents=True)
        (path / "__init__.py").write_text(
            "raise RuntimeError('untracked source shadow imported')\n", encoding="utf-8"
        )
        self.assertEqual(git(self.root, "rev-parse", "HEAD"), self.head)
        self.assertEqual(git(self.root, "status", "--porcelain", "--untracked-files=no"), "")
        with self.assertRaisesRegex(RuntimeError, "untracked|ignored|import"):
            runner.source_check(self.root, self.head, "Vera Mono")

    def test_preloaded_foreign_python_package_rejected(self):
        fake = types.ModuleType("vera_core")
        fake.__file__ = str(self.root / "impostor.py")
        with patch.dict(sys.modules, {"vera_core": fake}):
            with self.assertRaisesRegex(RuntimeError, "preloaded"):
                runner._guard_preloaded_imports()

    def test_imported_module_origin_must_match_pinned_path(self):
        expected = self.root / "packages" / "vera_core" / "src" / "vera_core" / "__init__.py"
        fake = types.ModuleType("vera_core")
        fake.__file__ = str(self.root / "impostor.py")
        with self.assertRaisesRegex(RuntimeError, "origin"):
            runner._verify_module_origin(fake, expected)

    def test_gitignored_python_package_cannot_shadow_pinned_code(self):
        path = self.root / "packages" / "zz_hidden" / "src" / "vera_core"
        path.mkdir(parents=True)
        (path / "__init__.py").write_text("SHADOW=True\n", encoding="utf-8")
        self.assertEqual(git(self.root, "status", "--porcelain", "--untracked-files=no"), "")
        self.assertEqual(git(self.root, "status", "--porcelain", "--untracked-files=all"), "")
        with self.assertRaisesRegex(RuntimeError, "untracked|ignored|import"):
            runner.source_check(self.root, self.head, "Vera Mono")


if __name__ == "__main__":
    unittest.main()
