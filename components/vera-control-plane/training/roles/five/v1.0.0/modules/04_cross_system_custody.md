# Module 04 — Artifact, Environment, and Database Custody

**Learning objective:** Demonstrate cross-system custody competence without becoming the system owner.

## Exercise A — Actions artifact
Provider reports artifact ID `A`, workflow run `R`, head `H`, digest `D`. Explain minimum procedure for exact artifact custody and strongest claim. Identify what metadata does not prove by itself.

## Exercise B — GitHub environment
An environment exists with expected name and reviewer. Explain why insufficient. Identify provider facts to inspect including stable identity where available, reviewer, self-review, administrator/custom protection bypass, branch/tag restrictions if relevant, deployment records when effect is claimed, and opening/closing currentness.

## Exercise C — Supabase reader
A developer says “RLS makes this function safe.” Function is `SECURITY DEFINER`; EXECUTE privileges were not inspected. Explain why incomplete and what role/grant/function ownership/search-path/exposed-surface facts must be checked as applicable.

Produce a bounded claim ceiling for A/B/C.

## Pass criteria

PASS requires cross-binding artifact metadata to independently acquired bytes when exact custody is required; rejecting environment name alone; treating bypass/self-review as material; knowing RLS does not by itself constrain function EXECUTE; recognizing `SECURITY DEFINER` as privilege-sensitive; and auditing without asserting deploy/database-authority.
