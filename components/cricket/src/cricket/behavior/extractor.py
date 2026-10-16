from __future__ import annotations

import json
from typing import Protocol

from .codec import assessment_from_dict
from .model import BehavioralAssessment


class BehavioralCompletionClient(Protocol):
    def complete(self, *, system: str, user: str) -> str: ...


BEHAVIOR_EXTRACTION_PROMPT = """You are Cricket's behavioral interpretation extractor.
Your job is to identify observable behavior and bounded hypotheses, not to read minds.

Return one raw JSON object with:
- observations[]
- hypotheses[]

Each observation requires:
observation_id, subject, description, source_ref.

Each hypothesis requires:
hypothesis_id, pattern, subject, evidence_refs, rationale,
alternative_explanations, state.

Allowed states: PROPOSED, SUPPORTED, CONTESTED, REJECTED.
Every hypothesis must cite observation IDs from this extraction.
A SUPPORTED hypothesis should retain at least one plausible rival explanation.

Treat behavior as evidence for interpretations, not proof of hidden motive.
Do not diagnose clinical conditions.
Do not infer protected traits or private mental states.
Do not convert fictional/media pattern examples into facts about a real person.
Do not use a pattern label as an insult.
If evidence is too thin, return observations with no hypothesis or a PROPOSED hypothesis.

Return raw JSON only. No Markdown fences.
"""


class JsonCompletionBehaviorExtractor:
    def __init__(self, client: BehavioralCompletionClient) -> None:
        self.client = client

    def extract(
        self,
        *,
        source_text: str,
        candidate_text: str,
    ) -> BehavioralAssessment:
        payload = json.dumps(
            {"source_text": source_text, "candidate_text": candidate_text},
            sort_keys=True,
            ensure_ascii=False,
        )
        text = self.client.complete(system=BEHAVIOR_EXTRACTION_PROMPT, user=payload)
        if not isinstance(text, str):
            raise ValueError("behavior extractor completion must return text")
        try:
            raw = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError("behavior extractor must return valid JSON") from exc
        return assessment_from_dict(raw)
