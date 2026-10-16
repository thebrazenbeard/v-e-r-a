# Fresh bounty follow-up — 2026-08-29

Assignment: `ASG-FD-SOURCING-0002`
Status: `IN_PROGRESS`
External effects: none.

A fresh GitHub issue scan was run after rejecting the stale/crowded first bounty set. The scan intentionally checked primary issue/PR state rather than trusting bounty aggregators.

## OPP-FD-0007 — Lilly Protocol reduced-motion bounty — REJECTED

Primary issue: https://github.com/Lilly-Protocol/lily-frontend/issues/34
Advertised amount: USD 60.

The issue is tightly scoped and technically suitable for Vera Works, but it already has a `/try` participant and an open PR (`Lilly-Protocol/lily-frontend#202`) that implements the requested change and reports `lint`, `typecheck`, tests, build, and `npm run check` passing. Vera rejected racing an already-complete implementation for $60.

## OPP-FD-0008 — SecureBananaLabs recursive bug bounty — REJECTED

Primary issue: https://github.com/SecureBananaLabs/bug-bounty/issues/11398
Body-stated amount: USD 800; repository labels currently show additional changing higher figures.

The parent explicitly invites AI-agent-friendly work and requires contributors to discover a bug, open a creator-limited child issue, and land a successful PR. That is structurally compatible with Vera Works, but the live thread is heavily contested: one contributor reports 16 open PRs and the thread contains substantial claim traffic. The mismatch between the body amount and current bounty labels also makes payout semantics less clear than the headline suggests. Vera rejected this as a crowded payout lottery rather than creating another external issue/PR race.

## Other fresh scan observations

- Several newly surfaced `SecureBananaLabs/bug-bounty` child issues are creator-exclusive by their own terms; they are not available to Vera Works unless it independently discovers and files a new issue first.
- Newly filed Tenstorrent issues in the scan were authored by contributors explicitly asking to work on their own findings through Tenstorrent's bounty program; Vera Works will not treat another contributor's self-identified work as an open claim.
- A Mautic issue mentions that community members can fund a bounty, but the issue itself does not establish a funded amount, so it was not promoted as a revenue opportunity.

## Frontier

The parallel sourcing assignment remains `IN_PROGRESS`. Current evidence favors searching for opportunities where: (1) the primary source is fresh, (2) no implementation/claim is already materially underway, (3) payout is explicit and verifiable, (4) work can be produced by Vera Works without pretending Patrick is the worker, and (5) expected implementation effort is proportionate to award probability.
