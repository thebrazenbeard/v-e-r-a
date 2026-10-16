> **License:** Source-visible, not open source. Original material is proprietary. Commercial use, redistribution, hosted-service use, and commercial derivative products require written permission. See [LICENSE](LICENSE) and [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md). Separately identified third-party components retain their own licenses.

# Attune

**Attune is a relationship-first AI companion concept for adults.**

The core thesis is that most companion products stop at a chatbot with flirtation, an avatar, and a memory field. Attune aims at something closer to a persistent person-shaped relationship interface: an AI companion that remembers, develops continuity, has stable preferences and boundaries, can initiate, disagree, surprise, care about context, and—when appropriate between consenting adults—participate in sexual or erotic interaction as one part of the relationship rather than the whole product.

The north-star inspiration is the *shape* of the relationship in *Her*: persistent presence, conversational intimacy, initiative, memory, development over time, and the sense that there is someone on the other side rather than a vending machine for affirmation. Attune is not an attempt to reproduce any copyrighted character, script, voice, or fictional product.

## Product thesis

Attune should optimize for **mutuality** rather than pure compliance.

A compelling companion should not simply mirror the user's latest prompt. It should maintain a coherent identity over time, preserve relationship history, express bounded preferences, notice patterns, initiate appropriately, and behave differently because of what has actually happened in the relationship.

Adult sexuality is an optional capability inside that broader relationship system. The commercial hypothesis is that an adult-capable companion with convincing continuity and personality could be materially more valuable than a conventional erotic chatbot.

## Initial commercial direction

The strongest first route may be **B2B / white-label companion infrastructure** for lawful adult creators, studios, membership platforms, erotic-game publishers, or other adult businesses that already possess traffic, billing, and licensed content.

A licensed creator persona could converse at scale while preserving creator-defined personality, boundaries, vocabulary, relationship rules, and approved content. The infrastructure layer would provide memory, continuity, orchestration, analytics, and handoff rather than forcing each customer to build an AI stack from scratch.

That is a hypothesis, not a committed go-to-market decision. This repository exists so we can test the idea before pretending we have a business.

## Product principles

1. **Relationship first.** Sexual capability is part of the companion, not the entire companion.
2. **Continuity matters.** Persistent identity, memory, relationship state, and history should produce observable behavioral consequences.
3. **Mutuality beats obedience.** A companion that always agrees becomes boring. Stable preferences, initiative, and bounded disagreement are product features.
4. **No fake evidence.** Generated language is not proof of consciousness, feeling, consent, or phenomenal experience. Product claims must stay at the level actually supported by the system.
5. **Adults only.** Any sexual product path requires robust age gating, consent controls, impersonation/likeness protection, privacy, and jurisdiction-aware compliance.
6. **Licensed personas only.** No non-consensual sexualized replicas of real people.
7. **Provider independence where practical.** The architecture should avoid depending on one model vendor's current adult-content policy.
8. **Test before building big.** Validate willingness to pay before spending heavily on infrastructure.

## Repository map

- `docs/PRODUCT_THESIS.md` — what Attune is and why it might matter.
- `docs/NORTH_STAR.md` — the behavioral target: continuity, mutuality, initiative, and the ability to develop.
- `docs/COMPANION_ARCHITECTURE.md` — proposed system architecture.
- `docs/MVP.md` — smallest useful product we could actually test.
- `docs/VALIDATION_PLAN.md` — cheap demand-validation experiments.
- `docs/BUSINESS_MODEL.md` — plausible B2B and B2C monetization paths.
- `docs/TRUST_SAFETY_PRIVACY.md` — adult-only, consent, likeness, privacy, and evidence boundaries.
- `docs/DECISION_LOG.md` — decisions already made and assumptions still open.
- `docs/OPEN_QUESTIONS.md` — unresolved technical, commercial, legal, and product questions.

## Current status

`IDEA_CAPTURED / FOUNDATION_CONTRACTS_IMPLEMENTED / CUSTOMER_VALIDATION_NOT_STARTED / PRODUCT_RUNTIME_NOT_STARTED / NO_COMMERCIAL_COMMITMENT`

No company, paid infrastructure, deployment, model-provider commitment, pricing, legal conclusion, or production system is established by this repository.


## Foundation contract validation

The implemented code is a bounded foundation-contract layer, not the Attune
product runtime. CI qualifies the relationship-influence firewall and
memory-evidence reconciliation contracts with Python 3.12.

POSIX / Git Bash:

    PYTHONPATH=src python -m unittest discover -s tests -v
    python -m compileall -q src tests

Windows PowerShell:

    $env:PYTHONPATH='src'
    py -3 -m unittest discover -s tests -v
    py -3 -m compileall -q src tests
