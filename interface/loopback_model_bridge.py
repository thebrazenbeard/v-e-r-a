"""Read-only, loopback-only llama.cpp/KoboldCPP OpenAI chat bridge.

This bridge adds no model weights, memory, knowledge, tools, or effect authority.
Its advertised model is verified against the upstream's live /v1/models list.
"""

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import BoundedSemaphore
from urllib.error import HTTPError, URLError

from .server import GatewayError, _BoundedHTTPServer, _decode_json, _model_root, _read_json_from_model

MAX_BODY = 24 * 1024
MAX_REPLY = 1024 * 1024


class LoopbackModelBridge:
    def __init__(self, upstream: str, model_id: str, *, timeout: float = 30.0):
        self.upstream = _model_root(upstream)
        if (type(model_id) is not str or not model_id.strip() or len(model_id) > 128
                or model_id != model_id.strip()):
            raise ValueError("a nonempty, exact model ID is required")
        if timeout <= 0 or timeout > 120:
            raise ValueError("timeout must be between 0 and 120 seconds")
        self.model_id = model_id
        self.timeout = timeout

    def ready(self) -> None:
        health = _read_json_from_model(self.upstream + "/health", limit=4096,
                                       timeout=min(self.timeout, 3))
        if not isinstance(health, dict) or health.get("status") not in ("ok", "ready"):
            raise GatewayError("upstream is not ready")
        inventory = _read_json_from_model(self.upstream + "/v1/models", limit=256 * 1024,
                                          timeout=min(self.timeout, 3))
        rows = inventory.get("data") if isinstance(inventory, dict) else None
        if type(rows) is not list or not any(
                type(row) is dict and row.get("id") == self.model_id for row in rows[:128]):
            raise GatewayError("configured model ID absent from upstream inventory")

    def completion(self, body: object) -> dict:
        if type(body) is not dict or set(body) != {"model", "messages", "stream", "max_tokens"}:
            raise ValueError("only bounded chat parameters are accepted")
        if body["model"] != self.model_id or body["stream"] is not False:
            raise ValueError("model mismatch or streaming prohibited")
        tokens, messages = body["max_tokens"], body["messages"]
        if type(tokens) is not int or not 1 <= tokens <= 512:
            raise ValueError("invalid token bound")
        if type(messages) is not list or not 1 <= len(messages) <= 13:
            raise ValueError("invalid message count")
        total = 0
        for message in messages:
            if (type(message) is not dict or set(message) != {"role", "content"}
                    or message["role"] not in ("system", "user", "assistant")
                    or type(message["content"]) is not str
                    or not 0 < len(message["content"]) <= 6000):
                raise ValueError("only bounded text messages are accepted")
            total += len(message["content"])
        if total > 20000 or messages[-1]["role"] != "user":
            raise ValueError("invalid conversation")
        self.ready()  # Fail closed if an upstream has changed models since discovery.
        response = _read_json_from_model(self.upstream + "/v1/chat/completions",
                                         payload=body, limit=MAX_REPLY, timeout=self.timeout)
        try:
            choice = response["choices"][0]
            message = choice["message"]
            answer = message["content"]
            if ("tool_calls" in message or "function_call" in message
                    or choice.get("finish_reason") == "tool_calls"
                    or ("model" in response and response["model"] != self.model_id)):
                raise GatewayError("upstream attempted a tool response or changed identity")
        except (KeyError, IndexError, TypeError) as exc:
            raise GatewayError("invalid upstream chat response") from exc
        if type(answer) is not str or len(answer) > 16000:
            raise GatewayError("invalid upstream chat text")
        # Do not pass through upstream metadata, tools, extensions, or server hints.
        return {"model": self.model_id, "choices": [{"index": 0, "message": {
            "role": "assistant", "content": answer}, "finish_reason": "stop"}]}


def create_server(bridge: LoopbackModelBridge, port: int = 11439) -> ThreadingHTTPServer:
    if type(port) is not int or not 0 <= port <= 65535:
        raise ValueError("invalid local listening port")

    class Handler(BaseHTTPRequestHandler):
        def _json(self, code: int, value: dict) -> None:
            raw = json.dumps(value, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self) -> None:
            if self.path not in ("/health", "/api/tags"):
                self._json(404, {"error": "unknown route"})
                return
            try:
                bridge.ready()
            except (GatewayError, HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
                self._json(503, {"status": "unavailable", "error": type(exc).__name__})
                return
            if self.path == "/health":
                self._json(200, {"status": "ok", "model": bridge.model_id,
                                 "effect_authority": False})
            else:
                self._json(200, {"models": [{"name": bridge.model_id}]})

        def do_POST(self) -> None:
            if self.path != "/v1/chat/completions":
                self._json(404, {"error": "unknown route"})
                return
            try:
                size = int(self.headers.get("Content-Length", "-1"))
                if not 0 < size <= MAX_BODY:
                    raise ValueError("invalid body length")
                body = _decode_json(self.rfile.read(size))
                answer = bridge.completion(body)
            except (ValueError, UnicodeError) as exc:
                self._json(400, {"error": str(exc)})
                return
            except (GatewayError, HTTPError, URLError, TimeoutError, OSError) as exc:
                self._json(503, {"error": "upstream unavailable", "category": type(exc).__name__})
                return
            self._json(200, answer)

        def log_message(self, *_args) -> None:
            pass  # Prompts must never land in HTTP logs.

    server = _BoundedHTTPServer(("127.0.0.1", port), Handler)
    server.request_slots = BoundedSemaphore(16)
    server.daemon_threads = True
    return server


def main() -> None:
    parser = argparse.ArgumentParser(description="Local Vera GGUF server chat adapter")
    parser.add_argument("--upstream", required=True, help="http://127.0.0.1:PORT")
    parser.add_argument("--model-id", required=True, help="exact upstream /v1/models ID")
    parser.add_argument("--port", type=int, default=11439)
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()
    bridge = LoopbackModelBridge(args.upstream, args.model_id, timeout=args.timeout)
    with create_server(bridge, port=args.port) as server:
        print(f"Vera local model bridge listening on 127.0.0.1:{server.server_address[1]}", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()
