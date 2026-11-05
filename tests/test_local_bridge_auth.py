"""Synthetic multi-hop bearer tests. No physical llama-server or owner secrets."""

import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import tempfile
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from interface.loopback_model_bridge import LoopbackModelBridge, create_server
from interface.server import make_server


UPSTREAM_KEY = "synthetic-upstream-secret-only-0123456789"
BRIDGE_KEY = "synthetic-bridge-client-only-0123456789"
MODEL = "mock-q5-for-auth-contract"


class AuthenticatedModel(BaseHTTPRequestHandler):
    seen = []

    def _send(self, code, payload):
        raw = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _authenticated(self):
        type(self).seen.append((self.path, self.headers.get("Authorization"),
                                self.headers.get("X-Vera-Bridge-Key")))
        if self.headers.get("Authorization") != f"Bearer {UPSTREAM_KEY}":
            self._send(401, {"error": "upstream key rejected"})
            return False
        return True

    def do_GET(self):
        if not self._authenticated():
            return
        if self.path == "/health":
            self._send(200, {"status": "ok"})
        elif self.path == "/v1/models":
            self._send(200, {"data": [{"id": MODEL}]})
        else:
            self._send(404, {})

    def do_POST(self):
        if not self._authenticated():
            return
        request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        self._send(200, {"model": MODEL, "choices": [{"message": {
            "role": "assistant", "content": "synthetic reply to " + request["messages"][-1]["content"]},
            "finish_reason": "stop"}]})

    def log_message(self, *_args):
        pass


