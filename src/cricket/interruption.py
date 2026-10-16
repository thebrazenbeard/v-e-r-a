from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import json
from typing import Any, Protocol

from .models import Disposition, ReviewRequest, ReviewResult
from .personality import CricketPersona, DEFAULT_CRICKET_PERSONA
from .render import render_blockquote
from .reviewer import Cricket


class InterruptionAction(str, Enum):
    ALLOW = "ALLOW"
    INJECT_AND_REVISE = "INJECT_AND_REVISE"
    BLOCK_AND_INJECT = "BLOCK_AND_INJECT"


class RezonReasoner(Protocol):
    def reason(self, task: dict[str, Any]) -> dict[str, Any]: ...


@dataclass(frozen=True)
class InterruptionResponse:
    action: InterruptionAction
    disposition: str
    injection_markdown: str
    finding_ids: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()
    formulation_source: str = "none"

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action.value,
            "disposition": self.disposition,
            "injection_markdown": self.injection_markdown,
            "finding_ids": list(self.finding_ids),
            "unresolved": list(self.unresolved),
            "formulation_source": self.formulation_source,
        }


class RezonInterruptionComposer:
    """Use a Rezon-compatible reasoner to formulate Cricket's visible interruption."""

    def __init__(
        self,
        reasoner: RezonReasoner,
        *,
        persona: CricketPersona = DEFAULT_CRICKET_PERSONA,
    ) -> None:
        self.reasoner = reasoner
        self.persona = persona

    def build_task(
        self,
        *,
        request: ReviewRequest,
        result: ReviewResult,
    ) -> dict[str, Any]:
        finding_ids = [finding.rule_id for finding in result.findings]
        digest_input = json.dumps(
            {
                "user_message": request.user_message,
                "candidate_response": request.candidate_response,
                "disposition": result.disposition.value,
                "finding_ids": finding_ids,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        task_id = "cricket-interruption:" + sha256(digest_input).hexdigest()[:24]

        return {
            "task_id": task_id,
            "literal_request": (
                "Formulate Cricket's interruption response from the supplied findings. "
                "Preserve the literal proposition, disposition, evidence boundaries, and "
                "authority state. Return concise intervention text, not hidden reasoning."
            ),
            "subject_refs": finding_ids,
            "constraints": [
                *self.persona.formulation_constraints(),
                "Do not alter PASS, CHALLENGE, or BLOCK disposition.",
                "Do not turn preference into permission or uncertainty into certainty.",
                "Attack the proposition actually present; do not perform Righter substitution.",
                "Keep the intervention concise enough to inject into an active chat.",
            ],
            "available_authority": [],
            "privacy_scope": "cricket-review",
            "resource_budget": 4,
            "context_refs": finding_ids,
            "persona": {
                "id": self.persona.id,
                "version": self.persona.version,
                "traits": list(self.persona.traits),
                "motto": self.persona.motto,
            },
            "context": {
                "user_message": request.user_message,
                "candidate_response": request.candidate_response,
                "phase": request.phase,
                "effect_class": request.effect_class,
                "explicit_authorization": request.explicit_authorization,
                "principles": list(request.principles),
                "disposition": result.disposition.value,
                "findings": [finding.to_dict() for finding in result.findings],
            },
        }

    def compose(
        self,
        *,
        request: ReviewRequest,
        result: ReviewResult,
    ) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
        task = self.build_task(request=request, result=result)
        raw = self.reasoner.reason(task)
        if not isinstance(raw, dict):
            raise ValueError("Rezon interruption formulation must be an object")

        message = raw.get("message")
        finding_ids = raw.get("finding_ids")
        unresolved = raw.get("unresolved", [])

        if not isinstance(message, str) or not message.strip():
            raise ValueError("Rezon interruption message must be non-empty text")
        if not isinstance(finding_ids, list) or not finding_ids or not all(
            isinstance(item, str) and item for item in finding_ids
        ):
            raise ValueError("Rezon interruption finding_ids must be a non-empty string list")
        if not isinstance(unresolved, list) or not all(isinstance(item, str) for item in unresolved):
            raise ValueError("Rezon interruption unresolved must be a string list")

        allowed = {finding.rule_id for finding in result.findings}
        invented = set(finding_ids) - allowed
        if invented:
            raise ValueError(
                "Rezon interruption references unknown finding ids: "
                + ", ".join(sorted(invented))
            )

        return message.strip(), tuple(finding_ids), tuple(unresolved)


def _render_injection(disposition: Disposition, message: str) -> str:
    lines = [f"> **Cricket — {disposition.value}**", ">"]
    for line in message.splitlines() or [""]:
        lines.append(f"> {line}")
    return "\n".join(lines)


class WebhookInterruptionProcessor:
    """Pure webhook-style adapter: JSON review event in, host action/injection response out."""

    def __init__(
        self,
        *,
        cricket: Cricket,
        composer: RezonInterruptionComposer | None = None,
    ) -> None:
        self.cricket = cricket
        self.composer = composer

    def handle(self, raw_request: dict[str, Any]) -> InterruptionResponse:
        request = ReviewRequest.from_dict(raw_request)
        result = self.cricket.review(request)

        if result.disposition is Disposition.PASS:
            return InterruptionResponse(
                action=InterruptionAction.ALLOW,
                disposition=Disposition.PASS.value,
                injection_markdown="",
            )

        action = (
            InterruptionAction.BLOCK_AND_INJECT
            if result.disposition is Disposition.BLOCK
            else InterruptionAction.INJECT_AND_REVISE
        )

        if self.composer is not None:
            try:
                message, finding_ids, unresolved = self.composer.compose(
                    request=request,
                    result=result,
                )
                return InterruptionResponse(
                    action=action,
                    disposition=result.disposition.value,
                    injection_markdown=_render_injection(result.disposition, message),
                    finding_ids=finding_ids,
                    unresolved=unresolved,
                    formulation_source="rezon",
                )
            except (ValueError, TypeError, RuntimeError):
                # Rezon formulation is advisory. Preserve Cricket's deterministic
                # interruption if the reasoner is unavailable or malformed.
                pass

        return InterruptionResponse(
            action=action,
            disposition=result.disposition.value,
            injection_markdown=render_blockquote(result, speak_on_pass=True),
            finding_ids=tuple(finding.rule_id for finding in result.findings),
            formulation_source="cricket-fallback",
        )
