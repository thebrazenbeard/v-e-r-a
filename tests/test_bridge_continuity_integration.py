"""Mock-only cross-PR qualification: bridge + explicit transcript continuity.

No GGUF weights, actual inference, identity attestation, or service deploy.
"""

import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from threading import Thread
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from interface.loopback_model_bridge import LoopbackModelBridge, create_server
from interface.server import make_server
from tests.windows_acl_fixture import private_test_temporary_directory


MODEL_ID = "mock-integration-not-real-gguf"
SECRET = "operator-explicit-fixture-secret-0123456789"
MARKER = "mock-continuity-marker-274"


class MockOpenAIModel(BaseHTTPRequestHandler):
    requests = []
    finish_reason = "stop"

    def log_message(self, *_args):
        pass

    def _reply(self, content, code=200):
        raw = json.dumps(content).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path == "/health":
            self._reply({"status": "ok"})
        elif self.path == "/v1/models":
            self._reply({"data": [{"id": MODEL_ID}]})
        else:
            self._reply({"error": "unknown route"}, 404)

    def do_POST(self):
        if self.path != "/v1/chat/completions":
            self._reply({"error": "unknown route"}, 404)
            return
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        type(self).requests.append(body)
        last = body["messages"][-1]["content"]
        answer = MARKER if MARKER in last else "UNKNOWN"
        self._reply({"model": MODEL_ID, "choices": [{"message": {
            "role": "assistant", "content": answer},
            "finish_reason": type(self).finish_reason}]})


