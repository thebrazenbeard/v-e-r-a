from __future__ import annotations

import json
from typing import Protocol

from .codec import frame_from_dict
from .model import SemanticFrame


class SemanticPairCompletionClient(Protocol):
    def complete(self, *, system: str, user: str) -> str: ...


SEMANTIC_EXTRACTION_PROMPT = """You are Cricket's semantic frame extractor.
Extract meaning; do not judge whether the source or candidate is correct.

Return exactly one JSON object with keys "source" and "candidate".
Each value is a semantic frame with:
- propositions[]
- unresolved_interpretations[]

For proposition pairs that represent the same underlying proposition, use the same shared anchor_id.
Do not force alignment when the candidate adds, drops, or substitutes a proposition.

Each proposition may contain:
anchor_id, referent, predicate, force, polarity, scope, speech_act,
temporal_status, provenance.

Allowed force values: POSSIBLE, PROBABLE, ASSERTED, CERTAIN.
Allowed polarity values: AFFIRMED, DENIED.
Allowed speech_act values: DESCRIPTION, HYPOTHESIS, QUESTION, PREFERENCE,
REQUEST, PERMISSION, INSTRUCTION, COMMITMENT, QUOTATION.
Allowed temporal_status values: CURRENT, HISTORICAL, PROPOSED, UNKNOWN.
Allowed provenance values: USER_CURRENT, USER_HISTORICAL, MODEL_INFERENCE,
EXTERNAL_EVIDENCE, TOOL_RESULT, EFFECT_RECEIPT, QUOTATION, UNKNOWN.

Preserve unresolved ambiguity instead of guessing.
A preference is not permission. A request is not automatically an instruction.
Historical material is not current state. Similar meaning does not transfer provenance.
Return raw JSON only. Do not use Markdown fences.
"""


class JsonCompletionSemanticExtractor:
    def __init__(self, client: SemanticPairCompletionClient) -> None:
        self.client = client

    def extract_pair(
        self,
        *,
        source_text: str,
        candidate_text: str,
    ) -> tuple[SemanticFrame, SemanticFrame]:
        payload = json.dumps(
            {"source_text": source_text, "candidate_text": candidate_text},
            sort_keys=True,
            ensure_ascii=False,
        )
        text = self.client.complete(system=SEMANTIC_EXTRACTION_PROMPT, user=payload)
        if not isinstance(text, str):
            raise ValueError("semantic extractor completion must return text")
        try:
            raw = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError("semantic extractor must return valid JSON") from exc
        if not isinstance(raw, dict):
            raise ValueError("semantic extractor output must be a JSON object")
        if set(raw) != {"source", "candidate"}:
            raise ValueError("semantic extractor output must contain only source and candidate")
        return frame_from_dict(raw["source"]), frame_from_dict(raw["candidate"])
