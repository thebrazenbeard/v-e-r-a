"""TEST-only 3-subprocess boundary smoke: upstream → bridge → Vera browser API.

No GGUF weights, host services, persistent memory or credentials are involved.
Run: python -m unittest tests.test_three_process_loopback_smoke -v
"""

from __future__ import annotations

import json
import socket
import subprocess
import sys
import time
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, Request, build_opener

from tests.mock_openai_service import MODEL


_NO_PROXY = build_opener(ProxyHandler({}))


def _free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _get(url, headers=None):
    with _NO_PROXY.open(Request(url, headers=headers or {}), timeout=2) as response:
        return response.status, json.load(response)


def _post(url, body, headers):
    request = Request(url, data=json.dumps(body).encode("utf-8"),
                      headers=headers, method="POST")
    try:
        with _NO_PROXY.open(request, timeout=3) as response:
            return response.status, json.load(response)
    except HTTPError as exc:
        return exc.code, json.load(exc)


def _wait_ready(url, process):
    deadline = time.monotonic() + 7
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise AssertionError(f"test subprocess exited with {process.returncode}")
        try:
            status, _ = _get(url)
            if status == 200:
                return
        except (OSError, URLError, HTTPError):
            pass
        time.sleep(0.05)
    raise AssertionError("test subprocess did not become ready")


class ThreeProcessLoopbackSmoke(unittest.TestCase):
    def test_real_http_boundaries_without_model_weights(self):
        ports = []
        while len(ports) < 3:
            port = _free_port()
            if port not in ports:
                ports.append(port)
        upstream_port, bridge_port, ui_port = ports
        upstream = f"http://127.0.0.1:{upstream_port}"
        bridge = f"http://127.0.0.1:{bridge_port}"
        ui = f"http://127.0.0.1:{ui_port}"

        commands = [
            [sys.executable, "-m", "tests.mock_openai_service",
             "--port", str(upstream_port)],
            [sys.executable, "-m", "interface.loopback_model_bridge",
             "--upstream", upstream, "--model-id", MODEL,
             "--port", str(bridge_port), "--timeout", "2"],
            [sys.executable, "-m", "interface", "--port", str(ui_port),
             "--ollama-url", bridge, "--max-response-tokens", "192"],
        ]
        # Process scopes belong only to this test. Every child is terminated
        # even on assertions/exceptions, and no shared default port is used.
        children = []
        try:
            for index, command in enumerate(commands):
                child = subprocess.Popen(command, stdin=subprocess.DEVNULL,
                                         stdout=subprocess.DEVNULL,
                                         stderr=subprocess.DEVNULL,
                                         close_fds=True)
                children.append(child)
                _wait_ready((upstream + "/health" if index == 0 else
                             bridge + "/health" if index == 1 else
                             ui + "/api/session"), child)
            status, session = _get(ui + "/api/session")
            self.assertEqual(status, 200)
            headers = {"X-Vera-Session": session["token"]}
            status, model_list = _get(ui + "/api/models", headers)
            self.assertEqual((status, model_list["models"]), (200, [MODEL]))
            status, server_state = _get(ui + "/api/status", headers)
            self.assertEqual((status, server_state["durable_memory"]),
                             (200, "not_connected"))
            self.assertEqual(server_state["persona_source"]["qualification"], "SOURCE_ONLY")
            self.assertFalse(server_state["persona_source"]["identity_attested"])
            with _NO_PROXY.open(ui + "/", timeout=2) as page:
                self.assertEqual(page.status, 200)  # Actual HTML is served.
                self.assertIn(b'<form', page.read())
            post_headers = {**headers, "Origin": ui,
                            "Content-Type": "application/json"}

            history = []
            for question in ("Who are you?", "What changed?", "A correction: be concise"):
                history.append({"role": "user", "content": question})
                code, result = _post(ui + "/api/chat",
                                     {"model": MODEL, "messages": history},
                                     post_headers)
                self.assertEqual((code, result["response_completion_status"]),
                                 (200, "complete"))
                self.assertEqual(result["response_token_limit"], 192)
                history.append({"role": "assistant", "content": result["reply"]})

            for question, expected in (("limited", "length_limited"),
                                       ("filtered", "filtered"),
                                       ("unknown", "unknown")):
                code, result = _post(ui + "/api/chat",
                                     {"model": MODEL, "messages": [
                                         {"role": "user", "content": question}]},
                                     post_headers)
                self.assertEqual((code, result["response_completion_status"]),
                                 (200, expected))
                self.assertNotEqual(result["response_completion_status"], "complete")
            for question in ("wrong-role", "empty-stop"):
                code, result = _post(ui + "/api/chat",
                                     {"model": MODEL, "messages": [
                                         {"role": "user", "content": question}]},
                                     post_headers)
                self.assertEqual(code, 503)
                self.assertNotIn("reply", result)

            upstream_requests = _get(upstream + "/__mock__/calls")[1]["calls"]
            self.assertEqual(len(upstream_requests), 8)
            for turn in upstream_requests:
                self.assertEqual(turn["max_tokens"], 192)
                self.assertEqual(turn["messages"][0]["role"], "system")
                self.assertIn("Your name here is Vera", turn["messages"][0]["content"])
                self.assertNotIn(session["token"], json.dumps(turn))
                self.assertEqual(turn["messages"][-1]["role"], "user")
            self.assertEqual([row["role"] for row in upstream_requests[2]["messages"]],
                             ["system", "user", "assistant", "user",
                              "assistant", "user"])
        finally:
            for child in reversed(children):
                if child.poll() is None:
                    child.terminate()
            for child in reversed(children):
                try:
                    child.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait(timeout=3)


if __name__ == "__main__":
    unittest.main()
