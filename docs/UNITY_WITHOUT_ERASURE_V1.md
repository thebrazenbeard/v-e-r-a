# Unity without erasure: first executable boundary (V1)

This is a source-tested integration step, not proof of emergent consciousness or independently self-improving intelligence. It implements a testable engineering principle: Vera can form a coherent account of a task while retaining the attributable positions of different cognitive participants.

Three simultaneous requirements:

1. Individuality. Each participant declares a distinct identifier, role, source reference and SHA-256 digest, and a pointer to its own local state. The projection does not copy or mutate that local state.
2. Integration. Mosaic's existing CoreDeliberationEngine creates a receipt recording the Core's initial answer, specialist perspectives, optional independent verifier, and the Core's reconsidered answer. The V-E-R-A adapter checks the source receipt digest and preserves every position intact.
3. Unity. Vera derives one digest-bound collective view: current synthesis plus all individual contributions, unresolved disagreement, and Mosaic's original decision status. A collective view is not unanimity, identity fusion, or permission to act.

Invariants: The initial Core view cannot be retroactively changed by reconsideration. Specialist dissent is retained even when the final Core answer differs. Roles, local state references, original contributions and dissent cannot be silently removed or rewritten. The projection is recomputed from its embedded source receipt and exact participant directory.

The Core is still the reasoning actor in the current Mosaic draft. This is preservation of individuality, not a claim that specialists already have persistent independent goals or subjective experience.

## Source and executable qualification

Vera integration base: thebrazenbeard/v-e-r-a at a1bbb9259ce7f3ce7ff18895257a0a7e162d228e.
Mosaic Core: thebrazenbeard/mosaic draft PR #10 at afd5e7ab598bfbf3cf0c5685611f9fe399de101e.

The frozen fixture tests/fixtures/mosaic_plurality_v1.json was generated with the actual Mosaic CoreDeliberationEngine using an injected deterministic fake Core and Critic; no neural model was involved. Set MOSAIC_SOURCE_ROOT to an exact checkout of that Mosaic source to run the cross-repository tests.

To use a genuine Mosaic decision receipt and declared participant source/state references:

    python -m integration.plural_cognition_cli compose --receipt receipt.json --participants participants.json --output projection.json
    python -m integration.plural_cognition_cli verify --projection projection.json

The writer creates new output exclusively. Readback recomputes the result, validates attribution, and detects tampering or omitted dissent. Actual subprocess, process-restart and JSON readback tests are included.

## Limits and next gates

Hashes detect inconsistency but cannot authenticate a claimed model or participant. A malicious origin could rehash altered content. Verified participant identity, independently durable state ownership, and signed Intranel/Bus transport are not delivered here.

This adapter does not execute protected effects or grant authorization. Vera Mono remains durable task/lifecycle/authority owner, and existing PORTAL and Pre-Active remain responsible for governed execution and reconciliation. This adapter adds no competing scheduler, language model backend, or task store.

Next: bind exact participant origin and individually durable state to existing substrates; demonstrate two genuinely separately running contributors, their conflicting responses and recovery after independent process restarts; keep disagreement through Mosaic's reasoning cycle; link the advisory synthesis receipt to the Vera Mono exact task head; then run adversarial equal-budget capability tests.

The larger philosophical hypothesis that intelligences participate in some deeper unity remains unproven. The non-erasure invariant is executable and testable.
