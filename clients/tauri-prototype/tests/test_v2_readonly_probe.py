"""Hermetic synthetic contract tests. No sockets or real credentials."""

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import ProxyHandler


SOURCE = Path(__file__).with_name("v2_readonly_probe.py")
SPEC = importlib.util.spec_from_file_location("vera_v2_probe", SOURCE)
probe_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe_module)

SYNTHETIC_TOKEN = "synthetic_qualified_owner_token_001"
SYNTHETIC_SESSION = "syntheticsession01"
ROOT = "http://127.0.0.1:18781"


class FakeResponse:
    def __init__(self, code, body):
        self.status = code
        self.body = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")
        self.headers = {"Content-Length": str(len(self.body))}

    def read(self, limit):
        return self.body[:limit]

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        pass


class FakeOpener:
    def __init__(self, responses=None):
        self.requests = []
        self.responses = responses if responses is not None else {
            "/v2/models": (200, {"node": "local", "mode": "response_only", "models": ["fake-model"]}),
            "/v2/sessions": (200, {"sessions": [SYNTHETIC_SESSION]}),
        }

    def open(self, request, timeout):
        self.requests.append((request.get_method(), request.full_url,
                              request.get_header("Authorization"), timeout))
        assert request.get_method() == "GET", "mutating request attempted"
        assert request.full_url.startswith(ROOT + "/v2/"), "unexpected authority"
        code, body = self.responses.get(request.full_url.removeprefix(ROOT), (404, {}))
        if code != 200:
            raise HTTPError(request.full_url, code, "synthetic error", {}, None)
        return FakeResponse(code, body)


