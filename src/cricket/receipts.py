from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class JsonlReceiptLedger:
    """Single-writer append-only review receipt ledger with a SHA-256 hash chain."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def _rows(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        rows: list[dict[str, Any]] = []
        for line_number, line in enumerate(
            self.path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not line.strip():
                continue
            raw = json.loads(line)
            if not isinstance(raw, dict):
                raise ValueError(f"receipt line {line_number} must be an object")
            rows.append(raw)
        return rows

    def append(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("receipt payload must be an object")
        rows = self._rows()
        if rows and not self.verify():
            raise RuntimeError("receipt ledger failed verification; refusing append")
        previous_digest = rows[-1]["receipt_digest"] if rows else None
        record = dict(payload)
        record["previous_digest"] = previous_digest
        record["receipt_digest"] = canonical_digest(record)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
        return record

    def verify(self) -> bool:
        if not self.path.exists():
            return False
        previous_digest: str | None = None
        try:
            rows = self._rows()
        except (OSError, ValueError, json.JSONDecodeError):
            return False
        for row in rows:
            if row.get("previous_digest") != previous_digest:
                return False
            supplied = row.get("receipt_digest")
            if not isinstance(supplied, str):
                return False
            unsigned = dict(row)
            unsigned.pop("receipt_digest", None)
            if canonical_digest(unsigned) != supplied:
                return False
            previous_digest = supplied
        return True
