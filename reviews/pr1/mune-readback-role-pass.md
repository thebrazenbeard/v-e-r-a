# On-Theo PR #1 — Mune Citation / Readback Role-Pass

Status: `PASS_WITH_LIMITATIONS`
Review subject: `thebrazenbeard/on-theo@c1f6df5ea1fee0c5ac8d84a7b5c2b81fb905fd3e`
Role lens: `Mune / citation readback / registry correspondence / reproducibility`
Execution provenance: same current Vera model/runtime, isolated readback pass; not an independent model sample or separate terminal execution.

## Exact-head structure

PR #1 remains one commit over `main@eedbcf660c2cfe6cff5636e798806b0cd3d56efc`, with exactly eight additive files and no deletions.

## Registry correspondence

Checked claim-to-source edges in `registry/claims.yaml` against `registry/sources.yaml`. All referenced IDs resolve: `SRC-ORIGEN-CONTRA-CELSUM`, `MAT-ABDES-PANTERA-INSCRIPTION`, `SRC-BAVLI-SHABBAT-104B`, `SCH-BLUMELL-2007-CELSUS-JEW`, and `SCH-NIEHOFF-2013-CELSUS-JEW`.

Checked transmission endpoints in `registry/transmissions.yaml`; no dangling source IDs were found in the frozen V1 registries reviewed.

## Locator readback

- Origen, *Contra Celsum* I.28 supports the bounded proposition that Celsus's Jewish speaker attacks the virgin-birth claim and supplies an adultery/illegitimate-birth counter-story. The passage does not name Panthera there.
- I.32 supports the bounded proposition that Origen reports the accusation that Mary bore a child to a soldier named Panthera and immediately rejects the story as fabricated.
- I.69 supports the repeated Panthera-paternity statement but remains the same Origen work and is not an independent witness.
- Shabbat 104b supports the textual occurrence of ben Stada, ben Pandeira, and Miriam in the checked passage; the displayed passage does not explicitly name Jesus/Yeshua.
- The cited Tiberius Julius Abdes Pantera inscription/transcription supports a first-century Roman soldier/person with that name; it does not support Mary, Jesus/Yeshua, Nazareth, conception, or paternity linkage.

## Limitations

### MU-L1 — scholarly arguments are not full-paper readbacks

Blumell and Niehoff are correctly registered as scholarly interpretation with publisher/institutional access modes. PR #1 uses them only for the direction of their arguments. Detailed use of their evidence, counterarguments, or source reconstruction requires full-text verification.

### MU-L2 — access surface is not witness identity

New Advent, Sefaria, and the inscription database are modern access/transcription surfaces. They must not be treated as the physical ancient witnesses themselves. PR #2's later witness-node correction is the right architectural direction.

### MU-L3 — review receipt remains prose-only

`docs/REVIEW_PROTOCOL_V1.md` defines what a review receipt must bind, but PR #1 does not yet provide a machine-readable receipt schema or registry. This pass therefore persists a human-readable exact-head artifact only.

## Result

The checked proposition-to-source edges are coherent at the level asserted, and the packet does not count Origen I.32/I.69 as independent sources or silently identify Shabbat 104b with Jesus. Result is `PASS_WITH_LIMITATIONS` because full-paper scholarly readback, witness/access separation, and machine-readable receipt structure remain incomplete.