class V2ReadonlyProbeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="vera-v2-synthetic-")
        self.addCleanup(self.temp.cleanup)
        self.token_file = Path(self.temp.name) / "synthetic-token.txt"
        self.token_file.write_text(SYNTHETIC_TOKEN, encoding="ascii")
        self.opener = FakeOpener()

    def run_cli(self, *arguments, opener=None):
        output = io.StringIO()
        fake = opener or self.opener
        # Assert production request factory disables proxies and redirects.
        def factory(*handlers):
            self.assertTrue(any(isinstance(h, ProxyHandler) and h.proxies == {}
                                for h in handlers))
            self.assertTrue(any(isinstance(h, probe_module.RejectRedirects)
                                for h in handlers))
            return fake
        with patch.object(probe_module, "build_opener", side_effect=factory):
            with contextlib.redirect_stdout(output):
                code = probe_module.main(list(arguments))
        return code, json.loads(output.getvalue()), output.getvalue()

    def test_dry_run_never_reads_nonexistent_token_or_accesses_gateway(self):
        code, result, _ = self.run_cli("--token-file", str(self.token_file.with_name("not-present")))
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "dry_run")
        self.assertFalse(result["network_attempted"])
        self.assertFalse(result["token_file_read"])
        self.assertEqual(self.opener.requests, [])

    def test_valid_synthetic_probe_is_read_only(self):
        code, result, _ = self.run_cli("--probe", "--root", ROOT,
                                       "--token-file", str(self.token_file))
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["models_count"], 1)
        self.assertEqual(result["sessions_count"], 1)
        self.assertFalse(result["generation_attempted"])
        self.assertEqual([(method, url) for method, url, _, _ in self.opener.requests],
                         [("GET", ROOT + "/v2/models"), ("GET", ROOT + "/v2/sessions")])
        self.assertTrue(all(auth == f"Bearer {SYNTHETIC_TOKEN}"
                            for _, _, auth, _ in self.opener.requests))

    def test_output_contains_neither_credentials_nor_inventory(self):
        code, _, output = self.run_cli("--probe", "--root", ROOT,
                                       "--token-file", str(self.token_file))
        self.assertEqual(code, 0)
        for forbidden in (SYNTHETIC_TOKEN, SYNTHETIC_SESSION, "fake-model", self.temp.name):
            self.assertNotIn(forbidden, output)

    def test_external_and_ambiguous_roots_are_rejected(self):
        rejected = ("https://127.0.0.1:18781", "http://localhost:18781",
                    "http://127.0.0.1:18781/a", "http://127.0.0.1:18781?x=1",
                    "http://user@127.0.0.1:18781", "http://127.0.0.1:18781@evil:80",
                    "http://127.0.0.2:18781", "http://127.0.0.1:18781#frag")
        for root in rejected:
            with self.subTest(root=root):
                code, result, _ = self.run_cli("--root", root)
                self.assertEqual(code, 1)
                self.assertEqual(result["reason"], "invalid_loopback_root")

    def test_missing_token_produces_only_fixed_failure(self):
        code, result, _ = self.run_cli("--probe", "--token-file", "missing-file")
        self.assertEqual(code, 1)
        self.assertEqual(result["reason"], "invalid_or_missing_token_file")

    def test_bad_token_format_is_rejected_before_network(self):
        self.token_file.write_text("bad\n", encoding="ascii")
        code, result, _ = self.run_cli("--probe", "--root", ROOT,
                                       "--token-file", str(self.token_file))
        self.assertEqual(self.opener.requests, [])
        self.assertEqual(code, 1)
        self.assertEqual(result["reason"], "invalid_or_missing_token_file")

    def test_owner_authority_mismatch_fails_closed(self):
        fake = FakeOpener({"/v2/models": (200, {"node": "remote", "mode": "response_only", "models": []})})
        code, result, _ = self.run_cli("--probe", "--root", ROOT,
                                       "--token-file", str(self.token_file), opener=fake)
        self.assertEqual(code, 1)
        self.assertEqual(result["reason"], "wrong_gateway_authority")

    def test_auth_rejection_fails_closed(self):
        fake = FakeOpener({"/v2/models": (403, {})})
        code, result, _ = self.run_cli("--probe", "--root", ROOT,
                                       "--token-file", str(self.token_file), opener=fake)
        self.assertEqual(code, 1)
        self.assertEqual(result["reason"], "unauthorized")

    def test_redirect_is_never_followed(self):
        fake = FakeOpener({"/v2/models": (302, {})})
        code, result, _ = self.run_cli("--probe", "--root", ROOT,
                                       "--token-file", str(self.token_file), opener=fake)
        self.assertEqual(code, 1)
        self.assertEqual(result["reason"], "redirect_refused")
        self.assertEqual(len(fake.requests), 1)

    def test_malformed_json_is_rejected(self):
        fake = FakeOpener({"/v2/models": (200, b"{" * 100)})
        code, result, _ = self.run_cli("--probe", "--root", ROOT,
                                       "--token-file", str(self.token_file), opener=fake)
        self.assertEqual(code, 1)
        self.assertEqual(result["reason"], "invalid_response_json")

    def test_oversized_response_is_rejected(self):
        fake = FakeOpener({"/v2/models": (200, b"x" * 65_537)})
        code, result, _ = self.run_cli("--probe", "--root", ROOT,
                                       "--token-file", str(self.token_file), opener=fake)
        self.assertEqual(code, 1)
        self.assertEqual(result["reason"], "response_too_large")

    def test_invalid_session_inventory_is_rejected(self):
        fake = FakeOpener({
            "/v2/models": (200, {"node": "local", "mode": "response_only", "models": []}),
            "/v2/sessions": (200, {"sessions": ["../../secret-session"]}),
        })
        code, result, _ = self.run_cli("--probe", "--root", ROOT,
                                       "--token-file", str(self.token_file), opener=fake)
        self.assertEqual(code, 1)
        self.assertEqual(result["reason"], "invalid_session_inventory")

    def test_missing_opt_in_token_path_fails_without_network(self):
        code, result, _ = self.run_cli("--probe")
        self.assertEqual(code, 1)
        self.assertEqual(result["reason"], "token_file_required")
        self.assertEqual(self.opener.requests, [])


if __name__ == "__main__":
    unittest.main()
