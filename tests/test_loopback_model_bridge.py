"""Mock-protocol tests only: never claim a physical GGUF inference run."""

import json
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import socket
from threading import Event, Thread
import time
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from interface.loopback_model_bridge import LoopbackModelBridge, create_server


class MockModel(BaseHTTPRequestHandler):
    model_id = "mock-vera-gguf-v1"
    mode = "ok"
    chat_calls = 0
    chat_entered = Event()
    release_chat = Event()

    def _send(self, value, code=200, *, drip=False):
        data = json.dumps(value).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        try:
            if drip:
                for byte in data:
                    self.wfile.write(bytes([byte]))
                    self.wfile.flush()
                    time.sleep(0.02)  # Faster than 0.05s idle timeout; >2s total.
            else:
                self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError, OSError):
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
        if type(self).mode == "block":
            type(self).chat_entered.set()
            type(self).release_chat.wait(timeout=0.4)
        if type(self).mode == "header_drip":
            try:
                for byte in b"HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n":
                    self.wfile.write(bytes([byte]))
                    self.wfile.flush()
                    time.sleep(0.02)
            except (BrokenPipeError, ConnectionResetError, OSError):
                pass
            return
        reason = "length" if type(self).mode == "truncated" else "stop"
        message = {"content": "mock reply: " + request["messages"][-1]["content"]}
        if type(self).mode != "missing_role":
            message["role"] = ("system" if type(self).mode == "system_role" else
                               "user" if type(self).mode == "user_role" else "assistant")
        if type(self).mode == "empty_answer":
            message["content"] = ""
        choice = {"message": message}
        if type(self).mode != "missing_reason":
            choice["finish_reason"] = None if type(self).mode == "null_reason" else reason
        self._send({"model": type(self).model_id, "choices": [choice]},
                   drip=(type(self).mode == "drip"))

    def log_message(self, *_args):
        pass


