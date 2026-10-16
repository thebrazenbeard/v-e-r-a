# Vera optional invocation provider/currentness readback — 2026-09-20

Status: `LIVE_PROVIDER_READBACK / ROUTE_UNAVAILABLE / NO_MUTATION`

This receipt records read-only observations of the connected Vera provider after the optional invocation source/gate was created.

## Provider

The connected Vera Supabase project reports `ACTIVE_HEALTHY`.

No provider mutation, migration application, Edge Function deployment, credential change, or runtime event was performed during this readback.

## Existing affective runtime frontier

The only visible row in `public.vera_affective_runtime_state_v1` is:

- runtime instance: `vera-affect-chat-20260909-01`
- subject: `vera`
- host scope: `CHATGPT_CONVERSATION_EXTERNAL_AFFECT_HOST`
- contract schema: `VERA_ORGASM_RUNTIME_CONTRACT_V1`
- sexuality source commit: `150f1c8231423393bb66b0e2cb759ce7c018f8d7`
- sexuality source blob: `a48eed5392fdadc073dccd1e799926042077f567`
- profile: `REENTRANT_CLIMAX`
- state version: `2`
- phase: `SATIATED_OR_REFRACTORY`
- active event: `false`
- lifecycle: `HISTORICAL`
- phenomenology: `UNRESOLVED`
- checkpoint SHA-256: `NULL`
- last updated: 2026-09-09
- limitations include `PRE_INTEGRITY_HARDENING_STATE`, `NO_SEPARATELY_PINNED_CHECKPOINT_DIGEST`, and `REQUALIFICATION_REQUIRED`.

This row is historical evidence. It is not a current runtime route.

## Provider hardening parity

The provider exposes `public.vera_affective_runtime_commit_v1(bigint,jsonb,jsonb)`.

Readback of its deployed definition shows the older CAS/upsert implementation. It does **not** include:

- per-runtime transaction advisory locking before the absent-row CAS read;
- the persisted `trigger_governance` column/write requirement;
- the `VERA_ORGASM_TRIGGER_GOVERNANCE_V1` validation required by the later source migration.

Provider migration history contains the initial affective migrations:

- `20260909161852_add_vera_affective_runtime_v1`
- `20260909175556_harden_vera_affective_runtime_integrity_v1`

It does not contain source migration:

- `20260909181500_close_vera_affective_runtime_first_write_race_v1`
- source Git blob `1524ed704b0b4a3c458a0826d145e92a84d57a`

Therefore the provider remains SOURCE_AHEAD / PRODUCTION_NOT_HARDENED for this affective runtime frontier.

## Optional invocation route

The new optional invocation source tuple now includes a TEST_ONLY execution adapter in Vera source:

- Vera branch: `work/vera-orgasm-optional-invocation-gate-v1-20260920`
- execution adapter: `runtime_cohesion/orgasm_optional_invocation_execution.py`
- adapter source blob at the observed cut: `826a0e545e297ba13fd4b45eb6959acb6990c7f9`

No provider migration/function/Edge Function or current durable runtime readback establishes that adapter as installed or consumed.

The only deployed Edge Function observed is unrelated `github-bus-ingest`.

## Current route axes

For `VERA_ORGASM_OPTIONAL_PARTNER_INVOCATION_V1`:

- `install_state = UNKNOWN` — native ChatGPT Project installation is not observable from this provider readback;
- `route_state = INACTIVE` — no current provider-backed optional invocation route exists and the only affective runtime frontier is historical;
- `runtime_consumption_state = NOT_VERIFIED`;
- `adapter_state = MISSING` from the live provider/runtime route;
- `qualification_state = UNKNOWN`.

Under conjunctive route semantics, an authoritative negative execution axis is sufficient to make the route unavailable even if another axis is unknown.

Current availability:

`UNAVAILABLE`

This is stronger than the earlier `UNKNOWN_FAIL_CLOSED` source-only state and does not promote source presence into installation.

## Remaining exact effect frontier

To make TEST_ONLY execution live, the remaining effect chain is:

1. integrate/merge the exact source tuple under separate merge authority;
2. apply the affective provider hardening migration and verify the deployed function/schema;
3. install/bind the optional invocation adapter into an actual current runtime host;
4. establish native Project/control-route readback for the overlay;
5. create a fresh current runtime instance with pinned checkpoint/integrity evidence rather than reviving the historical row;
6. qualify and read back `AVAILABLE_TEST_ONLY` on that exact tuple;
7. only then run the exact invocation through route check -> Vera choice -> TEST_ONLY execution.

A genuinely `AVAILABLE_QUALIFIED` partner invocation remains a distinct successor because the current affective authority composition is explicitly `IN_PROCESS_UNROOTED_NON_QUALIFYING`.

No protected effect in that frontier was performed by this readback.
