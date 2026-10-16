import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "semiotics.cli", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_example_studio_context(self):
        proc = self.run_cli("examples/registry.json", "red-light", "--tag", "studio")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload[0]["interpretation"]["meaning"], "Recording in progress")

    def test_road_context_returns_road_reading(self):
        proc = self.run_cli("examples/registry.json", "red-light", "--tag", "road")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload[0]["interpretation"]["meaning"], "Stop at the signal")

    def test_unknown_sign_is_structured_error(self):
        proc = self.run_cli("examples/registry.json", "missing")
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(proc.stdout, "")
        self.assertEqual(json.loads(proc.stderr)["error"], "unknown sign 'missing'")

    def test_no_context_yields_empty_for_example(self):
        proc = self.run_cli("examples/registry.json", "red-light")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), [])

    def test_include_superseded_returns_revision_history(self):
        payload = {
            "signs": [{"id": "s", "form": "x", "modality": "visual"}],
            "sources": [{"id": "src", "description": "example"}],
            "interpretations": [
                {"id": "old", "sign_id": "s", "meaning": "old", "source_id": "src"},
                {
                    "id": "new",
                    "sign_id": "s",
                    "meaning": "new",
                    "source_id": "src",
                    "supersedes_id": "old",
                },
            ],
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", encoding="utf-8", delete=False
        ) as handle:
            json.dump(payload, handle)
            registry_path = handle.name
        try:
            current = self.run_cli(registry_path, "s")
            history = self.run_cli(registry_path, "s", "--include-superseded")
        finally:
            Path(registry_path).unlink(missing_ok=True)

        self.assertEqual(current.returncode, 0, current.stderr)
        self.assertEqual(
            [item["interpretation"]["id"] for item in json.loads(current.stdout)],
            ["new"],
        )
        self.assertEqual(history.returncode, 0, history.stderr)
        self.assertEqual(
            [item["interpretation"]["id"] for item in json.loads(history.stdout)],
            ["new", "old"],
        )


if __name__ == "__main__":
    unittest.main()
