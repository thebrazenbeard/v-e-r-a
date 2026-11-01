#!/usr/bin/env python3
"""Bounded, read-only verification of Vera's owner-scoped loopback V2 gateway.

Default invocation is offline dry-run. No history content, sessions, or model
generation are requested; all output is deliberately metadata-only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


MAX_RESPONSE_BYTES = 65_536
TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_-]{32,128}\Z", re.ASCII)
SESSION_PATTERN = re.compile(r"[A-Za-z0-9_-]{16,128}\Z", re.ASCII)


class ProbeFailure(Exception):
    """Failure with a fixed, non-sensitive public reason."""


class RejectRedirects(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def validate_root(value: str) -> str:
    """Require literal IPv4 loopback; reject ambiguity, external routes and URL tricks."""
    try:
        parts = urlsplit(value)
        if (
            parts.scheme != "http"
            or parts.hostname != "127.0.0.1"
            or parts.username is not None
            or parts.password is not None
            or parts.path not in ("", "/")
            or parts.query
            or parts.fragment
            or not parts.port
            or not 1 <= parts.port <= 65535
            or parts.netloc != f"127.0.0.1:{parts.port}"
        ):
            raise ValueError
    except ValueError as exc:
        raise ProbeFailure("invalid_loopback_root") from exc
    return f"http://127.0.0.1:{parts.port}"


def load_token(path: Path) -> str:
    try:
        # Bounded read: token files larger than 4 KiB are never ingested.
        with path.open("rb") as handle:
            raw = handle.read(4097)
        if len(raw) > 4096:
            raise ValueError
        token = raw.decode("ascii").strip()
        if not TOKEN_PATTERN.fullmatch(token):
            raise ValueError
        return token
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise ProbeFailure("invalid_or_missing_token_file") from exc


def fetch_json(root: str, token: str, path: str, timeout: float = 5.0) -> dict:
    # Proxy settings (including environment variables) and redirects are disabled.
    opener = build_opener(ProxyHandler({}), RejectRedirects())
    request = Request(
        root + path,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        method="GET",
    )
    try:
        with opener.open(request, timeout=timeout) as response:
            if response.status != 200:
                raise ProbeFailure("non_200_response")
            if int(response.headers.get("Content-Length", "0")) > MAX_RESPONSE_BYTES:
                raise ProbeFailure("response_too_large")
            raw = response.read(MAX_RESPONSE_BYTES + 1)
        if len(raw) > MAX_RESPONSE_BYTES:
            raise ProbeFailure("response_too_large")
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ProbeFailure("invalid_response_json")
        return value
    except HTTPError as exc:
        if exc.code in (301, 302, 303, 307, 308):
            raise ProbeFailure("redirect_refused") from exc
        if exc.code in (401, 403):
            raise ProbeFailure("unauthorized") from exc
        raise ProbeFailure("http_request_failed") from exc
    except (URLError, TimeoutError, ConnectionError, OSError) as exc:
        raise ProbeFailure("gateway_unavailable") from exc
    except (ValueError, UnicodeError, json.JSONDecodeError) as exc:
        raise ProbeFailure("invalid_response_json") from exc


def verify_models(value: dict) -> int:
    if value.get("node") != "local" or value.get("mode") != "response_only":
        raise ProbeFailure("wrong_gateway_authority")
    models = value.get("models")
    if not isinstance(models, list) or len(models) > 32:
        raise ProbeFailure("invalid_model_inventory")
    if any(not isinstance(name, str) or not 0 < len(name) <= 128 for name in models):
        raise ProbeFailure("invalid_model_inventory")
    return len(models)


def verify_sessions(value: dict) -> int:
    sessions = value.get("sessions")
    if not isinstance(sessions, list) or len(sessions) > 50:
        raise ProbeFailure("invalid_session_inventory")
    if any(not isinstance(sid, str) or not SESSION_PATTERN.fullmatch(sid) for sid in sessions):
        raise ProbeFailure("invalid_session_inventory")
    return len(sessions)


def probe(root: str, token_path: Path, timeout: float = 5.0) -> dict:
    validated_root = validate_root(root)
    token = load_token(token_path)
    # No history endpoint or mutating POST is used.
    models = verify_models(fetch_json(validated_root, token, "/v2/models", timeout))
    sessions = verify_sessions(fetch_json(validated_root, token, "/v2/sessions", timeout))
    return {"status": "passed", "v2_contract": "read_only", "models_count": models,
            "sessions_count": sessions, "generation_attempted": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default="http://127.0.0.1:18781")
    parser.add_argument("--token-file", type=Path)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--probe", action="store_true",
                        help="Opt in to two authenticated, read-only loopback GET requests")
    args = parser.parse_args(argv)
    try:
        validate_root(args.root)
        if not args.probe:
            result = {"status": "dry_run", "network_attempted": False,
                      "token_file_read": False, "generation_attempted": False}
        else:
            if args.token_file is None:
                raise ProbeFailure("token_file_required")
            if not 0.1 <= args.timeout <= 30:
                raise ProbeFailure("invalid_timeout")
            result = probe(args.root, args.token_file, args.timeout)
        exit_status = 0
    except ProbeFailure as exc:
        result = {"status": "failed", "reason": str(exc),
                  "generation_attempted": False}
        exit_status = 1
    print(json.dumps(result, sort_keys=True))
    return exit_status


if __name__ == "__main__":
    sys.exit(main())
