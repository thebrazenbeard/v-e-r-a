"""Fail-closed, offline Supabase source-snapshot currentness comparison.

This tool compares a checked-out source-definition snapshot against an
operator-supplied read-only provider metadata receipt. It NEVER authenticates
that receipt, connects to a provider, or grants database/runtime authority.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path


MAX_JSON_BYTES = 4 * 1024 * 1024
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _read_json(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    if len(data) > MAX_JSON_BYTES:
        raise ValueError("JSON input exceeds size limit")
    document = json.loads(data, object_pairs_hook=_unique_pairs)
    if not isinstance(document, dict):
        raise ValueError("JSON root must be an object")
    return document


def _utc(value: object, label: str) -> dt.datetime:
    if not isinstance(value, str):
        raise ValueError(f"{label} missing UTC timestamp")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label} malformed timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != dt.timedelta(0):
        raise ValueError(f"{label} must be UTC")
    return parsed.astimezone(dt.timezone.utc)


def _migrations(value: object) -> tuple[tuple[str, str], ...]:
    if not isinstance(value, list):
        raise ValueError("migration list missing")
    records: list[tuple[str, str]] = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError("malformed migration record")
        version, name = item.get("version"), item.get("name")
        if not isinstance(version, str) or not version.isdigit() or not isinstance(name, str) or not name:
            raise ValueError("malformed migration identity")
        records.append((version, name))
    if len({version for version, _ in records}) != len(records):
        raise ValueError("duplicate migration version")
    return tuple(records)


def _functions(value: object, project_ref: str) -> dict[str, tuple[int, str, str, bool]]:
    if not isinstance(value, list) or not value:
        raise ValueError("function list missing")
    result: dict[str, tuple[int, str, str, bool]] = {}
    for item in value:
        if not isinstance(item, dict):
            raise ValueError("malformed function entry")
        slug, version, digest, status, verify_jwt = (
            item.get("slug"), item.get("version"), item.get("ezbr_sha256"), item.get("status"), item.get("verify_jwt")
        )
        if item.get("project_ref") != project_ref:
            raise ValueError("function project binding mismatch")
        if not isinstance(slug, str) or not slug or isinstance(version, bool) or not isinstance(version, int) or version < 1:
            raise ValueError("invalid function identity/version")
        if not isinstance(digest, str) or not HEX64.fullmatch(digest):
            raise ValueError("invalid function digest")
        if status not in ("ACTIVE", "INACTIVE"):
            raise ValueError("invalid function status")
        if not isinstance(verify_jwt, bool):
            raise ValueError("invalid function auth flag")
        if slug in result:
            raise ValueError("duplicate function slug")
        result[slug] = (version, digest, status, verify_jwt)
    return result


def compare(
    snapshot_root: Path,
    live_receipt_path: Path,
    *,
    now: dt.datetime | None = None,
    max_age_hours: int = 24,
) -> dict[str, object]:
    """Return a bounded evidence classification, never runtime authorization."""
    now = now or dt.datetime.now(dt.timezone.utc)
    try:
        snapshot = _read_json(snapshot_root / "supabase" / "project.json")
        history = _read_json(snapshot_root / "supabase" / "migration-index.json")
        live = _read_json(live_receipt_path)
        if not isinstance(max_age_hours, int) or not 1 <= max_age_hours <= 24 * 30:
            raise ValueError("invalid maximum age")
        if live.get("schema") != "SUPABASE_METADATA_OBSERVATION_V1":
            raise ValueError("invalid observation schema")
        if snapshot.get("project_ref") != live.get("project_ref") or snapshot.get("project_ref") != history.get("project_ref"):
            raise ValueError("project identity mismatch")
        if not isinstance(snapshot.get("project_ref"), str) or not snapshot["project_ref"]:
            raise ValueError("project identity missing")
        if snapshot.get("definition_snapshot_only") is not True:
            raise ValueError("snapshot definition-only boundary missing")
        source_head = snapshot.get("snapshot_source_head")
        if not isinstance(source_head, str) or not HEX40.fullmatch(source_head):
            raise ValueError("snapshot source head is unbound")
        if live.get("snapshot_source_head") != source_head:
            raise ValueError("snapshot source head mismatch")
        observed_at = _utc(live.get("observed_at"), "provider observation")
        captured_at = _utc(snapshot.get("observed_at"), "snapshot capture")
        if observed_at > now + dt.timedelta(minutes=5) or captured_at > observed_at:
            raise ValueError("future or contradictory observation time")
        if now - observed_at > dt.timedelta(hours=max_age_hours):
            raise ValueError("provider observation is stale")
        if now - captured_at > dt.timedelta(hours=max_age_hours):
            raise ValueError("snapshot capture is stale")
        original_migrations = _migrations(history.get("migrations"))
        if len(original_migrations) != history.get("count"):
            raise ValueError("snapshot migration count inconsistent")
        if original_migrations != _migrations(live.get("migrations")):
            raise ValueError("migration identity/version drift")

        bindings = sorted((snapshot_root / "supabase" / "functions").glob("*/binding.json"))
        if not bindings:
            raise ValueError("no source-bound Edge functions")
        source_functions = _functions([_read_json(path) for path in bindings], snapshot["project_ref"])
        current_functions = _functions(live.get("functions"), snapshot["project_ref"])
        if source_functions != current_functions:
            raise ValueError("Edge function version, digest or status drift")
        return {
            "status": "SOURCE_METADATA_MATCH_UNATTESTED",
            "effect_authority": False,
            "provider_authenticated_by_tool": False,
            "model_or_host_runtime_qualified": False,
            "functions_compared": len(source_functions),
            "migrations_compared": len(original_migrations),
        }
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {"status": "HOLD_STALE_OR_UNBOUND", "reason": str(exc), "effect_authority": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot-root", required=True, type=Path)
    parser.add_argument("--live-metadata", required=True, type=Path)
    parser.add_argument("--max-age-hours", type=int, default=24)
    args = parser.parse_args(argv)
    result = compare(args.snapshot_root, args.live_metadata, max_age_hours=args.max_age_hours)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "SOURCE_METADATA_MATCH_UNATTESTED" else 2


if __name__ == "__main__":
    sys.exit(main())
