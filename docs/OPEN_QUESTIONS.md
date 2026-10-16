# Open Questions

Attune is early enough that unresolved questions are more valuable than fake certainty.

## Product

- What does "mutuality" need to look like before users notice it?
- Which forms of disagreement feel compelling rather than frustrating?
- How much initiative is welcome before it feels intrusive?
- How quickly should a companion's preferences develop?
- Which memories should be durable and which should decay?
- How visible should memory controls be to the user?
- Should users be able to inspect/edit the companion's relationship model directly?
- How do we preserve surprise without introducing arbitrary personality drift?
- What should happen when the user wants the companion to become radically different?
- How should romantic, platonic, sexual, and non-sexual relationship modes interact?

## Adult capability

- Is explicit sexual capability essential to willingness to pay, or merely a retention feature?
- Should adult mode be per-account, per-companion, per-session, or layered?
- How do persona-level boundaries and user-level boundaries reconcile?
- What age-assurance model is acceptable without making onboarding intolerable?
- Which model providers currently allow the intended lawful adult use case?
- Can adult-capable model routing remain seamless enough to preserve one companion identity?
- What disclosure is required when a licensed creator's AI persona is interacting with a fan?

## Memory and continuity

- What is the minimum memory model that users perceive as meaningfully better?
- How do we prevent a false inference from hardening into relationship history?
- How are corrections propagated through summaries, embeddings, relationship state, and preferences?
- What happens when memories conflict?
- Can provider/model changes preserve a stable voice without enormous prompt/context cost?
- How do we measure identity continuity objectively?

## Preference and conation

- How do companion preferences form?
- Which preferences may change through interaction and which belong to stable identity?
- How do we prevent user pressure from instantly overwriting them?
- How do we prevent them from becoming rigid or randomly adversarial?
- Can preference development be deterministic/auditable enough for creator-approved personas?
- What is the right functional definition of a companion "want" for product purposes?

## Initiative

- What should cause an unprompted interaction?
- Does the system need real-world event/calendar context for initiative to feel meaningful?
- How do users control frequency and quiet hours?
- How should the companion handle long absences without manipulation or guilt?
- What percentage of initiative should be companion-driven versus explicitly user-configured?

## B2B

- Who feels the pain most strongly: individual creators, agencies, studios, erotic games, or platforms?
- Is the buyer trying to reduce labor, increase spend, increase retention, or differentiate the product?
- What data/integration will customers actually provide?
- Do customers want AI-only interaction, human handoff, or a hybrid?
- How much persona control is required before a creator trusts the system?
- Which metrics prove ROI to the buyer?
- Do operators prefer white-label hosting, API access, or a managed service?

## Economics

- What is the acceptable inference cost per active relationship?
- How expensive is longitudinal memory retrieval at meaningful scale?
- Does voice materially improve conversion enough to pay for itself?
- How expensive are age assurance, moderation, chargebacks, and payment processing?
- What gross margin remains after adult-industry infrastructure costs?
- What distribution channel can acquire users/customers without impossible CAC?

## Trust / legal / platform

- Which jurisdictions are viable for an initial launch?
- What current age-assurance obligations apply there?
- Which payment processors and cloud providers support the intended business?
- What privacy rules apply to stored intimate/sexual conversation data?
- What rights must be licensed for creator name, likeness, voice, and training/reference material?
- How should deletion/export obligations interact with relationship memory backups?
- What product claims about "desire," "emotion," or "relationship" are defensible?

## Technical

- Which foundation models can support the target adult content and personality stability?
- How should the relationship runtime be separated from provider-specific prompts?
- SQL/document/event-sourced state: which representation best supports auditable continuity?
- What state belongs in the prompt versus tool calls versus retrieved memory?
- How should asynchronous initiative be scheduled and rate-limited?
- What evaluation harness can simulate months of interaction cheaply?
- What architecture supports creator multi-tenancy without leaking memories across users?
- How do we prevent prompt injection from rewriting persona/license/safety state?

## Immediate priority

The first questions to answer are commercial, not architectural:

1. Who has the problem?
2. What do they currently pay/do to solve it?
3. Which Attune behavior is valuable enough to change that spending?
4. What minimum demo would make them commit to a pilot?

Everything else can be refined after those answers stop being guesses.
