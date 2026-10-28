"""Launch Vera's intentionally local-only interface."""

from __future__ import annotations

import argparse
import sys
from .server import make_server
from .vault_acl import require_private_regular_file


def main():
    parser = argparse.ArgumentParser(description="Vera local response-only interface")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    parser.add_argument("--memory-db", help="Optional local SQLite file; disabled if omitted")
    parser.add_argument("--memory-secret-file", help="Private operator-controlled vault bearer secret")
    parser.add_argument("--memory-rollback-anchor",
                        help="Optional separate owner-private, non-backed-up revision witness; "
                             "DB-only rollback fails closed; whole-host rollback remains possible")
    parser.add_argument("--acknowledge-plaintext-vault-risk", action="store_true",
                        help="Deprecated compatibility flag; does not relax encryption or access checks")
    args = parser.parse_args()
    if bool(args.memory_db) != bool(args.memory_secret_file):
        parser.error("--memory-db and --memory-secret-file must be supplied together")
    if args.memory_rollback_anchor and not args.memory_db:
        parser.error("--memory-rollback-anchor requires --memory-db and --memory-secret-file")
    secret = None
    if args.memory_secret_file:
        try:
            target = require_private_regular_file(args.memory_secret_file,
                                                  label="vault secret file")
            if not 0 < target.stat().st_size <= 512:
                raise ValueError("vault secret file must contain 1..512 bytes")
            secret = target.read_text(encoding="ascii").rstrip("\r\n")
        except (OSError, UnicodeError, ValueError) as exc:
            parser.error(f"invalid vault secret file: {type(exc).__name__}")
    try:
        server = make_server(port=args.port, ollama_url=args.ollama_url,
                             memory_db_path=args.memory_db, memory_secret=secret,
                             memory_rollback_anchor_path=args.memory_rollback_anchor,
                             acknowledge_plaintext_vault_risk=args.acknowledge_plaintext_vault_risk)
    except (OSError, ValueError) as exc:
        parser.error(f"interface config refused: {exc}")
    if args.memory_db:
        print("Transcript vault: AES-256-GCM encrypted at rest with private-file ACL checks; "
              "SQLite deletion is NOT forensic erasure; backups and historical filesystem "
              "images may persist. Authenticated local identity remains application-scoped.",
              file=sys.stderr, flush=True)
        if args.memory_rollback_anchor:
            print("External rollback witness active: DB-only rollback is refused; "
                  "whole-host backup rollback and forensic remnants remain possible. "
                  "A crash between witness and DB commit can require manual recovery.",
                  file=sys.stderr, flush=True)
    print(f"Vera interface: http://127.0.0.1:{server.server_port}/ (local only)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
