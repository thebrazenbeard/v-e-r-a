"""Negative integration contract: a Vera browser tab is not VeraOS authority.

Pinned source review: v-e-r-a Draft PR #31 at
1e73447d2f8dad13db2678d40505c6b23de705a1 and VeraOS Draft #74 at
ae82817427dc32946452f95a73474cc93fc0561d. Accepted main is separate.

The tests launch only a disposable localhost HTTP interface. No real model,
Windows named pipe, WSL service, or external device is contacted.
"""

from __future__ import annotations

import json
import threading
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from interface.server import make_server


class VeraOSAdmissionBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        # This endpoint deliberately has no model server at the other end.
        # All requests exercise UI validation/status only, not inference.
        self.app = make_server(port=0, ollama_url="http://127.0.0.1:1")
        self.base = f"http://127.0.0.1:{self.app.server_port}"
        thread = threading.Thread(target=self.app.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(thread.join, 3)
        self.addCleanup(self.app.server_close)
        self.addCleanup(self.app.shutdown)

    def request(self, path: str, *, method: str = "GET", body: dict | None = None,
                asserted_headers: dict[str, str] | None = None,
                app=None) -> tuple[int, dict]:
        app = self.app if app is None else app
        base = f"http://127.0.0.1:{app.server_port}"
        headers = {"X-Vera-Session": app.session_token}
        if method != "GET":
            headers.update({"Origin": base, "Content-Type": "application/json"})
        if asserted_headers:
            headers.update(asserted_headers)
        raw = None if body is None else json.dumps(body).encode("utf-8")
        req = Request(base + path, method=method, data=raw, headers=headers)
        try:
            with urlopen(req, timeout=5) as response:
                return response.status, json.loads(response.read())
        except HTTPError as exc:
            with exc:
                return exc.code, json.loads(exc.read())

    def test_source_persona_and_browser_session_do_not_claim_veraos_identity(self):
        headers = {
            "X-VeraOS-Windows-SID": "S-1-5-5-100-200",
            "X-VeraOS-Principal": "patrick",
            "X-VeraOS-Grant": "a" * 128,
        }
        code, status = self.request("/api/status", asserted_headers=headers)
        self.assertEqual(code, 200)
        self.assertEqual(status["authority"], "response_only")
        self.assertEqual(status["portal"], "not_connected")
        self.assertEqual(status["pre_active"], "not_connected")
        self.assertEqual(status["external_actions"], "not_connected")
        self.assertFalse(status["model_identity_attested"])
        self.assertFalse(status["persona_source"]["identity_attested"])
        for forbidden in ("authenticated_principal_id", "windows_sid", "veraos_task_id",
                          "production_authority", "effect_authority"):
            self.assertNotIn(forbidden, status)

    def test_browser_token_does_not_create_veraos_status_or_effect_endpoint(self):
        for method, path, payload in (
            ("GET", "/api/veraos/status", None),
            ("POST", "/api/veraos/tasks", {"worker": "digest", "filename": "data"}),
            ("POST", "/api/veraos/effects", {"effect": "protected.merge"}),
            ("DELETE", "/api/veraos/tasks/" + "a" * 32, None),
        ):
            with self.subTest(method=method, path=path):
                code, response = self.request(path, method=method, body=payload,
                    asserted_headers={"X-VeraOS-Grant": "b" * 128})
                self.assertEqual(code, 404)
                self.assertNotIn("task_id", response)
                self.assertNotIn("allowed", response)

    def test_model_chat_does_not_accept_injected_veraos_task_or_authority(self):
        baseline = {"model": "not-running", "messages": [
            {"role": "user", "content": "hello"}]}
        for injection in (
            {"veraos_task_id": "a" * 32},
            {"authenticated_principal_id": "patrick"},
            {"action": "deny-effect", "effect": "protected.merge"},
        ):
            with self.subTest(injection=injection):
                code, response = self.request("/api/chat", method="POST",
                                              body={**baseline, **injection})
                self.assertEqual(code, 400)
                self.assertNotIn("reply", response)

    def test_private_goal_read_cannot_be_promoted_by_browser_session(self):
        code, response = self.request("/api/goals/current", asserted_headers={
            "X-Vera-Goal-Access": "fake-capability",
            "X-VeraOS-Grant": "c" * 128,
        })
        self.assertEqual(code, 403)
        self.assertNotIn("goals", response)

    def test_forged_native_ping_claims_cannot_promote_status(self):
        # These are attacker-controlled HTTP strings, NOT the observed
        # Windows client token from a host-owned named-pipe endpoint.
        claimed = {
            "X-VeraOS-Verified": "true",
            "X-VeraOS-Windows-SID": "S-1-5-21-100-200-300-400",
            "X-VeraOS-Logon-LUID": "0000000000000123",
            "X-VeraOS-Issuer": "LAPPY",
            "X-VeraOS-Signature": "a" * 128,
        }
        code, status = self.request("/api/status", asserted_headers=claimed)
        self.assertEqual(code, 200)
        self.assertEqual(status["authority"], "response_only")
        self.assertEqual(status["portal"], "not_connected")
        self.assertEqual(status["external_actions"], "not_connected")
        for forbidden in ("windows_sid", "logon_luid", "verified_principal",
                          "veraos_status", "trusted_issuer", "effect_authority"):
            self.assertNotIn(forbidden, status)

    def test_expiry_replay_and_consent_headers_do_not_create_runtime_routes(self):
        # A browser session can replay arbitrary strings but cannot mint a
        # VeraOS projection, even when claims look timely and consented.
        claimed = {
            "X-VeraOS-Nonce": "replayed-browser-nonce",
            "X-VeraOS-Issued-At": "2026-11-05T00:00:00Z",
            "X-VeraOS-Expires-At": "2026-11-05T00:00:01Z",
            "X-VeraOS-Consent": "granted",
            "X-VeraOS-Signature": "b" * 128,
        }
        for _ in range(2):
            with self.subTest(replay=_):
                status, payload = self.request("/api/veraos/status",
                                               asserted_headers=claimed)
                self.assertEqual(status, 404)
                self.assertNotIn("production_authority", payload)
                self.assertNotIn("principal", payload)
                status, payload = self.request("/api/veraos/tasks", method="POST",
                    body={"task": "status-only"}, asserted_headers=claimed)
                self.assertEqual(status, 404)
                self.assertNotIn("task_id", payload)

    def test_signed_looking_task_body_and_goal_header_do_not_mint_authority(self):
        claimed = {
            "verified": True,
            "windows_sid": "S-1-5-21-100-200-300-400",
            "logon_luid": "0000000000000123",
            "consent": "granted",
            "issuer": "LAPPY",
            "signature": "c" * 128,
        }
        status, payload = self.request("/api/veraos/effects", method="POST",
            body={"effect": "protected.merge", **claimed},
            asserted_headers={"X-VeraOS-Verified": "true"})
        self.assertEqual(status, 404)
        self.assertNotIn("receipt", payload)
        self.assertNotIn("allowed", payload)

        status, private = self.request("/api/goals/current", asserted_headers={
            "X-VeraOS-Verified": "true", "X-VeraOS-Signature": "c" * 128,
            "X-Vera-Goal-Access": "claimed-consent-not-a-capability",
        })
        self.assertEqual(status, 403)
        self.assertNotIn("goals", private)

    def test_windows_shaped_headers_cannot_read_write_or_delete_private_vault(self):
        # An opted-in local vault is a separate capability class. Plausible
        # Windows claims plus a browser session cannot substitute for its key.
        with TemporaryDirectory() as root:
            vault = make_server(port=0, ollama_url="http://127.0.0.1:1",
                memory_db_path=Path(root) / "vault.sqlite3",
                memory_secret="v" * 48)
            thread = threading.Thread(target=vault.serve_forever, daemon=True)
            thread.start()
            self.addCleanup(thread.join, 3)
            self.addCleanup(vault.server_close)
            self.addCleanup(vault.shutdown)
            claims = {
                "X-VeraOS-Windows-SID": "S-1-5-21-100-200-300-400",
                "X-VeraOS-Logon-LUID": "0000000000000123",
                "X-VeraOS-Verified": "true",
                "X-VeraOS-Issuer": "host-owned-LAPPY",
                "X-VeraOS-Consent": "granted",
                "X-VeraOS-Signature": "a" * 128,
                "X-Vera-Vault-Key": "not-the-vault-key",
            }
            for method, body in (
                ("GET", None),
                ("POST", {"messages": [{"role": "user", "content": "private"}],
                          "expected_revision": 0}),
                ("DELETE", None),
            ):
                with self.subTest(method=method):
                    code, response = self.request("/api/transcript", app=vault,
                        method=method, body=body, asserted_headers={
                            **claims, "X-Vera-Vault-Revision": "0"})
                    self.assertEqual(code, 403)
                    self.assertNotIn("messages", response)
                    self.assertNotIn("revision", response)
            self.assertEqual(vault.transcript_store.read()["status"], "empty")

    def test_claimed_consented_stm_archive_has_no_browser_ingest_route(self):
        claims = {
            "X-VeraOS-Windows-SID": "S-1-5-21-100-200-300-400",
            "X-VeraOS-Issuer": "LAPPY",
            "X-VeraOS-Consent": "archive-granted",
            "X-VeraOS-Nonce": "nonce-12345",
            "X-VeraOS-Signature": "b" * 128,
        }
        for method, path, body in (
            ("GET", "/api/conversation", None),
            ("GET", "/api/conversation/history", None),
            ("POST", "/api/conversation", {"messages": [
                {"role": "user", "content": "private chat"}], "consent": True}),
            ("POST", "/api/conversation/history", {"archive": True}),
            ("POST", "/api/stm/admit", {"consent": True, "owner": "patrick"}),
        ):
            with self.subTest(method=method, path=path):
                code, response = self.request(path, method=method, body=body,
                    asserted_headers=claims)
                self.assertEqual(code, 404)
                self.assertNotIn("receipt", response)
                self.assertNotIn("messages", response)

    def test_lookalike_routes_and_proxy_headers_do_not_rewrite_authority(self):
        # The server must not rewrite forwarded host/path or percent-encoded
        # lookalikes into a privileged route.
        claimed = {
            "X-Forwarded-Host": "127.0.0.1:8765",
            "X-Forwarded-Proto": "https",
            "X-Original-URL": "/api/veraos/effects",
            "X-Rewrite-URL": "/api/veraos/tasks",
            "X-VeraOS-Grant": "c" * 128,
        }
        for path in ("/api/veraos/status?nonce=trusted",
                     "/api/%76eraos/status", "/api/veraos/status%2f",
                     "/api/veraos/tasks/../effects", "/api/veraos/effects"):
            with self.subTest(path=path):
                code, response = self.request(path, asserted_headers=claimed)
                self.assertEqual(code, 404)
                self.assertNotIn("allowed", response)
        for method, path, body in (
            ("POST", "/api/veraos/tasks?consent=true", {"task": "run"}),
            ("POST", "/api/%76eraos/effects", {"effect": "protected.merge"}),
        ):
            with self.subTest(path=path):
                code, response = self.request(path, method=method, body=body,
                    asserted_headers=claimed)
                self.assertEqual(code, 404)
                self.assertNotIn("allowed", response)

    def test_claim_headers_do_not_trigger_existing_model_backend(self):
        # Unknown task/effect/memory routes reject before even inspecting the
        # local model endpoint. No false claim of real host-side isolation.
        claims = {"X-VeraOS-Windows-SID": "S-1-5-21-100-200-300-400",
                  "X-VeraOS-Verified": "true", "X-VeraOS-Grant": "d" * 128}
        with patch("interface.server._chat") as chat, \
             patch("interface.server._models") as models:
            for method, path, body in (
                ("POST", "/api/veraos/tasks", {"task": "execute"}),
                ("POST", "/api/veraos/effects", {"effect": "protected.merge"}),
                ("POST", "/api/stm/admit", {"memory": "sensitive"}),
            ):
                code, _ = self.request(path, method=method, body=body,
                    asserted_headers=claims)
                self.assertEqual(code, 404)
            chat.assert_not_called()
            models.assert_not_called()


if __name__ == "__main__":
    unittest.main()
