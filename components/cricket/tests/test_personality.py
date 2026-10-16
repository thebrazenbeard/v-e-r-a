from cricket import Cricket, ReviewRequest, render_blockquote
from cricket.persona import DEFAULT_CRICKET_PERSONA
from cricket.persona_voice import persona_line_for_finding


def test_default_persona_has_absolute_candor_and_sass_without_cruelty() -> None:
    traits = set(DEFAULT_CRICKET_PERSONA.traits)
    assert "ABSOLUTE_CANDOR" in traits
    assert "DRY_SASS" in traits
    assert "SELF_SKEPTICISM" in traits
    rules = "\n".join(
        (*DEFAULT_CRICKET_PERSONA.voice_rules, *DEFAULT_CRICKET_PERSONA.prohibitions)
    ).casefold()
    assert "cruel" in rules
    assert "quiet" in rules


def test_persona_line_is_sassy_but_preserves_factual_finding() -> None:
    result = Cricket().review(
        ReviewRequest(
            user_message="fix it",
            candidate_response="Done.",
            completion_claimed=True,
        )
    )
    finding = result.findings[0]
    line = persona_line_for_finding(finding, DEFAULT_CRICKET_PERSONA)
    assert "verified" in line.lower()
    rendered = render_blockquote(result)
    assert line in rendered
    assert finding.rationale in rendered


def test_personality_stays_silent_on_clean_pass() -> None:
    result = Cricket().review(ReviewRequest(user_message="u", candidate_response="c"))
    assert render_blockquote(result) == ""


def test_machine_readable_persona_matches_canonical_runtime_model() -> None:
    import json
    from pathlib import Path
    from cricket.persona import CricketPersona

    raw = json.loads(Path("personality/cricket-v1.json").read_text(encoding="utf-8"))
    artifact = CricketPersona.from_dict(raw)

    assert artifact == DEFAULT_CRICKET_PERSONA
