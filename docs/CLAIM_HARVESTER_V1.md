# Vera Works Claim Harvester V1

## Purpose

Claim Harvester is a read-first Vera Works subsystem for finding value that is legitimately claimable under an authoritative rule without turning "unclaimed" into "ownerless."

The target operating pattern is:

```text
machines hunt -> evidence accumulates -> entitlement is tested -> effect boundary is explicit
```

It is designed for the passive/no-person-to-person-communication revenue lane.

## Hard rule

A claim is not executable merely because value exists, a wallet is inactive, a deadline is approaching, another person has not claimed it, or a semantic loophole can be imagined.

V1 recognizes these eligibility classes:

- `ENTITLED` — the governing source designates the relevant identity, wallet, account, or class.
- `OPEN_CLAIM` — the governing source explicitly offers value to any claimant satisfying published conditions.
- `AMBIGUOUS` — wording may support a theory, but ownership/eligibility is unresolved.
- `NOT_OURS` — the value belongs to another party or there is no entitlement path.
- `UNKNOWN` — evidence is insufficient.

Only `ENTITLED` and `OPEN_CLAIM` may advance beyond research, and only after authoritative evidence plus beneficiary matching.

## Portfolio composition

Claim Harvester deliberately reuses portfolio capabilities instead of creating another monolith:

1. **Discovery** — nominates sources/opportunities across changing public surfaces.
2. **Ingest** — preferred exact-byte acquisition/provenance boundary for HTTP/GitHub/file material.
3. **Roots** — reconstructs source lineage and earliest accessible authoritative evidence.
4. **Lou-Pole / FreeRowCochkar** — pressure-tests literal eligibility language and exclusion boundaries.
5. **Claim Harvester core** — applies deterministic source, beneficiary, window, value, and external-effect gates.
6. **Voss / Cricket** — hostile review and proposition-preserving challenge for material ambiguity.
7. **WIP** — crash/replay discipline for long-running scans and ambiguous effects.
8. **Project Runner** — assignment, scheduling, lease, and bounded execution spine.
9. **Pre-Active** — optional unattended re-entry/monitoring once a qualified installed runtime is actually present.
10. **Vera Works** — durable assignment, hold, financial, and authority state.

These are semantic roles, not automatic runtime bindings. Source presence is not installation or active execution.

## Privacy boundary

Full wallet addresses are runtime inputs, not Git configuration.

Git may store:

- a wallet alias such as `vera-fund-btc` or `vera-fund-evm`;
- the chain family;
- a one-way SHA-256 fingerprint when useful for evidence binding;
- public claim-source evidence that does not leak private credentials.

Git must not store:

- seed phrases;
- private keys;
- wallet passwords;
- signing credentials;
- recovery codes;
- unrelated financial transaction history;
- identity/tax secrets.

The example configuration therefore references environment-variable names rather than addresses.

## Deterministic V1 gates

For each normalized `CandidateObservation`, the core evaluates:

1. Is the eligibility explicitly `ENTITLED` or `OPEN_CLAIM`?
2. Is the evidence authoritative: government, regulator, court administrator, official/first-party protocol?
3. Is the claim window currently open?
4. Does a wallet beneficiary exactly match a configured runtime wallet, or has an identity/open-class condition been independently verified?
5. Does the candidate require person-to-person communication? If yes, it is outside the current lane.
6. Is expected value positive when enough monetary data exists?
7. Does the path require terms/account acceptance? If yes, create a Patrick decision boundary.
8. Does it require identity verification or a wallet signature? If yes, create a Patrick action boundary.
9. Otherwise, stop at `READY_FOR_EFFECT_AUTHORIZATION`.

Critically, `READY_FOR_EFFECT_AUTHORIZATION` does **not** perform the claim. It means the candidate is ready for an exact effect packet under the Vera Works external-effect rules.

## Financial semantics

A discovered candidate is not a receivable.

```text
discovered candidate
    != verified entitlement
    != approved external claim
    != receivable
    != received cash/token
    != available Vera Fund
```

The existing Vera Works financial event model remains authoritative. Claim Harvester does not create `RECEIVABLE` or `RECEIVED` events merely because its own assessment is positive.

## Runtime configuration

See `work/claim-harvester/config.example.json`.

The V1 core loads wallet targets from environment variables at runtime. Example:

```powershell
$env:VERA_WORKS_BTC_ADDRESS = "<public receiving address>"
$env:VERA_WORKS_EVM_ADDRESS = "<public receiving address>"
```

Public addresses are not signing secrets, but they expose financial graph information and are therefore still kept out of the repository by default.

## Candidate normalization

Outer discovery/acquisition lanes produce normalized dictionaries accepted by `CandidateObservation.from_dict`.

Every candidate should retain:

- exact claim/source identifier;
- authoritative URI;
- digest of the acquired source artifact;
- observation time;
- exact eligibility class;
- beneficiary semantics;
- claim window;
- value/fee/reserve estimates when known;
- external-boundary flags;
- evidence references.

The outer lane may be a web researcher, an Ingest-backed source adapter, an official JSON/API feed, a manually reviewed source, or a future Pre-Active observer. Claim Harvester does not pretend that discovery provenance is identical across those lanes.

## Append-only assessment ledger

`ClaimLedger` stores JSONL assessment records with deterministic idempotency keys. Repeating the exact same assessment does not append a duplicate row.

This ledger is local operational evidence only. It does not replace canonical Vera Works immutable events for assignments, holds, or financial state.

## Failure model

- Secondary/affiliate/listicle evidence -> research only.
- Ambiguous ownership -> research only.
- Wallet mismatch -> reject.
- Expired claim -> close.
- Human conversation required -> out of current lane.
- Terms/account boundary -> Patrick decision hold.
- Identity/signature boundary -> Patrick action hold.
- No explicit effect authorization -> do not claim.

## V1 non-goals

V1 does not:

- brute-force keys or seed phrases;
- sweep dormant wallets;
- exploit forgotten accounts/contracts;
- front-run other claimants;
- bypass KYC, jurisdiction, or eligibility rules;
- sign transactions;
- submit forms;
- create accounts;
- accept terms;
- publish data;
- treat airdrop rumor pages as authoritative;
- continuously run merely because source code exists.

Those require separate authority and, where relevant, Patrick's legal/financial action.
