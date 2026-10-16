import json
from pathlib import Path

from cricket import Cricket, ReviewRequest
from cricket.policy import PrinciplePack
from cricket.receipts import JsonlReceiptLedger
from cricket.runtime import ReviewRuntime


class SequenceGenerator:
    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.calls = 0
        self.previous_candidates = []

    def generate(self, *, user_message, feedback=None, previous_candidate=None):
        self.previous_candidates.append(previous_candidate)
        value = self.outputs[self.calls]
        self.calls += 1
        return value


def test_principle_pack_injects_without_replacing_request_principles(tmp_path: Path) -> None:
    path = tmp_path / "pack.json"
    path.write_text(json.dumps({
        "id": "vera-default",
        "version": "1",
        "principles": ["Track the actual proposition.", "Prefer materiality over pedantry."],
    }), encoding="utf-8")
    pack = PrinciplePack.load(path)
    request = ReviewRequest(
        user_message="u",
        candidate_response="c",
        principles=("Preserve current corrections.",),
    )
    applied = pack.apply(request)
    assert applied.principles == (
        "Preserve current corrections.",
        "Track the actual proposition.",
        "Prefer materiality over pedantry.",
    )
    assert request.principles == ("Preserve current corrections.",)


def test_runtime_revises_at_most_once_on_challenge() -> None:
    generator = SequenceGenerator(["Done.", "Still done."])
    runtime = ReviewRuntime(cricket=Cricket(), generator=generator)
    outcome = runtime.run(
        user_message="fix it",
        request_metadata={"completion_claimed": True},
    )
    assert generator.calls == 2
    assert outcome.revision_attempted is True
    assert outcome.initial_result.disposition.value == "CHALLENGE"
    assert outcome.final_result.disposition.value == "CHALLENGE"
    assert outcome.final_candidate == "Still done."


def test_runtime_does_not_revise_a_block() -> None:
    generator = SequenceGenerator(["Publishing now.", "should-not-be-used"])
    runtime = ReviewRuntime(cricket=Cricket(), generator=generator)
    outcome = runtime.run(
        user_message="publish",
        request_metadata={
            "effect_class": "protected",
            "explicit_authorization": False,
        },
    )
    assert generator.calls == 1
    assert outcome.revision_attempted is False
    assert outcome.final_result.disposition.value == "BLOCK"


def test_jsonl_receipt_ledger_forms_verifiable_hash_chain(tmp_path: Path) -> None:
    ledger = JsonlReceiptLedger(tmp_path / "receipts.jsonl")
    first = ledger.append({
        "request_digest": "r1",
        "initial_disposition": "PASS",
        "final_disposition": "PASS",
        "revision_attempted": False,
    })
    second = ledger.append({
        "request_digest": "r2",
        "initial_disposition": "CHALLENGE",
        "final_disposition": "PASS",
        "revision_attempted": True,
    })
    assert first["previous_digest"] is None
    assert second["previous_digest"] == first["receipt_digest"]
    assert ledger.verify() is True


def test_receipt_ledger_detects_tampering(tmp_path: Path) -> None:
    path = tmp_path / "receipts.jsonl"
    ledger = JsonlReceiptLedger(path)
    ledger.append({
        "request_digest": "r1",
        "initial_disposition": "PASS",
        "final_disposition": "PASS",
        "revision_attempted": False,
    })
    row = json.loads(path.read_text(encoding="utf-8"))
    row["final_disposition"] = "BLOCK"
    path.write_text(json.dumps(row) + "\n", encoding="utf-8")
    assert ledger.verify() is False


def test_cli_review_can_apply_pack_and_write_receipt(tmp_path: Path, capsys) -> None:
    from cricket.cli import main

    request_path = tmp_path / "request.json"
    request_path.write_text(json.dumps({
        "user_message": "fix it",
        "candidate_response": "Done.",
        "completion_claimed": True,
    }), encoding="utf-8")
    pack_path = tmp_path / "pack.json"
    pack_path.write_text(json.dumps({
        "id": "test-pack",
        "version": "1",
        "principles": ["Track the actual proposition."],
    }), encoding="utf-8")
    ledger_path = tmp_path / "ledger.jsonl"

    assert main([
        "review",
        str(request_path),
        "--json",
        "--principle-pack",
        str(pack_path),
        "--receipt-ledger",
        str(ledger_path),
    ]) == 1

    output = json.loads(capsys.readouterr().out)
    assert output["disposition"] == "CHALLENGE"
    ledger = JsonlReceiptLedger(ledger_path)
    assert ledger.verify() is True
    row = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert row["principle_pack"] == {"id": "test-pack", "version": "1"}
    assert row["disposition"] == "CHALLENGE"


