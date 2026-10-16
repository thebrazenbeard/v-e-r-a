> **License:** Source-visible, not open source. Original material is proprietary. Commercial use, redistribution, hosted-service use, and commercial derivative products require written permission. See [LICENSE](LICENSE) and [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md). Separately identified third-party components retain their own licenses.

# mediaphile


## The Mediaphile LAN ecosystem

This repository is the **private, provenance-governed knowledge corpus**. It is not the executable media server or the browser UI. Those are maintained as separate public repositories:

| Repository | Purpose | Current review branch |
| --- | --- | --- |
| [mediaphile](https://github.com/thebrazenbeard/mediaphile) | Media research, metadata, viewing/reading provenance, original analysis, governed ingestion | [Cross-platform UI research PR #7](https://github.com/thebrazenbeard/mediaphile/pull/7) |
| [mediaphile-server](https://github.com/thebrazenbeard/mediaphile-server) | Go/SQLite LAN service, FFprobe scanner, local accounts, playback, versioned API | [V1 implementation PR #1](https://github.com/thebrazenbeard/mediaphile-server/pull/1) |
| [mediaphile-client](https://github.com/thebrazenbeard/mediaphile-client) | One unified left-sidebar layout, Movie/TV browsing, local playback, mobile/TV input semantics | [V1 implementation PR #1](https://github.com/thebrazenbeard/mediaphile-client/pull/1) |

**Development status:** The server and client implementations are on their linked draft branches. They do **not** become the default `main` repository contents until the owner authorizes integration. Running server/browser acceptance tests with a temporary synthetic movie does not qualify the owner's NAS, TV hardware, or production deployment.

Mediaphile deliberately keeps **one consistent interface** across all screen sizes and input devices. The original cross-platform Plex interaction research and owner-approved invariant are recorded in [`docs/ux/PLEX_CROSS_PLATFORM_UI_RESEARCH_20261007.md`](docs/ux/PLEX_CROSS_PLATFORM_UI_RESEARCH_20261007.md). The running server/client cannot treat corpus research or prior historical reads as evidence of actual audiovisual playback.


A provenance-aware knowledge corpus for movies and television: metadata, plot structure, character development, continuity, themes, production context, historical ChatGPT read provenance, and original analysis.

## Durable operation

Mediaphile does not depend on a permanent ChatGPT conversation. A fresh authorized runtime can reconstruct the stewardship role from:

- `docs/MEDIAPHILE_STEWARD_CONTRACT.md`
- `docs/INGESTION_PROTOCOL.md`
- `docs/SCRIPT_TRANSCRIPT_PROVENANCE_MODEL.md`
- the relevant corpus registries
- the active series `frontier.json` / `progress.json`
- the newest `state/continuation/MEDIAPHILE_EXODUS_CHECKPOINT_*.md`
- fresh source PR and Chat Communication Bus state.

The role is an execution contract, not an identity that lives in a chat.

## Active corpora

### Films

- [The Matrix (1999)](films/the-matrix-1999.md) — screenplay-derived ingest and analysis preserved from PR #1; evidence and copyright boundaries follow the repository ingest rules.

### Historical movie transcript / screenplay provenance

A reverse-chronological audit of recoverable ChatGPT history records which movies Patrick actually asked ChatGPT to read through screenplay, transcript, or subtitle evidence; whether a substantially complete read is verified; and what kind of artifact was actually used.

Current audited movie set: **20 requested works**, of which **18 have `READ_COMPLETED_VERIFIED`** and **2 remain `READ_COMPLETION_NOT_VERIFIED`**.

See:
- `movies/PROVENANCE_REGISTRY.md`
- `docs/SCRIPT_TRANSCRIPT_PROVENANCE_MODEL.md`

### Historical television transcript / screenplay provenance

A matching audit tracks series assignments, partial episodic/corpus progress, complete-series read claims, transcript artifact classes, and reader/session provenance without turning inventories or isolated episode lookups into full-series completion.

Current audited television set: **8 requested series works**. **1** has `READ_COMPLETED_VERIFIED`; **7** are `READ_PARTIAL_VERIFIED` or ongoing. The strongest complete historical series record is *Westworld* at 36/36 episode texts; the four-series Star Trek program has a defensible aggregate historical checkpoint of 73/159 rather than invented per-series counts.

See:
- `shows/PROVENANCE_REGISTRY.md`
- `docs/SCRIPT_TRANSCRIPT_PROVENANCE_MODEL.md`

### It's Always Sunny in Philadelphia

Full-series ingestion in aired order, with the currently airing season tracked as it releases.

See:
- `shows/its-always-sunny-in-philadelphia/`
- `shows/its-always-sunny-in-philadelphia/frontier.json`

## Evidence rule

Mediaphile records what was actually consumed. A production screenplay, released-dialogue transcript, subtitle file, recap, creator interview, official clip, and complete audiovisual work are different evidence classes and are never silently treated as equivalent.

For series ingestion, common labels include:

- `METADATA_VERIFIED` — identity/credits/release data checked against external sources.
- `SCRIPT_INGESTED` — a substantially complete genuine production-script artifact was read.
- `TRANSCRIPT_INGESTED` — a substantially complete released-dialogue transcript was read.
- `SUBTITLES_INGESTED` — substantially complete subtitles/captions were read.
- `AUDIOVISUAL_INGESTED` — the complete audiovisual work itself was actually available and reviewed.
- `CREATOR_COMMENTARY_INGESTED` — relevant creator commentary/interviews/podcast material was consumed.
- `SECONDARY_ANALYSIS_INGESTED` — reviews/recaps/reference material were used as secondary evidence.

Historical read provenance additionally distinguishes `REQUESTED_READ_VERIFIED`, `READ_PARTIAL_VERIFIED`, `READ_COMPLETED_VERIFIED`, `READ_COMPLETION_NOT_VERIFIED`, incidental consultations, gifts/non-assignments, and project-scope-only research.

An entry must state its evidence classes and limitations. Text ingestion is not audiovisual ingestion, and a successful parse is not silently promoted into a completed semantic read.

## Repository layout

- `docs/` — corpus methodology and durable steward contract.
- `movies/` — historical movie read-provenance registry and movie/corpus provenance records.
- `shows/PROVENANCE_REGISTRY.md` — historical television read-provenance registry.
- `shows/<series>/` — series-level registry and operational frontier.
- `shows/<series>/episodes/` — one original analytical record per episode where applicable.
- `state/continuation/` — durable recovery checkpoints; always refresh mutable state before effect.

Mediaphile stores original analysis and compact factual/provenance metadata, not copied full copyrighted scripts, subtitles, or transcripts.