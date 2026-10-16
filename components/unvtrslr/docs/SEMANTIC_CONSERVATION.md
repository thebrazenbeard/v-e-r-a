# Semantic Conservation

## Why conservation matters

A translator needs a definition of what counts as preserving meaning.

Surface similarity is not sufficient. Two sentences can look different while preserving the same tested semantic structure, and two nearly identical sentences can differ in agency, certainty, causality, or scope.

UNVTRSLR therefore treats translation as a **semantic conservation problem**.

The target is not literal equivalence. The target is preservation of the source distinctions that matter within a declared scope, plus explicit accounting for everything that changes.

## Semantic invariants

A semantic invariant is a relationship, distinction, or consequence that should survive a faithful transformation.

For a transfer event such as a human sentence equivalent to “John gave Mary the key,” candidate invariants may include:

- a transfer occurred;
- giver identity = John;
- recipient identity = Mary;
- transferred entity = key;
- direction of transfer = John -> Mary;
- event precedes the recipient's resulting possession/access state, if that consequence is licensed;
- certainty/evidential status of the source claim.

A target expression such as “Mary received the key from John” can preserve these invariants despite substantial surface change.

## Invariants are scoped, not metaphysically absolute

The project should avoid claiming to know the complete meaning of an expression.

A translation may preserve all invariants tested by the current experiment while still missing distinctions the evaluator has not probed.

Therefore every conservation judgment should include:

- semantic scope;
- evidence base;
- tested transformations;
- unresolved distinctions;
- confidence.

## Conservation ledger

Every translation or cross-system mapping should produce a machine-readable ledger.

### PRESERVED

A tested source invariant is retained in the target.

### TRANSFORMED

The target uses a different representational structure but preserves the tested semantic function.

Example: absolute coordinates in one system rendered as an egocentric spatial relation in another.

### INFERRED

The target expresses content not directly present in the source but derived through an explicit inference.

Inference may be useful, but it must not be confused with translation.

### OMITTED

A source distinction is absent from the target realization.

Omission may be unavoidable, optional, or a defect.

### ADDED

The target contains semantic content unsupported by the source or declared inference rules.

Unsupported additions are a translation failure mode.

### AMBIGUITY_COLLAPSED

The source supports multiple live interpretations but the target selects one.

This should be visible even if the selected interpretation is likely.

### UNRESOLVED

The system cannot yet establish what source structure should be preserved.

### UNTRANSLATABLE

The source contains a demonstrated distinction for which no faithful target equivalent currently exists.

### APPROXIMATED

The target preserves only a bounded functional approximation.

### CONTEXT_REQUIRED

The mapping is valid only when a specified context is retained or reconstructed.

## Conservation dimensions

A mature evaluator should separately score dimensions rather than compressing everything into one fidelity number.

Candidate dimensions include:

- referential identity;
- relational structure;
- temporal structure;
- quantitative structure;
- spatial structure;
- agent/patient roles;
- causal status;
- modality/possibility/necessity;
- evidential status;
- epistemic uncertainty;
- communicative force;
- affective or motivational structure;
- social-role structure;
- provenance;
- context dependence;
- compositional behavior;
- predictive consequences.

Not every communication system will expose every dimension.

## Equivalence classes

UNVTRSLR should use typed equivalence rather than one binary `same meaning` flag.

### EXACT_WITHIN_SCOPE

All currently tested semantic invariants match and no known source distinction is lost.

### FUNCTIONALLY_EQUIVALENT

Different representations support the same tested behaviors or predictions under the relevant tasks.

### CONTEXTUALLY_EQUIVALENT

The mapping is equivalent only under specific environmental, social, temporal, or interactional context.

### PARTIAL_OVERLAP

Some invariants map cleanly while others do not.

### ONE_TO_MANY

One source category corresponds to several target distinctions.

### MANY_TO_ONE

Several source distinctions collapse into one target category.

### APPROXIMATE

The target captures a useful but knowingly incomplete approximation.

### UNKNOWN

Evidence is insufficient.

### NO_FAITHFUL_EQUIVALENT

The source distinction has been demonstrated but no target representation preserving it has yet been established.

## Tests for semantic conservation

### Paraphrase test

Can substantially different target forms preserve the same semantic structure?

### Contrast test

Does changing one semantic invariant produce a corresponding target distinction?

### Novel-instance test

Does the mapping hold for instances not used to establish it?

### Context-transfer test

Does the mapping survive irrelevant context changes and fail appropriately when relevant context changes?

### Role-reversal test

Can both parties use the mapping productively?

### Composition test

Can established semantic units combine in previously unseen structures?

### Intervention test

If the mapped meaning implies an action-relevant distinction, does an intervention produce the predicted result?

### Counterfactual test

Can the semantic structure support predictions about unobserved alternatives?

### Adversarial minimal-pair test

Construct source cases differing in exactly one target-relevant invariant and verify that the translator does not collapse them.

### Round-trip test

Render source semantics into target, then independently infer semantics from the target and compare conservation ledgers.

Round-trip surface similarity is not enough; the comparison must occur at the semantic-evidence layer.

## Information loss is not always failure

Some target systems may lack distinctions present in the source.

A faithful translator may therefore need to:

- explain the missing distinction;
- create a compound paraphrase;
- teach a new target convention;
- retain the source form alongside the paraphrase;
- mark the result as approximate;
- decline to translate.

The choice should be explicit and task-dependent.

## Nonlinguistic conservation

For nonlinguistic systems, conservation may be behavioral or relational rather than lexical.

Example: a honeybee-like vector signal may encode direction and distance through orientation and duration. A faithful English renderer need not preserve the motion pattern; it should preserve the tested spatial vector and uncertainty.

Conversely, translating English into the dance-like channel may require dropping distinctions that channel cannot express.

That asymmetry should be recorded rather than hidden.

## Provenance conservation

A crucial invariant is **how the system knows**.

These are not equivalent:

- “X caused Y.”
- “The other agent claims X caused Y.”
- “X occurred before Y.”
- “The model predicts X probably causes Y.”

A target rendering that erases those differences is semantically defective even if the nouns and verbs match.

## Uncertainty conservation

Likewise, these are not equivalent:

- certain;
- probable;
- possible;
- ambiguous between two interpretations;
- unknown;
- not observed.

The renderer must not turn probabilistic semantic states into categorical assertions merely for fluency.

## Conservation as an anti-hallucination boundary

A renderer should be able to prove that every target claim is linked to:

- a preserved source structure;
- a declared inference;
- or an explicitly supplied context fact.

Target claims with no ancestry should be flagged as `ADDED`.

This creates a practical mechanism for separating translation from helpful elaboration.

## Research challenge

The hard problem is discovering which invariants matter without having a human evaluator define them all in advance.

The project should therefore evaluate both:

1. human-specified invariants in control tasks;
2. invariants discovered by the agents and later validated through behavior, intervention, and generalization.

A universal translator cannot rely forever on a human-provided semantic answer key.
