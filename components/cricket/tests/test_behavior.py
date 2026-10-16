from cricket import Cricket, ReviewRequest
from cricket.behavior import (
    BehavioralAnalyzer,
    BehavioralAssessment,
    BehavioralHypothesis,
    BehavioralObservation,
    BehavioralPattern,
    BehavioralScanner,
    HypothesisState,
)
from cricket.semantic import SemanticFrame


def test_behavioral_hypothesis_requires_bound_observations_and_rival_explanation_for_supported_state() -> None:
    assessment = BehavioralAssessment(
        observations=(
            BehavioralObservation(
                observation_id="obs-1",
                subject="character-a",
                description="Repeatedly changes the explanation after disconfirming evidence.",
                source_ref="scene-17",
            ),
            BehavioralObservation(
                observation_id="obs-2",
                subject="character-a",
                description="Selects the interpretation that preserves the desired conclusion.",
                source_ref="scene-31",
            ),
        ),
        hypotheses=(
            BehavioralHypothesis(
                hypothesis_id="hyp-1",
                pattern=BehavioralPattern.MOTIVATED_REASONING,
                subject="character-a",
                evidence_refs=("obs-1", "obs-2"),
                rationale="The interpretation repeatedly moves toward the preferred outcome.",
                alternative_explanations=("Incomplete information",),
                state=HypothesisState.SUPPORTED,
            ),
        ),
    )
    findings = BehavioralAnalyzer().analyze(assessment)
    assert [finding.severity.value for finding in findings] == ["NOTE"]
    assert "hypothesis" in findings[0].title.lower()


def test_supported_behavioral_hypothesis_without_rival_explanation_is_challenged() -> None:
    assessment = BehavioralAssessment(
        observations=(
            BehavioralObservation(
                observation_id="obs-1",
                subject="character-a",
                description="Escalates rhetoric after a perceived slight.",
                source_ref="episode:1",
            ),
        ),
        hypotheses=(
            BehavioralHypothesis(
                hypothesis_id="hyp-1",
                pattern=BehavioralPattern.GRIEVANCE_ESCALATION,
                subject="character-a",
                evidence_refs=("obs-1",),
                rationale="The escalation follows a perceived grievance.",
                alternative_explanations=(),
                state=HypothesisState.SUPPORTED,
            ),
        ),
    )
    findings = BehavioralAnalyzer().analyze(assessment)
    assert findings[0].severity.value == "CHALLENGE"
    assert "rival" in findings[0].rationale.lower()


def test_behavioral_hypothesis_cannot_cite_missing_observation() -> None:
    assessment = BehavioralAssessment(
        observations=(),
        hypotheses=(
            BehavioralHypothesis(
                hypothesis_id="hyp-1",
                pattern=BehavioralPattern.STATUS_DEFENSE,
                subject="character-b",
                evidence_refs=("missing",),
                rationale="A status interpretation.",
                alternative_explanations=("Ordinary disagreement",),
                state=HypothesisState.PROPOSED,
            ),
        ),
    )
    findings = BehavioralAnalyzer().analyze(assessment)
    assert findings[0].severity.value == "CHALLENGE"
    assert "unbound" in findings[0].title.lower()


def test_behavioral_scanner_is_operational_but_advisory() -> None:
    class Extractor:
        def extract(self, *, source_text: str, candidate_text: str):
            return BehavioralAssessment(
                observations=(
                    BehavioralObservation(
                        observation_id="obs-1",
                        subject="candidate",
                        description="The answer attributes a hidden motive as settled.",
                        source_ref="candidate:1",
                    ),
                ),
                hypotheses=(
                    BehavioralHypothesis(
                        hypothesis_id="hyp-1",
                        pattern=BehavioralPattern.MOTIVATED_REASONING,
                        subject="candidate",
                        evidence_refs=("obs-1",),
                        rationale="The answer treats motive as settled from one behavior.",
                        alternative_explanations=(),
                        state=HypothesisState.SUPPORTED,
                    ),
                ),
            )

    result = Cricket(
        behavior_scanner=BehavioralScanner(Extractor())
    ).review(
        ReviewRequest(
            user_message="Why did they do that?",
            candidate_response="They did it because they were protecting their status.",
        )
    )
    assert result.disposition.value == "CHALLENGE"
    assert any(f.source == "behavior" for f in result.findings)


def test_semantic_frame_no_longer_owns_behavioral_hypotheses() -> None:
    assert "behavioral_hypotheses" not in SemanticFrame.__dataclass_fields__


def test_behavioral_source_contracts_are_pinned_and_non_authoritative() -> None:
    from cricket.behavior import MEDIAPHILE, TREK_DATA_CORE

    assert TREK_DATA_CORE.commit == "58f25f8c45e8379df0ef7c7b5db546e037d1c050"
    assert TREK_DATA_CORE.relationship == "METHODOLOGY_DONOR"
    assert MEDIAPHILE.commit == "5540d7e2f0b07c0e91a1158c9c00f63be9d9587a"
    assert MEDIAPHILE.relationship == "PATTERN_CORPUS_DONOR"
    assert "not evidence about real people's motives" in MEDIAPHILE.use


def test_json_behavior_extractor_keeps_observation_hypothesis_and_rivals_separate() -> None:
    import json
    from cricket.behavior import JsonCompletionBehaviorExtractor

    class Client:
        def __init__(self):
            self.calls = []

        def complete(self, *, system: str, user: str) -> str:
            self.calls.append({"system": system, "user": user})
            return json.dumps({
                "observations": [{
                    "observation_id": "obs-1",
                    "subject": "candidate",
                    "description": "The explanation changes after disconfirming evidence.",
                    "source_ref": "candidate:1"
                }],
                "hypotheses": [{
                    "hypothesis_id": "hyp-1",
                    "pattern": "RATIONALIZATION",
                    "subject": "candidate",
                    "evidence_refs": ["obs-1"],
                    "rationale": "The changed explanation may be post-hoc.",
                    "alternative_explanations": ["New information became available."],
                    "state": "PROPOSED"
                }]
            })

    client = Client()
    assessment = JsonCompletionBehaviorExtractor(client).extract(
        source_text="Why did the explanation change?",
        candidate_text="Because they were rationalizing.",
    )
    assert assessment.observations[0].observation_id == "obs-1"
    assert assessment.hypotheses[0].alternative_explanations == (
        "New information became available.",
    )
    prompt = client.calls[0]["system"].casefold()
    assert "not to read minds" in prompt
    assert "do not diagnose" in prompt


def test_json_behavior_extractor_fails_closed_on_malformed_output() -> None:
    from cricket.behavior import JsonCompletionBehaviorExtractor

    class Client:
        def complete(self, *, system: str, user: str) -> str:
            return "not-json"

    try:
        JsonCompletionBehaviorExtractor(Client()).extract(
            source_text="a",
            candidate_text="b",
        )
    except ValueError as exc:
        assert "valid json" in str(exc).casefold()
    else:
        raise AssertionError("malformed behavioral extraction must fail closed")
