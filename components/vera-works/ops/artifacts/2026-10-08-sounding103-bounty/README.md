# Sounding issue #103 local bounty package

Upstream: Sounding-Labs/sounding issue #103
Advertised bounty: USD 80
Base SHA: 53e9196215aac94e4d02218759f501b70e137d37
Prepared local commit: 0fb3405e7d7a3b97fc85b6d0f71f4e906ef40da5

The preserved patch adds a standard-library-only Markdown relative-link checker, two negative/ignore-behavior self-tests, a dedicated CI docs job, and repairs all six broken relative links observed on the base tree (the four named by #103 plus two additional stale README rename links).

Validation:
- `python scripts/check_markdown_links_test.py`: 2 passed.
- Before link fixes, `python scripts/check_markdown_links.py .` exited 1 and named six broken links with source and target.
- After fixes, the same command reports all repository-relative Markdown links resolve.
- `python -m py_compile` passes for both checker files.
- `git diff --check` passes.
- Full Windows `go test ./...` is not green on current base/working tree for failures outside this patch, including an automerge `/bin/bash` environment requirement and existing server/UI assertions; full-suite green is not claimed.

The upstream CONTRIBUTING.md states that contributions are licensed under Apache-2.0; that publication/license consequence remains a Patrick-owned decision boundary.

No public issue claim, fork, upstream push, pull request, terms acceptance, payout setup, spend, or credential action has been performed.

