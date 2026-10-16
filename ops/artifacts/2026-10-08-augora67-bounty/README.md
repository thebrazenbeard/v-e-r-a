# Augora issue #67 cloud-prepared bounty package

Upstream: `Augora-Labs/augora#67`  
Advertised bounty: USD 100  
Observed issue state: OPEN, zero comments, no assignee  
Source: `frontend/script.js` blob `5251e255391d6420e1f286c9fbec41bf257bfd0e`; `frontend/index.html` blob `d5221c048812e80fbacd60f330b1a13de664c427`  
Prepared patch: `augora-issue-67.patch`

The draft patch makes the network metrics consistent with the app's Testnet-only transaction flow:

- defines one `STELLAR_NETWORK` object carrying the display name and Testnet Horizon URL;
- derives `HORIZON_URL` from that object;
- updates the live connection label and network heading from the same network-name constant; and
- changes the three metric captions to explicitly identify Testnet.

## Validation state

**NOT YET EXECUTED.** Lappy is unavailable through Executor, so `node scripts/validate-frontend.mjs` and repository checks have not been run against this draft.

Canonical authorization permits applying/revising/testing this patch on Lappy once connectivity returns. It does **not** authorize an issue claim, fork, external push, pull request to Augora, terms acceptance, payout setup, identity/tax/payment submission, or spend.
