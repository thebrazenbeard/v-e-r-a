# Cricket Webhook-Style Interruption Injection

Cricket's control surface is webhook-shaped even when used in-process.

## Flow

```text
host candidate
    |
    v
Cricket review
    |
    +-- PASS ---------------------------> ALLOW
    |
    +-- CHALLENGE
    |      |
    |      v
    |   Rezon formulation
    |      |
    |      v
    |   Cricket persona rendering ------> INJECT_AND_REVISE
    |
    +-- BLOCK
           |
           v
        Rezon formulation
           |
           v
        Cricket persona rendering ------> BLOCK_AND_INJECT
```

Cricket decides **whether** an interruption exists and preserves the finding/disposition.

Rezon decides **how to formulate the interruption**, using a bounded task containing:

- literal user message;
- candidate response;
- Cricket findings;
- current disposition;
- explicit authority state;
- current principles;
- Cricket persona/version;
- constraints forbidding new facts, findings, diagnoses, or authority.

The host decides **where/how to inject it** into the active conversation or execution flow.

## Rezon failure

Rezon is not a safety-critical single point of failure. If it is unavailable, malformed, references unknown findings, or otherwise violates the formulation contract, Cricket uses its deterministic finding renderer.

`REZON_UNAVAILABLE != INTERRUPTION_LOST`

## Authority boundary

Rezon output fields such as a suggested disposition or alleged authority are ignored. It cannot downgrade a Cricket BLOCK or grant permission.

`FORMULATION != AUTHORIZATION`

## Chat behavior

- `ALLOW`: emit candidate normally; Cricket is silent.
- `INJECT_AND_REVISE`: inject Cricket blockquote and permit one bounded revision.
- `BLOCK_AND_INJECT`: suppress the candidate/effect and inject Cricket's objection.

## Personality

The Rezon formulation task carries Cricket Persona V1. The intended style is absolute candor with dry sass, bounded by:

- sass != evidence;
- candor != certainty;
- personality != authority;
- behavioral hypothesis != hidden motive fact.
