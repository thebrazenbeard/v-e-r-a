from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Mapping


SCHEMA = "VERA_HOSTILE_REVIEWER_STATE_V1"
VALID_MODES = {"OFF", "ON"}
REQUIRED_SCOPE = "VERA_PROJECT_ALL_CHATS"
SOURCE_STATUS = "SOURCE_CANDIDATE_NOT_INSTALLED"
STATE_KEYS = {"schema", "generation", "mode", "scope", "source_status", "last_change"}
LAST_CHANGE_KEYS = {"kind", "note"}
VALID_CHANGE_KINDS = {"INITIAL_SOURCE_DEFAULT", "EXPLICIT_CONTROL_CHANGE"}


class HostileReviewerControlError(RuntimeError):
    pass


def _validate_state(value: Mapping[str, Any]) -> None:
    if type(value) is not dict:
        raise HostileReviewerControlError("state must be an exact JSON object")
    if set(value) != STATE_KEYS:
        raise HostileReviewerControlError("state keys do not match the closed control schema")
    if value["schema"] != SCHEMA:
        raise HostileReviewerControlError("unexpected hostile reviewer state schema")
    generation = value["generation"]
    if type(generation) is not int or generation < 0:
        raise HostileReviewerControlError("generation must be an exact non-negative integer")
    if type(value["mode"]) is not str or value["mode"] not in VALID_MODES:
        raise HostileReviewerControlError("state contains unsupported mode")
    if value["scope"] != REQUIRED_SCOPE:
        raise HostileReviewerControlError("state is not bound to all-chat project scope")
    if value["source_status"] != SOURCE_STATUS:
        raise HostileReviewerControlError("source status must preserve the not-installed ceiling")
    last_change = value["last_change"]
    if type(last_change) is not dict or set(last_change) != LAST_CHANGE_KEYS:
        raise HostileReviewerControlError("last_change must match the closed schema")
    if type(last_change["kind"]) is not str or last_change["kind"] not in VALID_CHANGE_KINDS:
        raise HostileReviewerControlError("unsupported last_change kind")
    if type(last_change["note"]) is not str:
        raise HostileReviewerControlError("last_change note must be a string")


def load_state(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    _validate_state(value)
    return value


def _acquire_mutation_lock(path: Path) -> tuple[int, Path]:
    lock_path = path.with_name(f".{path.name}.lock")
    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise HostileReviewerControlError(
            "concurrent mutation lock is already held; fail closed and reconcile"
        ) from exc
    try:
        os.write(fd, f"pid={os.getpid()}\n".encode("ascii"))
        os.fsync(fd)
    except Exception:
        os.close(fd)
        try:
            os.unlink(lock_path)
        except FileNotFoundError:
            pass
        raise
    return fd, lock_path


def _release_mutation_lock(fd: int, lock_path: Path) -> None:
    os.close(fd)
    try:
        os.unlink(lock_path)
    except FileNotFoundError as exc:
        raise HostileReviewerControlError(
            "mutation lock disappeared before release; outcome requires reconciliation"
        ) from exc


def set_mode(
    path: Path,
    *,
    mode: str,
    expected_generation: int,
    change_kind: str = "EXPLICIT_CONTROL_CHANGE",
    note: str = "",
) -> dict[str, Any]:
    if type(mode) is not str or mode not in VALID_MODES:
        raise HostileReviewerControlError(f"unsupported mode: {mode!r}")
    if type(expected_generation) is not int or expected_generation < 0:
        raise HostileReviewerControlError("expected_generation must be an exact non-negative integer")
    if change_kind != "EXPLICIT_CONTROL_CHANGE":
        raise HostileReviewerControlError("set_mode requires EXPLICIT_CONTROL_CHANGE")
    if type(note) is not str:
        raise HostileReviewerControlError("note must be a string")

    lock_fd, lock_path = _acquire_mutation_lock(path)
    operation_error: BaseException | None = None
    try:
        current = load_state(path)
        if current["generation"] != expected_generation:
            raise HostileReviewerControlError(
                f"stale generation: expected {expected_generation}, observed {current['generation']}"
            )

        updated = dict(current)
        updated["generation"] = expected_generation + 1
        updated["mode"] = mode
        updated["last_change"] = {"kind": change_kind, "note": note}

        payload = json.dumps(updated, indent=2, sort_keys=True) + "\n"
        path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as tmp:
            tmp.write(payload)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_name = tmp.name

        try:
            os.replace(tmp_name, path)
        finally:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)

        readback = load_state(path)
        if readback != updated:
            raise HostileReviewerControlError("post-write readback mismatch")
        return readback
    except BaseException as exc:
        operation_error = exc
        raise
    finally:
        try:
            _release_mutation_lock(lock_fd, lock_path)
        except HostileReviewerControlError:
            if operation_error is None:
                raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("state_path", type=Path)
    parser.add_argument("--mode", required=True, choices=sorted(VALID_MODES))
    parser.add_argument("--expected-generation", required=True, type=int)
    parser.add_argument("--note", default="")
    args = parser.parse_args()

    result = set_mode(
        args.state_path,
        mode=args.mode,
        expected_generation=args.expected_generation,
        note=args.note,
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
