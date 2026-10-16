# Augora issue #68 cloud-prepared bounty package

Upstream: `Augora-Labs/augora#68`  
Advertised bounty: USD 85  
Observed issue state: OPEN, zero comments, no assignee  
Source file: `frontend/soroban.js` blob `510c2422c680bf8a256a834f13e477f4397f5bd7`  
Prepared patch: `augora-issue-68.patch`

The draft patch removes the duplicated Stellar SDK network constant from the two transaction paths:

- removes `Networks` from both SDK destructurings;
- uses `TESTNET.networkPassphrase` when constructing `placeBet`;
- uses `TESTNET.networkPassphrase` when decoding the signed `placeBet` XDR;
- uses `TESTNET.networkPassphrase` when constructing `reducePosition`; and
- uses `TESTNET.networkPassphrase` when decoding the signed `reducePosition` XDR.

That satisfies the source-level acceptance condition that no `Networks.TESTNET` reference remain in `frontend/soroban.js`.

## Validation state

**NOT YET EXECUTED.** Lappy is currently unavailable through Executor, so `node scripts/validate-frontend.mjs` and any repository checks have not been run against this draft.

Canonical authorization permits applying/revising/testing the patch on Lappy when connectivity returns. It does **not** authorize a bounty claim, fork, external push, pull request to Augora, terms acceptance, payout setup, identity/tax/payment submission, or spend.
