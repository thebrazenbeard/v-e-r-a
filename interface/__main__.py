"""Launch Vera's intentionally local-only interface."""

from __future__ import annotations

import argparse
from .server import make_server


def main():
    parser = argparse.ArgumentParser(description="Vera local response-only interface")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    args = parser.parse_args()
    server = make_server(port=args.port, ollama_url=args.ollama_url)
    print(f"Vera interface: http://127.0.0.1:{server.server_port}/ (local only)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
