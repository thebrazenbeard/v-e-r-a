# V1 Witness Model Addendum

Status: `PROPOSED / STACKED ON PR #1 / REVIEW REQUIRED`

## Defect discovered during source deepening

The initial V1 architecture gives each source a `physical_witness_date`. That is adequate only when witness identity is simple. It is insufficient for works that survive in multiple manuscripts, inscriptions, fragments, recensions, or printed states with variant readings.

The Tosefta Panthera/Pandera research exposed the problem directly: the work/tradition, the Vienna manuscript, and the Vienna-specific `Yeshua ben Panteira` reading are related but not identical evidence objects.

## Required distinction

V1 should model at least:

- `SOURCE` — work, artifact, edition, inscription, corpus, or other evidence-bearing source identity;
- `WITNESS` — a particular physical or recoverable textual witness of a source;
- `CLAIM` — an atomic proposition supported/opposed by a source and, when necessary, a specific witness.

A witness record should contain:

- stable witness ID;
- `witness_of` source ID;
- witness kind;
- shelfmark / inventory identifier where known;
- witness date and precision;
- provenance/custody note where useful;
- access mode;
- exact locator(s);
- limitations.

A claim-support edge may cite both `source_id` and `witness_id`.

## Invariants

1. Witness date does not silently become composition date.
2. A witness-specific reading does not silently become the reading of every witness or edition.
3. A digital edition's report of a manuscript variant is not silently promoted to autoptic manuscript readback.
4. Multiple witnesses of one work do not become independent historical sources merely by being physically distinct.
5. A later witness may preserve earlier wording; that possibility is evidence-dependent and must not be assumed either way.
6. Manuscript disagreement is preserved as data rather than normalized away before analysis.

## Candidate relation

```text
WIT-TOSEFTA-VIENNA-COD-HEBR-20
  --WITNESS_OF-->
SRC-TOSEFTA-CHULLIN-2-6
```

The proposition about the Vienna `Yeshua ben Panteira` variant then cites both IDs. This is preferable to assigning the fourteenth-century Vienna date to `SRC-TOSEFTA-CHULLIN-2-6` itself.

## Promotion implication

If accepted, the next canonical registry cut should introduce `registry/witnesses.yaml` (or an equivalently explicit witness node type) and migrate any source records whose physical-witness field currently conflates work identity with a particular surviving witness.

This addendum does not modify PR #1's frozen head. It is a stacked correction discovered by executing the research method against real variant evidence.
