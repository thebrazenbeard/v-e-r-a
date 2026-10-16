# Star Wars theatrical-film corpus — historical text provenance

Historical assignment date: `2026-08-14`

Patrick directed a Star Wars movie ingestion, corrected the initial single-film framing to **all of them**, and then told ChatGPT to take the turn until the task was complete. The preserved completion record says transcript-level primary text was obtained for the first twelve theatrical films then in scope; the newly released *The Mandalorian and Grogu* did not have a comparable complete transcript available in that pass.

The historical source family was primarily Forever Dreaming's third-party film transcript archive, with Springfield! Springfield! also used in the comparison and providing the 2008 *Clone Wars* theatrical-film dialogue source. These are released-dialogue text sources, not production screenplays.

## Work ledger

### Star Wars: Episode IV — A New Hope (1977)
- Request: `REQUESTED_READ_VERIFIED`
- Completion: `READ_COMPLETED_VERIFIED`
- Artifact: `RELEASED_DIALOGUE_TRANSCRIPT`
- Historical/current source: https://transcripts.foreverdreaming.org/viewtopic.php?t=35558

### Star Wars: Episode V — The Empire Strikes Back (1980)
- Request: `REQUESTED_READ_VERIFIED`
- Completion: `READ_COMPLETED_VERIFIED`
- Artifact: `RELEASED_DIALOGUE_TRANSCRIPT`
- Historical source identified in the preserved pass: Forever Dreaming; Springfield! Springfield! was also consulted for this film.

### Star Wars: Episode VI — Return of the Jedi (1983)
- Request: `REQUESTED_READ_VERIFIED`
- Completion: `READ_COMPLETED_VERIFIED`
- Artifact: `RELEASED_DIALOGUE_TRANSCRIPT`
- Historical source: Forever Dreaming transcript, preserved historical locator `viewtopic.php?t=35569`.

### Star Wars: Episode I — The Phantom Menace (1999)
- Request: `REQUESTED_READ_VERIFIED`
- Completion: `READ_COMPLETED_VERIFIED`
- Artifact: `RELEASED_DIALOGUE_TRANSCRIPT`
- Historical source family: Forever Dreaming.

### Star Wars: Episode II — Attack of the Clones (2002)
- Request: `REQUESTED_READ_VERIFIED`
- Completion: `READ_COMPLETED_VERIFIED`
- Artifact: `RELEASED_DIALOGUE_TRANSCRIPT`
- Historical source family: Forever Dreaming.

### Star Wars: Episode III — Revenge of the Sith (2005)
- Request: `REQUESTED_READ_VERIFIED`
- Completion: `READ_COMPLETED_VERIFIED`
- Artifact: `RELEASED_DIALOGUE_TRANSCRIPT`
- Historical/current source: https://transcripts.foreverdreaming.org/viewtopic.php?t=35544

### Star Wars: The Clone Wars (2008 theatrical film)
- Request: `REQUESTED_READ_VERIFIED`
- Completion: `READ_COMPLETED_VERIFIED`
- Artifact: `RELEASED_DIALOGUE_TRANSCRIPT`
- Current independently verified movie-text source: https://www.springfieldspringfield.co.uk/movie_script.php?movie=star-wars-the-clone-wars
- Important boundary: this is the **theatrical film**, not the later television episode archive.

### Star Wars: Episode VII — The Force Awakens (2015)
- Request: `REQUESTED_READ_VERIFIED`
- Completion: `READ_COMPLETED_VERIFIED`
- Artifact: `RELEASED_DIALOGUE_TRANSCRIPT`
- Historical source family: Forever Dreaming.

### Rogue One: A Star Wars Story (2016)
- Request: `REQUESTED_READ_VERIFIED`
- Completion: `READ_COMPLETED_VERIFIED`
- Artifact: `RELEASED_DIALOGUE_TRANSCRIPT`
- Historical locator: https://transcripts.foreverdreaming.org/viewtopic.php?t=35522
- A newer Forever Dreaming copy also exists at `viewtopic.php?t=144489`; no claim is made that the two pages are byte-identical.

### Star Wars: Episode VIII — The Last Jedi (2017)
- Request: `REQUESTED_READ_VERIFIED`
- Completion: `READ_COMPLETED_VERIFIED`
- Artifact: `RELEASED_DIALOGUE_TRANSCRIPT`
- Historical source family: Forever Dreaming; preserved historical locator `viewtopic.php?t=35523`.

### Solo: A Star Wars Story (2018)
- Request: `REQUESTED_READ_VERIFIED`
- Completion: `READ_COMPLETED_VERIFIED`
- Artifact: `RELEASED_DIALOGUE_TRANSCRIPT`
- Current source: https://transcripts.foreverdreaming.org/viewtopic.php?t=37640

### Star Wars: Episode IX — The Rise of Skywalker (2019)
- Request: `REQUESTED_READ_VERIFIED`
- Completion: `READ_COMPLETED_VERIFIED`
- Artifact: `RELEASED_DIALOGUE_TRANSCRIPT`
- Historical/current source: https://transcripts.foreverdreaming.org/viewtopic.php?t=39942

### The Mandalorian and Grogu (2026)
- Request: `REQUESTED_READ_VERIFIED` as part of the contemporaneous full theatrical-film corpus.
- Completion: `READ_COMPLETION_NOT_VERIFIED`
- Historical pass explicitly says no comparable complete transcript had been established and therefore gives this film lower evidentiary weight.
- This record must not be retroactively promoted merely because a transcript source becomes available later; a later fresh read would be a new ingestion event.

## Provenance judgment

The first twelve films are high-confidence **historical completed text reads** because the preserved conversation records both the corpus assignment and the completion claim. Their text provenance is more modest: third-party dialogue transcripts rather than studio production scripts. Mediaphile therefore preserves `READ_COMPLETED_VERIFIED` independently from artifact class.

Exact per-title URL recovery is incomplete for some of the middle corpus even though the preserved interaction states that transcript-level text was obtained. Missing exact URL locators are not replaced with invented ones. Current source discovery can corroborate availability but does not rewrite the historical source chain.
