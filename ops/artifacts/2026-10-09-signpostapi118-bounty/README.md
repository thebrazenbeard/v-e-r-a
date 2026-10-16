# Signpost API issue #118 local bounty package

Upstream: Signpost-Labs/signpost-api issue #118
Advertised bounty: USD 85
Upstream base: 175a8c1db9856598d943c62180861afed0c6e45c
Prepared local commit: 4ccc3a4503017ae736dc3f9d1f97877796093321

The patch removes the dead-in-production convertPlaceholders duplicate, points the parity suite at the production translatePlaceholders implementation, preserves the stricter quote-aware behavior from the removed implementation, and adds a regression assertion covering question marks inside quoted SQL.

Validation:
- Targeted parity suite: 6 passed, 2 live-Postgres tests skipped, 0 failed.
- TypeScript typecheck: exit 0.
- ESLint on touched files: exit 0.
- git diff --check: exit 0.
- Normal Husky/lint-staged commit hook: passed.
- Full npm run test: exit 0 after 372.66 seconds.
- Fresh issue check before freeze: OPEN, zero comments, no assignee.

No issue claim, fork, upstream push, pull request, terms acceptance, payout setup, identity/tax submission, spend, or credential action has been performed.
