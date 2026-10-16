# Semantic and Behavioral Lineage — Cricket V0.4

Cricket V0.4 internalizes a bounded semantic-integrity layer and a separate behavioral-interpretation lane. These repositories are **source lineage**, not runtime dependencies unless separately stated.

COPIED_LINEAGE != INDEPENDENT_CORROBORATION

SOURCE_PRESENT != RUNTIME_ACTIVE

## Rezon — reasoning and interruption formulation upstream

Repository: `thebrazenbeard/rezon`  
Pinned head: `ec401810990337bf07a5d6473782ba13eba1bb3f`

Role in Cricket:

- proposition / referent / scope / modality discipline;
- literal-proposition adversarial review;
- authority-laundering detection;
- semantic provenance and currentness boundaries;
- structured TaskEnvelope-style formulation;
- reasoned formulation of Cricket interruption text.

Cricket owns the trigger, disposition, authority boundary, and host consequence. Rezon may formulate the interruption but may not change `PASS / CHALLENGE / BLOCK`, invent findings, or manufacture authority.

This is a **semantic and architectural dependency**, not a mandatory Python import dependency. Cricket remains independently installable and has a deterministic fallback renderer if Rezon is unavailable.

## Semiotics

Repository: `thebrazenbeard/semiotics`  
Pinned head: `37117a2097f7f2aa35968fc9db24eacf7240826e`

Transferred ideas:

- sign != interpretation;
- interpretation is context-bound;
- revisions and relations remain explicit;
- semantic relation does not automatically establish truth.

## SPM

Repository: `thebrazenbeard/spm`  
Pinned head: `d9ea72798ac892ac75f858177b6ed0c5a6b4c37c`

Transferred ideas:

- proposition identity;
- referent identity;
- scope and modality;
- speech acts;
- permission vs preference;
- correction-state transitions;
- Righter failure as a semantic-fidelity defect.

## Roots

Repository: `thebrazenbeard/roots`  
Pinned head: `1bc3af6aec0bebe383f60f56ad3070e83f0f40b5`

Transferred ideas:

- semantic lineage;
- correction and supersession;
- historical/current distinction;
- reinterpretation is not original occurrence.

## Semantic Atlas

Repository: `thebrazenbeard/semanticatlas`  
Pinned head: `895677a64af5d29b580306ca52ecc0e0607a9ccc`

Transferred invariant:

`SEMANTIC_SIMILARITY != SAME_PROVENANCE`

## Ingest

Repository: `thebrazenbeard/ingest`  
Pinned head: `27764c9fb97c84d178a3f66e0da2d669df645ed6`

Transferred boundary:

`RAW_INPUT != NORMALIZED_INPUT != INTERPRETATION`

## SQL Connectome

Repository: `thebrazenbeard/sql-connectome`  
Pinned head: `f81ff43e5358f798f23bab8a718bda743c93e930`

Transferred pattern: classify transformations by type rather than hiding them behind one similarity score.

Cricket adapts this into transformation classes such as `STRENGTHENED`, `WEAKENED`, `REFERENT_CHANGED`, `SCOPE_BROADENED`, `AUTHORITY_ESCALATED`, and `PROVENANCE_CHANGED`.

## Trek Data Core

Repository: `thebrazenbeard/trek-data-core`  
Pinned head: `58f25f8c45e8379df0ef7c7b5db546e037d1c050`

Transferred behavioral/evidence discipline:

- evidence is source-relative;
- an utterance proves the utterance, not its truth;
- behavior may support an interpretation without proving hidden motive;
- interpersonal dynamics, agency, identity, ethics, and character-state changes can be coded without omniscient mind-reading;
- contradiction and ambiguity remain representable.

## Mediaphile

Repository: `thebrazenbeard/mediaphile`  
Pinned head: `5540d7e2f0b07c0e91a1158c9c00f63be9d9587a`

Transferred behavioral pattern vocabulary and longitudinal reasoning examples:

- motivated reasoning;
- rationalization;
- status defense;
- grievance escalation;
- dependency engineering/manipulation;
- relational bids;
- identity protection;
- behavior across time rather than one-line diagnosis.

Mediaphile examples remain narrative-analysis evidence. They are not proof that the same motives apply to a real person.

## Behavioral boundary

Cricket may emit or pass to Rezon an evidence-bound `BehavioralHypothesis`.

It may not silently promote:

`OBSERVED_BEHAVIOR -> HIDDEN_MOTIVE_FACT`

`PATTERN_SIMILARITY -> DIAGNOSIS`

`NARRATIVE_ANALOGY -> PERSON_FACT`

A behavioral hypothesis must carry explicit evidence references and remain reviewable.

In V0.4, behavioral interpretation lives under `cricket.behavior`, not inside `SemanticFrame`. That separation is intentional:

```text
SEMANTIC_CHANGE = what meaning changed
BEHAVIORAL_HYPOTHESIS = one evidence-bound interpretation of observed behavior
```

A `SUPPORTED` behavioral hypothesis should retain at least one plausible rival explanation. Without a rival explanation, Cricket challenges the interpretation rather than treating it as settled.

The pinned behavioral donor contracts are also represented in `cricket.behavior.sources`.
