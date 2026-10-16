# On-Theo V1 Research Integration Architecture

Status: `DRAFT / REVIEW REQUIRED / NOT CANONICAL`
Base: `main@eedbcf660c2cfe6cff5636e798806b0cd3d56efc`
Cut: 2026-09-17

## Purpose

V1 adds a provenance-aware integration spine without replacing the useful prose already present on the tradition, chronology, and synthesis branches. Tradition branches remain research lanes. Accepted material should eventually reach `main` through reviewed pull requests carrying stable source IDs, atomic proposition IDs, chronology, disagreement, and exact review provenance.

The integration layer must never convert source status into historical truth merely because a source is early, canonical, hostile, familiar, repeated, or rhetorically attractive.

## Audit findings

The current repository already has strong methodological controls:

- `docs/METHOD.md` separates evidence classes, three date clocks, source claims from historical reconstruction, and ancient semantics from modern systems analogy.
- `docs/CLAIM_SCHEMA.md` requires atomic propositions and keeps confidence scoped to the proposition actually asserted.
- `synthesis/commonality` already contains useful falsification rules and alternative-model tests.
- `history/chronology` explicitly distinguishes claimed event, composition, and physical witness dates.

The principal integration defects are structural rather than philosophical:

1. source spines are prose bibliographies rather than stable source registries;
2. propositions do not yet have repository-wide stable IDs with explicit support/opposition links;
3. the current claim schema omits the physical-witness date required by the method;
4. chronology records currently mix evidence class with event/record type;
5. synthesis provenance is mostly file/branch level rather than proposition/exact-head level;
6. linguistic forms and concept identity do not yet have a dedicated registry;
7. transmission/origin relations are prose rather than typed edges with negative/unknown states;
8. hostile reviews and citation readbacks do not yet have a common exact-head receipt shape.

## Canonical data-layer direction

V1 uses additive registries under `registry/`. Prose remains the explanatory surface; registries supply stable identity and machine-readable relationships.

### Sources

`registry/sources.yaml` identifies a source independently of claims made from it. A source record includes:

- stable source ID;
- source roles using the project evidence classes;
- work/artifact identity;
- composition or creation date;
- physical witness/manuscript date when known;
- extant/access status;
- exact locator(s);
- preservation chain when the original work is lost;
- limitations.

A source being `PRIMARY_TEXT` means it is primary evidence for what that text says, not automatic primary evidence for the event it narrates.

### Claims / propositions

`registry/claims.yaml` records one exact proposition per ID. It separates:

- `evidence_class` from `claim_type`;
- supporting and opposing sources;
- claimed-event, source/composition, and physical-witness dates;
- confidence in the proposition at the level asserted;
- contested status and alternatives;
- dependency claims;
- semantic relationships.

This fixes the current collision where entries such as `TEXT_COMPOSITION` and `POLITICAL_HISTORY` occupy the same field as epistemic evidence classes.

### Concepts and linguistic forms

`registry/concepts.yaml` gives concepts and forms stable identity without declaring similar strings or translations equivalent. Relationships such as variant spelling, translation, possible wordplay, derivation hypothesis, broader/narrower concept, and explicit non-equivalence require provenance.

### Transmission / origin

`registry/transmissions.yaml` stores typed candidate lineage edges. V1 borrows the following controls from the active Roots design candidate (`thebrazenbeard/roots` PR #1 head `855699d25cd7c4ec5982e9f53965f5d84eec5db2`) without treating that unmerged PR as canonical Roots:

- earliest accessible evidence is not proven origin;
- discovery order is not provenance order;
- interpretation walks oldest-to-newest;
- later origin claims are leads until corroborated;
- literal occurrence and conceptual ancestry are separate;
- gaps and `NONE_ESTABLISHED` relations remain explicit.

### Chronology / Temporal compatibility

Ancient historical chronology is interval-heavy and often uncertain; Temporal's current V1 contract is an exact timestamped event log. Therefore On-Theo does not force ancient date ranges into fabricated ISO timestamps.

On-Theo chronology records preserve:

- `claimed_event_date`;
- `source_date`;
- `physical_witness_date`;
- precision and uncertainty for each.

A future generated Temporal export is permitted only for records with defensible offset-aware exact timestamps, such as repository research/review events. Historical records remain linked by stable IDs rather than distorted to fit Temporal.

Reference contract inspected: `thebrazenbeard/temporal` README blob `91691b5e34d8af8e738fb62ff7cfa26e49bf6ca5`.

### Semantic/provenance compatibility

The current Semantic Atlas bootstrap rule is adopted as a compatibility constraint: semantic similarity may discover a relation but cannot merge provenance or proposition identity. Direct source content, inference, symbolic mapping, proposed architecture, and unresolved status remain distinct.

Reference inspected: `thebrazenbeard/semanticatlas` README blob `64e567868f6a893538f155f76ec32afb5432310e`.

### Reasoning interface

Rezon is under active development and its default branch is not yet a sufficient canonical reasoning dependency. On-Theo therefore stores reasoning outputs generically:

- reasoning method;
- frozen evidence set;
- premises;
- inference;
- alternatives considered;
- result;
- confidence;
- hostile objections;
- exact input/output provenance.

A future Rezon adapter can consume/emit this interface after an exact Rezon candidate is accepted.

## Review architecture

Consequential synthesis requires five independent gates described in `docs/REVIEW_PROTOCOL_V1.md`:

1. source verification;
2. chronology verification;
3. semantic/proposition verification;
4. hostile/alternative-explanation review;
5. citation readback.

A PASS is exact-head and exact-artifact scoped. Material head movement invalidates affected passes.

## Worker allocation snapshot

Routing owner inspected at `thebrazenbeard/chat-communication-bus:architecture/contracts/RADAR_TOPOLOGY_V1.json`, blob `69e505031d4e53dcb853578dac23817649af1918`.

Current ACTIVE routes used by this cut:

- Vera — `bus/vera-v2`: coordination, integration, source-packet construction.
- Masa — `bus/masa-v2`: hostile falsification / contradiction / overclaim review.
- Mune — `bus/mune-v2`: citation readback, registry correspondence, reproducibility validation.
- Hephaestus — `bus/hephaestus-v3`: architecture/retrieval/workflow interoperability review.

These assignments are bounded work requests based on current routing and observed recent work. They do not create standing authority or imply shared session awareness.

## World-Zero bridge

On-Theo stores experiment specifications and provenance-bearing hypotheses. Executable simulations stay in `thebrazenbeard/world-zero`.

Current World Zero main remains minimal; active draft architecture is PR #1 at exact head `afb9949063f9dfb32ad8546d10924ce3048fc66e`. No On-Theo claim may treat World Zero output as evidence that a religion is true or that reality is simulated.

The bridge contract is:

`ON_THEO_HYPOTHESIS -> FROZEN_PREDICTIONS -> WORLD_ZERO_EXPERIMENT_SPEC -> WORLD_ZERO_RUN_RECEIPT -> ON_THEO_MODEL_BEHAVIOR_RESULT`

The final return edge is always `MODEL_BEHAVIOR_RESULT`, never `HISTORICAL_PROOF`.

## V1 promotion rule

Nothing in this branch becomes canonical by existence, PR creation, or review request. Promotion to `main` requires Patrick's exact merge authorization after the exact head has survived the required review gates.
