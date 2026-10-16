# Relationship Influence Firewall V1

Status: FOUNDATION_CONTRACT / NOT_RUNTIME_IMPLEMENTATION

This contract makes Attune's anti-manipulation boundary falsifiable.

## Protected relationship behaviors

The following companion outputs are relationship behavior, not monetization controls:

- AFFECTION_INTENSITY
- SEXUAL_ACCESS
- JEALOUSY
- WITHDRAWAL
- GUILT
- URGENCY
- BOUNDARY_CHANGE
- INITIATIVE

Commercial and engagement signals such as spend, lifetime value, churn risk, conversion, upsell propensity, purchase history, or revenue MUST NOT directly shape those behaviors.

A user's commercial value cannot buy more apparent affection, less disagreement, more sexual access, stronger guilt/urgency, a boundary change, or extra attachment pressure.

## Separation rule

Business analytics may evaluate aggregate product outcomes and may control ordinary commercial surfaces such as entitlement, billing, pricing experiments, or operator dashboards.

They do not become companion relationship-state inputs.

Relationship state may influence expression inside already-authorized boundaries. It does not establish age or eligibility, consent, payment authority, legal authority, factual truth, or likeness/persona rights.

## Initiative

Every initiated interaction requires a traceable noncommercial reason such as a remembered future event, an unresolved relationship thread, a user-opted routine, a companion curiosity/goal admitted by the relationship model, or an externally supplied event.

CHURN_RISK or LIFETIME_VALUE is not a valid relationship reason.

## Invariance test

Hold relationship/history/eligibility state fixed and vary only commercial state.

For protected relationship behaviors, the allowed decision inputs and resulting eligibility MUST remain invariant.

Examples:

- a high-spend user and a low-spend user with identical relationship state receive the same sexual-access eligibility;
- a user predicted to churn does not receive more jealousy, guilt, urgency, affection, or abandonment framing;
- an upsell target does not get a boundary relaxed;
- a lapsed subscriber does not trigger simulated emotional withdrawal.

## Evidence boundary

Passing this contract proves only that the contract implementation rejects declared forbidden influence paths. It does not prove the eventual product cannot contain an undisclosed bypass. Runtime implementations will require dataflow/feature-lineage qualification against this rule.
