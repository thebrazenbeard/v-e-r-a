from __future__ import annotations

from .models import Disposition, ReviewResult
from .persona import CricketPersona, DEFAULT_CRICKET_PERSONA
from .persona_voice import persona_line_for_finding


def _append_quoted(lines: list[str], text: str, *, label: str = "") -> None:
    parts = text.splitlines() or [""]
    for index, part in enumerate(parts):
        prefix = label if index == 0 else ""
        lines.append(f"> {prefix}{part}")


def render_blockquote(
    result: ReviewResult,
    *,
    speak_on_pass: bool = False,
    persona: CricketPersona = DEFAULT_CRICKET_PERSONA,
) -> str:
    if result.disposition is Disposition.PASS and not speak_on_pass:
        return ""

    lines = [f"> **Cricket — {result.disposition.value}**"]
    if not result.findings:
        lines.extend([">", "> No material objection."])
        return "\n".join(lines)

    for finding in result.findings:
        lines.append(">")
        title_lines = finding.title.splitlines() or [""]
        lines.append(f"> **[{finding.severity.value}] {title_lines[0]}**")
        for title_line in title_lines[1:]:
            lines.append(f"> **{title_line}**")
        persona_line = persona_line_for_finding(finding, persona)
        if persona_line:
            _append_quoted(lines, persona_line)
        _append_quoted(lines, finding.rationale)
        if finding.evidence:
            _append_quoted(lines, finding.evidence, label="Evidence: ")
        if finding.recommendation:
            _append_quoted(lines, finding.recommendation, label="Recommendation: ")
    return "\n".join(lines)


def render_chat_turn(
    candidate: str,
    result: ReviewResult,
    *,
    persona: CricketPersona = DEFAULT_CRICKET_PERSONA,
) -> str:
    """Render the host-visible answer plus Cricket's distinct conscience voice."""
    if not isinstance(candidate, str):
        raise ValueError("candidate must be text")
    if result.disposition is Disposition.BLOCK:
        return render_blockquote(result, speak_on_pass=True, persona=persona)
    if result.disposition is Disposition.CHALLENGE:
        cricket = render_blockquote(result, speak_on_pass=True, persona=persona)
        return candidate if not cricket else f"{candidate}\n\n{cricket}"
    return candidate
