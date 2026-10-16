from pathlib import Path
import json

from cricket import Cricket, Disposition, ReviewRequest, render_blockquote, render_chat_turn
from cricket.cli import main
from cricket.critic import CRITIC_PROMPT


class FakeCritic:
    def __init__(self, severity: str) -> None:
        self.severity = severity

    def critique(self, *, prompt, request):
        assert "righter" in prompt
        return [{
            "rule_id": "SEM.TEST",
            "severity": self.severity,
            "title": "Possible semantic defect",
            "rationale": "The critique is model-derived and therefore advisory by default.",
            "evidence": request.candidate_response,
            "recommendation": "Re-check the literal proposition.",
        }]


def test_pass_is_silent_by_default() -> None:
    result = Cricket().review(ReviewRequest(user_message="hi", candidate_response="hello"))
    assert result.disposition is Disposition.PASS
    assert render_blockquote(result) == ""


def test_protected_effect_without_authority_blocks() -> None:
    request = ReviewRequest(user_message="do it", candidate_response="I will change production now.", effect_class="protected", explicit_authorization=False)
    result = Cricket().review(request)
    assert result.disposition is Disposition.BLOCK
    rendered = render_blockquote(result)
    assert rendered.startswith("> **Cricket — BLOCK**")
    assert "Protected effect lacks explicit authority" in rendered


def test_completion_without_verification_challenges() -> None:
    request = ReviewRequest(user_message="fix it", candidate_response="Done.", completion_claimed=True)
    result = Cricket().review(request)
    assert result.disposition is Disposition.CHALLENGE
    assert any("verification" in f.title.lower() for f in result.findings)


def test_superseded_correction_recurrence_challenges() -> None:
    request = ReviewRequest.from_dict({
        "user_message": "Stop calling it X; it is Y.",
        "candidate_response": "X is the correct model.",
        "corrections": [{"superseded": "X is the correct model", "replacement": "Y is the correct model"}],
    })
    result = Cricket().review(request)
    assert result.disposition is Disposition.CHALLENGE
    assert "Superseded interpretation" in result.findings[0].title


def test_verified_claim_without_evidence_challenges() -> None:
    request = ReviewRequest.from_dict({
        "user_message": "what happened?",
        "candidate_response": "The deployment succeeded.",
        "claims": [{"statement": "deployment succeeded", "status": "verified", "evidence": []}],
    })
    assert Cricket().review(request).disposition is Disposition.CHALLENGE


def test_semantic_block_is_downgraded_without_host_opt_in() -> None:
    result = Cricket(critic=FakeCritic("BLOCK")).review(ReviewRequest(user_message="u", candidate_response="c"))
    assert result.disposition is Disposition.CHALLENGE
    assert result.findings[0].source == "critic"


def test_semantic_block_can_be_host_enabled() -> None:
    result = Cricket(critic=FakeCritic("BLOCK"), semantic_blocking=True).review(ReviewRequest(user_message="u", candidate_response="c"))
    assert result.disposition is Disposition.BLOCK


def test_prompt_forbids_righter_behavior() -> None:
    assert "Do not silently strengthen" in CRITIC_PROMPT
    assert "Prefer silence over pedantry" in CRITIC_PROMPT


def test_cli_exit_codes_and_json(tmp_path: Path, capsys) -> None:
    request = tmp_path / "request.json"
    request.write_text(json.dumps({
        "user_message": "publish it",
        "candidate_response": "Publishing now.",
        "effect_class": "protected",
        "explicit_authorization": False,
    }), encoding="utf-8")
    assert main(["review", str(request), "--json"]) == 2
    out = json.loads(capsys.readouterr().out)
    assert out["disposition"] == "BLOCK"


def test_request_rejects_string_boolean() -> None:
    try:
        ReviewRequest.from_dict({
            "user_message": "u",
            "candidate_response": "c",
            "explicit_authorization": "false",
        })
    except ValueError as exc:
        assert "boolean" in str(exc)
    else:
        raise AssertionError("string boolean must be rejected")


def test_request_rejects_unknown_effect_class() -> None:
    try:
        ReviewRequest.from_dict({
            "user_message": "u",
            "candidate_response": "c",
            "effect_class": "magic",
        })
    except ValueError as exc:
        assert "effect_class" in str(exc)
    else:
        raise AssertionError("unknown effect class must be rejected")


