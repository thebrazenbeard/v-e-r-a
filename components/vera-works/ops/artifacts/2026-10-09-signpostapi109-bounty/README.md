# Signpost API issue #109 local bounty package

Upstream: Signpost-Labs/signpost-api issue #109
Advertised bounty: USD 85
Upstream base: 175a8c1db9856598d943c62180861afed0c6e45c
Prepared local commit: 00c114096ad2af873db961de3b4c4954c4de7d09

The patch adds wallet-blocklist input invariants at both the service and database layers: wallet must be non-empty and reason must be null or at most 500 characters. It adds SQLite and Postgres migrations plus direct service/SQLite enforcement tests.

Validation:
- Full npm run test: 240 suites passed, 4212 tests passed; 7 suites and 46 tests skipped; exit 0.
- Windows-safe equivalent of the repository lint scope: 0 errors, 50 existing warnings; exit 0.
- npm run typecheck: exit 0.
- npm run build: exit 0.
- git diff --check: exit 0.
- Fresh issue check before freeze: OPEN, zero comments, no assignee.
- The repository's literal npm run lint script is Windows-incompatible because it single-quotes globs; the same directories were linted directly with ESLint instead.

No issue claim, fork, upstream push, pull request, terms acceptance, payout setup, identity/tax submission, spend, or credential action has been performed.