class LoopbackModelBridgeTests(unittest.TestCase):
    def setUp(self):
        MockModel.mode = "ok"
        MockModel.model_id = "mock-vera-gguf-v1"
        MockModel.chat_calls = 0
        MockModel.chat_entered = Event()
        MockModel.release_chat = Event()
        self.upstream = ThreadingHTTPServer(("127.0.0.1", 0), MockModel)
        self.upstream.daemon_threads = True
        self.upstream_thread = Thread(target=self.upstream.serve_forever, daemon=True)
        self.upstream_thread.start()
        port = self.upstream.server_address[1]
        self.bridge = LoopbackModelBridge(f"http://127.0.0.1:{port}",
                                          "mock-vera-gguf-v1", timeout=0.05)
        self.server = create_server(self.bridge, port=0, body_deadline=0.3)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"

    def tearDown(self):
        MockModel.release_chat.set()
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

    def test_default_short_reply_budget_fails_closed_before_upstream(self):
        body = self.request_body()
        body["max_tokens"] = 65
        with self.assertRaises(HTTPError) as failure:
            self.post(body)
        self.assertEqual(failure.exception.code, 400)
        self.assertEqual(MockModel.chat_calls, 0)

    def test_only_one_upstream_completion_runs_at_a_time(self):
        # An unrelated process on the same host can call this loopback bridge
        # directly, bypassing the UI gateway's own one-model slot.
        MockModel.mode = "block"
        self.bridge.timeout = 0.5
        first = []

        def first_chat():
            try:
                first.append(self.post(self.request_body())[0])
            except Exception as exc:
                first.append(type(exc).__name__)

        worker = Thread(target=first_chat, daemon=True)
        worker.start()
        try:
            self.assertTrue(MockModel.chat_entered.wait(timeout=0.5))
            with self.assertRaises(HTTPError) as failure:
                self.post(self.request_body())
            self.assertEqual(failure.exception.code, 429)
            self.assertEqual(MockModel.chat_calls, 1)
        finally:
            MockModel.release_chat.set()
            worker.join(timeout=1)
        self.assertEqual(first, [200])

    def test_owner_can_explicitly_raise_token_cap_within_hard_limit(self):
        override = LoopbackModelBridge(self.bridge.upstream,
                                       "mock-vera-gguf-v1", timeout=0.05,
                                       max_chat_tokens=96)
        self.assertEqual(override.max_chat_tokens, 96)
        with self.assertRaises(ValueError):
            LoopbackModelBridge(self.bridge.upstream,
                                "mock-vera-gguf-v1", max_chat_tokens=513)

    def test_preserves_upstream_length_finish_reason(self):
        MockModel.mode = "truncated"
        _, chat = self.post(self.request_body())
        self.assertEqual(chat["choices"][0]["finish_reason"], "length")

    def test_missing_or_null_upstream_finish_reason_is_rejected(self):
        for mode in ("missing_reason", "null_reason"):
            MockModel.mode = mode
            with self.assertRaises(HTTPError) as failure:
                self.post(self.request_body())
            self.assertEqual(failure.exception.code, 503, mode)

    def test_non_assistant_role_or_empty_upstream_reply_is_rejected(self):
        for mode in ("missing_role", "system_role", "user_role", "empty_answer"):
            MockModel.mode = mode
            with self.assertRaises(HTTPError) as failure:
                self.post(self.request_body())
            self.assertEqual(failure.exception.code, 503, mode)

    def test_rejects_dns_rebinding_host_and_cross_origin(self):
        port = self.server.server_address[1]
        for host, origin in (("evil.example", None),
                             (f"127.0.0.1:{port}", "http://evil.example")):
            connection = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
            try:
                connection.putrequest("GET", "/health", skip_host=True)
                connection.putheader("Host", host)
                if origin:
                    connection.putheader("Origin", origin)
                connection.endheaders()
                response = connection.getresponse()
                self.assertEqual(response.status, 403)
                response.read()
            finally:
                connection.close()
        self.assertEqual(MockModel.chat_calls, 0)

    def test_slow_partial_bodies_release_workers_and_preserve_health(self):
        port = self.server.server_address[1]
        sockets = []
        try:
            for _ in range(16):
                client = socket.create_connection(("127.0.0.1", port), timeout=2)
                client.sendall((f"POST /v1/chat/completions HTTP/1.1\r\n"
                                f"Host: 127.0.0.1:{port}\r\n"
                                "Content-Length: 1000\r\n\r\n{").encode())
                sockets.append(client)
                time.sleep(0.01)
            # Real deadline is 12 s; test injects 0.3 s to verify the same path.
            time.sleep(0.55)
            _, health = self.get("/health")
            self.assertEqual(health["status"], "ok")
            self.assertEqual(MockModel.chat_calls, 0)
        finally:
            for client in sockets:
                client.close()

    def test_sixteen_upstream_trickle_responses_expire_and_health_recovers(self):
        MockModel.mode = "drip"
        results = []
        started = time.monotonic()

        def request_chat():
            try:
                self.post(self.request_body())
                results.append("unexpected 200")
            except HTTPError as exc:
                results.append(exc.code)
            except OSError as exc:
                results.append(type(exc).__name__)

        clients = [Thread(target=request_chat, daemon=True) for _ in range(16)]
        for client in clients:
            client.start()
        # One shared deadline, not 16 separate two-second waits.
        join_deadline = started + 2.5
        for client in clients:
            client.join(timeout=max(0, join_deadline - time.monotonic()))
        self.assertFalse(any(client.is_alive() for client in clients),
                         "dripping responses held clients beyond aggregate deadline")
        self.assertLess(time.monotonic() - started, 2.5)
        self.assertNotIn("unexpected 200", results)
        self.assertGreater(MockModel.chat_calls, 0)
        MockModel.mode = "ok"
        status, health = self.get("/health")
        self.assertEqual((status, health["status"]), (200, "ok"))

    def test_upstream_trickling_response_headers_hit_aggregate_deadline(self):
        MockModel.mode = "header_drip"
        started = time.monotonic()
        with self.assertRaises(HTTPError) as failure:
            self.post(self.request_body())
        self.assertEqual(failure.exception.code, 503)
        self.assertLess(time.monotonic() - started, 0.6)

    def test_timeout_cap_is_shorter_than_ui_gateway_timeout(self):
        with self.assertRaises(ValueError):
            LoopbackModelBridge(self.bridge.upstream, "mock-vera-gguf-v1", timeout=90)

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
