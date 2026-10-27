"""Bounded, loopback-only model chat gateway for the Vera interface.

This deliberately has no Portal, Pre-Active, Empathy, filesystem tool, or
remote-node capability. Those require authenticated adapters and receipts.
"""

from __future__ import annotations

import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
from threading import BoundedSemaphore
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


STATIC = Path(__file__).with_name("static")
MAX_REQUEST = 24 * 1024
MAX_MODEL_BYTES = 1024 * 1024
MAX_MODELS_BYTES = 256 * 1024
CHAT_TIMEOUT_SECONDS = 90
MODELS_TIMEOUT_SECONDS = 6
_ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
}


class GatewayError(Exception):
    """A model service or protocol response was unsuitable for display."""


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise GatewayError("model endpoint redirect refused")


# Never send private chat prompts through environment-configured HTTP proxies.
_LOCAL_OPENER = build_opener(ProxyHandler({}), _NoRedirect())


def _reject_duplicate_keys(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("duplicate JSON key")
        obj[key] = value
    return obj


def _decode_json(raw):
    return json.loads(raw.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON")))


def _model_root(url: str) -> str:
    """No caller-controlled scheme, hostname, path or remote proxy targets."""
    parsed = urlsplit(url)
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("invalid local model port") from exc
    if (parsed.scheme != "http" or parsed.hostname != "127.0.0.1"
            or parsed.username or parsed.password or parsed.path not in ("", "/")
            or parsed.query or parsed.fragment or port is None):
        raise ValueError("model endpoint must be explicit local HTTP loopback")
    return f"http://127.0.0.1:{port}"


def _read_json_from_model(url: str, *, payload: dict | None = None,
                          limit: int, timeout: int) -> object:
    raw_body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = Request(url, data=raw_body, headers={"Content-Type": "application/json"}
                  if raw_body is not None else {}, method="POST" if raw_body else "GET")
    with _LOCAL_OPENER.open(req, timeout=timeout) as response:
        raw = response.read(limit + 1)
    if len(raw) > limit:
        raise GatewayError("model response exceeded limit")
    try:
        return _decode_json(raw)
    except (ValueError, UnicodeError) as exc:
        raise GatewayError("model returned malformed JSON") from exc


def _models(model_root: str) -> list[str]:
    payload = _read_json_from_model(model_root + "/api/tags", limit=MAX_MODELS_BYTES,
                                    timeout=MODELS_TIMEOUT_SECONDS)
    if not isinstance(payload, dict) or not isinstance(payload.get("models"), list):
        raise GatewayError("model inventory format not recognized")
    names = []
    for row in payload["models"][:128]:
        if isinstance(row, dict) and type(row.get("name")) is str:
            name = row["name"]
            if 0 < len(name) <= 128 and name not in names:
                names.append(name)
    return names


def _valid_chat(payload: object) -> tuple[str, list[dict[str, str]]]:
    if type(payload) is not dict or set(payload) != {"model", "messages"}:
        raise ValueError("only model and messages are accepted")
    model, entries = payload["model"], payload["messages"]
    if type(model) is not str or not 0 < len(model) <= 128:
        raise ValueError("invalid model")
    try:
        model.encode("utf-8")
    except UnicodeError as exc:
        raise ValueError("invalid model encoding") from exc
    if type(entries) is not list or not 1 <= len(entries) <= 12:
        raise ValueError("invalid message count")
    messages = []
    total = 0
    for item in entries:
        if (type(item) is not dict or set(item) != {"role", "content"}
                or item.get("role") not in ("user", "assistant")
                or type(item.get("content")) is not str
                or not 0 < len(item["content"]) <= 4000):
            raise ValueError("only bounded user and assistant text is permitted")
        total += len(item["content"])
        try:
            item["content"].encode("utf-8")
        except UnicodeError as exc:
            raise ValueError("invalid message encoding") from exc
        messages.append({"role": item["role"], "content": item["content"]})
    if messages[-1]["role"] != "user" or total > 16000:
        raise ValueError("conversation must end with a bounded user message")
    return model, messages


def _chat(model_root: str, model: str, messages: list[dict[str, str]]) -> str:
    request = {
        "model": model,
        "stream": False,
        "messages": [{"role": "system", "content": (
            "You are responding through Vera's local model interface. "
            "This session grants no tools, durable memory, identity attestation, "
            "or external effects. Be accurate about limits and never claim "
            "to have executed changes from chat text."
        )}, *messages],
    }
    payload = _read_json_from_model(model_root + "/v1/chat/completions",
                                    payload=request, limit=MAX_MODEL_BYTES,
                                    timeout=CHAT_TIMEOUT_SECONDS)
    try:
        choice = payload["choices"][0]
        msg = choice["message"]
        if ("tool_calls" in msg or "function_call" in msg
                or choice.get("finish_reason") == "tool_calls"):
            raise GatewayError("model attempted a tool response")
        answer = msg["content"]
    except (TypeError, KeyError, IndexError) as exc:
        raise GatewayError("invalid model response") from exc
    if type(answer) is not str or len(answer) > 16000:
        raise GatewayError("invalid model text")
    try:
        answer.encode("utf-8")
    except UnicodeError as exc:
        raise GatewayError("invalid model text encoding") from exc
    return answer


def make_server(*, port: int = 8765, ollama_url: str = "http://127.0.0.1:11434") -> ThreadingHTTPServer:
    """Create the restricted server without launching services or models."""
    if type(port) is not int or not 0 <= port <= 65535:
        raise ValueError("invalid interface port")
    model_root = _model_root(ollama_url)

    class Handler(BaseHTTPRequestHandler):
        server_version = "VeraLocalInterface/1"

        def log_message(self, *_args):
            # Never accidentally log prompts or session tokens.
            pass

        def _host_ok(self) -> bool:
            return self.headers.get("Host") == f"127.0.0.1:{self.server.server_port}"

        def _session_ok(self) -> bool:
            return (self.headers.get("Sec-Fetch-Site", "same-origin") == "same-origin"
                    and hmac.compare_digest(self.headers.get("X-Vera-Session", ""),
                                            self.server.session_token))

        def _headers(self, code, content_type, size):
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(size))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", (
                "default-src 'none'; script-src 'self'; style-src 'self'; "
                "connect-src 'self'; img-src 'self' data:; base-uri 'none'; "
                "frame-ancestors 'none'; form-action 'none'"
            ))
            self.end_headers()

        def _send(self, code: int, payload: dict):
            raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self._headers(code, "application/json; charset=utf-8", len(raw))
            self.wfile.write(raw)

        def _reject(self, code: int, message: str):
            self._send(code, {"error": message})

        def do_GET(self):
            if not self._host_ok():
                return self._reject(403, "invalid local host")
            path = urlsplit(self.path)
            if path.query or path.fragment:
                return self._reject(404, "not found")
            if path.path in _ASSETS:
                filename, mime = _ASSETS[path.path]
                raw = (STATIC / filename).read_bytes()
                self._headers(200, mime, len(raw))
                self.wfile.write(raw)
            elif path.path == "/api/session":
                self._send(200, {"token": self.server.session_token, "mode": "response_only"})
            elif path.path == "/api/models":
                if not self._session_ok():
                    return self._reject(403, "local session rejected")
                try:
                    self._send(200, {"models": _models(self.server.model_root), "node": "local"})
                except (OSError, URLError, HTTPError, GatewayError):
                    self._send(503, {"models": [], "error": "local model endpoint unavailable"})
            elif path.path == "/api/status":
                if not self._session_ok():
                    return self._reject(403, "local session rejected")
                self._send(200, {
                    "interface": "online", "model_node": "local",
                    "portal": "not_connected", "pre_active": "not_connected",
                    "empathy": "not_connected", "authority": "response_only",
                })
            else:
                self._reject(404, "not found")

        def do_POST(self):
            if not self._host_ok():
                return self._reject(403, "invalid local host")
            if self.path != "/api/chat":
                return self._reject(404, "not found")
            expected_origin = f"http://127.0.0.1:{self.server.server_port}"
            if (self.headers.get("Origin") != expected_origin
                    or not self._session_ok()):
                return self._reject(403, "local session rejected")
            if self.headers.get("Content-Type", "").split(";", 1)[0].strip() != "application/json":
                return self._reject(415, "JSON required")
            try:
                length = int(self.headers.get("Content-Length", ""))
            except ValueError:
                return self._reject(411, "request length required")
            if length <= 0 or length > MAX_REQUEST or self.headers.get("Transfer-Encoding"):
                return self._reject(413, "request exceeds limit")
            try:
                model, messages = _valid_chat(_decode_json(self.rfile.read(length)))
            except (UnicodeError, ValueError):
                return self._reject(400, "invalid chat request")
            if not self.server.model_slots.acquire(blocking=False):
                return self._reject(429, "model worker busy")
            try:
                if model not in _models(self.server.model_root):
                    return self._reject(400, "model not installed locally")
                reply = _chat(self.server.model_root, model, messages)
                self._send(200, {"reply": reply, "model": model,
                                 "node": "local", "mode": "response_only"})
            except (OSError, URLError, HTTPError, GatewayError, ValueError):
                self._reject(503, "local model inference unavailable")
            finally:
                self.server.model_slots.release()

        def do_OPTIONS(self):
            self._reject(403, "cross-origin interface access disabled")

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.daemon_threads = True
    server.session_token = secrets.token_urlsafe(32)
    server.model_root = model_root
    server.model_slots = BoundedSemaphore(1)
    return server
