"""Read-only, loopback-only llama.cpp/KoboldCPP OpenAI chat bridge.

This bridge adds no model weights, memory, knowledge, tools, or effect authority.
Its advertised model is verified against the upstream's live /v1/models list.
"""

from __future__ import annotations

import argparse
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import BoundedSemaphore, Timer
import socket
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit

from .server import GatewayError, _BoundedHTTPServer, _decode_json, _model_root

MAX_BODY = 24 * 1024
MAX_REPLY = 1024 * 1024
CLIENT_IO_TIMEOUT_SECONDS = 8
CLIENT_BODY_DEADLINE_SECONDS = 12
MAX_UPSTREAM_TIMEOUT_SECONDS = 75  # UI gateway gives the whole exchange 90s.


def _bounded_upstream_json(root: str, path: str, *, payload: dict | None = None,
                           limit: int, timeout: float) -> object:
    """Aggregate wall-clock bound, including a trickling HTTP status/body.

    A socket's read timeout alone measures only idle time: a peer sending one
    byte every few milliseconds can otherwise occupy all bridge workers.
    A monotonic deadline and a forced socket shutdown bound the whole exchange.
    """
    deadline = time.monotonic() + timeout
    port = urlsplit(root).port  # root was validated by _model_root at init.
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=timeout)
    expired = False
    guard_socket: socket.socket | None = None

    def abort() -> None:
        nonlocal expired
        expired = True
        sock = guard_socket or connection.sock
        if sock is not None:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

    timer = Timer(timeout, abort)
    timer.daemon = True
    timer.start()
    try:
        raw_body = None if payload is None else json.dumps(
            payload, ensure_ascii=False).encode("utf-8")
        connection.request("POST" if raw_body is not None else "GET", path,
                           body=raw_body,
                           headers={"Content-Type": "application/json", "Connection": "close"}
                           if raw_body is not None else {"Connection": "close"})
        # http.client can detach/close connection.sock on Connection: close
        # while its HTTPResponse file still owns the readable socket. Keep an
        # independent handle so the timer can shut down that same TCP stream.
        guard_socket = connection.sock.dup() if connection.sock is not None else None
        response = connection.getresponse()
        if response.status != 200:
            raise GatewayError("upstream returned an error status")
        raw = response.read(limit + 1)
        if expired or time.monotonic() >= deadline:
            raise TimeoutError("upstream aggregate deadline exceeded")
        if len(raw) > limit:
            raise GatewayError("upstream response exceeded byte limit")
        try:
            return _decode_json(raw)
        except (ValueError, UnicodeError) as exc:
            raise GatewayError("upstream returned malformed JSON") from exc
    except (OSError, http.client.HTTPException) as exc:
        if expired or time.monotonic() >= deadline:
            raise TimeoutError("upstream aggregate deadline exceeded") from exc
        raise GatewayError("upstream transport failed") from exc
    finally:
        timer.cancel()
        connection.close()
        if guard_socket is not None:
            guard_socket.close()


class LoopbackModelBridge:
    def __init__(self, upstream: str, model_id: str, *, timeout: float = 30.0):
        self.upstream = _model_root(upstream)
        if (type(model_id) is not str or not model_id.strip() or len(model_id) > 128
                or model_id != model_id.strip()):
            raise ValueError("a nonempty, exact model ID is required")
        if timeout <= 0 or timeout > MAX_UPSTREAM_TIMEOUT_SECONDS:
            raise ValueError("timeout must be between 0 and 75 seconds")
        self.model_id = model_id
        self.timeout = timeout

    def ready(self) -> None:
        health = _bounded_upstream_json(self.upstream, "/health", limit=4096,
                                        timeout=min(self.timeout, 3))
        if not isinstance(health, dict) or health.get("status") not in ("ok", "ready"):
            raise GatewayError("upstream is not ready")
        inventory = _bounded_upstream_json(self.upstream, "/v1/models",
                                           limit=256 * 1024, timeout=min(self.timeout, 3))
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
        response = _bounded_upstream_json(self.upstream, "/v1/chat/completions",
                                          payload=body, limit=MAX_REPLY, timeout=self.timeout)
        try:
            choice = response["choices"][0]
            message = choice["message"]
            if type(message) is not dict or message.get("role") != "assistant":
                raise GatewayError("upstream returned a non-assistant message")
            answer = message["content"]
            if ("tool_calls" in message or "function_call" in message
                    or choice.get("finish_reason") == "tool_calls"
                    or ("model" in response and response["model"] != self.model_id)):
                raise GatewayError("upstream attempted a tool response or changed identity")
        except (KeyError, IndexError, TypeError) as exc:
            raise GatewayError("invalid upstream chat response") from exc
        if type(answer) is not str or not 0 < len(answer) <= 16000:
            raise GatewayError("invalid upstream chat text")
        finish_reason = choice.get("finish_reason")
        if finish_reason not in (None, "stop", "length", "content_filter"):
            raise GatewayError("invalid or unsupported finish reason")
        # Do not pass through upstream metadata, tools, extensions, or server hints.
        forwarded = {"index": 0, "message": {"role": "assistant", "content": answer}}
        # An absent finish reason cannot be promoted into evidence of a
        # completed reply. The downstream Vera interface reports UNKNOWN.
        if "finish_reason" in choice:
            forwarded["finish_reason"] = finish_reason
        return {"model": self.model_id, "choices": [forwarded]}


