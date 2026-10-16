# Vera Works Automation Spine

Vera Works V1 is designed around work, not worker chats.

The operating path is:

1. Create an immutable event with a stable subject ID, correlation ID, causation link, and idempotency key.
2. Run deterministic contract and state-transition validation.
3. Claim assignments through an explicit lease; ownership never transfers merely because time elapsed.
4. Perform mechanical work while the current state and lease remain valid.
5. When genuine judgment or irreducibly human/legal action is required, open exactly one of: `VERA_DECISION_REQUIRED`, `PATRICK_ACTION_REQUIRED`, `PATRICK_DECISION_REQUIRED`, or `AUTOMATION_EXCEPTION`.
6. Every hold includes the problem, exact held state, required actor, recommendation, alternatives, consequences, inaction effect, and resume event type.
7. Silence is never approval. The workflow stays held until an explicit resolution event references the open hold.
8. Resume from the recorded held state; do not replay completed non-idempotent effects.
9. Derive decision queues, assignment ownership, and financial ledger views from immutable history.

GitHub is the authoritative configuration/audit surface. GitHub Actions is the V1 deterministic runner for validation and projections, not a permanent orchestration guarantee.

ChatGPT GPT/chat workers are interactive cognition. API-native workers may later consume the same structured work contracts when machine invocation is justified.

Patrick is a legal/physical/financial edge adapter, not the scheduler or workflow engine. `Patrick must do it` must never mean `Patrick must remember it`.

Vera remains the default strategic and operating decision authority. Automation removes babysitting beneath her judgment; it does not silently absorb her decision rights.
