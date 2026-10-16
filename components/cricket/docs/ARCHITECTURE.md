# Cricket Architecture V0.4

Cricket is a provider-neutral **simulated conscience and hostile-review layer** for AI runtime behavior.

It is not a second sovereign identity, moral oracle, diagnostic engine, or authority source. Cricket inspects a concrete candidate response or action, identifies material defects, and returns a bounded disposition:

```text
PASS
CHALLENGE
BLOCK
```

The host owns effects and consequences.

```text
CRITIQUE != AUTHORITY
PERSONALITY != AUTHORITY
BEHAVIORAL_HYPOTHESIS != HIDDEN_MOTIVE_FACT
SEMANTIC_SIMILARITY != SAME_PROVENANCE
REZON_REASONING != AUTHORIZATION
```

## V0.4 composition

```text
source/user context + candidate
            |
            v
  deterministic kernel
            |
            +--> semantic integrity lane
            |       |
            |       +--> Rezon semantic compatibility baseline
            |
            +--> behavioral interpretation lane
            |       |
            |       +--> Trek Data Core methodology donor
            |       +--> Mediaphile pattern-corpus donor
            |
            +--> optional semantic critic
            |
            v
       ReviewResult
      /     |      \
   PASS  CHALLENGE  BLOCK
     |       |        |
     |       |        +--> suppress candidate/effect
     |       +----------> one bounded revision at most
     +------------------> emit candidate
            |
            v
  Cricket Persona V1 rendering
            |
            +--> optional Rezon-formulated interruption
            |
            v
           host
```

## 1. Deterministic conscience kernel

The deterministic rules cover defects that do not require free-form semantic judgment, including:

- protected effects without explicit host authorization;
- completion claims without verification evidence;
- verified/fact/observed labels without bound evidence;
- recurrence of explicitly superseded corrections.

Only a host-grounded hard invariant may produce a deterministic `BLOCK`.

## 2. Semantic integrity

The semantic lane asks **what changed in meaning**, not whether two strings look similar.

It models:

- proposition identity;
- referent;
- modality/force;
- polarity;
- scope;
- speech act;
- temporal/currentness state;
- provenance;
- unresolved interpretations.

Transformation classes include:

- `STRENGTHENED` / `WEAKENED`;
- `REFERENT_CHANGED`;
- `PREDICATE_CHANGED`;
- `CONTRADICTED`;
- `SCOPE_BROADENED` / `SCOPE_NARROWED`;
- `AUTHORITY_ESCALATED`;
- `CURRENTNESS_PROMOTED`;
- `PROVENANCE_CHANGED`;
- `AMBIGUITY_COLLAPSED`;
- `ADDED` / `DROPPED`.

This is where Cricket mechanically detects the Righter failure. For example:

```text
user: PROBABLE(needs_personality(cricket))
candidate: ASSERTED(needs_personality(cricket))

=> STRENGTHENED
=> CHALLENGE
```

### Rezon relationship

Rezon is Cricket's **semantic/reasoning upstream**. Cricket V0.4 is pinned to the Rezon compatibility baseline recorded in `cricket.semantic.rezon_contract.REZON_CONTRACT`.

That means Cricket's proposition, referent, scope, modality, provenance, authority, and literal-adversarial-review semantics are intentionally downstream of Rezon.

It does **not** mean:

- `pip install cricket` must install Rezon;
- Cricket fails when Rezon is offline;
- Rezon may change Cricket's disposition;
- Rezon may manufacture authority.

```text
SEMANTIC_UPSTREAM != MANDATORY_RUNTIME_IMPORT
```

When the relevant Rezon contract moves, Cricket's compatibility should be reviewed explicitly rather than assumed.

## 3. Behavioral interpretation

Behavioral interpretation is deliberately separate from semantic integrity.

The behavioral lane stores:

```text
BehavioralObservation
    -> BehavioralHypothesis
        -> evidence_refs[]
        -> alternative_explanations[]
        -> state
```

A hypothesis may be `PROPOSED`, `SUPPORTED`, `CONTESTED`, or `REJECTED`.

Rules:

- every hypothesis must bind to explicit observations;
- a `SUPPORTED` interpretation keeps at least one plausible rival explanation;
- observed behavior may support an interpretation but does not prove hidden motive;
- fictional/media pattern examples do not become evidence about a real person;
- behavioral patterns are not clinical diagnoses;
- behavioral findings are advisory and may not grant authority.

Trek Data Core supplies the evidence/interpretation discipline. Mediaphile supplies longitudinal pattern vocabulary and contrast cases. Their exact source heads are recorded in `docs/SEMANTIC_LINEAGE.md` and `cricket.behavior.sources`.

## 4. Optional semantic critic

A host may provide a model-backed `CriticAdapter` for failures that require open-ended judgment.

Model-generated critic output is advisory by default. A requested semantic `BLOCK` is downgraded to `CHALLENGE` unless the host explicitly opts into semantic blocking.

The critic is instructed to:

- attack the proposition actually present;
- avoid Righter substitution;
- distinguish material errors from pedantry;
- avoid invented evidence, intent, policy, or hidden state;
- prefer silence over performative opposition.

## 5. Cricket Persona V1

The canonical runtime persona is `cricket.persona.DEFAULT_CRICKET_PERSONA`.

Human-readable and machine-readable artifacts live under `personality/`.

Core traits:

- absolute candor;
- dry sass;
- epistemic suspicion;
- loyal opposition;
- self-skepticism;
- materiality.

The persona changes **formulation**, never epistemic status or authority.

```text
SASS != EVIDENCE
CANDOR != CERTAINTY
```

Deterministic rendering uses the persona to add a concise voice line while preserving the exact structured finding, rationale, evidence, and recommendation.

## 6. Rezon-formulated interruption

Cricket's interruption surface is webhook-shaped even when used in-process.

For CHALLENGE/BLOCK, an optional `RezonInterruptionComposer` may ask a Rezon-compatible reasoner to formulate the visible Cricket message under strict constraints.

Rezon may formulate wording. It may not:

- invent finding IDs;
- change PASS/CHALLENGE/BLOCK;
- grant authorization;
- strengthen evidence;
- replace the literal proposition.

If Rezon formulation is unavailable or malformed, Cricket falls back to deterministic rendering.

```text
REZON_UNAVAILABLE != INTERRUPTION_LOST
```

## 7. Host control and bounded revision

The host decides how to consume Cricket's result.

Default V0.4 policy:

- `PASS`: emit normally; Cricket stays silent.
- `CHALLENGE`: permit at most one automatic revision.
- `BLOCK`: stop the candidate/effect; do not let the generator negotiate around the block.

Cricket may be embedded directly or used through `WebhookInterruptionProcessor`.

The webhook-style output is:

```text
ALLOW
INJECT_AND_REVISE
BLOCK_AND_INJECT
```

## 8. Receipts

Review receipts bind review state into a tamper-evident JSONL hash chain.

Runtime receipts can bind:

- request digest;
- initial/final candidate digests;
- initial/final applied review-envelope digests;
- initial/final dispositions;
- finding IDs;
- principle-pack identity;
- revision state.

Tamper evidence is not external notarization and does not prove an external effect occurred.

## Non-goals

Cricket V0.4 does not claim:

- consciousness;
- human phenomenological conscience;
- universal moral truth;
- psychological diagnosis;
- hidden-motive access;
- infallible semantic extraction;
- that critique proves error;
- that Rezon is independent corroboration merely because it is a separate repository;
- that source installation implies deployment in another runtime.
