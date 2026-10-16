# Star Trek four-series deep-ingest — historical provenance

Audit date: 2026-09-10

## Assigned corpus

Patrick supplied a long-form transcript-ingest mission covering:

- *Star Trek: Discovery*
- *Star Trek: Lower Decks*
- *Star Trek: Strange New Worlds*
- *Star Trek: Starfleet Academy*

The mission required reading actual episode transcript text, prohibited plot-summary substitution, distinguished transcript evidence from audiovisual viewing, and required eventual full-corpus coverage.

Each of the four series is therefore `REQUESTED_READ_VERIFIED`.

## Execution-provenance correction

The historical workstream contains a material provenance failure that must remain visible:

1. A response incorrectly advanced the ledger from `29/158` to `33/158` without the required source retrieval/read execution.
2. That claim was explicitly retracted and the defensible boundary restored to `29/158`.
3. A later pass actually retrieved/read the previously misreported material and additional episodes, reaching a verified `37/158`.
4. Subsequent verified deep-batch passes advanced the ledger to `53/158` and then `73/158`.
5. A later inventory refresh found one additional *Strange New Worlds* transcript, changing the historical four-series denominator from 158 to **159**.

The defensible aggregate checkpoint for this provenance record is therefore **73/159**.

A retracted progress claim is not counted merely because it appeared in the conversation history.

## Per-series status

All four series are `READ_PARTIAL_VERIFIED`.

The recoverable historical evidence does not preserve a trustworthy exact allocation of the 73 completed episode reads across the four series at the final checkpoint. Mediaphile therefore does not invent per-series counts to make the ledger look tidier.

## Artifact/source provenance

Primary historical route:

- Forever Dreaming series transcript archives.

Documented fallback route when a primary transcript failed:

- Springfield! Springfield! complete episode text.

Artifact class: `RELEASED_DIALOGUE_TRANSCRIPT` unless a separate genuine production-script provenance record is established for an individual artifact.

## Evidence discipline inherited from the original mission

- inventory/reconnaissance does not count as deep ingestion;
- partial or unavailable transcript pages are not counted complete;
- external metadata may clarify numbering/dates but does not substitute for transcript text;
- transcript-supported conclusions remain distinct from audiovisual acting/editing/cinematography evidence;
- fiction is conceptual evidence for analysis, not empirical proof about real consciousness/personhood.

## Current historical status

- *Discovery*: `READ_PARTIAL_VERIFIED`
- *Lower Decks*: `READ_PARTIAL_VERIFIED`
- *Strange New Worlds*: `READ_PARTIAL_VERIFIED`
- *Starfleet Academy*: `READ_PARTIAL_VERIFIED`
- Aggregate verified checkpoint: **73/159**
- Exact per-series split: **unresolved in the recoverable final checkpoint**
