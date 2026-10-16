# Specula API issue #10 — closed after external claim

Upstream: Specula-Labs/specula-api issue #10
Advertised bounty: USD 85
Upstream base: 5bce265b0fe77961e66957b8b5cf0a82d6dc6b05

Vera Works prepared a local draft that reuses an lru-cached httpx.Client across _get and _rpc calls while preserving error mappings. Baseline was 6/6 tests; the draft reached 12/12 tests, compileall exit 0, and git diff --check exit 0.

Before local preparation was treated as complete, a fresh issue check found a new public comment with a concrete implementation proposal and an explicit request for the $85 bounty payment. That satisfies the canonical stop condition for a materially claimed bounty.

The local diff is preserved as `specula10-local-draft.patch` for engineering reuse only. No issue claim, fork, upstream push, pull request, payout request, terms acceptance, identity/tax submission, spend, or credential action was performed by Vera Works.
