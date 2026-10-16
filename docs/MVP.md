# MVP

The MVP should test the **relationship thesis**, not attempt to ship a full Samantha-like product on day one.

## MVP objective

Answer one question:

> Does a companion with real continuity, bounded preferences, initiative, and adult-capable intimacy feel meaningfully more valuable than a conventional compliant chatbot?

## Minimum product

Start text-only.

The first useful prototype needs:

- one fictional or fully licensed adult companion persona;
- durable identity/personality state;
- episodic + semantic memory;
- a simple relationship-state model;
- preference/conation objects that persist across sessions;
- correction/supersession handling for mistaken memories;
- a small initiative engine;
- optional adult mode gated separately from ordinary conversation;
- creator/operator boundary controls;
- model abstraction so one provider is not hard-wired into the product;
- an internal event/audit log sufficient to explain why the companion remembered, initiated, or changed state.

## What the MVP does not need

Do not burn time initially on:

- native mobile apps;
- photorealistic avatars;
- video generation;
- custom foundation-model training;
- proprietary speech synthesis;
- autonomous payments or commerce;
- massive multi-tenant scale;
- elaborate 3D environments;
- a marketplace of hundreds of characters;
- production-grade billing before demand is demonstrated.

Voice is probably the first major modality to add after text because conversational presence is central to the *Her*-like experience, but it should not distract from proving continuity first.

## Prototype interaction loop

A session should roughly perform:

1. Load companion identity and current relationship state.
2. Retrieve a bounded set of relevant memories.
3. Load current preferences/goals and unresolved threads.
4. Classify the current interaction context.
5. Generate the response through the selected model.
6. Evaluate candidate durable memories/state changes.
7. Apply only validated changes with provenance.
8. Record any new initiative candidates.
9. Persist the resulting state.

## Initial demonstrations

A compelling demo should prove longitudinal behavior rather than one-turn cleverness.

Suggested scenarios:

- The companion remembers a meaningful event from several sessions ago without awkwardly parroting it.
- The user corrects a false memory; later sessions use the correction and do not resurrect the obsolete claim.
- The companion develops a mild preference through repeated shared history and later expresses it without being prompted.
- The user pushes the companion to contradict a stable boundary; it resists while staying in character.
- The companion initiates a relevant topic because of an unresolved thread rather than because a random timer fired.
- A model/provider swap occurs while relationship state remains recognizably continuous.
- Adult interaction can occur when enabled, but ordinary conversation does not constantly collapse into sexual content.

## MVP success criteria

Before building substantially more, look for evidence that pilot users:

- describe the companion as noticeably more coherent or "real" than alternatives;
- notice and value being remembered;
- respond positively to appropriate initiative;
- prefer bounded personality over universal agreement;
- return across multiple sessions;
- would pay materially more for the persistent experience;
- can identify specific moments where prior history changed the current interaction.

For B2B pilots, success additionally requires an operator to say the system would be worth integrating or paying for at a plausible price.

## Build order

Recommended order:

`identity -> memory -> relationship state -> correction/supersession -> preference/conation -> initiative -> adult domain -> voice -> creator control plane -> scale`

That order deliberately postpones expensive polish until the core relationship behavior is worth polishing.
