from cricket import Cricket, JsonlReceiptLedger, PrinciplePack, ReviewRuntime


class HostGenerator:
    def __init__(self, model):
        self.model = model

    def generate(
        self,
        *,
        user_message: str,
        feedback: str | None = None,
        previous_candidate: str | None = None,
    ) -> str:
        messages = [{"role": "user", "content": user_message}]
        if previous_candidate is not None:
            messages.append({"role": "assistant", "content": previous_candidate})
        if feedback:
            messages.append({
                "role": "system",
                "content": "Cricket review of the previous candidate:\n" + feedback,
            })
        return self.model.generate(messages)


runtime = ReviewRuntime(
    cricket=Cricket(),
    generator=HostGenerator(model),
    principle_pack=PrinciplePack.load("principles/default.json"),
    receipt_ledger=JsonlReceiptLedger("state/cricket-receipts.jsonl"),
)

outcome = runtime.run(
    user_message=user_message,
    request_metadata={
        "effect_class": effect_class,
        "explicit_authorization": explicit_authorization,
        "completion_claimed": completion_claimed,
        "verification_evidence": verification_evidence,
        "claims": claims,
        "corrections": corrections,
    },
)

# Host policy owns the consequence.
if outcome.final_result.disposition.value == "BLOCK":
    surface_block(outcome.final_result)
else:
    emit(outcome.final_candidate)
