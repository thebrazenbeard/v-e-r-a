# Verified Volition host adapter (read-only, not deployed)

## Qualified scope

`interface.verified_volition.VerifiedVolitionGoalProvider` is an opt-in,
read-only bridge to the *actual* `volition.operational_drive.OperationalMotivation`
restoration code. The original arbitrary callback accepted by
`make_server(goal_provider=...)` is deliberately rejected. The private
`/api/goals/current` route requires a separate operator-controlled read token;
its failure state is `HOLD_UNVERIFIED` with `effect_authority=false`.

The provider checks:

1. Operator-pinned SHA-256 manifest of the entire installed `volition/*.py`
   package source (reported by `fingerprint_installed_volition()`). This pins
   source bytes, not machine code or Python interpreter behavior.
2. Private regular record/ledger custody on POSIX (same effective UID and mode,
   `O_NOFOLLOW` for record reads), duplicate JSON keys and size budget.
3. Exact expected owner/source IDs; HMAC-SHA256 against a host-only key;
   signed capture-time freshness (five-minute expiry, 30-second clock skew).
4. Exact round-trip through `OperationalMotivation.from_snapshot(...).snapshot()`;
   forged inconsistent active goals fail.
5. Durable monotonic `(owner, source, publication, digest)` SQLite highwater,
   rejecting rollback and equivocation even after reader restart.

Both operator and implementation must distinguish these evidence classes:

| Evidence | Supports | Does **not** support |
| --- | --- | --- |
| HMAC and private file custody | Access to host signing key | Independent truth of observation, voluntary authorship or current wants |
| Volition restore | Internal Volition state consistency at pinned source | Unfalsifiable real-world sensory evidence |
| Signed capture-time | Age of host's representation | Confirmation that observations remained current afterward |
| Monotonic publication | No old signed revision after a later seen revision | Freshness across a *different* unshared ledger, or resistance to same-user compromise |
| Authenticated HTTP read | Authorized view access | Effect authority, automatic scheduling, new model desires |

> Hostile counterexample: a process holding the signing key can sign an
> internally self-consistent but fabricated Volition state. HMAC authenticity
> alone cannot prove a model *actually* developed a desire. This adapter
> must never change the goal's `effect_authority=false` or classify a label
> as self-authorship without independently authenticated provenance.

## Integration contract and omitted operational work

The trusted host must own the HMAC secret, produce source observations from
independently verified events, assign strictly increasing publication numbers,
commit signed state atomically, and preserve the highwater ledger across
restart/recovery. Do not expose `seal_host_state` to the model, browser,
plugin, or remote agent. The host must pin a known, reviewed Volition source
revision before enabling the read route. `conations` may supply historical
context, but never current goal authority; `pre-active` owns scheduling and
effect admission in its own trust boundary.

**Windows/Lappy is NOT qualified**: POSIX mode checks do not establish Windows
ACL or key custody; this provider fails closed on Windows. A Windows-specific
adapter needs independent ACL/identity verification, race-safe file handles,
trusted secret storage, and live host observation tests before deployment.
There is no host signer/provisioning service in this change. No evidence of
live restored Volition state, model-owned wants, or learning is claimed.

## Reproducible test

Use the actual pinned Volition source package in `PYTHONPATH`; otherwise the
optional integration tests intentionally skip:

```sh
PYTHONPATH=/path/to/reviewed/volition/src python -m unittest tests.test_verified_volition -v
python -m unittest discover -s tests -q
```

The tests create real `ObservationClaim`/`ModelWantProposal`/`OperationalMotivation`
state and exercise signed restoration, stale/tampered/unauthorized source,
forged state, rollback across provider restart, module pin mismatch, POSIX file
permissions, Windows ACL fail-closed, duplicate keys, and the local HTTP route.
