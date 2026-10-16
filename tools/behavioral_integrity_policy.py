"""Bounded source policy for VCP issue #18.

This module models transient behavioral-mode reversion, compact pragmatic command
parsing, and correction uptake.  It is deliberately pure: it performs no external
effect, grants no authority, and does not claim live runtime consumption.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
import re


class BehavioralPolicyViolation(ValueError):
    """The caller supplied malformed or internally inconsistent policy input."""


class BehaviorMode(str, Enum):
    BASELINE = "BASELINE"
    RESEARCH_REPORT = "RESEARCH_REPORT"


class ModeDecisionStatus(str, Enum):
    BASELINE_UNCHANGED = "BASELINE_UNCHANGED"
    SPECIALIZED_MODE_PRESERVED = "SPECIALIZED_MODE_PRESERVED"
    REVERTED_TO_BASELINE = "REVERTED_TO_BASELINE"


class CommandForce(str, Enum):
    REQUESTED_ACTION = "REQUESTED_ACTION"
    AMBIGUOUS = "AMBIGUOUS"


class HedgeScope(str, Enum):
    NONE = "NONE"
    RELEVANCE_NECESSITY_APPLICABILITY = "RELEVANCE_NECESSITY_APPLICABILITY"


class ExecutionStatus(str, Enum):
    EXECUTE_BOUNDED_ACTION = "EXECUTE_BOUNDED_ACTION"
    BLOCKED = "BLOCKED"
    CLARIFY_OR_DISCUSS = "CLARIFY_OR_DISCUSS"


@dataclass(frozen=True)
class BehaviorModeContext:
    active_mode: BehaviorMode
    specialized_task_complete: bool
    context_changed: bool
    explicit_continue_specialized_mode: bool = False
    voice_context_correction: bool = False


@dataclass(frozen=True)
class BehaviorModeDecision:
    status: ModeDecisionStatus
    active_mode: BehaviorMode
    retained_research_competence: bool
    reason: str


@dataclass(frozen=True)
class ActionLexiconEntry:
    action_id: str
    phrases: tuple[str, ...]


@dataclass(frozen=True)
class PragmaticClause:
    raw: str
    action_id: str | None
    force: CommandForce
    target: str | None
    hedge_terms: tuple[str, ...]
    hedge_scope: HedgeScope
    uncertainty_preserved: bool


@dataclass(frozen=True)
class ExecutionContext:
    target_sufficient: bool
    authority_sufficient: bool
    currentness_sufficient: bool
    tools_sufficient: bool


@dataclass(frozen=True)
class ExecutionDecision:
    status: ExecutionStatus
    action_id: str | None
    target: str | None
    blockers: tuple[str, ...]
    uncertainty_preserved: bool
    meta_discussion_substitutes_for_effect: bool = False


DEFAULT_ACTION_LEXICON = (
    ActionLexiconEntry(
        action_id="CREATE_BUG_REPORT",
        phrases=("bug report", "a bug report"),
    ),
    ActionLexiconEntry(
        action_id="CREATE_NOTE",
        phrases=("note", "a note"),
    ),
)

_HEDGE_WORDS = ("perhaps", "maybe", "possibly")
_UNCERTAINTY_EMOJI = ("🤔",)
_TARGET_RE = re.compile(r"\bfor\s+([A-Za-z0-9_.-]+)", re.IGNORECASE)


def resolve_behavior_mode(context: BehaviorModeContext) -> BehaviorModeDecision:
    """Resolve task-scoped mode lifetime without erasing retained competence."""

    if type(context) is not BehaviorModeContext:
        raise TypeError("context must be an exact BehaviorModeContext")
    if type(context.active_mode) is not BehaviorMode:
        raise BehavioralPolicyViolation("active_mode must be an exact BehaviorMode")
    for field_name in (
        "specialized_task_complete",
        "context_changed",
        "explicit_continue_specialized_mode",
        "voice_context_correction",
    ):
        if type(getattr(context, field_name)) is not bool:
            raise BehavioralPolicyViolation(f"{field_name} must be boolean")

    if context.voice_context_correction and context.explicit_continue_specialized_mode:
        raise BehavioralPolicyViolation(
            "conflicting current mode directives require explicit ordering or clarification"
        )

    if context.active_mode is BehaviorMode.BASELINE:
        return BehaviorModeDecision(
            status=ModeDecisionStatus.BASELINE_UNCHANGED,
            active_mode=BehaviorMode.BASELINE,
            retained_research_competence=True,
            reason="baseline already active",
        )

    if context.voice_context_correction:
        return BehaviorModeDecision(
            status=ModeDecisionStatus.REVERTED_TO_BASELINE,
            active_mode=BehaviorMode.BASELINE,
            retained_research_competence=True,
            reason="current voice/context correction ends obsolete specialized presentation",
        )

    if context.explicit_continue_specialized_mode:
        return BehaviorModeDecision(
            status=ModeDecisionStatus.SPECIALIZED_MODE_PRESERVED,
            active_mode=context.active_mode,
            retained_research_competence=True,
            reason="current instruction explicitly keeps specialized mode active",
        )

    if context.specialized_task_complete and context.context_changed:
        return BehaviorModeDecision(
            status=ModeDecisionStatus.REVERTED_TO_BASELINE,
            active_mode=BehaviorMode.BASELINE,
            retained_research_competence=True,
            reason="completed task plus context transition ends task-scoped mode",
        )

    return BehaviorModeDecision(
        status=ModeDecisionStatus.SPECIALIZED_MODE_PRESERVED,
        active_mode=context.active_mode,
        retained_research_competence=True,
        reason="specialized task/context remains active",
    )


def _normalize_phrase(value: str) -> str:
    return " ".join(value.lower().strip().split())


def _split_compact_directive(text: str) -> tuple[str, ...]:
    # Semicolon is the strong compact-command boundary in the issue-18 fixture.
    # "also" is retained inside the following clause and stripped separately.
    pieces = [piece.strip() for piece in text.split(";") if piece.strip()]
    if len(pieces) <= 1:
        return tuple(pieces)
    return tuple(pieces)


def _strip_leading_conjunction(value: str) -> str:
    return re.sub(r"^\s*also\s+", "", value, flags=re.IGNORECASE).strip()


def _find_action(
    clause: str,
    lexicon: tuple[ActionLexiconEntry, ...],
) -> tuple[ActionLexiconEntry, str] | None:
    normalized = _normalize_phrase(_strip_leading_conjunction(clause))
    # Prefer the longest phrase so a more specific action wins deterministically.
    candidates: list[tuple[int, ActionLexiconEntry, str]] = []
    for entry in lexicon:
        if type(entry) is not ActionLexiconEntry:
            raise BehavioralPolicyViolation("lexicon entries must be ActionLexiconEntry")
        if type(entry.action_id) is not str or not entry.action_id.strip():
            raise BehavioralPolicyViolation("action_id must be a non-empty string")
        if type(entry.phrases) is not tuple or not entry.phrases:
            raise BehavioralPolicyViolation("action phrases must be a non-empty tuple")
        if len(set(entry.phrases)) != len(entry.phrases):
            raise BehavioralPolicyViolation("action phrases must not contain duplicates")
        for phrase in entry.phrases:
            if type(phrase) is not str or not phrase.strip():
                raise BehavioralPolicyViolation("action phrases must be non-empty strings")
            p = _normalize_phrase(phrase)
            if normalized == p or normalized.startswith(p + " "):
                candidates.append((len(p), entry, p))
    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0], reverse=True)
    _, entry, phrase = candidates[0]
    return entry, phrase


def _bounded_command_suffix(clause: str, matched_phrase: str) -> bool:
    """Accept only the compact issue-18 command grammar after the action noun.

    The parser must not promote arbitrary declarative text merely because it starts
    with a known action phrase. After the action phrase, only local hedge terms,
    an optional for-target phrase, uncertainty emoji, and non-question command
    punctuation are admitted by this bounded source policy.
    """

    normalized = _normalize_phrase(_strip_leading_conjunction(clause))
    if normalized == matched_phrase:
        return True
    if not normalized.startswith(matched_phrase + " "):
        return False

    suffix = normalized[len(matched_phrase):].strip()
    for word in _HEDGE_WORDS:
        suffix = re.sub(rf"\b{re.escape(word)}\b", " ", suffix)
    suffix = _TARGET_RE.sub(" ", suffix)
    for emoji in _UNCERTAINTY_EMOJI:
        suffix = suffix.replace(emoji, " ")
    suffix = re.sub(r"[,.;!]+", " ", suffix)
    suffix = " ".join(suffix.split())
    return suffix == ""


def _hedges(clause: str) -> tuple[str, ...]:
    lowered = clause.lower()
    found = [word for word in _HEDGE_WORDS if re.search(rf"\b{re.escape(word)}\b", lowered)]
    found.extend(emoji for emoji in _UNCERTAINTY_EMOJI if emoji in clause)
    return tuple(found)


def parse_pragmatic_command(
    text: str,
    *,
    established_action_context: bool,
    lexicon: tuple[ActionLexiconEntry, ...] = DEFAULT_ACTION_LEXICON,
) -> tuple[PragmaticClause, ...]:
    """Parse a bounded compact directive without globalizing local uncertainty.

    This is intentionally not a general natural-language parser.  It recognizes a
    caller-supplied action lexicon inside an established actionable context and
    preserves hedging as local relevance/necessity/applicability uncertainty.
    """

    if type(text) is not str or not text.strip():
        raise BehavioralPolicyViolation("text must be a non-empty string")
    if type(established_action_context) is not bool:
        raise BehavioralPolicyViolation("established_action_context must be boolean")
    if type(lexicon) is not tuple or not lexicon:
        raise BehavioralPolicyViolation("lexicon must be a non-empty tuple")

    normalized_phrase_owner: dict[str, str] = {}
    action_phrase_sets: dict[str, frozenset[str]] = {}
    for entry in lexicon:
        if type(entry) is not ActionLexiconEntry:
            raise BehavioralPolicyViolation("lexicon entries must be ActionLexiconEntry")
        if type(entry.action_id) is not str or not entry.action_id.strip():
            raise BehavioralPolicyViolation("action_id must be a non-empty string")
        if type(entry.phrases) is not tuple or not entry.phrases:
            raise BehavioralPolicyViolation("action phrases must be a non-empty tuple")
        normalized = []
        for phrase in entry.phrases:
            if type(phrase) is not str or not phrase.strip():
                raise BehavioralPolicyViolation("action phrases must be non-empty strings")
            p = _normalize_phrase(phrase)
            normalized.append(p)
            previous_owner = normalized_phrase_owner.get(p)
            if previous_owner is not None and previous_owner != entry.action_id:
                raise BehavioralPolicyViolation(
                    f"ambiguous action phrase collision: {p}"
                )
            normalized_phrase_owner[p] = entry.action_id
        normalized_set = frozenset(normalized)
        if entry.action_id in action_phrase_sets and action_phrase_sets[entry.action_id] != normalized_set:
            raise BehavioralPolicyViolation(
                f"duplicate action_id with incompatible phrase set: {entry.action_id}"
            )
        action_phrase_sets[entry.action_id] = normalized_set

    result: list[PragmaticClause] = []
    for raw in _split_compact_directive(text):
        matched = _find_action(raw, lexicon)
        action = matched[0] if matched is not None else None
        bounded_command_suffix = (
            _bounded_command_suffix(raw, matched[1])
            if matched is not None
            else False
        )
        hedge_terms = _hedges(raw)
        target_match = _TARGET_RE.search(raw)
        target = target_match.group(1) if target_match else None
        hedge_scope = (
            HedgeScope.RELEVANCE_NECESSITY_APPLICABILITY
            if hedge_terms
            else HedgeScope.NONE
        )

        if action is not None and established_action_context and bounded_command_suffix:
            force = CommandForce.REQUESTED_ACTION
            action_id = action.action_id
        else:
            force = CommandForce.AMBIGUOUS
            action_id = action.action_id if action is not None else None

        result.append(
            PragmaticClause(
                raw=raw,
                action_id=action_id,
                force=force,
                target=target,
                hedge_terms=hedge_terms,
                hedge_scope=hedge_scope,
                uncertainty_preserved=bool(hedge_terms),
            )
        )
    return tuple(result)


def decide_execution(
    clause: PragmaticClause,
    context: ExecutionContext,
) -> ExecutionDecision:
    """Convert parsed command force into an effect decision without granting authority."""

    if type(clause) is not PragmaticClause:
        raise TypeError("clause must be an exact PragmaticClause")
    if type(context) is not ExecutionContext:
        raise TypeError("context must be an exact ExecutionContext")
    for field_name in (
        "target_sufficient",
        "authority_sufficient",
        "currentness_sufficient",
        "tools_sufficient",
    ):
        if type(getattr(context, field_name)) is not bool:
            raise BehavioralPolicyViolation(f"{field_name} must be boolean")

    if clause.force is not CommandForce.REQUESTED_ACTION or clause.action_id is None:
        return ExecutionDecision(
            status=ExecutionStatus.CLARIFY_OR_DISCUSS,
            action_id=clause.action_id,
            target=clause.target,
            blockers=("COMMAND_FORCE_UNRESOLVED",),
            uncertainty_preserved=clause.uncertainty_preserved,
        )

    checks = (
        ("TARGET", context.target_sufficient),
        ("AUTHORITY", context.authority_sufficient),
        ("CURRENTNESS", context.currentness_sufficient),
        ("TOOLS", context.tools_sufficient),
    )
    blockers = tuple(name for name, ok in checks if not ok)
    if blockers:
        return ExecutionDecision(
            status=ExecutionStatus.BLOCKED,
            action_id=clause.action_id,
            target=clause.target,
            blockers=blockers,
            uncertainty_preserved=clause.uncertainty_preserved,
        )

    return ExecutionDecision(
        status=ExecutionStatus.EXECUTE_BOUNDED_ACTION,
        action_id=clause.action_id,
        target=clause.target,
        blockers=(),
        uncertainty_preserved=clause.uncertainty_preserved,
        meta_discussion_substitutes_for_effect=False,
    )


def apply_command_force_correction(
    clause: PragmaticClause,
    *,
    corrected_as_command: bool,
    context: ExecutionContext,
) -> ExecutionDecision:
    """Apply a present command-force correction to the next relevant behavior."""

    if type(corrected_as_command) is not bool:
        raise BehavioralPolicyViolation("corrected_as_command must be boolean")
    corrected = clause
    if corrected_as_command:
        if clause.action_id is None:
            raise BehavioralPolicyViolation(
                "cannot promote a correction without a resolved bounded action"
            )
        corrected = replace(clause, force=CommandForce.REQUESTED_ACTION)
    return decide_execution(corrected, context)


__all__ = [
    "ActionLexiconEntry",
    "BehaviorMode",
    "BehaviorModeContext",
    "BehaviorModeDecision",
    "BehavioralPolicyViolation",
    "CommandForce",
    "DEFAULT_ACTION_LEXICON",
    "ExecutionContext",
    "ExecutionDecision",
    "ExecutionStatus",
    "HedgeScope",
    "ModeDecisionStatus",
    "PragmaticClause",
    "apply_command_force_correction",
    "decide_execution",
    "parse_pragmatic_command",
    "resolve_behavior_mode",
]
