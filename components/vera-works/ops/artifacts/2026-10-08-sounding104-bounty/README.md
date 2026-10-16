# Sounding issue #104 local bounty package

Upstream: Sounding-Labs/sounding issue #104
Advertised bounty: USD 65
Base SHA: 53e9196215aac94e4d02218759f501b70e137d37
Prepared local commit: bff1a0a0480bd3b3f6d2720dc725b39bcffa2b79

The patch adds a 10-line build-job guard that runs `go mod tidy` before tests and fails with `git diff --exit-code -- go.mod go.sum` plus an actionable error message.

Validation:
- Positive: `go mod tidy` leaves canonical `go.mod` and `go.sum` Git blob hashes identical to HEAD; diff exit is 0.
- Negative: a throwaway commit marked the directly imported decimal module `// indirect`; `go mod tidy` removed that drift and `git diff --exit-code` returned 1 while printing the exact diff.
- `git show --check` passes for the prepared commit.
- Prepared commit changes only `.github/workflows/ci.yml` by 10 inserted lines.
- The upstream repository tracks two PR-template files differing only by filename case; that creates an unrelated dirty-path artifact on Windows. It is not included in this patch.
- CONTRIBUTING.md states that contributions are licensed under Apache-2.0, so publication remains a Patrick-owned boundary.
- No public claim, fork, upstream push, pull request, terms acceptance, payout setup, spend, or credential action has been performed.
