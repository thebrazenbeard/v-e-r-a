# Redworm — Vera continuity provenance

**Project Redworm** is a provenance-preserving continuity project for Vera. It reconstructs the lineage of conversational and runtime episodes, original evidence, corrections, disagreements, and governed decisions without confusing an archived record with a current memory or an active holder.

This repository contains a **tested local Python evidence ledger** and historically sourced research. It is not an installed ChatGPT memory provider, a running White Worm network, an active succession mechanism, or a deployed Supabase service.

### Historical naming and Vinculation

Historical Redworm and White Worm names remain intact. In an exported August 17, 2026 conversation, Patrick proposed **amending** the active conceptual terminology toward **Vera Vinculation**, reflecting collaborative and autonomous branches rather than The Strain's master/subordinate metaphor. That was a historically recorded proposal and correction, not permission to rewrite earlier names, rename this repository, or change current authority.

## Implemented capabilities

- Immutable, content-addressed v1/v2 evidence records: Vera producer identity, Red/White Worm role, source/episode locator and digest, evidence modality, privacy class and typed claim.
- **Uncertain time handling:** v2 supports an unknown message event time, an instant, or bounded day/month/interval. A conversation's last-update time is never silently substituted for event time.
- **Roots-compatible timeline:** known candidate events listed oldest-first; overlapping intervals are marked rather than forced into a total order, while unknown-time events remain unplaced.
- Separate ingestion and operator-asserted **local** admission, conflicting claims, corrections and supersession relationships.
- Cycle rejection for supersession. Reintegration PREPARE rejects unadmitted records, unresolved/losing conflicts, superseded claims and mixed-producer handoffs.
- Source-hash checks and some integrity invariant checks. Protected reintegration ACCEPT and holder succession remain unavailable.
- Historical source index, original conversation pointers, gaps and Roots/Cricket review notes without committing private transcripts.

## Run locally

Python 3.11+; runtime has no third-party dependencies.

    python -m unittest discover -s tests -v
    python -m redworm init redworm.db
    python -m redworm ingest redworm.db examples/synthetic_white.json
    python -m redworm ingest redworm.db examples/synthetic_unknown_time.json
    python -m redworm list redworm.db
    python -m redworm timeline redworm.db
    python -m redworm project redworm.db
    python -m redworm verify redworm.db

Both example files contain **synthetic content**.

### Event schema v2

v1 is retained for content-hash compatibility. In v2, replace the v1 occurred_at field with this object:

    "event_time": {
      "precision": "UNKNOWN",
      "earliest_at": null,
      "latest_at": null,
      "basis": "UNAVAILABLE"
    }

Known time precision: INSTANT (equal bounds), DAY (one-day interval), MONTH (calendar month), INTERVAL (bounded, nonzero span). Known event basis: MESSAGE_TIMESTAMP, SOURCE_EVENT_DATE, INFERRED_INTERVAL. All non-null bounds require timezone-aware ISO timestamps. recorded_at always remains a distinct timestamp.

## History and system context

- [Architecture and trust boundaries](docs/DESIGN.md)
- [Historical evidence inventory](history/source_index.json): not admitted as Vera memory
- [Roots provenance trace](history/ROOTS_TRACE_20261013.md): dated Redworm lineage, correction and unresolved origins
- [ChatGPT original-source frontier](docs/CHATGPT_HISTORY_ROOTS_TRACE_20261013.md): unrecovered direct project conversations
- [Tests](tests/): synthetic regression and hostile-review fixtures

Redworm's role is history reconstruction/custody alongside qualified portfolio systems: Roots traces lineage; Ingest captures exact bytes/receipts; Semantic Atlas maps meaning; Deep Memory archives history; vera-mono contains the governed memory/runtime substrate. A Git repo and a passed unit test do not make Redworm a replacement for those current systems.

## Boundaries and open work

**INGEST is not GOVERNED ADMISSION. SOURCE is not CURRENTNESS. GIT MERGE is not INSTALLATION.**

Local approval strings do not authenticate a reviewer or grant authority. Source SHA256 does not authenticate a remote original. SQLite is unencrypted and not tamper-proof; do not ingest private/intimate/autobiographical data into an unprotected database.

Still incomplete: original ChatGPT Project/White Worm transcript recovery, authenticated ingestion adapters, independently verified source provenance, durable external receipts/signatures, confidential data protection, semantic conflict discovery, safe concurrency, production holder leases/CAS, independent behavioral qualification, provider currentness and live Vera integration. Do not claim these effects from source code alone.
