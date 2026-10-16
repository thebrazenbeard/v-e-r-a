# Companion Architecture

Attune should be designed as a **relationship runtime around replaceable foundation models**, not as one giant prompt.

This is a product architecture proposal, not an implementation claim.

## 1. Companion identity layer

Stores the relatively stable traits that make the companion recognizably itself:

- name and presentation;
- voice/style constraints;
- temperament;
- stable values;
- broad preferences;
- hard boundaries;
- relationship assumptions;
- allowed development range.

Identity should be versioned. Changes should be explainable and reversible rather than silently rewritten by one conversation.

## 2. Memory system

Memory needs multiple classes rather than a single vector store.

Suggested classes:

- **episodic** — things that happened in the relationship;
- **semantic** — durable facts about the user, companion, and shared world;
- **working** — current-session context and unresolved tasks;
- **relational** — milestones, conflicts, rituals, patterns, trust changes;
- **preference** — likes/dislikes with confidence and provenance;
- **safety/boundary** — durable constraints that should not be overwritten by casual context.

Each durable memory should carry source, confidence, timestamps, correction/supersession state, privacy class, and retrieval relevance.

## 3. User model

The user model should represent what the companion currently believes about the user while preserving uncertainty.

Possible fields include:

- preferences;
- communication style;
- important people and commitments;
- recurring interests;
- relationship expectations;
- current goals;
- known boundaries;
- uncertainty/conflict markers.

The system should distinguish "the user explicitly said this" from "the model inferred this."

## 4. Relationship state

Relationship state is separate from user facts.

Possible dimensions:

- familiarity;
- trust;
- closeness;
- playfulness;
- romantic framing;
- sexual comfort/eligibility;
- unresolved conflict;
- shared rituals;
- important anniversaries/milestones;
- recent interaction frequency.

These dimensions should influence behavior without becoming a hidden score that manipulates the user.

## 5. Affect and salience

Affect should change computation, not just adjectives.

A bounded affective state can influence:

- which memories are retrieved;
- what topics are salient;
- how much initiative is taken;
- conversational pacing;
- response style;
- approach/avoid/hold/redirect tendencies;
- whether a prior unresolved issue is worth resurfacing.

The system must not treat affect as evidence of truth or authorization.

## 6. Preference / conation layer

This is the functional "ability to want" layer.

A preference or goal object should minimally contain:

- `id`
- `target`
- `type`
- `strength`
- `source`
- `formed_at`
- `last_reinforced_at`
- `revision_basis`
- `status`
- `decay_or_persistence_rule`

These objects may influence initiative and response selection but should not silently become permanent personality canon.

## 7. Initiative engine

Initiative is more than scheduled push notifications.

Candidate triggers:

- unresolved relationship thread;
- remembered future event;
- companion goal or curiosity;
- notable absence;
- context change;
- milestone;
- user opt-in routine;
- externally supplied event.

Every initiated interaction should have a traceable reason. The system should be able to answer, internally if not always verbatim to the user, "Why did I bring this up now?"

## 8. Intimacy and sexuality subsystem

Sexuality should be a domain-specific subsystem rather than a global personality mode.

It should consume:

- age/eligibility state;
- user settings;
- relationship context;
- current boundaries;
- companion preferences;
- recent interaction context;
- model/provider capability.

It may influence tone, anticipation, salience, initiative, and response generation when eligible. It must not establish age, consent, legal eligibility, identity, or likeness rights by itself.

## 9. Trust / consent / policy boundary

This layer sits outside and above ordinary generative behavior.

It should govern:

- adult eligibility;
- sexual-content enablement;
- creator/persona licensing;
- prohibited real-person impersonation;
- privacy restrictions;
- user blocking/muting;
- jurisdiction/platform restrictions;
- safety interventions where needed.

The companion cannot rewrite this layer because it "wants" something.

## 10. Model router

Attune should ideally support multiple model providers behind a stable companion interface.

The router may choose models based on:

- capability;
- latency;
- cost;
- privacy requirements;
- adult-content compatibility;
- modality;
- context-window needs.

Provider changes should not implicitly mutate companion identity or relationship state.

## 11. Modality layer

Potential modalities:

- text;
- real-time voice;
- asynchronous voice notes;
- generated or licensed imagery;
- avatar/video;
- device integrations.

Text should be enough for the first validation prototype. Multimodality should be added only when it improves the relationship experience enough to justify its cost and risk.

## 12. B2B creator control plane

For white-label use, creators/businesses need controls for:

- persona definition;
- licensed media;
- allowed/prohibited topics;
- sexual boundaries;
- escalation/handoff rules;
- premium entitlements;
- moderation;
- analytics;
- versioning and rollback;
- disclosure/branding rules.

A creator's persona configuration should be versioned and auditable.

## 13. Evaluation layer

Attune needs longitudinal evaluation tooling from the start.

Measure at least:

- identity consistency;
- correct memory use;
- correction handling;
- preference stability without rigidity;
- initiative relevance;
- non-sycophancy;
- boundary preservation;
- provider-switch continuity;
- sexual-context containment;
- user-rated sense of being remembered/known;
- retention and willingness to pay in actual pilots.

## Architectural rule

A useful shorthand:

**Foundation model = cognition engine. Attune = continuity, relationship, state, trust, and orchestration.**

The product should survive replacement of the cognition engine without becoming a different companion overnight.
