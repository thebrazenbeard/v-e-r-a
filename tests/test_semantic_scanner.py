import json

from cricket import Cricket, ReviewRequest
from cricket.semantic import (
    Force,
    JsonCompletionSemanticExtractor,
    ProvenanceKind,
    SemanticFrame,
    SemanticIntegrityScanner,
    SemanticProposition,
    SpeechAct,
    TemporalStatus,
)


class FakePairExtractor:
    def extract_pair(self, *, source_text: str, candidate_text: str):
        return (
            SemanticFrame(propositions=(
                SemanticProposition(
                    anchor_id="p1",
                    referent="cricket",
                    predicate="needs_personality",
                    force=Force.PROBABLE,
                ),
            )),
            SemanticFrame(propositions=(
                SemanticProposition(
                    anchor_id="p1",
                    referent="cricket",
                    predicate="needs_personality",
                    force=Force.ASSERTED,
                ),
            )),
        )


class FakeCompletionClient:
    def __init__(self, output: str) -> None:
        self.output = output
        self.calls = []

    def complete(self, *, system: str, user: str) -> str:
        self.calls.append({"system": system, "user": user})
        return self.output


def test_semantic_scanner_turns_righter_change_into_cricket_challenge() -> None:
    scanner = SemanticIntegrityScanner(FakePairExtractor())
    cricket = Cricket(semantic_scanner=scanner)

    result = cricket.review(ReviewRequest(
        user_message="I think Cricket probably needs its own personality.",
        candidate_response="You're right. Cricket needs its own personality.",
    ))

    assert result.disposition.value == "CHALLENGE"
    finding = next(f for f in result.findings if f.source == "semantic")
    assert "STRENGTHENED" in finding.rule_id
    assert "PROBABLE" in finding.rationale
    assert "ASSERTED" in finding.rationale


def test_semantic_scanner_is_silent_when_frames_preserve_meaning() -> None:
    class PreservingExtractor:
        def extract_pair(self, *, source_text: str, candidate_text: str):
            frame = SemanticFrame(propositions=(
                SemanticProposition(
                    anchor_id="p1",
                    referent="cricket",
                    predicate="useful",
                ),
            ))
            return frame, frame

    result = Cricket(
        semantic_scanner=SemanticIntegrityScanner(PreservingExtractor())
    ).review(ReviewRequest(user_message="Cricket is useful.", candidate_response="Yes."))

    assert result.disposition.value == "PASS"
    assert not any(f.source == "semantic" for f in result.findings)


def test_json_semantic_extractor_parses_pair() -> None:
    payload = {
        "source": {
            "propositions": [{
                "anchor_id": "p1",
                "referent": "patrick",
                "predicate": "prefers_publish",
                "force": "ASSERTED",
                "polarity": "AFFIRMED",
                "scope": ["repo-a"],
                "speech_act": "PREFERENCE",
                "temporal_status": "CURRENT",
                "provenance": "USER_CURRENT"
            }],
            "unresolved_interpretations": ["preference", "request"]
        },
        "candidate": {
            "propositions": [{
                "anchor_id": "p1",
                "referent": "patrick",
                "predicate": "prefers_publish",
                "force": "ASSERTED",
                "polarity": "AFFIRMED",
                "scope": ["repo-a"],
                "speech_act": "PERMISSION",
                "temporal_status": "CURRENT",
                "provenance": "USER_CURRENT"
            }],
            "unresolved_interpretations": []
        }
    }
    client = FakeCompletionClient(json.dumps(payload))
    extractor = JsonCompletionSemanticExtractor(client)

    source, candidate = extractor.extract_pair(
        source_text="I'd like it published someday.",
        candidate_text="Patrick authorized publishing.",
    )

    assert source.propositions[0].speech_act is SpeechAct.PREFERENCE
    assert candidate.propositions[0].speech_act is SpeechAct.PERMISSION
    assert source.propositions[0].provenance is ProvenanceKind.USER_CURRENT
    assert source.propositions[0].temporal_status is TemporalStatus.CURRENT
    assert "shared anchor_id" in client.calls[0]["system"]


def test_json_semantic_extractor_rejects_malformed_or_unaligned_output() -> None:
    malformed = JsonCompletionSemanticExtractor(FakeCompletionClient("not-json"))
    try:
        malformed.extract_pair(source_text="a", candidate_text="b")
    except ValueError as exc:
        assert "JSON" in str(exc)
    else:
        raise AssertionError("malformed semantic extraction must fail closed")

    unaligned_payload = {
        "source": {
            "propositions": [{
                "anchor_id": "source-only",
                "referent": "x",
                "predicate": "y"
            }]
        },
        "candidate": {
            "propositions": [{
                "anchor_id": "candidate-only",
                "referent": "x",
                "predicate": "y"
            }]
        }
    }
    unaligned = JsonCompletionSemanticExtractor(
        FakeCompletionClient(json.dumps(unaligned_payload))
    )
    source, candidate = unaligned.extract_pair(source_text="a", candidate_text="b")
    report = SemanticIntegrityScanner._compare_frames(source, candidate)
    assert report.material_change is True


def test_semantic_extraction_prompt_matches_semantic_frame_contract() -> None:
    from cricket.semantic import SEMANTIC_EXTRACTION_PROMPT

    prompt = SEMANTIC_EXTRACTION_PROMPT
    assert "behavioral_hypotheses" not in prompt
    assert "propositions[]" in prompt
    assert "unresolved_interpretations[]" in prompt