@unittest.skipIf(os.name == "nt", "Windows key tests require independently provisioned DACL files")
class ProtectedBridgeAuthTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.upstream_file = self._secret("upstream.key", UPSTREAM_KEY)
        self.bridge_file = self._secret("bridge.key", BRIDGE_KEY)
        AuthenticatedModel.seen = []
        self.services = []
        self.model = self._start(ThreadingHTTPServer(("127.0.0.1", 0), AuthenticatedModel))
        self.model_url = f"http://127.0.0.1:{self.model.server_port}"

    def tearDown(self):
        for server, thread in reversed(self.services):
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def _secret(self, filename, value):
        target = Path(self.tmp.name) / filename
        fd = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "wb") as handle:
            handle.write(value.encode("ascii") + b"\n")
        return str(target)

    def _start(self, server):
        server.daemon_threads = True
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.services.append((server, thread))
        return server

    def _bridge(self, *, upstream_key=None, client_key=None, protected=True):
        obj = LoopbackModelBridge(
            self.model_url, MODEL, timeout=1,
            upstream_api_key_file=upstream_key or self.upstream_file,
            client_api_key_file=client_key or self.bridge_file,
            require_upstream_auth=protected)
        return self._start(create_server(obj, port=0))

    def _request(self, url, *, body=None, headers=None):
        raw = None if body is None else json.dumps(body).encode()
        req = Request(url, data=raw, headers=headers or {},
                      method="POST" if raw is not None else "GET")
        try:
            with urlopen(req, timeout=5) as reply:
                return reply.status, json.loads(reply.read())
        except HTTPError as exc:
            return exc.code, json.loads(exc.read())

    @staticmethod
    def _chat_body():
        return {"model": MODEL, "stream": False, "max_tokens": 32,
                "messages": [{"role": "user", "content": "hello"}]}

    def test_protected_bridge_rejects_missing_wrong_and_duplicate_client_keys(self):
        bridge = self._bridge()
        base = f"http://127.0.0.1:{bridge.server_port}"
        self.assertEqual(self._request(base + "/health")[0], 401)
        self.assertEqual(self._request(base + "/v1/chat/completions",
                                       body=self._chat_body())[0], 401)
        self.assertEqual(self._request(base + "/health", headers={
            "X-Vera-Bridge-Key": "wrong"})[0], 401)
        client = http.client.HTTPConnection("127.0.0.1", bridge.server_port, timeout=5)
        try:
            client.putrequest("GET", "/health")
            client.putheader("X-Vera-Bridge-Key", BRIDGE_KEY)
            client.putheader("X-Vera-Bridge-Key", "wrong")
            client.endheaders()
            self.assertEqual(client.getresponse().status, 401)
        finally:
            client.close()
        self.assertEqual(AuthenticatedModel.seen, [])

    def test_protected_ui_bridge_upstream_secret_isolation(self):
        bridge = self._bridge()
        ui = self._start(make_server(port=0,
            ollama_url=f"http://127.0.0.1:{bridge.server_port}",
            bridge_client_api_key_file=self.bridge_file))
        ui_url = f"http://127.0.0.1:{ui.server_port}"
        session = {"X-Vera-Session": ui.session_token}
        status, models = self._request(ui_url + "/api/models", headers=session)
        self.assertEqual(status, 200)
        self.assertEqual(models["models"], [MODEL])
        status, chat = self._request(ui_url + "/api/chat",
            body={"model": MODEL, "messages": [{"role": "user", "content": "hello"}]},
            headers={**session, "Origin": ui_url, "Content-Type": "application/json",
                     "X-Vera-Bridge-Key": "attacker-overwrite"})
        self.assertEqual(status, 200)
        self.assertEqual(chat["reply"], "synthetic reply to hello")
        self.assertEqual(chat["response_completion_status"], "complete")
        for path, bearer, bridge_header in AuthenticatedModel.seen:
            self.assertIn(path, ("/health", "/v1/models", "/v1/chat/completions"))
            self.assertEqual(bearer, "Bearer " + UPSTREAM_KEY)
            self.assertIsNone(bridge_header, "UI-to-bridge key must not reach raw model")
        self.assertNotIn(UPSTREAM_KEY, json.dumps(chat) + json.dumps(models))
        self.assertNotIn(BRIDGE_KEY, json.dumps(chat) + json.dumps(models))

    def test_missing_ui_key_fails_without_upstream_inference(self):
        bridge = self._bridge()
        ui = self._start(make_server(port=0,
            ollama_url=f"http://127.0.0.1:{bridge.server_port}"))
        url = f"http://127.0.0.1:{ui.server_port}"
        status, _ = self._request(url + "/api/models", headers={
            "X-Vera-Session": ui.session_token})
        self.assertEqual(status, 503)
        self.assertEqual(AuthenticatedModel.seen, [])

    def test_wrong_upstream_key_and_permissions_fail_closed(self):
        wrong = self._secret("wrong.key", "wrong-upstream-secret-only-0123456789")
        bridge = self._bridge(upstream_key=wrong)
        status, payload = self._request(
            f"http://127.0.0.1:{bridge.server_port}/health",
            headers={"X-Vera-Bridge-Key": BRIDGE_KEY})
        self.assertEqual(status, 503)
        self.assertNotIn(UPSTREAM_KEY, json.dumps(payload))
        self.assertNotIn("wrong-upstream-secret", json.dumps(payload))
        bad = self._secret("world-readable.key", "unsafe-file-secret-only-0123456789")
        os.chmod(bad, 0o644)
        with self.assertRaises(ValueError):
            LoopbackModelBridge(self.model_url, MODEL,
                                upstream_api_key_file=bad,
                                client_api_key_file=self.bridge_file,
                                require_upstream_auth=True)

    def test_no_single_key_for_both_layers_or_missing_key(self):
        with self.assertRaises(ValueError):
            LoopbackModelBridge(self.model_url, MODEL,
                                upstream_api_key_file=self.upstream_file,
                                require_upstream_auth=True)
        # Even without the explicit protected flag, a partial setup would
        # otherwise turn a key-protected raw model into an open local proxy.
        with self.assertRaises(ValueError):
            LoopbackModelBridge(self.model_url, MODEL,
                                upstream_api_key_file=self.upstream_file)
        with self.assertRaises(ValueError):
            LoopbackModelBridge(self.model_url, MODEL,
                                client_api_key_file=self.bridge_file)
        with self.assertRaises(ValueError):
            LoopbackModelBridge(self.model_url, MODEL,
                                upstream_api_key_file=self.upstream_file,
                                client_api_key_file=self.upstream_file,
                                require_upstream_auth=True)


if __name__ == "__main__":
    unittest.main()
