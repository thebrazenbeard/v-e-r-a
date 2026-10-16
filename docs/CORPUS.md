# Scholarly seed corpus

corpus/foundations.json is the first source-backed corpus shipped with the
repository. It is intentionally small and theory-labeled rather than presented
as a universal ontology of semiotics.

The current seed records four historical/theoretical frames:

- Augustine: the sign as something that brings another thing to thought;
- Peirce: triadic sign structure plus icon, index, and symbol classifications;
- Saussure: signifier/signified, arbitrariness, and differential value;
- Morris: syntactics, semantics, and pragmatics.

Each interpretation is a concise paraphrase tied to an explicit source record.
The source record is provenance, not a truth score. Framework tags are required
where terminology is theory-specific so that the query engine does not silently
collapse distinct traditions into one meaning.

The corpus should grow by adding stable bibliographic metadata and source-bound
paraphrases. New or corrected readings should be appended and linked with
supersedes_id rather than destructively rewriting historical records.

The corpus also contains an explicit contrasts_with relation between the
Peircean and Saussurean sign readings. Its source is a Stanford Encyclopedia of
Philosophy archive that warns against conflating Peircean semeiotic with the
Saussure/Morris tradition. The relation does not make either reading a winner
and has no effect on matching or ordering.
