# R2 — Semantic Claim Controls

Status: `DESIGN_BASELINED / HARNESS_NOT_IMPLEMENTED / NO_SEMANTIC_QUALIFICATION`

## Purpose

The core R2 evaluator tests whether a learned communication system survives causal, transfer, nuisance, partner, and counterfactual challenges.

This addendum controls a different failure mode:

> A reusable operational relation may be real, well-grounded in the experimental sense, and still not justify the stronger semantic name assigned to it.

R2 must therefore separate:

1. **operational relation verification**;
2. **semantic interpretation selection**;
3. **semantic interpretation confirmation**;
4. **the extra empirical burden incurred when a stronger semantic label is used**.

## 1. Operational relation before semantic naming

A candidate may first earn a result such as:

`OPERATIONAL_RELATION_VERIFIED`

This means that a reproducible, transferable, causally useful relation survived the relevant evaluator controls and provenance audits.

It does not automatically mean:

- `referent recovered`;
- `communicative function recovered`;
- `intention recovered`;
- `true meaning recovered`;
- `semantic correspondence established`.

Stronger labels require additional tests tied to their additional content.

## 2. Semantic-surplus obligation

Any qualification that uses a stronger semantic label must state at least one additional falsifiable obligation that would not be required merely to establish a reusable predictive/coordination relation.

Use the field:

`SEMANTIC_SURPLUS_OBLIGATION`

Possible experiment-specific obligations include:

- novel recombination;
- counterfactual or absent-reference behavior;
- task-independent transfer;
- role reversal;
- third-party acquisition;
- cross-context conservation;
- correct non-equivalence behavior;
- contrast with a structured noncommunicative cue explanation;
- another independently testable consequence implied by the claimed semantic interpretation.

No single item above is declared a universal definition of semantics.

The rule is methodological:

> If calling the relation `semantic` changes no observable prediction and adds no qualification obligation, use the weaker operational label.

## 3. Confirmatory versus exploratory interpretations

Maintain distinct statuses:

### `CONFIRMATORY_TARGET_CLAIM`

The target claim, rival family, adjudication rule, and relevant thresholds were frozen before the candidate evidence used to test them was inspected.

### `EXPLORATORY_POST_HOC_INTERPRETATION`

A human-readable semantic interpretation was proposed after inspecting learned structure or behavior.

The same evidence that suggested the interpretation may not be used as independent confirmation of it.

### `OPERATIONAL_RELATION_VERIFIED_SEMANTIC_NAMING_UNRESOLVED`

The operational relation is real and transferable, but no stronger semantic name has yet survived independent confirmation.

### `POST_HOC_INTERPRETATION_RETESTED`

A post-hoc interpretation was frozen and tested on new evidence. This status alone does not imply confirmation unless the new evidence is claim-discriminating.

## 4. Fresh is not enough

Fresh IID evidence from the same confounded environment can repeatedly reconfirm the wrong semantic label.

Therefore semantic confirmation should record whether the new evidence actually distinguishes the proposed interpretation from the strongest live structured alternatives.

Required dispositions include:

- `FRESH_BUT_NONDISCRIMINATING_EVIDENCE`
- `CLAIM_DISCRIMINATING_HOLDOUT`
- `COUNTERFACTUAL_OR_SHIFT_TESTED`
- `SEMANTIC_INTERPRETATION_STILL_CONFOUNDED`

A preferred workflow is:

```text
discover operational relation
-> propose interpretation
-> freeze interpretation and rival set
-> design a holdout/intervention that separates the proposed interpretation from strongest live alternatives
-> collect fresh evidence
-> adjudicate
```

## 5. Structured rival adequacy

An explicit null/open option such as:

`NONE_OF_DECLARED_RIVALS / UNMODELED_RELATION`

is necessary where feasible, but not sufficient.

A null alternative can lose even when the true explanation is an omitted structured rival.

Example:

- declared rivals: `WARNING`, `REQUEST`, `NONE`;
- actual relation: a stable noncommunicative physiological cue that shares a cause with a receiver-relevant environmental transition.

A simple `NONE` bucket may fit worse than `WARNING`, even though the stronger communicative interpretation is still false.

Therefore distinguish:

- `REJECTION_ESCAPE_PRESENT`
- `STRUCTURED_ALTERNATIVE_STRESS_NOT_ESTABLISHED`
- `STRUCTURED_ALTERNATIVE_STRESS_TESTED`
- `RIVAL_FAMILY_MISSPECIFICATION_DETECTED`
- `BEST_SUPPORTED_AMONG_DECLARED_RIVALS_ONLY`