def create_server(bridge: LoopbackModelBridge, port: int = 11439, *,
                  body_deadline: float = CLIENT_BODY_DEADLINE_SECONDS) -> ThreadingHTTPServer:
    if type(port) is not int or not 0 <= port <= 65535:
        raise ValueError("invalid local listening port")
    if not 0 < body_deadline <= CLIENT_BODY_DEADLINE_SECONDS:
        raise ValueError("invalid client deadline")

    class Handler(BaseHTTPRequestHandler):
        def setup(self) -> None:
            super().setup()
            self.connection.settimeout(CLIENT_IO_TIMEOUT_SECONDS)
            self._body_deadline = time.monotonic() + body_deadline
            # Covers request-line/header parsing, before do_GET/do_POST run.
            self._read_timer = Timer(body_deadline, self._expire_connection)
            self._read_timer.daemon = True
            self._read_timer.start()

        def _expire_connection(self) -> None:
            try:
                self.connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

        def finish(self) -> None:
            self._read_timer.cancel()
            try:
                super().finish()
            except (BrokenPipeError, ConnectionResetError, OSError):
                pass  # A cancelled client cannot be given a reply.

        def _check_origin(self) -> bool:
            host = self.headers.get_all("Host", [])
            expected = f"127.0.0.1:{self.server.server_address[1]}"
            if len(host) != 1 or host[0] != expected:
                self._json(403, {"error": "invalid Host"})
                return False
            origins = self.headers.get_all("Origin", [])
            if (len(origins) > 1 or (origins and origins[0] != f"http://{expected}")
                    or self.headers.get("Sec-Fetch-Site", "same-origin")
                    not in ("same-origin", "none")):
                self._json(403, {"error": "cross-origin request forbidden"})
                return False
            return True

        def _read_body(self, size: int) -> bytes:
            chunks = []
            remaining = size
            while remaining:
                wait = self._body_deadline - time.monotonic()
                if wait <= 0:
                    raise TimeoutError("request body deadline exceeded")
                self.connection.settimeout(min(CLIENT_IO_TIMEOUT_SECONDS, wait))
                block = self.rfile.read1(min(4096, remaining))
                if not block:
                    raise ValueError("incomplete request body")
                chunks.append(block)
                remaining -= len(block)
            self._read_timer.cancel()
            return b"".join(chunks)

        def _json(self, code: int, value: dict) -> None:
            raw = json.dumps(value, ensure_ascii=False).encode("utf-8")
            try:
                self.send_response(code)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(raw)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(raw)
            except (BrokenPipeError, ConnectionResetError, OSError):
                pass  # Cancellation is best effort; never retry side effects.

        def do_GET(self) -> None:
            self._read_timer.cancel()
            if not self._check_origin():
                return
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
            if not self._check_origin():
                return
            if self.path != "/v1/chat/completions":
                self._read_timer.cancel()
                self._json(404, {"error": "unknown route"})
                return
            try:
                if self.headers.get("Transfer-Encoding"):
                    raise ValueError("transfer encoding prohibited")
                size = int(self.headers.get("Content-Length", "-1"))
                if not 0 < size <= MAX_BODY:
                    raise ValueError("invalid body length")
                body = _decode_json(self._read_body(size))
                answer = bridge.completion(body)
            except (ValueError, UnicodeError) as exc:
                self._read_timer.cancel()
                self._json(400, {"error": str(exc)})
                return
            except (GatewayError, HTTPError, URLError, TimeoutError, OSError) as exc:
                self._read_timer.cancel()
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
