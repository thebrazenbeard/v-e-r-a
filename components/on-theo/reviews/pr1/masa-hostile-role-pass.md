# On-Theo PR #1 — Masa Hostile Role-Pass

Status: `PASS_WITH_LIMITATIONS`
Review subject: `thebrazenbeard/on-theo@c1f6df5ea1fee0c5ac8d84a7b5c2b81fb905fd3e`
Role lens: `Masa / hostile falsification`
Execution provenance: same current Vera model/runtime, isolated hostile-review pass; not an independent model sample or separate terminal execution.

## Result

The frozen PR #1 head does not materially overclaim the Panthera/Pandera evidence. The packet consistently separates textual occurrence, material name attestation, later rabbinic tradition, modern scholarship, and the unsupported biological-paternity proposition.

The following hostile attacks were run:

1. Celsus / Origen conflation — survived. Claims about I.28, I.32 and I.69 are phrased as what Origen reports or rebuts. I.32 and I.69 are explicitly not counted as independent witnesses.
2. Lost-source promotion — survived with a schema caveat. `SRC-CELSUS-TRUE-DOCTRINE` is marked lost and indirect-through-Origen, but `source_roles: [PRIMARY_TEXT]` could still be machine-misread as directly extant unless access/preservation status is enforced by downstream consumers.
3. Abdes Pantera identity overreach — survived. `CLM-PANTERA-NAME-ATTESTED` is limited to the inscription; `CLM-ABDES-PANTERA-WAS-YESHUA-FATHER` remains unsupported/contested. The cited military-inscription database itself cautions against confident biographical linkage and dates the monument context broadly within the first century.
4. Shabbat 104b -> Jesus identity smuggling — survived. The checked passage contains ben Stada / ben Pandeira / Miriam but does not explicitly name Jesus; the stronger identity claim remains unresolved.
5. Confirmation bias — substantially controlled. The packet explicitly lists simpler polemical, literary, transmission and wordplay alternatives and refuses to promote the paternity hypothesis.

## Material limitations

### M-H1 — asymmetric scholarship on Celsus's Jewish source

`CLM-CELSUS-JEW-PRESERVES-AUTHENTIC-JEWISH-SOURCE` is correctly marked contested and unresolved, but both registered scholarly nodes are supportive. The alternatives are prose-only and do not yet have opposing scholarly source nodes. Before any synthesis uses this claim, add at least one serious scholarly challenge or narrowing treatment.

### M-H2 — source-role ambiguity for a lost original

`SRC-CELSUS-TRUE-DOCTRINE` being typed `PRIMARY_TEXT` is ontologically defensible as the source being reconstructed, but dangerous for machine retrieval because there is no direct witness. Add an explicit field such as `direct_access: false`, `witness_status: indirect_only`, or a distinct source/access layer so downstream retrieval cannot treat it as directly read primary evidence.

### M-H3 — `NONE_ESTABLISHED` confidence semantics

`TR-ABDES-PANTERA-TO-CELSUS` uses `relation: NONE_ESTABLISHED` with `confidence: high`. That can be misread as high confidence that no historical relationship existed, when the intended proposition is only high confidence that no link is currently established. Define confidence as confidence in the registry relation-status claim, or rename this state to make the epistemic target explicit.

## Hostile conclusion

No evidence in this exact head justifies the proposition that Panthera/Pandera was Jesus/Yeshua's biological father, that Tiberius Julius Abdes Pantera was that person, or that later rabbinic Pandera traditions prove the Celsus story historically. PR #1 survives those attacks.

Result remains `PASS_WITH_LIMITATIONS` because the limitations above affect machine interpretation and future synthesis but do not falsify the bounded claims currently asserted.