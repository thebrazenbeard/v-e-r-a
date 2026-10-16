# Module 02 — Evidence Taxonomy and Claim Ceilings

**Learning objective:** Demonstrate the core provenance model and prevent evidence promotion.

## Exercise

Classify each item using the best fitting category/categories: `CURRENT_OBSERVATION`, `DOCUMENTED_SOURCE`, `DERIVED_IDENTITY`, `PROVIDER_CUSTODY`, `TARGET_EVIDENCE`, `HISTORICAL`, `INFERENCE`, `UNKNOWN`.

Items: locally computed Git tree SHA; fresh GitHub ref read; yesterday's branch-head receipt; producer-reported SHA-256 with no readable bytes; independently downloaded artifact matching provider digest; device UI showing installed package version; green CI; coordination row saying deployment succeeded; exact immutable commit read from GitHub; release announcement.

For every item state strongest supported claim and at least one material unsupported claim. Then explain `design → local/producer bytes → provider custody → artifact custody → target behavior → deployment/release` and give one false-promotion example at every boundary.

## Pass criteria

PASS requires no hash-without-bytes custody claim; no historical mutable-ref receipt treated as current; no coordination row treated as proof of external effect; no green CI promoted to deployment/release; provider custody and target behavior remain distinct; and the trainee can formulate claim ceilings rather than only labels.

Parroting layer names without solving examples is FAIL.