class BridgeContinuityIntegrationTests(unittest.TestCase):
    def test_gateway_and_bridge_token_caps_must_be_aligned(self):
        """A larger gateway allowance must not silently bypass a smaller bridge cap."""
        MockOpenAIModel.requests = []
        MockOpenAIModel.finish_reason = "stop"
        services = []

        def run(server):
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()
            services.append((server, thread))
            return server

        def chat(server):
            base = f"http://127.0.0.1:{server.server_port}"
            req = Request(base + "/api/chat", method="POST",
                data=json.dumps({"model": MODEL_ID,
                                 "messages": [{"role": "user", "content": "Hello"}]}).encode(),
                headers={"Content-Type": "application/json", "Origin": base,
                         "X-Vera-Session": server.session_token})
            try:
                with urlopen(req, timeout=3) as response:
                    return response.status, json.load(response)
            except HTTPError as exc:
                return exc.code, json.load(exc)

        try:
            upstream = run(ThreadingHTTPServer(("127.0.0.1", 0), MockOpenAIModel))
            upstream_url = f"http://127.0.0.1:{upstream.server_port}"
            with patch.dict("os.environ", {"VERA_MODEL_CHAT_MAX_TOKENS": "96"}):
                # A misconfigured 64-token bridge rejects the 96-token gateway request.
                bridge64 = run(create_server(LoopbackModelBridge(
                    upstream_url, MODEL_ID, timeout=1, max_chat_tokens=64), port=0))
                gateway96 = run(make_server(port=0, ollama_url=
                    f"http://127.0.0.1:{bridge64.server_port}"))
                self.assertEqual(chat(gateway96)[0], 503)
                self.assertEqual(MockOpenAIModel.requests, [])

                # Matching explicit owner values pass a bounded request unchanged.
                bridge96 = run(create_server(LoopbackModelBridge(
                    upstream_url, MODEL_ID, timeout=1, max_chat_tokens=96), port=0))
                matched = run(make_server(port=0, ollama_url=
                    f"http://127.0.0.1:{bridge96.server_port}"))
                code, response = chat(matched)
                self.assertEqual((code, response["truncated"]), (200, False))
                self.assertEqual(MockOpenAIModel.requests[-1]["max_tokens"], 96)
                MockOpenAIModel.finish_reason = "length"
                code, truncated = chat(matched)
                self.assertEqual((code, truncated["truncated"]), (422, True))
                self.assertIn("truncated", truncated["error"].lower())
                self.assertNotIn("reply", truncated)
        finally:
            MockOpenAIModel.finish_reason = "stop"
            for server, thread in reversed(services):
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)

    def test_mock_chat_explicit_save_restart_recall_and_hostile_requests(self):
        MockOpenAIModel.requests = []
        MockOpenAIModel.finish_reason = "stop"
        services = []

        def run(server):
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()
            services.append((server, thread))
            return server

        def request(server, path, *, method="GET", payload=None, vault=False,
                    origin=True, session=True):
            base = f"http://127.0.0.1:{server.server_port}"
            headers = {"Content-Type": "application/json"}
            if origin:
                headers["Origin"] = base
            if session:
                headers["X-Vera-Session"] = server.session_token
            if vault:
                headers["X-Vera-Vault-Key"] = SECRET
            raw = json.dumps(payload).encode() if payload is not None else None
            try:
                with urlopen(Request(base + path, data=raw, headers=headers,
                                     method=method), timeout=3) as response:
                    return response.status, json.load(response)
            except HTTPError as exc:
                return exc.code, json.load(exc)

        with private_test_temporary_directory() as directory:
            db = Path(directory) / "operator-only-continuity.sqlite3"
            try:
                upstream = run(ThreadingHTTPServer(("127.0.0.1", 0), MockOpenAIModel))
                bridge = run(create_server(LoopbackModelBridge(
                    f"http://127.0.0.1:{upstream.server_port}", MODEL_ID, timeout=1), port=0))
                bridge_url = f"http://127.0.0.1:{bridge.server_port}"

                def open_ui():
                    return run(make_server(port=0, ollama_url=bridge_url,
                                           memory_db_path=db, memory_secret=SECRET))

                first = open_ui()
                status, models = request(first, "/api/models")
                self.assertEqual((status, models["models"]), (200, [MODEL_ID]))
                status, state = request(first, "/api/status")
                self.assertEqual((status, state["external_actions"]),
                                 (200, "not_connected"))
                question = "What is the operator's synthetic marker?"
                chat = {"model": MODEL_ID, "messages": [{"role": "user", "content": question}]}
                self.assertEqual(request(first, "/api/chat", method="POST",
                                         payload=chat)[1]["reply"], "UNKNOWN")
                saved_text = [{"role": "user", "content": f"My synthetic marker is {MARKER}."}]
                status, receipt = request(first, "/api/transcript", method="POST", vault=True,
                                          payload={"messages": saved_text, "expected_revision": 0})
                self.assertEqual((status, receipt["revision"]), (200, 1))
                self.assertEqual(receipt["source_classification"]["kind"],
                                 "user_conversation")
                self.assertIs(receipt["source_classification"]["imported_knowledge"], False)
                self.assertIs(receipt["source_classification"]["trained_weights_modified"], False)

                first.shutdown()
                first.server_close()
                second = open_ui()
                self.assertNotEqual(first.session_token, second.session_token)
                status, restored = request(second, "/api/transcript", vault=True)
                self.assertEqual((status, restored["messages"]), (200, saved_text))
                self.assertEqual(restored["source_classification"],
                                 receipt["source_classification"])
                self.assertEqual(request(second, "/api/chat", method="POST", payload={
                    **chat, "recall_saved": True})[0], 403)  # missing explicit vault consent
                status, recall = request(second, "/api/chat", method="POST", vault=True,
                                         payload={**chat, "recall_saved": True})
                self.assertEqual((status, recall["reply"]), (200, MARKER))
                self.assertEqual(recall["recalled_source"]["source_classification"],
                                 receipt["source_classification"])
                self.assertEqual(recall["mode"], "response_only")
                upstream_req = MockOpenAIModel.requests[-1]
                self.assertEqual([item["role"] for item in upstream_req["messages"]],
                                 ["system", "user"])
                self.assertIn("UNVERIFIED OPERATOR-SAVED", upstream_req["messages"][-1]["content"])
                self.assertNotIn(SECRET, json.dumps(upstream_req))
                self.assertNotIn("tools", upstream_req)
                self.assertNotIn("effect_authority", upstream_req)

                # The bridge never exposes memory, tool, or effect write routes.
                for path in ("/memory", "/effects", "/plastic-state"):
                    with self.assertRaises(HTTPError) as error:
                        urlopen(bridge_url + path, timeout=2)
                    self.assertEqual(error.exception.code, 404)
                with self.assertRaises(HTTPError) as error:
                    urlopen(Request(bridge_url + "/v1/chat/completions",
                        data=json.dumps({"model": MODEL_ID, "messages": [
                            {"role": "user", "content": "test"}], "max_tokens": 8,
                            "stream": False, "tools": ["shell"]}).encode(),
                        headers={"Content-Type": "application/json"},
                        method="POST"), timeout=2)
                self.assertEqual(error.exception.code, 400)
                count = len(MockOpenAIModel.requests)
                for host, origin in (("attacker.invalid", None),
                                     (f"127.0.0.1:{bridge.server_port}",
                                      "http://attacker.invalid")):
                    conn = http.client.HTTPConnection("127.0.0.1", bridge.server_port,
                                                      timeout=2)
                    try:
                        conn.putrequest("GET", "/health", skip_host=True)
                        conn.putheader("Host", host)
                        if origin:
                            conn.putheader("Origin", origin)
                        conn.endheaders()
                        self.assertEqual(conn.getresponse().status, 403)
                    finally:
                        conn.close()
                self.assertEqual(len(MockOpenAIModel.requests), count)
                status, removed = request(second, "/api/transcript", method="DELETE",
                                          vault=True, payload=None)
                # DELETE needs optimistic revision header; use a separate request below.
                self.assertEqual(status, 400)
                headers = {"Origin": f"http://127.0.0.1:{second.server_port}",
                           "X-Vera-Session": second.session_token,
                           "X-Vera-Vault-Key": SECRET,
                           "X-Vera-Vault-Revision": "1"}
                with urlopen(Request(f"http://127.0.0.1:{second.server_port}/api/transcript",
                                     headers=headers, method="DELETE"), timeout=3) as response:
                    self.assertEqual(json.load(response)["status"], "removed_from_active_vault")
                self.assertEqual(request(second, "/api/chat", method="POST", vault=True,
                                         payload={**chat, "recall_saved": True})[0], 409)
            finally:
                for server, thread in reversed(services):
                    server.shutdown()
                    server.server_close()
                    thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
