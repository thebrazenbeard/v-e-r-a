"""Mock-protocol tests only: never claim a physical GGUF inference run."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import time
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from interface.loopback_model_bridge import LoopbackModelBridge, create_server


class MockModel(BaseHTTPRequestHandler):
    model_id = "mock-vera-gguf-v1"
    mode = "ok"
    chat_calls = 0

    def _send(self, value, code=200):
        data = json.dumps(value).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        try:
            self.wfile.write(data)
        except BrokenPipeError:
            pass

    def do_GET(self):
        if self.path == "/health":
            if type(self).mode == "timeout":
                time.sleep(0.15)
            self._send({"status": "ok"})
        elif self.path == "/v1/models":
            self._send({"data": [{"id": type(self).model_id}]})
        else:
            self._send({"error": "not found"}, 404)

    def do_POST(self):
        type(self).chat_calls += 1
        length = int(self.headers["Content-Length"])
        request = json.loads(self.rfile.read(length))
        self._send({"model": type(self).model_id, "choices": [{"message": {
            "role": "assistant", "content": "mock reply: " + request["messages"][-1]["content"]}}]})

    def log_message(self, *_args):
        pass


class LoopbackModelBridgeTests(unittest.TestCase):
    def setUp(self):
        MockModel.mode = "ok"
        MockModel.model_id = "mock-vera-gguf-v1"
        MockModel.chat_calls = 0
        self.upstream = ThreadingHTTPServer(("127.0.0.1", 0), MockModel)
        self.upstream.daemon_threads = True
        self.upstream_thread = Thread(target=self.upstream.serve_forever, daemon=True)
        self.upstream_thread.start()
        port = self.upstream.server_address[1]
        self.bridge = LoopbackModelBridge(f"http://127.0.0.1:{port}",
                                          "mock-vera-gguf-v1", timeout=0.05)
        self.server = create_server(self.bridge, port=0)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"

    def tearDown(self):
        for server, thread in ((self.server, self.thread),
                               (self.upstream, self.upstream_thread)):
            server.shutdown()
            server.server_close()
            thread.join(timeout=1)

    def get(self, path):
        with urlopen(self.url + path, timeout=2) as response:
            return response.status, json.load(response)

    def post(self, body):
        request = Request(self.url + "/v1/chat/completions",
                          data=json.dumps(body).encode(), method="POST",
                          headers={"Content-Type": "application/json"})
        with urlopen(request, timeout=2) as response:
            return response.status, json.load(response)

    def request_body(self):
        return {"model": "mock-vera-gguf-v1", "stream": False, "max_tokens": 32,
                "messages": [{"role": "user", "content": "hello"}]}

    def test_health_discovery_and_chat_are_mock_only(self):
        _, health = self.get("/health")
        self.assertEqual(health["model"], "mock-vera-gguf-v1")
        self.assertIs(health["effect_authority"], False)
        _, inventory = self.get("/api/tags")
        self.assertEqual(inventory["models"], [{"name": "mock-vera-gguf-v1"}])
        _, chat = self.post(self.request_body())
        self.assertEqual(chat["choices"][0]["message"]["content"], "mock reply: hello")
        self.assertEqual(MockModel.chat_calls, 1)

    def test_wrong_model_prevents_forwarding(self):
        body = self.request_body()
        body["model"] = "other-model"
        with self.assertRaises(HTTPError) as failure:
            self.post(body)
        self.assertEqual(failure.exception.code, 400)
        self.assertEqual(MockModel.chat_calls, 0)

    def test_live_upstream_identity_mismatch_fails_closed(self):
        MockModel.model_id = "swapped-model"
        with self.assertRaises(HTTPError) as failure:
            self.post(self.request_body())
        self.assertEqual(failure.exception.code, 503)
        self.assertEqual(MockModel.chat_calls, 0)

    def test_timeout_fails_closed(self):
        MockModel.mode = "timeout"
        with self.assertRaises(HTTPError) as failure:
            self.get("/health")
        self.assertEqual(failure.exception.code, 503)
        self.assertEqual(MockModel.chat_calls, 0)

    def test_no_memory_or_effect_routes_and_no_tool_payloads(self):
        for path in ("/memory", "/effects", "/plastic-state"):
            with self.assertRaises(HTTPError) as failure:
                self.get(path)
            self.assertEqual(failure.exception.code, 404)
        body = self.request_body()
        body["tools"] = [{"type": "function", "function": {"name": "shell"}}]
        with self.assertRaises(HTTPError) as failure:
            self.post(body)
        self.assertEqual(failure.exception.code, 400)
        self.assertEqual(MockModel.chat_calls, 0)

    def test_remote_target_and_blank_model_rejected(self):
        with self.assertRaises(ValueError):
            LoopbackModelBridge("http://192.0.2.1:1234", "model")
        with self.assertRaises(ValueError):
            LoopbackModelBridge("http://127.0.0.1:1234", "  ")


if __name__ == "__main__":
    unittest.main()
