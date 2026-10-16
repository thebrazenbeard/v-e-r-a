# It's Always Sunny in Philadelphia

## Corpus status

- Series status: `AIRING`
- Ingestion strategy: strict aired order for the historical corpus + current-release tracking
- Historical corpus: Seasons 1–17 complete at the repository's recorded text-ingestion level
- Requested target: complete through `S18E04` — `2026: A Virtual Insanity`
- Current released frontier: `S18E06` — `The War on Alcohol`
- Text-ingestion frontier: `S18E06`
- S18E06 evidence state: `METADATA_INGESTED` + `TRANSCRIPT_INGESTED`; audiovisual false
- Current official episode units represented under the corpus counting rule: `184`
- Next scheduled episode: `S18E07` — `Gilligan's Island: A Conspiracy Theorist's Paradise` — 2026-09-21
- Season 18 scheduled extent currently cataloged: `S18E10` on 2026-10-12
- As of: `2026-09-19`

Season 18 is currently airing. Episodes 1–6 have aired/released and released-dialogue text is ingested through S18E06. S18E07 is still a scheduled future unit at this checkpoint.

The corpus uses its explicit episode-unit counting rule while preserving work-level provenance. The televised hour-long *A Very Sunny Christmas* is one continuous work but occupies linked S06E13 and S06E14 records in this corpus. Some third-party guides count that work differently and can therefore differ by one in overall episode numbering; preserve that conflict rather than silently normalizing it.

## Primary tracking sources

- FX / FXX current series listing: https://abc.com/show/f80b5776-908c-4fe3-80c1-40850eaab5a4
- Disney+ Season 18 release schedule: https://www.disneyplus.com/explore/articles/its-always-sunny-in-philadelphia-season-18
- TVMaze episode guide: https://www.tvmaze.com/shows/347/its-always-sunny-in-philadelphia/episodeguide
- TheTVDB aired-order guide: https://thetvdb.com/series/its-always-sunny-in-philadelphia/allseasons/official
- Released-dialogue transcript source for S18E06: https://www.transcripts.foreverdreaming.org/viewtopic.php?p=377674

## Operational frontier

`frontier.json` is the machine-readable current-release/source frontier. It separates cataloged, released, source-available/ingested, text-ingested, audiovisual-ingested, and next-expected states. It is an operational snapshot, not permanent truth; refresh release/source state before mutation.

`progress.json` remains the broader season/corpus progress ledger.

## Series-level analytical questions

The corpus tracks more than plot. Across the run it tests and refines claims about:

- how the Gang's moral logic, self-image, and mutual dependency change;
- Dennis's vanity/control pathology and how early traits develop into later characterization;
- Mac's identity, insecurity, religiosity, masculinity, and later coming-out arc, while separating true foreshadowing from retroactive resonance;
- Charlie's competence/incompetence split, literacy, obsession with the Waitress, family history, and unusual moral baseline;
- Dee's movement from comparatively grounded participant toward the Gang's full pathology and scapegoat role;
- Frank's arrival in Season 2 and the effect he has on the show's reality, escalation, money, and moral ceiling;
- recurring secondary characters and cumulative damage caused by the Gang;
- Paddy's Pub as business, home base, social ecosystem, and recurring economic constraint;
- shifts in the show's satire, production style, performance register, and degree of realism over time.

## Evidence model

Episode records describe what was actually ingested:

- `METADATA_INGESTED` — episode identity/release/credits or equivalent metadata was verified.
- `TEXT_INGESTED` / `TRANSCRIPT_INGESTED` — a substantially complete released-dialogue transcript/subtitle source was actually read.
- `SCRIPT_INGESTED` — a substantially complete genuine production-script artifact was actually read.
- `SECONDARY_ANALYSIS_INGESTED` — secondary plot/context material was read and kept distinct from primary text evidence.
- `AUDIOVISUAL_INGESTED` — reserved for complete audiovisual review; text alone never qualifies.

Visual performance, editing, blocking, music, sound design, and timing remain unverified unless complete audiovisual evidence or a specifically bounded clip was actually reviewed.

See `episodes/` for individual records, `progress.json` for the broader ledger, and `frontier.json` for the exact current-release frontier.