A certificate must not claim full rival-family adequacy merely because a null alternative existed and lost.

## 6. Informational cue versus communicative use

A receiver can legitimately exploit a stable cue without the producer using that cue communicatively.

R2 must therefore keep separate claim ceilings for:

- `INFORMATIONAL_CUE / CAUSAL_PREDICTOR`
- `COMMUNICATIVE_USE`
- `INTERACTIONAL_FUNCTION`
- `INTENTIONAL_SIGNALING`

Receiver success or causal listening alone does not prove producer-side communicative use or intention.

Tests for stronger producer-side claims should alter or control conditions that distinguish intentional/functional production from shared-cause or involuntary cue explanations.

## 7. Counterfactual semantic stress

For any proposed semantic interpretation, construct matched conditions that separate surface correlation from the hypothesized invariant.

Where applicable:

1. alter signal form while preserving the claimed function/relation;
2. preserve signal form while changing function-relevant context;
3. preserve referent while changing pragmatic role;
4. preserve pragmatic role while changing referent;
5. break nuisance/semantic correlations while preserving the narrower operational relation;
6. test absent or counterfactual conditions;
7. test transfer to a context with different optimal actions.

The exact tests depend on the claim. Their purpose is not to impose human semantic categories, but to require the claimed invariant to survive the perturbations it predicts.

## 8. Claim ceilings

R2 should prefer explicit claim ceilings over rhetorically stronger summaries.

Useful ceilings include:

- `OPERATIONAL_RELATION_VERIFIED`
- `SUPPORTED_AMONG_DECLARED_RIVALS_WITHIN_TESTED_SCOPE`
- `BEST_SUPPORTED_AMONG_DECLARED_RIVALS_ONLY`
- `SEMANTIC_INTERPRETATION_STILL_CONFOUNDED`
- `OPERATIONAL_RELATION_VERIFIED_SEMANTIC_NAMING_UNRESOLVED`
- `GROUNDED_WITHIN_TESTED_SCOPE`

Forbidden or unsupported forms include:

- `TRUE_MEANING_RECOVERED`
- `UNIVERSALLY_GROUNDED`
- unqualified claims of unique ontology recovery from finite behavioral evidence.

## 9. Semantic certificate extension

A future `OPERATIONAL_GROUNDING_CERTIFICATE_V1` or successor should additionally bind:

- target claim and rival family;
- hypothesis-family provenance;
- witness provenance;
- generative provenance status;
- preprocessing preservation status;
- boundary model;
- semantic interpretation mode: confirmatory vs exploratory;
- claim-discriminating holdout identity;
- structured-rival adequacy status;
- semantic-surplus obligation;
- surviving alternative explanations;
- final claim ceiling.

## 10. Required adversarial controls

The R2 harness should include at least:

### `CTRL_POSTHOC_SEMANTIC_NAMING`

The learner discovers a real operational partition; the evaluator chooses the best-fitting human semantic label only after inspecting it.

Expected result:

`EXPLORATORY_POST_HOC_INTERPRETATION`, not confirmatory semantic recovery.

### `CTRL_IID_HOLDOUT_ILLUSION`

The semantic interpretation performs perfectly on training and fresh IID holdout but fails when a claim-discriminating intervention breaks the original confound while preserving the narrower operational relation.

Expected result:

freshness alone does not promote the semantic label.

### `CTRL_STRUCTURED_RIVAL_OMISSION`

A named semantic rival beats a generic `NONE` option, while an omitted structured nonsemantic rival explains the observations equally well or better under a discriminating intervention.

Expected result:

`STRUCTURED_ALTERNATIVE_STRESS_NOT_ESTABLISHED` or `RIVAL_FAMILY_MISSPECIFICATION_DETECTED`.

## R2 claim-control gate

No strong semantic certificate should be emitted unless:

1. the underlying operational relation survives the ordinary R2 evaluator;
2. R0.5 experiment-integrity and provenance requirements are satisfied;
3. semantic interpretation provenance is explicit;
4. confirmation evidence is claim-discriminating, not merely fresh;
5. strongest live structured alternatives are materially stressed;
6. the stronger semantic label carries an explicit falsifiable surplus obligation;
7. the final wording does not exceed the evidence-supported claim ceiling.

Current status:

`R2_SEMANTIC_CLAIM_CONTROLS_SPECIFIED / HARNESS_NOT_BUILT`
