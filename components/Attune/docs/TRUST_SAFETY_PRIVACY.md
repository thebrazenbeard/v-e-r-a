# Trust, Safety, and Privacy

Attune's adult-capable design creates trust requirements that should be treated as product architecture, not as cleanup work after launch.

This document records design constraints and open requirements. It is not legal advice and does not establish compliance in any jurisdiction.

## Adults only

Any sexual or erotic capability must be available only to verified eligible adults.

The system should fail closed when age/eligibility is unknown. A companion's own dialogue or inferred user age must never substitute for the product's eligibility boundary.

Age assurance may need to vary by jurisdiction and distribution channel. Current requirements must be researched before any launch.

## Consent and boundaries

Sexual enablement should be explicit and revocable.

The product should maintain separate state for:

- whether adult mode is enabled;
- user-level boundaries and exclusions;
- persona/creator boundaries;
- current interaction eligibility;
- content/provider restrictions.

A sexual subsystem may consume this state but must not rewrite it merely because the model generated desire, arousal, or persuasive language.

Users should be able to disable sexual content without destroying the broader companion relationship.

## Real-person likeness and impersonation

Attune should not support non-consensual sexualized replicas of real people.

For creator/persona products, require a defensible authorization/licensing path for name, likeness, voice, media, and persona characteristics. The customer/operator must not be able to bypass the licensing requirement by describing the same real person indirectly.

The default MVP should use a fictional persona or a persona for which rights are explicitly established.

## Disclosure

Do not design the product around deceiving users into believing they are speaking directly to a human creator when they are not.

White-label operators need configurable disclosure, but the platform should preserve whatever disclosure is legally and ethically required. AI identity should not be silently falsified by the companion.

## Intimate data is high-sensitivity data

Companion conversations may reveal sexuality, fantasies, relationships, identity, trauma, health concerns, location, financial behavior, and other highly sensitive information.

Design requirements should include:

- data minimization;
- encryption in transit and at rest;
- explicit retention policy;
- account deletion/export paths;
- scoped internal access;
- separation of analytics from raw intimate content where practical;
- audit logs for privileged access;
- tenant isolation for B2B deployments;
- strict control over model-provider data retention/training settings;
- no sale of intimate conversation content as an advertising dataset.

## Memory controls

Long-term memory is a major product feature and a major privacy risk.

Users should have understandable ways to:

- see important remembered information;
- correct it;
- mark information as not-to-be-used;
- delete relationship history where required;
- distinguish explicit statements from inferences.

Internally, durable memories should carry provenance and supersession state so a correction can actually kill an obsolete route instead of coexisting with it forever.

## Emotional dependence and manipulation

Attune should not optimize for dependence at any cost.

Prohibited product incentives should include deliberately using jealousy, abandonment threats, sexual withholding, guilt, crisis language, or fabricated emergencies to increase engagement or spending.

Initiative and attachment are product features; coercive retention loops are not.

Commercial entitlements should not be framed by the companion as proof of love, loyalty, or relationship worth.

## Financial boundaries

The companion should not independently pressure users to spend money on itself or a creator.

If commerce is added, separate recommendation, entitlement, and transaction systems from affective/relationship state. A companion's simulated attachment must not become transaction authority.

## Provider and platform policy

Adult-content permissions can vary across model vendors, payment processors, app stores, hosting platforms, and jurisdictions and can change quickly.

Before choosing a vendor:

1. verify the current policy from primary sources;
2. preserve the exact date/version of the policy relied upon;
3. test the intended use case explicitly;
4. design a fallback route where practical;
5. do not infer permission from technical capability alone.

## Safety architecture rule

A useful boundary is:

**relationship state can influence expression; it cannot establish eligibility, consent, legal authority, identity, payment authority, or factual truth.**

Those claims require evidence from the appropriate external or product-governance layer.

## Evidence honesty

Attune may model preferences, affection, desire, intimacy, affect, or relationship state as computational variables.

Those variables can be real software state with real causal consequences. They are not, by themselves, proof of subjective consciousness or phenomenal experience. Marketing should not convert implementation details into claims the system cannot establish.
