"""Real three-repository regression for V-E-R-A PR #1's advisory-only CLI.

Requires exact separate Vera Mono and PORTAL source checkouts.
Without VERA_MONO_SOURCE_ROOT and PORTAL_SOURCE_ROOT this suite SKIPs,
never silently qualifies the runtime using fake components.

No device routing, protected actions, model inference, or network side effects.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "integration" / "vera_portal_runtime.py"
PACKET = ROOT / "integration" / "example_readonly_task_packet.json"
MONO = os.environ.get("VERA_MONO_SOURCE_ROOT")
PORTAL = os.environ.get("PORTAL_SOURCE_ROOT")


def call(arguments: list[str]) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, "-B", str(RUNNER), *arguments],
        cwd=ROOT, text=True, capture_output=True, timeout=40,
        env={**os.environ, "PYTHONDONTWRITEBYTE": "1"},
    )
    raw = proc.stdout if proc.returncode == 0 else proc.stderr
    return proc.returncode, json.loads(raw)


@unittest.skipUnless(MONO and PORTAL, "Requires exact separate Vera Mono and PORTAL checkouts")
class ActualSourceAdvisoryIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="vera-three-repo-")
        self.addCleanup(self.tmp.cleanup)
        self.state = Path(self.tmp.name)
        self.task = "task-real-source-1"
        self.ledger = self.state / "tasks.sqlite"
        self.base = [
            "--vera-mono", str(MONO), "--portal", str(PORTAL),
            "--ledger", str(self.ledger),
        ]

    def cli(self, command: str, *args: str) -> tuple[int, dict]:
        return call([*self.base, command, *args])

    def open(self) -> tuple[int, dict]:
        return self.cli("open", "--task", self.task, "--packet", str(PACKET),
                        "--lifecycle-digest", "a" * 64)

    def route(self, receipt: str, advertisements: Path | None = None) -> tuple[int, dict]:
        cmd = [
            "--task", self.task, "--node", "lappy",
            "--target-kind", "repository", "--target", "thebrazenbeard/portal",
            "--capability", "repository_read", "--receipt", str(self.state / receipt),
        ]
        if advertisements:
            cmd += ["--advertisements", str(advertisements)]
        return self.cli("route", *cmd)

    def advertisement(self, current: bool = True) -> Path:
        path = self.state / "advertisements.json"
        route = {
            "adapter_id": "github", "route_id": "test-read",
            "node_id": "lappy", "target_kind": "repository",
            "target_id": "thebrazenbeard/portal",
            "capabilities": ["repository_read"],
            "effect_capabilities": ["NO_PROTECTED_EFFECT"],
            "authorized_effects": ["NO_PROTECTED_EFFECT"],
            "available": True, "attached": True, "current": current,
        }
        path.write_text(json.dumps([route]), encoding="utf-8")
        return path

    def verify(self, path: str) -> tuple[int, dict]:
        return self.cli("verify", "--task", self.task,
                        "--receipt", str(self.state / path))

    def test_real_sqlite_held_proposed_and_new_process_revalidation(self) -> None:
        status, opened = self.open()
        self.assertEqual(status, 0, opened)
        self.assertEqual(opened["status"], "TASK_OPENED")
        self.assertFalse(opened["effect_authority"])
        status, held = self.route("held.json")
        self.assertEqual(status, 0, held)
        self.assertEqual(held["status"], "HELD")
        self.assertIsNone(held["route"])
        status, replay_held = self.verify("held.json")
        self.assertEqual(status, 0, replay_held)
        self.assertEqual(replay_held["proposal_state"], "HELD")
        status, proposed = self.route("proposed.json", self.advertisement())
        self.assertEqual(status, 0, proposed)
        self.assertEqual(proposed["status"], "ROUTE_PROPOSED")
        self.assertFalse(proposed["executed"])
        self.assertFalse(proposed["effect_authority"])
        self.assertEqual(proposed["advertisement_currentness"], "CALLER_SUPPLIED_UNATTESTED")
        status, replay_proposed = self.verify("proposed.json")
        self.assertEqual(status, 0, replay_proposed)
        self.assertEqual(replay_proposed["proposal_state"], "ROUTE_PROPOSED")
        self.assertEqual(replay_proposed["route"]["route_id"], "test-read")
        # We have only opened one task. No execution receipt or closeout is produced.
        self.assertTrue(self.ledger.is_file())

    def test_tampering_and_journal_advance_invalidate_old_receipts(self) -> None:
        status, opened = self.open()
        self.assertEqual(status, 0, opened)
        self.assertEqual(self.route("held.json")[0], 0)
        self.assertEqual(self.route("proposed.json", self.advertisement())[0], 0)
        forged = json.loads((self.state / "proposed.json").read_text(encoding="utf-8"))
        forged["assessment"]["route"]["route_id"] = "forged"
        (self.state / "forged.json").write_text(json.dumps(forged), encoding="utf-8")
        status, denied = self.verify("forged.json")
        self.assertEqual(status, 2, denied)
        self.assertIn("digest mismatch", denied["reason"])
        # Invoke Vera Mono's real task ledger in a separate Python process.
        script = (
            "import sys; from pathlib import Path; "
            "sys.path[:0]=[str(p) for p in Path(sys.argv[1]).glob('packages/*/src')]; "
            "from vera_core.task_execution import TaskExecutionLedger; "
            "l=TaskExecutionLedger(Path(sys.argv[2])); "
            "l.bind_dependency('task-real-source-1','dep:integration-test',"
            "kind='COORDINATION_COMMAND',target_id='command:changed')"
        )
        proc = subprocess.run(
            [sys.executable, "-B", "-c", script, str(MONO), str(self.ledger)],
            capture_output=True, text=True, timeout=40,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        for prior in ("held.json", "proposed.json"):
            status, denied = self.verify(prior)
            self.assertEqual(status, 2, denied)
            self.assertIn("stale task", denied["reason"])

    def test_duplicate_open_and_receipt_overwrite_fail_closed(self) -> None:
        self.assertEqual(self.open()[0], 0)
        status, denied = self.open()
        self.assertEqual(status, 2, denied)
        self.assertIn("already exists", denied["reason"])
        self.assertEqual(self.route("held.json")[0], 0)
        status, denied = self.route("held.json")
        self.assertEqual(status, 2, denied)
        self.assertIn("receipt destination exists or has no parent", denied["reason"])

    def test_preloaded_shadow_modules_fail_closed_with_real_source_checkouts(self) -> None:
        # Separate clean Python processes: attacker loads a module object into
        # sys.modules BEFORE pinned-source components() gets to import its code.
        for shadow in ("vera_core", "vera_core.task_execution",
                       "portfolio_runtime", "portal.route_resolver"):
            with self.subTest(shadow=shadow):
                script = (
                    "import sys,types; from pathlib import Path; "
                    "from integration import vera_portal_runtime as r; "
                    "fake=types.ModuleType(sys.argv[3]); "
                    "fake.__file__=str(Path(sys.argv[1])/'impostor.py'); "
                    "sys.modules[sys.argv[3]]=fake; "
                    "r.components(Path(sys.argv[1]),Path(sys.argv[2]))"
                )
                proc = subprocess.run(
                    [sys.executable, "-B", "-c", script,
                     str(MONO), str(PORTAL), shadow],
                    cwd=ROOT, text=True, capture_output=True, timeout=40,
                    env={**os.environ, "PYTHONDONTWRITEBYTE": "1"},
                )
                self.assertNotEqual(proc.returncode, 0, shadow)
                self.assertIn("preloaded", proc.stderr, proc.stderr)

    def test_concurrent_open_does_not_create_two_open_events(self) -> None:
        args = [*self.base, "open", "--task", self.task, "--packet", str(PACKET),
                "--lifecycle-digest", "a" * 64]
        processes = [
            subprocess.Popen(
                [sys.executable, "-B", str(RUNNER), *args],
                cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, env={**os.environ, "PYTHONDONTWRITEBYTE": "1"},
            ) for _ in range(2)
        ]
        for process in processes:
            out, err = process.communicate(timeout=40)
            self.assertIn(process.returncode, (0, 2), (out, err))
        # One task must be readable and its event history must have one open.
        script = (
            "import sys,json; from pathlib import Path; "
            "sys.path[:0]=[str(p) for p in Path(sys.argv[1]).glob('packages/*/src')]; "
            "from vera_core.task_execution import TaskExecutionLedger; "
            "l=TaskExecutionLedger(Path(sys.argv[2])); "
            "events=l.events('task-real-source-1'); "
            "print(json.dumps({'open_events':sum(e.event_type=='TASK_OPENED' for e in events),"
            "'total_events':len(events)}))"
        )
        query = subprocess.run([sys.executable, "-B", "-c", script, str(MONO),
                                str(self.ledger)],
                               capture_output=True, text=True, timeout=40)
        self.assertEqual(query.returncode, 0, query.stderr)
        record = json.loads(query.stdout)
        self.assertEqual(record["open_events"], 1, record)
        self.assertEqual(record["total_events"], 1, record)


if __name__ == "__main__":
    unittest.main()
