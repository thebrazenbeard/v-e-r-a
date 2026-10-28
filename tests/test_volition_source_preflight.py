"""Pre-import Volition source custody regressions without a real Volition install."""

from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

from interface.goal_view import GoalViewError
from interface.verified_volition import (
    _runtime_fingerprint, fingerprint_installed_volition,
)


class VolitionSourcePreflightTests(unittest.TestCase):
    def _package(self, parent):
        package = parent / "volition"
        package.mkdir()
        (package / "__init__.py").write_text("from pathlib import Path\n"
            "Path(__file__).with_name('imported.marker').write_text('executed')\n",
            encoding="utf-8")
        (package / "operational_drive.py").write_text(
            "class OperationalMotivation:\n    @classmethod\n"
            "    def from_snapshot(cls, value):\n        return cls()\n",
            encoding="utf-8")
        (package / "engine.py").write_text("# inert test engine\n", encoding="utf-8")
        return package

    def test_wrong_digest_never_executes_package_initializer(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            package = self._package(root)
            script = (
                "import sys\n"
                f"sys.path.insert(0, {str(root)!r})\n"
                "from interface.verified_volition import _runtime_fingerprint\n"
                "from interface.goal_view import GoalViewError\n"
                "try:\n"
                "    _runtime_fingerprint('0' * 64)\n"
                "except GoalViewError as exc:\n"
                "    assert 'revision mismatch' in str(exc), str(exc)\n"
                "else:\n"
                "    raise AssertionError('mismatched pin accepted')\n"
            )
            run = subprocess.run([sys.executable, "-c", script],
                                 cwd=Path(__file__).resolve().parents[1],
                                 capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertFalse((package / "imported.marker").exists(),
                             "source-pin mismatch executed package initializer")

    def test_preloaded_wrong_origin_fails_before_import(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self._package(root)
            fake = types.ModuleType("volition.operational_drive")
            fake.__file__ = str(root / "spoofed.py")
            with patch.object(sys, "path", [str(root), *sys.path]):
                digest = fingerprint_installed_volition()
                with patch.dict(sys.modules, {"volition.operational_drive": fake}):
                    with self.assertRaisesRegex(GoalViewError, "preloaded Volition"):
                        _runtime_fingerprint(digest)
            self.assertFalse((root / "volition" / "imported.marker").exists())


if __name__ == "__main__":
    unittest.main()
