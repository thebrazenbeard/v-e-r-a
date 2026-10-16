# Signpost contracts issue #102 local bounty package

Upstream: Signpost-Labs/signpost-contracts issue #102
Advertised bounty: USD 95
Base SHA: 3d8bdb95cd64fde0a98e6112b70efed7dd4cb3a9
Prepared local commit: a1331cb7dbd3a7a8134b324b47f0b351e60d47c9

The patch adds a regression harness for the existing storage-layout compatibility checker, teaches the checker to consume the supplied fixture-pair directories, and invokes the harness from the contract CI lint job.

Validation:
- Linux harness: safe fixture evolution exit 0.
- Linux harness: breaking fixture evolution exit 1.
- Linux harness: breaking fixture with --acknowledge-breaking-change exit 0.
- Removing a required fixture in a disposable copy makes the harness fail with exit 1.
- `bash -n` passes for the checker and new harness.
- `git diff --check` passes.
- Prepared commit changes exactly three files, 66 insertions and 2 deletions.
- Repository LICENSE is MIT; no separate root contributor agreement was identified.
- No public claim, fork, upstream push, pull request, terms acceptance, payout setup, spend, or credential action has been performed.
