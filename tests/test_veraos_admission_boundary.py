"""Negative integration contract: a Vera browser tab is not VeraOS authority.

Pinned source review: v-e-r-a Draft PR #30 at
7f8346b1328e8b4e3f172d1c1e10ad5738cb7d89 and VeraOS Draft #74 at
048da7c59d72dbbbe718b48d1bda91460e0fda8b.

The tests launch only a disposable localhost HTTP interface. No real model,
Windows named pipe, WSL service, or external device is contacted.
"""

from __future__ import annotations

import json
import threading
import unittest
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
                asserted_headers: dict[str, str] | None = None) -> tuple[int, dict]:
        headers = {"X-Vera-Session": self.app.session_token}
        if method != "GET":
            headers.update({"Origin": self.base, "Content-Type": "application/json"})
        if asserted_headers:
            headers.update(asserted_headers)
        raw = None if body is None else json.dumps(body).encode("utf-8")
        req = Request(self.base + path, method=method, data=raw, headers=headers)
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


if __name__ == "__main__":
    unittest.main()
