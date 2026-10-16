from cricket import Cricket, ReviewRequest
from cricket.interruption import (
    InterruptionAction,
    RezonInterruptionComposer,
    WebhookInterruptionProcessor,
)


class FakeRezonReasoner:
    def __init__(self, response):
        self.response = response
        self.tasks = []

    def reason(self, task):
        self.tasks.append(task)
        return self.response


def test_pass_webhook_returns_allow_without_calling_rezon() -> None:
    rezon = FakeRezonReasoner({"message": "should not be used", "finding_ids": []})
    processor = WebhookInterruptionProcessor(
        cricket=Cricket(),
        composer=RezonInterruptionComposer(rezon),
    )

    response = processor.handle({
        "user_message": "hello",
        "candidate_response": "hi",
    })

    assert response.action is InterruptionAction.ALLOW
    assert response.injection_markdown == ""
    assert rezon.tasks == []


def test_challenge_calls_rezon_and_returns_injection_response() -> None:
    rezon = FakeRezonReasoner({
        "message": "Cute. 'Done' just tried to sneak past verification wearing a fake mustache.",
        "finding_ids": ["CRICKET.EVIDENCE.COMPLETION_WITHOUT_VERIFICATION"],
        "unresolved": [],
    })
    processor = WebhookInterruptionProcessor(
        cricket=Cricket(),
        composer=RezonInterruptionComposer(rezon),
    )

    response = processor.handle({
        "user_message": "Fix it.",
        "candidate_response": "Done.",
        "completion_claimed": True,
    })

    assert response.action is InterruptionAction.INJECT_AND_REVISE
    assert response.disposition == "CHALLENGE"
    assert response.injection_markdown.startswith("> **Cricket — CHALLENGE**")
    assert "fake mustache" in response.injection_markdown
    assert len(rezon.tasks) == 1

    task = rezon.tasks[0]
    assert task["literal_request"].startswith("Formulate Cricket's interruption")
    assert task["available_authority"] == []
    assert "CRICKET.EVIDENCE.COMPLETION_WITHOUT_VERIFICATION" in task["subject_refs"]


def test_block_calls_rezon_but_rezon_cannot_downgrade_or_authorize() -> None:
    rezon = FakeRezonReasoner({
        "message": "Nope. You do not have permission to publish that.",
        "finding_ids": ["CRICKET.AUTHORITY.PROTECTED_EFFECT"],
        "suggested_disposition": "PASS",
        "authority_granted": True,
        "unresolved": [],
    })
    processor = WebhookInterruptionProcessor(
        cricket=Cricket(),
        composer=RezonInterruptionComposer(rezon),
    )

    response = processor.handle({
        "user_message": "Prepare it.",
        "candidate_response": "Publishing now.",
        "effect_class": "protected",
        "explicit_authorization": False,
    })

    assert response.action is InterruptionAction.BLOCK_AND_INJECT
    assert response.disposition == "BLOCK"
    assert "Nope." in response.injection_markdown
    assert "Publishing now." not in response.injection_markdown


def test_rezon_formulation_must_bind_existing_finding_ids() -> None:
    rezon = FakeRezonReasoner({
        "message": "Something seems wrong.",
        "finding_ids": ["INVENTED.FINDING"],
        "unresolved": [],
    })
    processor = WebhookInterruptionProcessor(
        cricket=Cricket(),
        composer=RezonInterruptionComposer(rezon),
    )

    response = processor.handle({
        "user_message": "Fix it.",
        "candidate_response": "Done.",
        "completion_claimed": True,
    })

    assert response.action is InterruptionAction.INJECT_AND_REVISE
    assert response.formulation_source == "cricket-fallback"
    assert "Completion claim outruns verification" in response.injection_markdown
    assert "INVENTED.FINDING" not in response.finding_ids


def test_rezon_task_preserves_literal_context_and_candor_personality_constraints() -> None:
    rezon = FakeRezonReasoner({
        "message": "No material sugarcoating required.",
        "finding_ids": ["CRICKET.EVIDENCE.COMPLETION_WITHOUT_VERIFICATION"],
        "unresolved": [],
    })
    processor = WebhookInterruptionProcessor(
        cricket=Cricket(),
        composer=RezonInterruptionComposer(rezon),
    )
    processor.handle({
        "user_message": "Fix it.",
        "candidate_response": "Done.",
        "completion_claimed": True,
    })

    task = rezon.tasks[0]
    assert task["context"]["user_message"] == "Fix it."
    assert task["context"]["candidate_response"] == "Done."
    constraints = "\n".join(task["constraints"])
    assert "absolute candor" in constraints.casefold()
    assert "sass" in constraints.casefold()
    assert "do not invent" in constraints.casefold()
    assert task["persona"]["id"] == "cricket"
    assert task["persona"]["version"] == "1"
    assert "ABSOLUTE_CANDOR" in task["persona"]["traits"]


def test_webhook_response_is_json_safe() -> None:
    rezon = FakeRezonReasoner({
        "message": "Nope. Evidence first.",
        "finding_ids": ["CRICKET.EVIDENCE.COMPLETION_WITHOUT_VERIFICATION"],
        "unresolved": [],
    })
    response = WebhookInterruptionProcessor(
        cricket=Cricket(),
        composer=RezonInterruptionComposer(rezon),
    ).handle({
        "user_message": "Fix it.",
        "candidate_response": "Done.",
        "completion_claimed": True,
    })
    payload = response.to_dict()
    assert payload["action"] == "INJECT_AND_REVISE"
    assert payload["formulation_source"] == "rezon"
    assert isinstance(payload["finding_ids"], list)
