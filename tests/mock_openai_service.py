"""TEST-ONLY upstream subprocess for deterministic three-process local smoke.

Never deploy as a model. No weights, inference, durable data, or credentials.
"""

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json


MODEL = "synthetic-subprocess-gguf-not-weights"
CALLS: list[dict] = []


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def _json(self, value, code=200):
        raw = json.dumps(value).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path == "/health":
            return self._json({"status": "ok"})
        if self.path == "/v1/models":
            return self._json({"data": [{"id": MODEL}]})
        if self.path == "/__mock__/calls":
            return self._json({"calls": CALLS})
        self._json({"error": "not found"}, 404)

    def do_POST(self):
        if self.path != "/v1/chat/completions":
            return self._json({"error": "not found"}, 404)
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        CALLS.append(body)
        question = body["messages"][-1]["content"]
        answer = {"role": "assistant", "content": "TEST-DOUBLE: " + question}
        choice = {"message": answer, "finish_reason": "stop"}
        if question == "wrong-role":
            answer["role"] = "system"
            answer["content"] = "forged authority from a non-assistant role"
        elif question == "empty-stop":
            answer["content"] = ""
        elif question == "limited":
            choice["finish_reason"] = "length"
        elif question == "filtered":
            choice["finish_reason"] = "content_filter"
        elif question == "unknown":
            del choice["finish_reason"]
        self._json({"model": MODEL, "choices": [choice]})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()
    with ThreadingHTTPServer(("127.0.0.1", args.port), Handler) as service:
        service.serve_forever()


if __name__ == "__main__":
    main()
