"""Regression checks for the pinned Volition suite entrypoint."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import contextlib
import io
import os
import sys

from scripts import run_pinned_volition_tests as runner


class PinnedVolitionRunnerTests(TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.volition = Path(self.temp.name)
        package = self.volition / "src" / "volition"
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("", encoding="utf-8")

    def invoke(self):
        with patch.object(sys, "argv", ["runner.py", "--volition-root", str(self.volition)]):
            return runner.main()

    def test_exact_clean_pin_invokes_full_suite_with_isolated_path(self):
        with patch.object(runner.subprocess, "check_output", side_effect=[runner.PIN, ""]) as git, \
             patch.object(runner.subprocess, "call", return_value=0) as call:
            self.assertEqual(self.invoke(), 0)
        self.assertEqual(git.call_count, 2)
        args, kw = call.call_args
        self.assertEqual(args[0], [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"])
        self.assertEqual(kw["cwd"], runner.ROOT)
        self.assertEqual(
            kw["env"]["PYTHONPATH"],
            os.pathsep.join([str(runner.ROOT), str(self.volition / "src")]),
        )

    def test_mismatched_revision_is_rejected_before_running_tests(self):
        with patch.object(runner.subprocess, "check_output", return_value="wrong-revision"), \
             patch.object(runner.subprocess, "call") as call, \
             contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as exc:
                self.invoke()
        self.assertEqual(exc.exception.code, 2)
        call.assert_not_called()

    def test_dirty_pinned_checkout_is_rejected_before_running_tests(self):
        with patch.object(runner.subprocess, "check_output", side_effect=[runner.PIN, "?? untracked"]), \
             patch.object(runner.subprocess, "call") as call, \
             contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as exc:
                self.invoke()
        self.assertEqual(exc.exception.code, 2)
        call.assert_not_called()

    def test_missing_source_is_rejected_without_invoking_git_or_tests(self):
        (self.volition / "src" / "volition" / "__init__.py").unlink()
        with patch.object(runner.subprocess, "check_output") as git, \
             patch.object(runner.subprocess, "call") as call, \
             contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as exc:
                self.invoke()
        self.assertEqual(exc.exception.code, 2)
        git.assert_not_called()
        call.assert_not_called()
