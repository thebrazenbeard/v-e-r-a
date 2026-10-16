# Vera Control Plane v1 Baseline

Record class: `DESIGN_BASELINE_NONAUTHORIZING`  
Execution authority: `NONE`  
Memory admission: `NONE`

## Purpose

Vera Control Plane v1 is a local-first, operator-controlled administration plane. This document records approved design decisions. It does not release software, activate policy, authorize an effect, install the application, grant credentials, or admit memory.

## Architecture baseline

The v1 design separates:

- trusted core;
- deterministic authority and policy engine;
- read and reconciliation adapters;
- bounded effect executor;
- independent readback verifier;
- signed, hash-chained local receipt ledger;
- Windows operator console and security acceptance.

Observer, planner, approver, executor, verifier, receipt, and memory-admission authority remain logically distinct. Direct supported APIs and connectors are preferred. Visible Windows Accessibility or UI Automation may be added only as a separately authorized last-mile adapter where no supported public interface exists; accessibility-element identity is preferred over coordinate clicking.

## Authority versions

Current execution authority comes only from the separately bound active R8A2 governing set. R9A0 is an unreleased design input: it may influence compatibility design and shadow evaluation, but it cannot authorize execution, expand permission, route a credential, or activate itself.

An active-authority digest change fails closed. Future activation requires separate explicit authority, exact predecessor and successor identities, immutable digests, and readback of the active binding.

## First proof workflow

The first proof must:

1. Reconcile fresh Supabase, GitHub, and Google Drive evidence.
2. Produce one exact proposed effect and inverse.
3. Obtain exact operator approval or derive one packet-bound grant from a narrow preauthorization.
4. Perform one bounded, reversible, non-production effect.
5. Independently read the source of truth back.
6. Seal one local receipt only after readback.

The proof target is a dedicated, noncanonical `WORKING_PROJECT` Drive test record. Its one exact state transition has no canonical- or autobiographical-memory implication.

## Receipt states

The operator interface distinguishes:

- `REQUEST_ACCEPTED`;
- `EFFECT_OBSERVED`;
- `READBACK_VERIFIED`;
- `RECEIPT_SEALED_LOCAL`.

`RECEIPT_SEALED_LOCAL` means locally signed, hash-chained, read back, and tamper-evident within the local trust domain. It does not mean immutable or externally witnessed. A future separately authorized state may be named `RECEIPT_EXTERNALLY_WITNESSED`.

## Cross-chat relay provenance

Any message composed by this control plane or an associated Work task and sent into a ChatGPT conversation must begin with:

```text
[WORK RELAY — NOT PATRICK DIRECT SPEECH]
```

The relay must name its Work sender and purpose, state that its wording was Work-authored, identify any Patrick-direct authority separately, and classify the message as transport rather than direct user speech or memory admission. Quoted user text must be visibly quoted and traceable to its locator. Send admission, turn materialization, recipient response, and verified action are separate states.

## Exclusions

- Basic Memory Cloud is neither a dependency nor a fallback.
- Audit and receipt storage cannot invoke memory admission.
- No production mutation, credential action, paid-service action, merge, deployment, installation, deletion, model training, canonical-memory write, or policy activation is authorized by this baseline.
- No change to `thebrazenbeard/vera` or `thebrazenbeard/vera-R9A0` is authorized by this baseline.

All currently governing hard exclusions remain controlling.
