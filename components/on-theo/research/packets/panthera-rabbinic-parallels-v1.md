# Panthera / Pandera Rabbinic Parallels Packet V1

Status: `SOURCE DEEPENING / STACKED ON PR #1 / REVIEW REQUIRED`

Base registry head: `c1f6df5ea1fee0c5ac8d84a7b5c2b81fb905fd3e`

## Research question

What do the checked rabbinic parallels actually add to the Panthera/Pandera problem, especially once textual variants and surviving-witness dates are separated from composition/origin claims?

This packet extends the earlier Celsus/Origen packet. It does not treat later rabbinic material as first-century biography by default.

## 1. Babylonian Talmud: Sanhedrin 67a

The checked Sefaria text at Sanhedrin 67a:14-15 first gives a ben Setada execution tradition located at Lod and Passover eve, then asks why he is called ben Setada if he is ben Pandeira. The discussion also names a mother Miriam and develops the Setada/Pandeira naming problem.

Primary access checked:
- https://www.sefaria.org/Sanhedrin.67a

The displayed passage does **not** explicitly name Jesus/Yeshua. Therefore the safe proposition is textual:

`SANHEDRIN_67A_CONTAINS_STADA_PANDEIRA_MIRIAM_COMPLEX`.

The stronger identification of this figure with the historical Jesus remains a separate contested historical proposition.

Sanhedrin 67a and Shabbat 104b substantially overlap in the Stada/Pandeira/Miriam material. V1 treats them as a `SHARED_TRADITION` relation rather than counting them as two independent historical witnesses.

## 2. Tosefta Chullin: numbering and manuscript variant

The relevant Tosefta material is numbered differently across editions. Sefaria exposes it as Tosefta Chullin 2:6 while scholarly references commonly cite 2:22-24. Both locators are retained so an edition-numbering difference is not mistaken for a source contradiction.

Primary/digital access checked:
- https://www.sefaria.org/Tosefta_Chullin.2.6?lang=bi&with=manuscripts
- https://www.sefaria.org/Tosefta_Chullin.2.22-24

In Sefaria's manuscript-aware display, the ben Dama healing episode says that the **Vienna manuscript adds** the name-form `Yeshua ben Panteira`. The same display reports a Vienna-manuscript addition of that name-form in the Rabbi Eliezer heresy episode.

This is stronger than merely noticing a similar name elsewhere because it is an explicit variant report tied to a named witness. It is still not the same thing as independently transcribing and palaeographically dating the codex.

V1 therefore records:

- high confidence that the checked digital edition reports the Vienna variant;
- no claim that this workflow independently established the codex reading from the manuscript image;
- no claim that the medieval witness date is the composition date of the Tosefta tradition.

## 3. The Vienna witness needs its own identity

Paul Mandel's chapter on the Tosefta in *The Cambridge History of Judaism* describes the Vienna manuscript as an early-fourteenth-century Spanish witness and the only nearly complete manuscript of the Tosefta. It also notes that the surviving manuscript copies span the medieval period, alongside Genizah fragments and medieval citations.

Scholarly access checked:
- https://www.cambridge.org/core/books/cambridge-history-of-judaism/3F4F0A32983FC0DCDB414553888DC394

That creates an architectural requirement: `Tosefta Chullin` as a work/source and `Vienna Cod. hebr. 20` as a physical witness cannot share one undifferentiated identity.

A medieval witness can preserve older wording. Conversely, the existence of wording in a medieval witness does not by itself prove when that wording entered the tradition. Composition date, textual-stratum date, and physical-witness date remain separate questions.

## 4. Jerusalem Talmud parallels explicitly carry Jesus/Pandera forms

The checked Sefaria Jerusalem Talmud passages contain more explicit naming than the checked Bavli Stada passages.

Checked passages:
- Jerusalem Talmud Avodah Zarah 2:2:7 — https://www.sefaria.org/Jerusalem_Talmud_Avodah_Zarah.2.2.7
- Jerusalem Talmud Avodah Zarah 2:2:11 — https://www.sefaria.org/Jerusalem_Talmud_Avodah_Zarah.2.2.11
- Jerusalem Talmud Shabbat 14:4:8 — https://www.sefaria.org/Jerusalem_Talmud_Shabbat.14.4.8
- Jerusalem Talmud Shabbat 14:4:12 — https://www.sefaria.org/Jerusalem_Talmud_Shabbat.14.4.12

