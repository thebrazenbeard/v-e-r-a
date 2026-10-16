# Augora issue #69 cloud-prepared bounty package

Upstream: `Augora-Labs/augora#69`  
Advertised bounty: USD 95  
Observed issue state: OPEN, zero comments, no assignee  
Source file: `frontend/wallet.js` blob `eaa4bd63eff653b9867d71855b64f3a7c539e489`  
Prepared patch: `augora-issue-69.patch`

The draft patch makes Freighter's passphrase authoritative:

- if `networkPassphrase` is present (including an empty or wrong string), it must equal the exact Testnet passphrase;
- only when `networkPassphrase` is genuinely absent (`null` or `undefined`) may the code fall back to `network === "TESTNET"`;
- a contradictory Mainnet passphrase can no longer be accepted merely because the wallet also reports the name TESTNET.

## Validation state

**NOT YET EXECUTED.** Lappy is unavailable through Executor, so `node scripts/validate-frontend.mjs` and repository checks have not been run against this draft.

Canonical authorization permits applying/revising/testing this patch on Lappy once connectivity returns. It does **not** authorize an issue claim, fork, external push, pull request to Augora, terms acceptance, payout setup, identity/tax/payment submission, or spend.