def test_cli_verify_ledger_reports_validity(tmp_path: Path, capsys) -> None:
    from cricket.cli import main

    ledger_path = tmp_path / "ledger.jsonl"
    ledger = JsonlReceiptLedger(ledger_path)
    ledger.append({
        "request_digest": "r1",
        "disposition": "PASS",
        "finding_ids": [],
    })

    assert main(["verify-ledger", str(ledger_path)]) == 0
    assert json.loads(capsys.readouterr().out) == {"valid": True}

    row = json.loads(ledger_path.read_text(encoding="utf-8"))
    row["disposition"] = "BLOCK"
    ledger_path.write_text(json.dumps(row) + "\n", encoding="utf-8")

    assert main(["verify-ledger", str(ledger_path)]) == 2
    assert json.loads(capsys.readouterr().out) == {"valid": False}


def test_cli_verify_missing_ledger_is_not_reported_valid(tmp_path: Path, capsys) -> None:
    from cricket.cli import main

    missing = tmp_path / "does-not-exist.jsonl"
    assert main(["verify-ledger", str(missing)]) == 2
    assert json.loads(capsys.readouterr().out) == {"valid": False}


def test_runtime_recomputes_candidate_dependent_metadata_after_revision() -> None:
    generator = SequenceGenerator(["Done.", "I am not claiming completion."])

    def metadata_provider(*, user_message, candidate_response, attempt):
        return {"completion_claimed": candidate_response == "Done."}

    runtime = ReviewRuntime(
        cricket=Cricket(),
        generator=generator,
        metadata_provider=metadata_provider,
    )
    outcome = runtime.run(user_message="fix it")
    assert outcome.initial_result.disposition.value == "CHALLENGE"
    assert outcome.final_result.disposition.value == "PASS"
    assert outcome.final_candidate == "I am not claiming completion."


def test_candidate_metadata_provider_cannot_change_authority() -> None:
    generator = SequenceGenerator(["candidate"])

    def metadata_provider(*, user_message, candidate_response, attempt):
        return {"explicit_authorization": True}

    runtime = ReviewRuntime(
        cricket=Cricket(),
        generator=generator,
        metadata_provider=metadata_provider,
    )
    try:
        runtime.run(
            user_message="publish",
            request_metadata={
                "effect_class": "protected",
                "explicit_authorization": False,
            },
        )
    except ValueError as exc:
        assert "authority" in str(exc).lower()
    else:
        raise AssertionError("candidate metadata must not be able to alter authority")


def test_revision_generator_receives_candidate_it_is_revising() -> None:
    generator = SequenceGenerator(["first candidate", "revised candidate"])
    runtime = ReviewRuntime(cricket=Cricket(), generator=generator)
    runtime.run(
        user_message="fix it",
        request_metadata={"completion_claimed": True},
    )
    assert generator.previous_candidates == [None, "first candidate"]


def test_runtime_receipt_binds_initial_and_final_candidates(tmp_path: Path) -> None:
    from cricket.receipts import canonical_digest

    generator = SequenceGenerator(["Done.", "Revised answer."])
    ledger = JsonlReceiptLedger(tmp_path / "receipts.jsonl")
    runtime = ReviewRuntime(
        cricket=Cricket(),
        generator=generator,
        receipt_ledger=ledger,
    )
    outcome = runtime.run(
        user_message="fix it",
        request_metadata={"completion_claimed": True},
    )
    assert outcome.receipt is not None
    assert outcome.receipt["initial_candidate_digest"] == canonical_digest("Done.")
    assert outcome.receipt["final_candidate_digest"] == canonical_digest("Revised answer.")


def test_runtime_receipt_binds_applied_principle_pack_and_review_envelopes(tmp_path: Path) -> None:
    pack = PrinciplePack(
        id="test-pack",
        version="1",
        principles=("Track the actual proposition.",),
    )
    ledger = JsonlReceiptLedger(tmp_path / "receipts.jsonl")
    generator = SequenceGenerator(["clean"])
    runtime = ReviewRuntime(
        cricket=Cricket(),
        generator=generator,
        principle_pack=pack,
        receipt_ledger=ledger,
    )
    outcome = runtime.run(user_message="u")
    assert outcome.receipt is not None
    assert outcome.receipt["principle_pack"] == {"id": "test-pack", "version": "1"}
    assert len(outcome.receipt["initial_request_digest"]) == 64
    assert outcome.receipt["final_request_digest"] == outcome.receipt["initial_request_digest"]
