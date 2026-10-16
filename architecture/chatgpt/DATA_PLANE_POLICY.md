# Data Plane Policy

## Canonical plane

GitHub is the canonical durable plane.

Research artifacts, claim ceilings, evidence classifications, source packets,
matrices, experiment receipts, and cross-repo provenance must remain recoverable
from Git history.

## Derived relational plane

WoWSQL is a candidate derived plane, not yet adopted.

If adopted, it should accelerate queries such as:
- claims by evidence class;
- claims by neutral axis;
- stale branch bindings;
- cross-repo provenance;
- transmission edges;
- research frontiers;
- verification receipts.

Suggested entities:
- repositories;
- repo_snapshots;
- branches;
- pull_requests;
- research_artifacts;
- sources;
- source_witnesses;
- claims;
- claim_evidence;
- claim_relations;
- comparison_axes;
- comparison_cells;
- transmission_edges;
- provenance_edges;
- research_frontiers;
- verification_receipts.

Every row representing research state should retain:
- repository;
- commit SHA;
- artifact path;
- content/blob hash where practical;
- evidence class;
- indexed timestamp/version.

The database must be rebuildable from GitHub.

## Supabase

No Supabase role is currently adopted. Patrick explicitly paused that decision.

## External document plane

Google Drive may contain source documents and working material.

Drive content becomes ON_THEO research state only after evaluation and
provenance-bearing persistence.
