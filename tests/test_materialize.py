"""Offline integration tests using genuine Git commits and local bare remotes."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "materialize.py"
spec = importlib.util.spec_from_file_location("materialize", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def cmd(*args: str, cwd: Path | None = None) -> str:
    proc = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=15)
    if proc.returncode:
        raise RuntimeError(f"{args}: {proc.stderr}")
    return proc.stdout.strip()


class MirrorIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        home = Path(self.tmp.name)
        self.remote = home / "source.git"
        self.repo = home / "source"
        self.destination = home / "components"
        self.destination.mkdir()
        cmd("init", "--bare", "--initial-branch=main", str(self.remote))
        cmd("clone", str(self.remote), str(self.repo))
        cmd("config", "user.name", "Vera Test", cwd=self.repo)
        cmd("config", "user.email", "vera@example.test", cwd=self.repo)
        (self.repo / "README.md").write_text("main\n")
        cmd("add", "README.md", cwd=self.repo)
        cmd("commit", "-m", "Main", cwd=self.repo)
        cmd("push", "-u", "origin", "main", cwd=self.repo)
        cmd("checkout", "-b", "portal", cwd=self.repo)
        (self.repo / "portal.txt").write_text("pinned portal\n")
        cmd("add", "portal.txt", cwd=self.repo)
        cmd("commit", "-m", "Mirror", cwd=self.repo)
        self.pin = cmd("rev-parse", "HEAD", cwd=self.repo)
        cmd("push", "-u", "origin", "portal", cwd=self.repo)
        cmd("checkout", "main", cwd=self.repo)
        self.registry = {
            "schema": module.SCHEMA,
            "mirror_repository": "thebrazenbeard/v-e-r-a",
            "mirror_default_branch": "main",
            "components": [
                {"name": "portal", "upstream": "thebrazenbeard/portal", "upstream_branch": "main", "state": "MIRRORED", "mirror_commit": self.pin, "reason": None},
                {"name": "mediaphile", "upstream": "thebrazenbeard/mediaphile", "upstream_branch": "main", "state": "HELD", "mirror_commit": None, "reason": "private source"},
            ],
        }
        (self.repo / "components.json").write_text(json.dumps(self.registry))

    def test_real_worktree_materialization_and_verification(self):
        self.assertEqual(module.main(["list", "--root", str(self.repo)]), 0)
        self.assertEqual(module.main(["check-origin", "--root", str(self.repo), "--only", "portal"]), 0)
        args = ["--root", str(self.repo), "--destination", str(self.destination), "--only", "portal"]
        self.assertEqual(module.main(["materialize", *args]), 0)
        path = self.destination / "portal"
        self.assertEqual((path / "portal.txt").read_text(), "pinned portal\n")
        self.assertEqual(cmd("rev-parse", "HEAD", cwd=path), self.pin)
        self.assertEqual(module.main(["verify", *args]), 0)
        self.assertEqual(module.main(["materialize", *args]), 2)
        (path / "portal.txt").write_text("changed\n")
        self.assertEqual(module.main(["verify", *args]), 2)

    def test_default_ignored_component_folder_is_safe(self):
        (self.repo / ".gitignore").write_text("/components/\n")
        folder = self.repo / "components"
        folder.mkdir()
        self.assertEqual(module.main(["materialize", "--root", str(self.repo), "--only", "portal"]), 0)
        self.assertEqual(cmd("rev-parse", "HEAD", cwd=folder / "portal"), self.pin)
        self.assertEqual(module.main(["verify", "--root", str(self.repo), "--only", "portal"]), 0)

    def test_remote_ref_change_fails_without_checkout(self):
        cmd("checkout", "portal", cwd=self.repo)
        (self.repo / "portal.txt").write_text("newer\n")
        cmd("commit", "-am", "Changed", cwd=self.repo)
        cmd("push", "origin", "portal", cwd=self.repo)
        cmd("checkout", "main", cwd=self.repo)
        args = ["--root", str(self.repo), "--destination", str(self.destination), "--only", "portal"]
        self.assertEqual(module.main(["materialize", *args]), 2)
        self.assertFalse((self.destination / "portal").exists())

    def test_private_branch_and_forged_registry_rejected(self):
        with self.assertRaises(module.SnapshotError):
            module.select(module.read_registry(self.repo / "components.json"), ["mediaphile"])
        self.registry["components"][0]["upstream"] = "attacker/portal"
        (self.repo / "components.json").write_text(json.dumps(self.registry))
        with self.assertRaises(module.SnapshotError):
            module.read_registry(self.repo / "components.json")

    def test_duplicate_names_or_pins_rejected(self):
        self.registry["components"].append(dict(self.registry["components"][0]))
        (self.repo / "components.json").write_text(json.dumps(self.registry))
        with self.assertRaises(module.SnapshotError):
            module.read_registry(self.repo / "components.json")


if __name__ == "__main__":
    unittest.main()
