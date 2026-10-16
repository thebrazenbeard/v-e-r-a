#!/usr/bin/env python3
"""Vera Mono task -> PORTAL advisory, using the real task ledger and resolver.

No scheduler, effect authorization, dispatch, or task completion is implemented.
A caller-supplied route advertisement is *not* host-attested currentness.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

MANIFEST = Path(__file__).with_name("source_bindings_v1.json")
PACKET_KEYS = frozenset({
    "purpose", "subject", "completion_state", "evidence_requirements",
    "writable_scope", "non_targets", "forbidden_shortcuts_or_effects",
    "priority_order", "unknowns", "return_shape", "relevant_surfaces",
})
ROUTE_KEYS = frozenset({
    "adapter_id", "route_id", "node_id", "target_kind", "target_id",
    "capabilities", "effect_capabilities", "authorized_effects",
    "available", "attached", "current",
})
LIST_FIELDS = ("capabilities", "effect_capabilities", "authorized_effects")


def load_json(path: Path, limit: int = 32768) -> Any:
    if not path.is_file() or path.stat().st_size > limit:
        raise ValueError("missing or oversized JSON input")
    return json.loads(path.read_text(encoding="utf-8"))


def _git(root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True,
        text=True, encoding="utf-8", errors="replace", timeout=15,
        check=False,
    )
    if proc.returncode:
        raise RuntimeError("cannot verify component source checkout")
    return proc.stdout.strip()


def source_check(root: Path, expected: str, label: str) -> None:
    if not root.is_dir() or _git(root, "rev-parse", "HEAD") != expected:
        raise RuntimeError(f"{label} is not at the exact source-bound head")
    if _git(root, "status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError(f"{label} has tracked modifications")
    # Git HEAD does not cover untracked files or ignored Python import shadows.
    # The exact source root must not admit extra executable packages, including
    # ignored ones, from any directory later added to sys.path.
    import_scopes = {"Vera Mono": ("packages",), "PORTAL": ("portal",)}
    if label not in import_scopes:
        raise RuntimeError("unrecognized component import scope")
    if _git(root, "status", "--porcelain", "--untracked-files=all",
            "--ignored=matching", "--", *import_scopes[label]):
        raise RuntimeError(f"{label} import roots contain untracked or ignored files")


def components(mono: Path, portal: Path) -> tuple[Any, ...]:
    bindings = load_json(MANIFEST)
    if bindings.get("schema") != "VERA_INTEGRATION_SOURCE_BINDINGS_V1":
        raise RuntimeError("unsupported source binding manifest")
    refs = bindings["components"]
    source_check(mono, refs["vera_mono"]["exact_head"], "Vera Mono")
    source_check(portal, refs["portal"]["exact_head"], "PORTAL")
    for path in sorted((mono / "packages").glob("*/src")):
        if path.is_dir():
            sys.path.insert(0, str(path))
    sys.path.insert(0, str(portal))
    from vera_core.task_execution import TaskExecutionLedger, TaskPacket
    from vera_core.portal_task_handoff import (
        export_portal_route_request, verify_portal_route_assessment,
    )
    from portal.vera_task_handoff import assess_vera_task_route
    from portal.route_resolver import PortalRouteAdvertisement
    return (TaskExecutionLedger, TaskPacket, export_portal_route_request,
            verify_portal_route_assessment, assess_vera_task_route,
            PortalRouteAdvertisement)


def packet_from_json(packet_type: type, path: Path) -> Any:
    data = load_json(path, 16384)
    if type(data) is not dict or set(data) != PACKET_KEYS:
        raise ValueError("task packet has missing or unknown fields")
    for key, val in data.items():
        if key in ("purpose", "subject", "completion_state"):
            if type(val) is not str:
                raise ValueError("invalid task text")
        elif type(val) is not list or any(type(x) is not str for x in val):
            raise ValueError("invalid task string array")
    record = packet_type(**{
        key: tuple(val) if isinstance(val, list) else val
        for key, val in data.items()
    })
    record.validate()
    return record


def ads_from_json(ad_type: type, file: Path | None) -> tuple[Any, ...]:
    if file is None:
        return ()
    raw = load_json(file)
    if type(raw) is not list or len(raw) > 32:
        raise ValueError("advertisements must be an array of at most 32 entries")
    result = []
    for ad in raw:
        if type(ad) is not dict or set(ad) != ROUTE_KEYS:
            raise ValueError("route advertisement has missing or unknown fields")
        for key in LIST_FIELDS:
            if type(ad[key]) is not list or any(type(x) is not str for x in ad[key]):
                raise ValueError("invalid advertised capabilities")
        for key in ("available", "attached", "current"):
            if type(ad[key]) is not bool:
                raise ValueError("invalid advertised boolean")
        result.append(ad_type(**{
            key: tuple(val) if key in LIST_FIELDS else val
            for key, val in ad.items()
        }))
    return tuple(result)


def save_receipt(path: Path, data: dict[str, Any]) -> None:
    if path.is_symlink() or path.exists() or not path.parent.is_dir():
        raise ValueError("receipt destination exists or has no parent")
    payload = (json.dumps(data, sort_keys=True, indent=2, ensure_ascii=False)
               + "\n").encode("utf-8")
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def response(task_id: str, status: str, **extra: Any) -> dict[str, Any]:
    return {
        "schema": "VERA_INTEGRATED_ROUTE_RUNTIME_V1", "task_id": task_id,
        "status": status, "executed": False, "task_closed": False,
        "effect_authority": False,
        "advertisement_currentness": "CALLER_SUPPLIED_UNATTESTED",
        **extra,
    }


def execute(args: argparse.Namespace) -> dict[str, Any]:
    (Ledger, Packet, export_request, verify_assessment, assess,
     Advertisement) = components(args.vera_mono, args.portal)
    if not args.ledger.parent.is_dir():
        raise ValueError("ledger parent directory does not exist")
    ledger = Ledger(args.ledger)
    if args.action == "open":
        if not re.fullmatch(r"[a-f0-9]{64}", args.lifecycle_digest):
            raise ValueError("lifecycle digest must be exactly 64 lowercase hex chars")
        # Never silently replace an existing durable task.
        if any(event.task_id == args.task for event in ledger.events()):
            raise ValueError("task already exists")
        packet = packet_from_json(Packet, args.packet)
        state = ledger.open_task(
            args.task, packet, lifecycle_evidence_digest=args.lifecycle_digest,
        )
        return response(args.task, "TASK_OPENED",
                        packet_digest=packet.packet_digest,
                        journal_head=state.journal_head_digest)
    if args.action == "route":
        request = export_request(
            ledger, args.task, node_id=args.node, target_kind=args.target_kind,
            target_id=args.target, required_capabilities=tuple(args.capability),
        )
        assessment = assess(request, ads_from_json(Advertisement, args.advertisements))
        verified = verify_assessment(ledger, request, assessment)
        if args.receipt is not None:
            save_receipt(args.receipt, {
                "schema": "VERA_PORTAL_ADVISORY_RECEIPT_V1",
                "request": request, "assessment": verified,
            })
        return response(args.task, verified["state"],
                        route=verified["route"], reason=verified["reason"],
                        assessment_digest=verified["assessment_digest"])
    if args.action == "verify":
        receipt = load_json(args.receipt)
        if type(receipt) is not dict or set(receipt) != {
            "schema", "request", "assessment",
        } or receipt["schema"] != "VERA_PORTAL_ADVISORY_RECEIPT_V1":
            raise ValueError("unrecognized advisory receipt")
        if type(receipt["request"]) is not dict or (
            receipt["request"].get("task_id") != args.task
        ):
            raise ValueError("receipt task mismatch")
        valid = verify_assessment(
            ledger, receipt["request"], receipt["assessment"],
        )
        return response(args.task, "ADVISORY_REVALIDATED",
                        proposal_state=valid["state"], route=valid["route"])
    raise AssertionError("unreachable")


def cli(argv: list[str] | None = None) -> dict[str, Any]:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vera-mono", required=True, type=Path)
    parser.add_argument("--portal", required=True, type=Path)
    parser.add_argument("--ledger", required=True, type=Path)
    sub = parser.add_subparsers(dest="action", required=True)
    opening = sub.add_parser("open")
    opening.add_argument("--task", required=True)
    opening.add_argument("--packet", type=Path, required=True)
    opening.add_argument("--lifecycle-digest", required=True)
    route = sub.add_parser("route")
    route.add_argument("--task", required=True)
    route.add_argument("--node", required=True)
    route.add_argument("--target-kind", required=True)
    route.add_argument("--target", required=True)
    route.add_argument("--capability", action="append", required=True)
    route.add_argument("--advertisements", type=Path)
    route.add_argument("--receipt", type=Path)
    verify = sub.add_parser("verify")
    verify.add_argument("--task", required=True)
    verify.add_argument("--receipt", type=Path, required=True)
    return execute(parser.parse_args(argv))


def main() -> None:
    try:
        print(json.dumps(cli(), sort_keys=True))
    except (OSError, ValueError, RuntimeError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "HELD", "executed": False,
                          "effect_authority": False,
                          "reason": str(exc)[:400]}), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
