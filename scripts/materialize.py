#!/usr/bin/env python3
"""Materialize pinned V-E-R-A component branches as separate Git worktrees.

The branch snapshot is NOT the canonical source repository. No network call or
protected action occurs in 'list' or 'verify' commands; 'materialize' performs
explicit Git fetch/checkout after ensuring remote branch equals the registry pin.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

SCHEMA = "VERA_COMPONENT_BRANCH_REGISTRY_V1"
_HEX = re.compile(r"^[0-9a-f]{40}$")
_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9-]{0,80}$")


class SnapshotError(RuntimeError):
    pass


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=120, check=False,
    )
    if result.returncode:
        raise SnapshotError(f"Git operation failed: {args[0]} ({result.stderr.strip()[-300:]})")
    return result.stdout.strip()


def read_registry(path: Path) -> list[dict[str, Any]]:
    if not path.is_file() or path.stat().st_size > 200_000:
        raise SnapshotError("Component registry missing or oversized")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if type(raw) is not dict or raw.get("schema") != SCHEMA or type(raw.get("components")) is not list:
        raise SnapshotError("Unexpected registry schema")
    if set(raw) != {"schema", "mirror_repository", "mirror_default_branch", "components"}:
        raise SnapshotError("Unexpected registry fields")
    if raw["mirror_repository"] != "thebrazenbeard/v-e-r-a" or raw["mirror_default_branch"] != "main":
        raise SnapshotError("Wrong mirror repository")
    seen = set()
    for item in raw["components"]:
        if type(item) is not dict or set(item) != {"name", "upstream", "upstream_branch", "state", "mirror_commit", "reason"}:
            raise SnapshotError("Invalid component shape")
        name, sha = item["name"], item["mirror_commit"]
        if type(name) is not str or not _NAME.fullmatch(name) or name in seen:
            raise SnapshotError("Invalid or duplicate component name")
        seen.add(name)
        if item["upstream"] != "thebrazenbeard/" + name or item["upstream_branch"] != "main":
            raise SnapshotError("Incorrect upstream source identity")
        if item["state"] == "MIRRORED":
            if type(sha) is not str or not _HEX.fullmatch(sha) or item["reason"] is not None:
                raise SnapshotError("Invalid pinned mirrored commit")
        elif item["state"] == "HELD":
            if sha is not None or type(item["reason"]) is not str or not item["reason"]:
                raise SnapshotError("Held component must explain absent snapshot")
        else:
            raise SnapshotError("Invalid component state")
    return raw["components"]


def select(components: list[dict[str, Any]], selected: list[str]) -> list[dict[str, Any]]:
    by_name = {row["name"]: row for row in components}
    if selected and len(selected) != len(set(selected)):
        raise SnapshotError("Duplicate --only selection")
    names = selected or [row["name"] for row in components if row["state"] == "MIRRORED"]
    result = []
    for name in names:
        if name not in by_name:
            raise SnapshotError(f"Unknown component: {name}")
        row = by_name[name]
        if row["state"] != "MIRRORED":
            raise SnapshotError(f"Component is held; no public snapshot available: {name}")
        result.append(row)
    return result


def origin_head(repo: Path, name: str) -> str:
    output = git(repo, "ls-remote", "--heads", "origin", f"refs/heads/{name}")
    if not output:
        raise SnapshotError(f"Mirrored branch is missing on origin: {name}")
    token = output.split()[0]
    if not _HEX.fullmatch(token):
        raise SnapshotError(f"Invalid origin branch SHA: {name}")
    return token


def check_origin(repo: Path, component: dict[str, Any]) -> None:
    if origin_head(repo, component["name"]) != component["mirror_commit"]:
        raise SnapshotError(f"Mirrored branch moved since registry pin: {component['name']}")


def materialize_one(repo: Path, destination: Path, component: dict[str, Any]) -> dict[str, str]:
    name = component["name"]
    target = destination / name
    # No overwrites, even for existing empty directories or symlink targets.
    if target.exists() or target.is_symlink():
        raise SnapshotError(f"Destination already exists; not replacing: {target}")
    check_origin(repo, component)
    # Use the origin branch, never the moving upstream main. Explicit pin verified again after fetch.
    git(repo, "fetch", "--no-tags", "origin", f"refs/heads/{name}")
    commit = git(repo, "rev-parse", "FETCH_HEAD")
    if commit != component["mirror_commit"] or origin_head(repo, name) != commit:
        raise SnapshotError(f"Mirror changed during fetch: {name}")
    git(repo, "worktree", "add", "--detach", str(target), commit)
    if git(target, "rev-parse", "HEAD") != commit or git(target, "status", "--porcelain"):
        raise SnapshotError(f"Materialized worktree is not exact and clean: {name}")
    return {"component": name, "path": str(target), "snapshot_commit": commit}


def verify_one(destination: Path, component: dict[str, Any]) -> dict[str, str]:
    target = destination / component["name"]
    if not target.is_dir() or target.is_symlink() or not (target / ".git").exists():
        raise SnapshotError(f"Not a materialized worktree: {component['name']}")
    if git(target, "rev-parse", "HEAD") != component["mirror_commit"]:
        raise SnapshotError(f"Worktree commit drift: {component['name']}")
    if git(target, "status", "--porcelain"):
        raise SnapshotError(f"Worktree has changes: {component['name']}")
    return {"component": component["name"], "status": "VERIFIED_EXACT"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("list", "materialize", "verify", "check-origin"))
    parser.add_argument("--only", action="append", default=[], metavar="NAME", help="Repeat for selected components")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--destination", type=Path, default=None)
    args = parser.parse_args(argv)
    try:
        repo = args.root.resolve(strict=True)
        registry = read_registry(repo / "components.json")
        held = [x for x in registry if x["state"] == "HELD"]
        if args.command == "list":
            print(json.dumps({"mirrored": len(registry) - len(held), "held": len(held), "components": registry}, indent=2))
            return 0
        selected = select(registry, args.only)
        destination = (args.destination if args.destination is not None else repo / "components").absolute()
        # Ensure output is not the source checkout root or another already tracked directory.
        if destination == repo:
            raise SnapshotError("Destination cannot be the source checkout root")
        results = []
        if args.command == "materialize":
            if not destination.is_dir():
                raise SnapshotError("Create the destination directory explicitly before materializing")
            for component in selected:
                results.append(materialize_one(repo, destination, component))
        elif args.command == "check-origin":
            for component in selected:
                check_origin(repo, component)
                results.append({"component": component["name"], "status": "PIN_MATCHES_ORIGIN"})
        else:
            for component in selected:
                results.append(verify_one(destination, component))
        print(json.dumps({"action": args.command, "verified": results}, indent=2))
        return 0
    except (SnapshotError, OSError, ValueError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "HELD", "reason": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
