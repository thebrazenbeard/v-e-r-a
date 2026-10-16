"""Redworm local operator commands. No implicit admission, succession or deployment."""
import argparse
import json
import sys
from pathlib import Path
from .core import Store, GuardrailError, IntegrityError

def main(argv=None):
    parser = argparse.ArgumentParser(prog="redworm")
    commands = parser.add_subparsers(dest="command", required=True)
    for cmd in ("init", "list", "project", "timeline", "verify"):
        commands.add_parser(cmd).add_argument("db")
    ingest = commands.add_parser("ingest")
    ingest.add_argument("db")
    ingest.add_argument("file")
    admit = commands.add_parser("admit")
    admit.add_argument("db")
    admit.add_argument("event_id")
    relate = commands.add_parser("relate")
    relate.add_argument("db")
    relate.add_argument("kind", choices=["CORRECTS", "SUPERSEDES"])
    relate.add_argument("before")
    relate.add_argument("after")
    conflict = commands.add_parser("conflict")
    conflict.add_argument("db")
    conflict.add_argument("first")
    conflict.add_argument("second")
    resolve = commands.add_parser("resolve")
    resolve.add_argument("db")
    resolve.add_argument("first")
    resolve.add_argument("second")
    resolve.add_argument("winner")
    prepare = commands.add_parser("prepare")
    prepare.add_argument("db")
    prepare.add_argument("episode")
    prepare.add_argument("ids", nargs="+")
    coverage = commands.add_parser("coverage")
    coverage.add_argument("db")
    coverage.add_argument("episode")
    coverage.add_argument("status", choices=["OBSERVED", "PARTIAL", "UNKNOWN", "MISSING"])
    coverage.add_argument("note")
    for sub in (admit, relate, resolve):
        sub.add_argument("--approval-ref", required=True)
        sub.add_argument("--readback-ref", required=True)
    admit.add_argument("--actor", required=True)
    args = parser.parse_args(argv)
    try:
        with Store(args.db) as s:
            cmd = args.command
            if cmd == "init":
                output = {"initialized": args.db}
            elif cmd == "ingest":
                eid, created = s.ingest(json.loads(Path(args.file).read_text(encoding="utf-8")))
                output = {"event_id": eid, "created": created, "admitted": False}
            elif cmd == "list":
                output = s.list()
            elif cmd == "project":
                output = s.project()
            elif cmd == "timeline":
                output = s.timeline()
            elif cmd == "verify":
                output = s.verify()
            elif cmd == "admit":
                output = {"recorded": s.admit(args.event_id, args.approval_ref, args.readback_ref, args.actor),
                          "authority_verified": False}
            elif cmd == "relate":
                output = {"recorded": s.relate(args.before, args.after, args.kind,
                                               args.approval_ref, args.readback_ref)}
            elif cmd == "conflict":
                s.conflict(args.first, args.second)
                output = {"conflict": "OPEN"}
            elif cmd == "resolve":
                output = {"resolved": s.resolve(args.first, args.second, args.winner,
                                                 args.approval_ref, args.readback_ref)}
            elif cmd == "prepare":
                output = {"handoff_id": s.prepare(args.episode, args.ids), "accepted": False}
            else:
                s.coverage(args.episode, args.status, args.note)
                output = {"episode": args.episode, "coverage": args.status}
            print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (GuardrailError, IntegrityError, OSError, json.JSONDecodeError) as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
