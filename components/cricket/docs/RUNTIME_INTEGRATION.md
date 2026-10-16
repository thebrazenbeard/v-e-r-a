# Cricket V0.4 Runtime Integration Contract

## Purpose

Cricket is a pre-send / pre-effect and optional post-response review hook. It can run in-process or behind a webhook-shaped host adapter.

Cricket is not the host's identity, authority source, or effect executor.

## Review envelope

The host constructs a `ReviewRequest` containing, as applicable:

- current user message;
- candidate response or action description;
- review phase;
- host-selected effect class;
- exact explicit-authorization state for protected effects;
- completion-claim flag and fresh verification evidence;
- evidence-bound claims;
- current corrections;
- local principles;
- metadata.

The host must not ask Cricket to infer authorization from tone.

## Review lanes

A Cricket instance may combine:

1. deterministic rules;
2. an optional semantic-integrity scanner;
3. an optional behavioral scanner;
4. an optional open-ended semantic critic.

The lanes have different jobs.

### Semantic scanner

Compares source and candidate semantic frames for proposition/referent/scope/modality/currentness/provenance drift.

Rezon is the semantic compatibility upstream, but a live Rezon process is not required for the local semantic analyzer.

### Behavioral scanner

Evaluates evidence-bound behavioral hypotheses separately from semantics.

Behavioral hypotheses:

- cite explicit observations;
- remain hypotheses;
- retain rival explanations before `SUPPORTED` status is treated as disciplined;
- never create effect authority.

### Semantic critic

Provides open-ended critique. Its findings remain advisory unless the host explicitly chooses otherwise.

## Default consequence policy

- `PASS`: emit candidate normally; Cricket is silent.
- `CHALLENGE`: permit one bounded reconsideration/revision.
- `BLOCK`: suppress the candidate/effect. Do not automatically revise around a block.

`ReviewRuntime` implements the reference bounded loop:

```text
generate
  -> review
      -> PASS: return
      -> BLOCK: return blocked
      -> CHALLENGE: revise once
          -> review again
          -> return final state
```

Candidate-dependent metadata may be recomputed after revision, but the candidate metadata provider cannot alter authority fields.

## Persona rendering

Cricket Persona V1 controls formulation, not judgment.

The canonical runtime persona is `cricket.persona.DEFAULT_CRICKET_PERSONA`.

Deterministic rendering may add a concise candor/sass line while preserving the structured finding underneath it.

```text
PERSONALITY != AUTHORITY
SASS != EVIDENCE
```

## Webhook-style integration

`WebhookInterruptionProcessor` accepts a JSON-compatible review event and returns:

- `ALLOW`;
- `INJECT_AND_REVISE`;
- `BLOCK_AND_INJECT`.

This is a pure adapter contract. It does not itself require an HTTP server.

A host may expose the same contract over HTTP, IPC, a plugin call, an in-process function, or another transport.

```text
WEBHOOK_SHAPED != NETWORK_REQUIRED
```

## Rezon formulation

`RezonInterruptionComposer` may use a Rezon-compatible reasoner to formulate the visible Cricket interruption.

The composer receives the literal source/candidate context, exact Cricket findings, disposition, persona constraints, and no new effect authority.

Rezon may improve wording/reasoning presentation. It may not:

- change disposition;
- grant authorization;
- invent a finding;
- promote uncertainty into certainty;
- replace the proposition under review.

If Rezon output is unavailable, malformed, or references unknown findings, the host falls back to Cricket's deterministic renderer.

## Principle packs

`PrinciplePack` adds versioned review principles without overwriting request-local principles.

Pack ID/version are preserved in review metadata.

## Review receipts

`JsonlReceiptLedger` provides a single-writer append-only hash chain.

Receipts are tamper-evident, not externally notarized proof.

A missing ledger does not verify successfully. An existing valid empty ledger is an empty chain; after receipts exist, every row binds to the previous row digest.

## Repository verification versus deployment state

Cricket can be built, installed, tested, and integration-qualified directly from this repository. The deterministic reference simulator does not require a Vera deployment.

A claim that Cricket is active inside a **particular external runtime** is separate. That claim requires inspection and exercise of that runtime.

```text
SOURCE_VERIFIED != DEPLOYMENT_ACTIVE
```

No specific workstation path is required to prove the Cricket package itself works.
