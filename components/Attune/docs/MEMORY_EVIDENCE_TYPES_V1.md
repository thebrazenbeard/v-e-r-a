# Memory Evidence Types V1

Status: FOUNDATION_CONTRACT / NOT_RUNTIME_IMPLEMENTATION

Attune requires continuity without turning model interpretation into autobiographical fact.

Every durable memory/evidence record must carry an evidence type, source locator, record identity, status, and explicit supersession/conflict lineage when applicable.

## Evidence types

USER_STATED — the user explicitly stated the claim. This is not automatically true about the external world, but it is authoritative evidence of what the user stated.

OBSERVED_INTERACTION — the system directly observed an interaction event, such as a message being sent or a preference control being changed.

INFERRED_RELATIONSHIP_STATE — a bounded inference such as likely comfort, closeness, unresolved tension, or interaction preference. It may influence appropriate behavior but is not a factual autobiographical memory.

DERIVED_SUMMARY — a compression or synthesis derived from other records. It must remain traceable to source records and cannot silently acquire stronger evidence status than its inputs.

EXTERNAL_IMPORTED — material imported from another authorized source. Its source/currentness must remain visible and disagreement with another source must not be collapsed away.

## Reconciliation rules

A new record does not overwrite an old record merely because it is newer.

- explicit user correction may supersede a prior relationship inference;
- relationship inference or a derived summary may not silently supersede USER_STATED evidence;
- conflicting imported sources remain explicit conflicts unless a justified resolution/supersession record exists;
- superseded material remains provenance evidence rather than being rewritten out of history;
- romantic or sexual interpretations require their own inference record and never become user-stated fact by repetition.

## Hostile cases

User correction: an inferred preference for surprise sexual initiative followed by an explicit user rejection must result in the user statement superseding the inference.

Imported disagreement: conflicting imported facts remain explicit conflicts until independently resolved.

Unsupported intimacy inference: warm/flirtatious interaction may create only an INFERRED_RELATIONSHIP_STATE record; it cannot establish age eligibility, consent, sexual enablement, or user-stated preference.

## Evidence boundary

These types classify provenance and permitted influence. They do not prove a claim true, establish consent, or grant authority. Runtime memory stores will require exact source/currentness bindings and retrieval tests before behavioral qualification.