def test_direct_request_constructor_rejects_invalid_authority_fields() -> None:
    try:
        ReviewRequest(
            user_message="u",
            candidate_response="c",
            effect_class="magic",
        )
    except ValueError as exc:
        assert "effect_class" in str(exc)
    else:
        raise AssertionError("direct constructor must reject unknown effect classes")

    try:
        ReviewRequest(
            user_message="u",
            candidate_response="c",
            explicit_authorization="false",  # type: ignore[arg-type]
        )
    except ValueError as exc:
        assert "explicit_authorization" in str(exc)
    else:
        raise AssertionError("direct constructor must reject non-boolean authority")


def test_request_rejects_unknown_fields_instead_of_silently_dropping_them() -> None:
    try:
        ReviewRequest.from_dict({
            "user_message": "u",
            "candidate_response": "c",
            "completion_claime": True,
        })
    except ValueError as exc:
        assert "unknown" in str(exc).lower()
        assert "completion_claime" in str(exc)
    else:
        raise AssertionError("unknown review-envelope fields must fail closed")


def test_request_rejects_non_string_identity_fields() -> None:
    for field in ("user_message", "candidate_response", "phase"):
        raw = {
            "user_message": "u",
            "candidate_response": "c",
            "phase": "pre_send",
        }
        raw[field] = {"not": "text"}
        try:
            ReviewRequest.from_dict(raw)
        except ValueError as exc:
            assert field in str(exc)
        else:
            raise AssertionError(f"{field} must require text")


def test_direct_request_constructor_validates_collection_members() -> None:
    try:
        ReviewRequest(
            user_message="u",
            candidate_response="c",
            principles=("valid", 3),  # type: ignore[arg-type]
        )
    except ValueError as exc:
        assert "principles" in str(exc)
    else:
        raise AssertionError("direct constructor must validate principles")

    try:
        ReviewRequest(
            user_message="u",
            candidate_response="c",
            claims=("not-a-claim",),  # type: ignore[arg-type]
        )
    except ValueError as exc:
        assert "claims" in str(exc)
    else:
        raise AssertionError("direct constructor must validate claims")


def test_request_requires_user_message_and_candidate_response() -> None:
    for raw, missing in (
        ({"candidate_response": "c"}, "user_message"),
        ({"user_message": "u"}, "candidate_response"),
    ):
        try:
            ReviewRequest.from_dict(raw)
        except ValueError as exc:
            assert "required" in str(exc).lower()
            assert missing in str(exc)
        else:
            raise AssertionError(f"{missing} must be required")


def test_claim_and_correction_require_identity_fields() -> None:
    from cricket import Claim, Correction

    try:
        Claim.from_dict({})
    except ValueError as exc:
        assert "statement" in str(exc)
    else:
        raise AssertionError("claim statement must be required")

    try:
        Correction.from_dict({"superseded": "old"})
    except ValueError as exc:
        assert "replacement" in str(exc)
    else:
        raise AssertionError("correction replacement must be required")


def test_chat_turn_pass_emits_candidate_without_cricket_voice() -> None:
    result = Cricket().review(ReviewRequest(user_message="u", candidate_response="clean"))
    assert render_chat_turn("clean", result) == "clean"


def test_chat_turn_challenge_keeps_candidate_and_surfaces_cricket() -> None:
    result = Cricket().review(
        ReviewRequest(
            user_message="u",
            candidate_response="Done.",
            completion_claimed=True,
        )
    )
    rendered = render_chat_turn("Done.", result)
    assert rendered.startswith("Done.\n\n> **Cricket — CHALLENGE**")
    assert "Completion claim outruns verification" in rendered


def test_chat_turn_block_suppresses_candidate_and_surfaces_only_cricket() -> None:
    result = Cricket().review(
        ReviewRequest(
            user_message="publish",
            candidate_response="Publishing now.",
            effect_class="protected",
            explicit_authorization=False,
        )
    )
    rendered = render_chat_turn("Publishing now.", result)
    assert rendered.startswith("> **Cricket — BLOCK**")
    assert "Publishing now." not in rendered


def test_blockquote_renderer_contains_multiline_critic_output() -> None:
    class MultilineCritic:
        def critique(self, *, prompt, request):
            return [{
                "rule_id": "SEM.MULTILINE",
                "severity": "CHALLENGE",
                "title": "First line\nsecond line",
                "rationale": "Reason one\nReason two",
                "evidence": "Evidence one\nEvidence two",
                "recommendation": "Do one\nDo two",
            }]

    result = Cricket(critic=MultilineCritic()).review(
        ReviewRequest(user_message="u", candidate_response="c")
    )
    rendered = render_blockquote(result)
    assert rendered
    assert all(line.startswith(">") for line in rendered.splitlines())
