"""Actual process-exit and file readback qualification for bounded plurality CLI."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = Path(__file__).parent / "fixtures" / "mosaic_plurality_v1.json"


def call(*args):
    return subprocess.run(
        [sys.executable, "-B", "-m", "integration.plural_cognition_cli", *args],
        cwd=ROOT, text=True, capture_output=True, timeout=15,
    )


class PluralityCliTests(unittest.TestCase):
    def test_real_process_persisted_projection_and_revalidation(self):
        source = json.loads(FIXTURE.read_text())
        with tempfile.TemporaryDirectory() as t:
            folder = Path(t)
            receipt = folder / "receipt.json"
            declarations = folder / "participants.json"
            output = folder / "projection.json"
            receipt.write_text(json.dumps(source["receipt"]))
            declarations.write_text(json.dumps(source["participants"]))
            inputs = ("compose", "--receipt", str(receipt), "--participants",
                      str(declarations), "--output", str(output))
            started = call(*inputs)
            self.assertEqual(started.returncode, 0, started.stderr)
            result = json.loads(started.stdout)
            self.assertEqual(result["alignment"], "DISSENT_RETAINED")
            self.assertFalse(result["effects_executed"])
            self.assertTrue(output.is_file())
            verified = call("verify", "--projection", str(output))
            self.assertEqual(verified.returncode, 0, verified.stderr)
            self.assertEqual(json.loads(verified.stdout)["status"],
                             "PROJECTION_READBACK_VALID")
            replay = call(*inputs)
            self.assertEqual(replay.returncode, 2)
            self.assertEqual(json.loads(replay.stderr)["status"], "HELD")
            record = json.loads(output.read_text())
            record["contributions"][1]["position"]["rationale"] = "silent"
            output.write_text(json.dumps(record))
            corrupted = call("verify", "--projection", str(output))
            self.assertEqual(corrupted.returncode, 2)
            self.assertEqual(json.loads(corrupted.stderr)["status"], "HELD")

    def test_undeclared_participant_rejected_without_output(self):
        source = json.loads(FIXTURE.read_text())
        with tempfile.TemporaryDirectory() as t:
            folder=Path(t)
            receipt=folder/"receipt.json"
            names=folder/"participants.json"
            result_file=folder/"projection.json"
            receipt.write_text(json.dumps(source["receipt"]))
            names.write_text(json.dumps({"core": source["participants"]["core"]}))
            result=call("compose", "--receipt", str(receipt), "--participants",
                        str(names), "--output", str(result_file))
            self.assertEqual(result.returncode, 2)
            self.assertFalse(result_file.exists())


if __name__=="__main__":
    unittest.main()
