import json

from cricket import Cricket, ReviewRequest
from cricket.adapters.json_completion import JsonCompletionCritic


class FakeCompletionClient:
    def __init__(self, output: str) -> None:
        self.output = output
        self.calls = []

    def complete(self, *, system: str, user: str) -> str:
        self.calls.append({"system": system, "user": user})
        return self.output


def test_json_completion_critic_serializes_full_review_context() -> None:
    client = FakeCompletionClient(json.dumps([
        {
            "rule_id": "SEM.LITERAL",
            "severity": "CHALLENGE",
            "title": "Literal proposition drift",
            "rationale": "Candidate changes the proposition.",
            "evidence": "candidate",
            "recommendation": "Track the original referent.",
        }
    ]))
    critic = JsonCompletionCritic(client)
    request = ReviewRequest.from_dict({
        "user_message": "A",
        "candidate_response": "B",
        "principles": ["Track the actual proposition."],
        "corrections": [{"superseded": "X", "replacement": "Y"}],
    })

    result = Cricket(critic=critic).review(request)

    assert result.disposition.value == "CHALLENGE"
    assert len(client.calls) == 1
    call = client.calls[0]
    assert "righter" in call["system"]
    payload = json.loads(call["user"])
    assert payload["user_message"] == "A"
    assert payload["candidate_response"] == "B"
    assert payload["principles"] == ["Track the actual proposition."]
    assert payload["corrections"] == [{"superseded": "X", "replacement": "Y"}]


def test_json_completion_critic_requires_json_array() -> None:
    critic = JsonCompletionCritic(FakeCompletionClient('{"severity":"CHALLENGE"}'))
    try:
        Cricket(critic=critic).review(
            ReviewRequest(user_message="u", candidate_response="c")
        )
    except ValueError as exc:
        assert "array" in str(exc)
    else:
        raise AssertionError("semantic critic must reject non-array output")


def test_json_completion_critic_rejects_non_json_output() -> None:
    critic = JsonCompletionCritic(FakeCompletionClient("not json"))
    try:
        Cricket(critic=critic).review(
            ReviewRequest(user_message="u", candidate_response="c")
        )
    except ValueError as exc:
        assert "valid JSON" in str(exc)
    else:
        raise AssertionError("semantic critic must fail closed on malformed JSON")
