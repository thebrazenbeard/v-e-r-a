# Vera Portfolio End-to-End Hostile Qualification V1

Status: **FAIL CLOSED — integration is not end-to-end qualified.**

The source architecture is substantially repaired. Discovery, Roots, Vera, and VCP now agree on the canonical 59-repository portfolio cut and its activation boundaries. Observable Native Project NV2A1 member files match current VCP source bytes. Both Supabase projects are healthy. Current Bus topology resolves Vera to `bus/vera-v2`, and the older Supabase `bus/vera-sol-v1` endpoint is correctly treated as historical/bootstrap projection rather than current routing authority.

The chain then breaks.

## First hard failure

Radar projection is not operating. `radar.projection_lane_state` has zero rows and `radar.projection_batches` has zero rows. The current Vera Bus messages written during this repair are absent from `radar.messages`. The newest projected Vera message is `vera-v2-0001` from September 4, 2026, and no sender has a newer projected message than September 4.

Database health therefore does **not** imply coordination health.

## Provider source custody failure

The active Supabase `github-bus-ingest` function is version 5 and its deployed `handler.ts` and `deno.json` match Bus PR #325 exactly. PR #325 is still an open draft and is not canonical Bus main. The deployed code is not byte-drifting from that candidate; the defect is that production consumes noncanonical source custody.

## CI boundary

Private GitHub Actions for the Vera registry repair, VCP binding repair, and Bus PR #325 did not execute. Their failed jobs report `steps: null`, meaning they never reached checkout or tests. These are **NO-RUNNER** failures, not test failures and not passes.

## WorkBridge

WorkBridgeMCP PR #5 current head `92c66159...` has successful current-head CI, but the real implementation remains unmerged. Current main is still the stub/generic-workflow state, and there is no evidence of installation, MCP registration, or Vera runtime consumption.

## What is qualified

- canonical 59-repository Discovery classification;
- Roots provenance/supersession boundaries;
- canonical Vera 59/42/17 runtime-source registry;
- canonical VCP exact binding to that registry;
- current Bus route authority `bus/vera-v2`;
- fresh Supabase project/schema/function inventory;
- observable Native Project member-byte fidelity to VCP source.

## What is not qualified

The full path:

`native Project -> source selection -> Bus -> Radar projection -> provider effect/readback -> workstation/runtime consumption -> recovery`

does not close. The first hard failure is Bus→Radar projection.

The system should remain fail-closed until the blockers in the machine-readable qualification are resolved and the complete path is rerun.
