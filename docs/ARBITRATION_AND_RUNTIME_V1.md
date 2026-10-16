# Arbitration and Runtime V1

Status: reference architecture.

## Why arbitration is not a weighted sum

MESO-CRCT state families answer different questions. Adding them together would create a number with no stable semantics.

The reference arbiter therefore uses typed competition and coalition evidence:

1. protection has its own independent path;
2. incentive salience is modulated by satiation;
3. upstream typed signals compete by current magnitude;
4. near-dominant signals are retained as supporting drivers;
5. the dominant signal determines the mode of recruitment;
6. attentional priority is a downstream allocation result and is not fed back into the arbiter.

This is deliberately simple. It is a falsifiable reference rule, not a claim that biology implements this exact algorithm.

## Modes

- `QUIESCENT` — no upstream driver crosses the orienting threshold.
- `ORIENTING` — perceptual or semantic relevance dominates.
- `MOTIVATIONAL` — motivational or incentive salience dominates.
- `EPISTEMIC` — information/learning value dominates.
- `PROTECTIVE` — hazard or avoidance crosses the independent protection threshold.

## Recruitment phases

Runtime classification is separate from arbitration:

- `QUIESCENT`
- `ORIENTED`
- `RECRUITED`
- `PROTECTIVE`
- `RESOLVING`

High priority alone is insufficient for `RECRUITED`. The reference classifier also requires cross-system coherence and persistence.

## Anti-feedback rule

Existing `attentional_priority` is recorded for audit but excluded from upstream arbitration.

Without this rule:

```text
attention -> priority -> more attention -> more priority -> ...
```

could become a self-maintaining loop even when the original stimulus no longer has semantic, motivational, perceptual, or epistemic support.

## Satiation rule

Satiation only damps incentive salience in the reference arbiter:

```text
effective_incentive = incentive_salience * (1 - satiation)
```

It does not erase meaning, threat, perceptual conspicuity, or epistemic relevance.

## Provenance and receipts

Each admitted state transition can emit a deterministic receipt binding:

- before/after runtime phase;
- arbitration mode and dominant/supporting drivers;
- source kind and source identifier;
- source revision when available;
- cryptographic fingerprints of before/after state.

The receipt proves what the reference runtime evaluated. It does not prove the source identifier was truthful. Production integration therefore still requires a trusted provenance/admission boundary outside this module.

## Direct register writes

The normal runtime path rejects provenance explicitly marked `DIRECT_REGISTER_WRITE`.

Authorized test stimulation must use the separate `TEST_STIMULATION` provenance class so tests cannot be reported as organic/environmental transitions.

This is only one anti-wireheading layer. It does not solve forged provenance, proxy reward exploitation, or higher-level causal incentives by itself.
