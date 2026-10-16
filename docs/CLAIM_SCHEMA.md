# Claim Record Schema

Use this schema for chronology entries, contested claims, and synthesis assertions.

```yaml
id: stable-kebab-case-id
title: short human-readable title
claim: exact proposition being recorded
classification:
  - PRIMARY_TEXT | MATERIAL_EVIDENCE | HISTORICAL_RECONSTRUCTION | LATER_TRADITION | SCHOLARLY_INTERPRETATION | PROJECT_INFERENCE | SPECULATIVE_MODEL | UNKNOWN
traditions:
  - judaism | christianity | islam | greco-roman | gnostic | other
claimed_event_date:
  start: null
  end: null
  precision: exact | approximate | range | unknown
source_date:
  start: null
  end: null
  precision: exact | approximate | range | unknown
source:
  work: null
  passage: null
  author_or_tradition: null
  url: null
provenance_note: null
confidence: high | medium | low | unresolved
contested: false
alternatives: []
transmission_relation:
  - DIRECT_DEPENDENCE_POSSIBLE | SHARED_TRADITION | STRUCTURAL_PARALLEL | PROJECT_ANALOGY | NONE_ESTABLISHED
notes: null
```

## Confidence means evidentiary confidence, not theological truth

`high` means the specific proposition is strongly supported at the level asserted. Example: "the Gospel of Mark contains a hometown rejection scene" can be high-confidence as a textual fact. "The hometown rejection happened exactly as narrated" is a different proposition requiring a different confidence judgment.

`unresolved` is preferred to false precision.

## Atomicity

One record should state one proposition. Do not bundle:

> Mary became pregnant outside marriage, Nazareth mocked Jesus, this caused adolescent isolation, and isolation produced his theology.

Instead split into source-attested pregnancy claims, evidence for/against paternity stigma, evidence for hometown hostility, absence of childhood records, and the later psychological hypothesis.

This allows one link in a chain to fail without destroying the rest.
