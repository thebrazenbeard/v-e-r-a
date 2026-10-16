from __future__ import annotations

from dataclasses import dataclass, replace
import json
from pathlib import Path

from .models import ReviewRequest


@dataclass(frozen=True)
class PrinciplePack:
    id: str
    version: str
    principles: tuple[str, ...]

    @classmethod
    def load(cls, path: str | Path) -> "PrinciplePack":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("principle pack must be an object")
        pack_id = raw.get("id")
        version = raw.get("version")
        principles = raw.get("principles")
        if not isinstance(pack_id, str) or not pack_id.strip():
            raise ValueError("principle pack id must be a non-empty string")
        if not isinstance(version, str) or not version.strip():
            raise ValueError("principle pack version must be a non-empty string")
        if not isinstance(principles, list) or not principles or not all(
            isinstance(item, str) and item.strip() for item in principles
        ):
            raise ValueError("principles must be a non-empty list of non-empty strings")
        return cls(
            id=pack_id.strip(),
            version=version.strip(),
            principles=tuple(item.strip() for item in principles),
        )

    def apply(self, request: ReviewRequest) -> ReviewRequest:
        merged = tuple(dict.fromkeys((*request.principles, *self.principles)))
        metadata = dict(request.metadata)
        metadata["principle_pack"] = {"id": self.id, "version": self.version}
        return replace(request, principles=merged, metadata=metadata)
