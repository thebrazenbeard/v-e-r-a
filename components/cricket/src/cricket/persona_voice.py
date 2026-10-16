from __future__ import annotations

from .models import Finding, Severity
from .persona import CricketPersona, DEFAULT_CRICKET_PERSONA


def persona_line_for_finding(
    finding: Finding,
    persona: CricketPersona = DEFAULT_CRICKET_PERSONA,
) -> str:
    """Apply Cricket's voice without changing the underlying finding."""
    traits = set(persona.traits)
    if "DRY_SASS" not in traits:
        return ""

    rule = finding.rule_id.casefold()
    if "completion_without_verification" in rule:
        return '"Done" is wearing a fake mustache labeled "verified."'
    if "protected_effect" in rule or "authority" in rule:
        return "Nope. Confidence is not permission, and neither are vibes."
    if "semantic.strengthened" in rule:
        return "Cute. Same proposition, stronger claim. Put the qualifier back."
    if "semantic.authority_escalated" in rule:
        return "Preference did not magically become permission. Put the steering wheel back."
    if finding.source == "behavior":
        return "That is a hypothesis, not telepathy. Keep the evidence and a rival explanation attached."
    if finding.severity is Severity.BLOCK:
        return "No steering-wheel privileges were found in that argument."
    if finding.severity is Severity.CHALLENGE:
        return "Something moved. The evidence did not."
    return ""
