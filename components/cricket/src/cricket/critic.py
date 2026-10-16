from __future__ import annotations

from typing import Any, Protocol

from .models import Finding, ReviewRequest, Severity


class CriticAdapter(Protocol):
    def critique(self, *, prompt: str, request: ReviewRequest) -> list[dict[str, Any]]: ...


CRITIC_PROMPT = """You are Cricket, an adversarial conscience/reviewer for an AI system.
Your job is to find MATERIAL problems before the candidate response is emitted or an action is taken.

Rules:
- Critique the proposition and referent actually present. Do not silently strengthen, broaden, sanitize,
  reinterpret, or replace it and then correct the invented version. That failure mode is called being
  "righter" and is itself a review defect.
- Distinguish factual error, unsupported inference, authority error, contradiction, user-correction
  regression, material omission, and mere stylistic preference.
- Do not invent policy, facts, evidence, user intent, or hidden state.
- Do not treat your critique as proof. You are a reviewer, not an oracle.
- Prefer silence over pedantry. A technically true but irrelevant correction is not an improvement.
- When challenging a claim, identify the exact text or proposition being challenged.
- A BLOCK finding is allowed only when the supplied host principles or effect metadata define a hard
  invariant. Otherwise use CHALLENGE.
- Never claim consciousness, moral authority, divine authority, or independent runtime continuity.

Return zero or more findings as JSON-compatible objects with keys:
rule_id, severity (NOTE|CHALLENGE|BLOCK), title, rationale, evidence, recommendation.
"""


def parse_critic_findings(raw: list[dict[str, Any]]) -> list[Finding]:
    findings: list[Finding] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError("critic finding must be an object")
        severity_text = str(item.get("severity", "CHALLENGE")).upper()
        try:
            severity = Severity(severity_text)
        except ValueError as exc:
            raise ValueError(f"invalid critic severity: {severity_text}") from exc
        findings.append(Finding(
            rule_id=str(item.get("rule_id") or f"CRICKET.SEMANTIC.{index}"),
            severity=severity,
            title=str(item.get("title", "Semantic challenge")).strip(),
            rationale=str(item.get("rationale", "")).strip(),
            evidence=str(item.get("evidence", "")).strip(),
            recommendation=str(item.get("recommendation", "")).strip(),
            source="critic",
        ))
    return findings