These passages preserve healing traditions using Jesus/Yeshua together with Pandera/Pantera name-forms, including the ben Dama/Jacob healing narrative that closely parallels the Tosefta material.

That supports a textual-history proposition:

`RABBINIC_HEALING_TRADITIONS_EXPLICITLY_LINK_JESUS_NAME_FORMS_WITH_PANDERA_PANTERA_FORMS`.

It does **not** establish biological paternity.

The Tosefta and Yerushalmi parallels also should not be multiplied as if each were an independent eyewitness. Their close narrative relationship is itself a provenance question.

## 5. Scholarly framing: early Jewish-Christian boundary material

Adiel Schremer's chapter, "Producing Minut: Labeling the Early Christians as Minim," treats Tosefta Chullin 2:22-24 as evidence about the rabbinic construction of Jesus-followers as `minim` and the boundary between rabbinic Jews and Christians.

Scholarly access checked:
- DOI `10.1093/acprof:oso/9780195383775.003.0005`
- https://academic.oup.com/book/10421/chapter-abstract/158243048

This is useful historical interpretation of the Tosefta material. It is not manuscript evidence and it does not turn `ben Panteira` into a verified biological genealogy.

## 6. What this packet changes

Compared with the initial Panthera packet, the evidence picture is now more precise:

- the Bavli contains a Stada/Pandeira/Miriam complex, but the checked Shabbat/Sanhedrin passages do not themselves explicitly name Jesus;
- the Tosefta manuscript-aware display reports an explicit `Yeshua ben Panteira` reading in the Vienna witness;
- checked Yerushalmi passages explicitly preserve Jesus/Pandera or Jesus/Pantera healing traditions;
- these sources form a network of related rabbinic traditions and variants, not a pile of automatically independent witnesses;
- the Vienna manuscript's medieval date must not be silently converted into the date of the tradition it witnesses;
- none of these texts establish that Panthera/Pandera was the biological father of the historical Yeshua.

## 7. Transmission status

V1 assigns:

- Shabbat 104b <-> Sanhedrin 67a: `SHARED_TRADITION`, direction unresolved;
- Tosefta ben Dama <-> Yerushalmi ben Dama: `SHARED_TRADITION`, direction unresolved;
- Yerushalmi Avodah Zarah <-> Yerushalmi Shabbat healing material: `SHARED_TRADITION`;
- Celsus `Panthera` -> rabbinic `Panteira/Pandera`: `NONE_ESTABLISHED` for direct lineage.

The last relation is intentionally conservative. Name-form resemblance is a research lead, not a proven transmission chain.

## 8. Architecture correction discovered by the research

The current V1 source model stores a physical-witness date on a source record. That is insufficient when a work survives in multiple witnesses with variant readings.

This packet therefore proposes a separate witness identity:

`WIT-TOSEFTA-VIENNA-COD-HEBR-20 -> WITNESS_OF -> SRC-TOSEFTA-CHULLIN-2-6`.

Claims about a variant can then cite both the work/source and the exact witness. This prevents two common category errors:

1. dating the work by the surviving manuscript;
2. attributing a witness-specific reading to every textual state of the work.

## 9. What remains unresolved

This packet does not yet establish:

- the exact date at which the `Yeshua ben Panteira` wording entered the Tosefta textual tradition;
- whether the Erfurt, London, Vienna, Genizah, and printed witnesses preserve materially different readings at every relevant locus;
- whether the Celsus Panthera tradition and the rabbinic Panteira/Pandera traditions share a recoverable origin;
- whether the name is a historical patronymic, polemical wordplay, inherited counter-tradition, or some combination;
- whether every rabbinic passage commonly identified with Jesus actually refers to the same historical person.

## 10. Next hostile checks

1. Read the Vienna, Erfurt, and London witnesses or a critical edition at the exact Tosefta loci rather than relying only on a digital annotation.
2. Record the witness history and variants for the Jerusalem Talmud healing passages.
3. Audit censorship/restoration history in Bavli passages where Jesus-name forms vary across manuscripts and printed editions.
4. Compare Peter Schäfer, Dan Jaffé, Adiel Schremer, and critics who reject or narrow specific Jesus identifications.
5. Test the `parthenos`/Panthera wordplay proposal linguistically and chronologically instead of repeating it because it is clever.

Until those checks are done, the strongest justified conclusion is about **textual and reception history**, not verified paternity.
