"""Real JS UI -> loopback gateway -> bridge -> synthetic model contract.

This tests message transport, provenance and recovery, *not* model cognition,
physical GGUF inference, trained adaptation or browser rendering fidelity.
"""

from __future__ import annotations

import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from threading import Thread
import unittest
from unittest.mock import patch

from interface import persona_profile, server as server_module
from interface.loopback_model_bridge import LoopbackModelBridge, create_server
from interface.server import make_server
from tests.test_persona_profile import _synthetic_profile


MODEL_ID = "synthetic-nonvera-dialogue-double"
HARNESS = Path(__file__).with_name("browser_chat_harness.cjs")


class ScriptedModel(BaseHTTPRequestHandler):
    requests = []
    mode = "stop"

    def log_message(self, *_args):
        pass

    def _json(self, body):
        raw = json.dumps(body).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path == "/health":
            self._json({"status": "ok"})
        elif self.path == "/v1/models":
            self._json({"data": [{"id": MODEL_ID}]})
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path != "/v1/chat/completions":
            self.send_error(404)
            return
        request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        type(self).requests.append(request)
        last = request["messages"][-1]["content"]
        if "I prefer" in last:
            text = "Iris noted."
        elif "Correction:" in last:
            text = "Correction noted: Nova."
        elif "What name" in last:
            # Deliberate script: context transport only, not model learning.
            found = any("Correction: call me Nova." == message["content"]
                        for message in request["messages"])
            text = "Nova." if found else "UNKNOWN"
        else:
            text = "Synthetic reply only."
        self._json({"model": MODEL_ID, "choices": [{"message": {
            "role": "assistant", "content": text}, "finish_reason": type(self).mode}]})


@unittest.skipUnless(shutil.which("node"), "Node.js required to execute actual app.js DOM double")
class BrowserMultiTurnIntegrationTests(unittest.TestCase):
    def setUp(self):
        ScriptedModel.mode = "stop"
        ScriptedModel.requests = []
        self.services = []
        self.upstream = self._run(ThreadingHTTPServer(("127.0.0.1", 0), ScriptedModel))
        self.base_upstream = f"http://127.0.0.1:{self.upstream.server_port}"

    def tearDown(self):
        for server, thread in reversed(self.services):
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def _run(self, server):
        server.daemon_threads = True
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.services.append((server, thread))
        return server

    def _start(self, *, token_limit=64):
        bridge = self._run(create_server(LoopbackModelBridge(
            self.base_upstream, MODEL_ID, timeout=2, max_chat_tokens=token_limit), port=0))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "synthetic.json"
            raw = json.dumps(_synthetic_profile(), sort_keys=True).encode()
            path.write_bytes(raw)
            presentation = Path(folder) / "synthetic-test-only.md"
            presentation.write_text("TEST-ONLY source substitute", encoding="utf-8")
            with patch.object(persona_profile, "SOURCE_SHA256", hashlib.sha256(raw).hexdigest()), \
                 patch.object(server_module, "verify_presentation_file"):
                gateway = make_server(port=0,
                    ollama_url=f"http://127.0.0.1:{bridge.server_port}",
                    persona_profile_path=path, require_persona=True,
                    persona_presentation_path=presentation,
                    max_response_tokens=token_limit)
        return self._run(gateway)

    def _browser(self, gateway, mode):
        base = f"http://127.0.0.1:{gateway.server_port}"
        proc = subprocess.run([shutil.which("node"), str(HARNESS), base, mode],
                              cwd=Path(__file__).resolve().parent.parent,
                              capture_output=True, text=True, timeout=15, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
        return json.loads(proc.stdout)

    def test_three_ui_turns_preserve_correction_and_pinned_prompt_without_attestation(self):
        result = self._browser(self._start(token_limit=96), "three_turns")
        self.assertEqual([m["role"] for m in result["messages"]],
                         ["user", "assistant", "user", "assistant", "user", "assistant"])
        self.assertEqual(result["messages"][-1]["content"], "Nova.")
        self.assertEqual(result["messages"][2]["content"], "Correction: call me Nova.")
        self.assertTrue(all(b["roleLabel"] in ("YOU", "MODEL OUTPUT / UNVERIFIED")
                            for b in result["bubbles"]))
        self.assertIn("UNVERIFIED", result["connection"])
        self.assertIn("weights not attested", result["modelDetail"])
        self.assertEqual(result["status"]["persona_prompt"], "pinned_owner_profile")
        self.assertIs(result["status"]["model_identity_attested"], False)
        self.assertEqual(result["status"]["durable_memory"], "not_connected")
        self.assertIn("No chat is saved", result["vaultStatus"])
        self.assertEqual(len(ScriptedModel.requests), 3)
        for n, request in enumerate(ScriptedModel.requests):
            self.assertEqual(request["max_tokens"], 96)
            self.assertEqual([m["role"] for m in request["messages"]],
                             ["system", *(["user", "assistant"] * n), "user"])
            self.assertEqual(sum(m["role"] == "system" for m in request["messages"]), 1)
            self.assertIn("Dry and observational", request["messages"][0]["content"])
            self.assertIn("not authentication", request["messages"][0]["content"])
            self.assertNotIn("tools", request)
            self.assertNotIn("vault", json.dumps(request).lower())

    def test_truncated_reply_is_visible_but_not_committed_as_completed_assistant(self):
        ScriptedModel.mode = "length"
        result = self._browser(self._start(), "truncated")
        self.assertEqual(result["messages"], [{
            "role": "user", "content": "Tell me what to do about the correction."}])
        self.assertEqual(result["promptRecovered"], "")
        self.assertEqual([b["roleLabel"] for b in result["bubbles"]],
                         ["YOU", "LOCAL MODEL / UNVERIFIED PARTIAL"])
        self.assertIn("cut off", result["bubbles"][-1]["content"].lower())
        self.assertEqual(ScriptedModel.requests[0]["max_tokens"], 64)

    def test_busy_gateway_returns_429_without_assistant_turn_or_upstream_call(self):
        gateway = self._start()
        self.assertTrue(gateway.model_slots.acquire(blocking=False))
        try:
            result = self._browser(gateway, "busy")
        finally:
            gateway.model_slots.release()
        self.assertEqual(result["messages"], [])
        self.assertEqual(result["promptRecovered"], "Briefly acknowledge me.")
        self.assertEqual([b["roleLabel"] for b in result["bubbles"]],
                         ["YOU", "INTERFACE / ERROR"])
        self.assertIn("worker busy", result["bubbles"][-1]["content"])
        self.assertEqual(ScriptedModel.requests, [])


if __name__ == "__main__":
    unittest.main()
