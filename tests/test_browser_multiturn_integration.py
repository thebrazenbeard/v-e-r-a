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
from urllib.request import Request, urlopen

from interface import persona_profile
from interface.loopback_model_bridge import LoopbackModelBridge, create_server
from interface.server import make_server
from tests.test_persona_profile import _synthetic_profile
from tests.windows_acl_fixture import private_test_temporary_directory


MODEL_ID = "synthetic-nonvera-dialogue-double"
VAULT_KEY = "synthetic-owner-vault-key-0123456789"
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

    def _start(self, *, token_limit=64, pinned_seed=True, with_vault=False):
        bridge = self._run(create_server(LoopbackModelBridge(
            self.base_upstream, MODEL_ID, timeout=2, max_chat_tokens=token_limit), port=0))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "synthetic.json"
            raw = json.dumps(_synthetic_profile(), sort_keys=True).encode()
            path.write_bytes(raw)
            with patch.object(persona_profile, "SOURCE_SHA256", hashlib.sha256(raw).hexdigest()), \
                 patch.dict(os.environ, {"VERA_MODEL_CHAT_MAX_TOKENS": str(token_limit)}):
                vault_options = {}
                if with_vault:
                    private_folder = Path(self.enterContext(private_test_temporary_directory()))
                    vault_options = {"memory_db_path": private_folder / "synthetic-vault.sqlite3",
                                     "memory_secret": VAULT_KEY}
                gateway = make_server(port=0,
                    ollama_url=f"http://127.0.0.1:{bridge.server_port}",
                    persona_profile_path=path if pinned_seed else None,
                    **vault_options)
        return self._run(gateway)

    def _seed_odd_vault(self, gateway):
        base = f"http://127.0.0.1:{gateway.server_port}"
        saved = [
            {"role": "user", "content": "Call me Iris."},
            {"role": "assistant", "content": "Iris noted."},
            {"role": "user", "content": "Correction: call me Nova."},
        ]
        req = Request(base + "/api/transcript", method="POST",
                      data=json.dumps({"messages": saved, "expected_revision": 0}).encode(),
                      headers={"Content-Type": "application/json", "Origin": base,
                               "X-Vera-Session": gateway.session_token,
                               "X-Vera-Vault-Key": VAULT_KEY})
        with urlopen(req, timeout=5) as response:
            self.assertEqual(response.status, 200)

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
        self.assertIn("provenance unverified", result["modelDetail"])
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

    def test_public_smoke_transport_at_64_96_128_with_and_without_prompt_seed(self):
        # These are protocol observations from the real app.js plus an explicit
        # scripted double, not baseline, seeded or R16 model-quality results.
        for cap in (64, 96, 128):
            for seeded in (False, True):
                with self.subTest(max_tokens=cap, seeded=seeded):
                    ScriptedModel.requests = []
                    result = self._browser(self._start(token_limit=cap,
                                                       pinned_seed=seeded), "three_turns")
                    self.assertEqual(result["messages"][-1]["content"], "Nova.")
                    self.assertIs(result["status"]["model_identity_attested"], False)
                    self.assertEqual(result["status"]["persona_prompt"],
                                     "pinned_owner_profile" if seeded else "not_connected")
                    self.assertEqual(len(ScriptedModel.requests), 3)
                    for request in ScriptedModel.requests:
                        self.assertEqual(request["max_tokens"], cap)
                        self.assertEqual(sum(m["role"] == "system"
                                             for m in request["messages"]), 1)
                        prompt_note = request["messages"][0]["content"]
                        self.assertEqual("Dry and observational" in prompt_note, seeded)
                        self.assertIn("no live observations", prompt_note)

    def test_seventh_and_eighth_turn_drop_complete_pairs_not_orphan_assistant(self):
        # Once 12 tab messages are exceeded, model context must still begin
        # with a real user instruction. An orphan assistant can violate local
        # template role alternation and confuse correction tracking.
        for mode, turns, first_history in (
                ("seven_turns", 7, "Correction: call me Nova."),
                ("eight_turns", 8, "What do you know about our context?")):
            with self.subTest(mode=mode):
                ScriptedModel.requests = []
                result = self._browser(self._start(), mode)
                self.assertEqual(result["messages"][-1]["content"], "Nova.")
                self.assertIs(result["status"]["model_identity_attested"], False)
                self.assertEqual(len(ScriptedModel.requests), turns)
                final = ScriptedModel.requests[-1]["messages"]
                self.assertEqual(len(final), 12)  # one system + five pairs + latest user
                self.assertEqual([m["role"] for m in final],
                                 ["system", "user", "assistant", "user", "assistant",
                                  "user", "assistant", "user", "assistant", "user",
                                  "assistant", "user"])
                self.assertEqual(final[1]["content"], first_history)
                self.assertIn("Correction: call me Nova.",
                              [m["content"] for m in final])
                self.assertEqual(final[-1]["content"], "What name should you use?")

    def test_odd_saved_user_turn_restores_as_editable_draft_and_key_rotation_revokes_it(self):
        gateway = self._start(with_vault=True)
        self._seed_odd_vault(gateway)
        result = self._browser(gateway, "restore_odd")
        self.assertEqual(result["restoredDraft"], "Correction: call me Nova.")
        self.assertEqual(result["restoredHistoryBeforeSubmit"], [
            {"role": "user", "content": "Call me Iris."},
            {"role": "assistant", "content": "Iris noted."}])
        self.assertIn("editable draft", result["restoredVaultStatus"])
        self.assertEqual(len(ScriptedModel.requests), 1)
        self.assertEqual([m["role"] for m in ScriptedModel.requests[-1]["messages"]],
                         ["system", "user", "assistant", "user"])
        self.assertEqual(ScriptedModel.requests[-1]["messages"][-1]["content"],
                         "Correction: call me Nova.")
        self.assertEqual(result["afterKeyRotation"],
                         {"prompt": "", "messages": 0, "bubbles": 0})
        self.assertIs(result["status"]["model_identity_attested"], False)

    def test_truncated_reply_stays_system_error_and_prompt_is_recoverable(self):
        ScriptedModel.mode = "length"
        for cap in (64, 96, 128):
            with self.subTest(max_tokens=cap):
                ScriptedModel.requests = []
                result = self._browser(self._start(token_limit=cap), "truncated")
                self.assertEqual(result["messages"], [])
                self.assertEqual(result["promptRecovered"],
                                 "Tell me what to do about the correction.")
                self.assertEqual([b["roleLabel"] for b in result["bubbles"]],
                                 ["YOU", "INTERFACE / ERROR"])
                self.assertIn("truncated", result["bubbles"][-1]["content"].lower())
                self.assertEqual(ScriptedModel.requests[0]["max_tokens"], cap)

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
