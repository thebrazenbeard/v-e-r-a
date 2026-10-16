from __future__ import annotations

from dataclasses import asdict
import json
from typing import Protocol

from ..models import ReviewRequest


class CompletionClient(Protocol):
    def complete(self, *, system: str, user: str) -> str: ...


class JsonCompletionCritic:
    """Adapt any strict text-completion client to Cricket's semantic CriticAdapter."""

    def __init__(self, client: CompletionClient) -> None:
        self.client = client

    def critique(self, *, prompt: str, request: ReviewRequest) -> list[dict]:
        user = json.dumps(
            asdict(request),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        text = self.client.complete(system=prompt, user=user)
        if not isinstance(text, str):
            raise ValueError("semantic critic completion must return text")
        try:
            raw = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError("semantic critic must return valid JSON") from exc
        if not isinstance(raw, list):
            raise ValueError("semantic critic output must be a JSON array")
        if not all(isinstance(item, dict) for item in raw):
            raise ValueError("semantic critic array entries must be objects")
        return raw
