from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
from typing import Sequence

from .critic import CRITIC_PROMPT
from .models import ReviewRequest
from .policy import PrinciplePack
from .receipts import JsonlReceiptLedger, canonical_digest
from .render import render_blockquote
from .reviewer import Cricket
from .simulator import run_reference_simulation
from .upstreams import UPSTREAM_CONTRACTS, UpstreamStatus, evaluate_upstreams


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cricket")
    sub = parser.add_subparsers(dest="command", required=True)

    review = sub.add_parser("review", help="review a JSON request")
    review.add_argument("request", help="path to request JSON or '-' for stdin")
    review.add_argument("--json", action="store_true", help="emit structured JSON")
    review.add_argument("--speak-on-pass", action="store_true")
    review.add_argument("--principle-pack", help="path to a versioned principle-pack JSON file")
    review.add_argument("--receipt-ledger", help="append a tamper-evident review receipt to this JSONL ledger")

    verify = sub.add_parser("verify-ledger", help="verify a Cricket JSONL receipt ledger")
    verify.add_argument("ledger")

    simulate = sub.add_parser("simulate", help="run Cricket's self-contained reference host simulation")
    simulate.add_argument("--state-dir", default=".cricket-sim", help="directory for simulation receipts")
    simulate.add_argument("--json", action="store_true", help="emit structured JSON")

    upstreams = sub.add_parser("upstreams", help="inspect Cricket's pinned upstream compatibility contracts")
    upstreams.add_argument("--observed", help="JSON mapping of repository name to observed commit")
    upstreams.add_argument("--json", action="store_true", help="emit structured JSON")

    sub.add_parser("prompt", help="print the semantic critic prompt contract")
    return parser


def _load_request(path: str) -> ReviewRequest:
    if path == "-":
        raw = json.load(sys.stdin)
    else:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return ReviewRequest.from_dict(raw)


def _exit_code(disposition: str) -> int:
    return 2 if disposition == "BLOCK" else 1 if disposition == "CHALLENGE" else 0


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "prompt":
        print(CRITIC_PROMPT)
        return 0

    if args.command == "verify-ledger":
        valid = JsonlReceiptLedger(args.ledger).verify()
        print(json.dumps({"valid": valid}, sort_keys=True))
        return 0 if valid else 2

    if args.command == "simulate":
        report = run_reference_simulation(args.state_dir)
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print("Cricket reference simulation")
            print(f"ledger_valid={report['ledger_valid']} receipt_count={report['receipt_count']}")
            for name, scenario in report["scenarios"].items():
                print(
                    f"{name}: initial={scenario['initial']} "
                    f"final={scenario['final']} "
                    f"revision_attempted={scenario['revision_attempted']}"
                )
        return 0 if report["ledger_valid"] else 2

    if args.command == "upstreams":
        observed = {}
        if args.observed:
            raw = json.loads(Path(args.observed).read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raise ValueError("observed upstream file must contain a JSON object")
            observed = raw
        report = evaluate_upstreams(observed)
        if args.json:
            print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
        else:
            print(f"Cricket upstream status: {report.status.value}")
            for item in report.results:
                observed_text = item.observed_commit or "unobserved"
                print(
                    f"{item.status.value}: {item.repository} "
                    f"pinned={item.pinned_commit} observed={observed_text} "
                    f"relationship={item.relationship}"
                )
        if report.status is UpstreamStatus.MOVED:
            return 2
        if report.status is UpstreamStatus.UNKNOWN:
            return 1
        return 0

    request = _load_request(args.request)
    if args.principle_pack:
        request = PrinciplePack.load(args.principle_pack).apply(request)

    result = Cricket().review(request)

    if args.receipt_ledger:
        pack = request.metadata.get("principle_pack")
        JsonlReceiptLedger(args.receipt_ledger).append(
            {
                "request_digest": canonical_digest(asdict(request)),
                "disposition": result.disposition.value,
                "finding_ids": [finding.rule_id for finding in result.findings],
                "principle_pack": pack,
            }
        )

    if args.json:
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    else:
        rendered = render_blockquote(result, speak_on_pass=args.speak_on_pass)
        if rendered:
            print(rendered)

    return _exit_code(result.disposition.value)


if __name__ == "__main__":
    raise SystemExit(main())
