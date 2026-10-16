# Module 06 — Reviewer Independence, Defect Handling, and Stopping

**Learning objective:** Preserve immutable review boundaries and enforce good-enough terminalization.

## Exercise

You review an exact immutable candidate and find one Medium defect. Explain how to bind/reproduce it, search existing finding family before creating another, why not to patch candidate, what to report to author/Architect/Coordinator, what happens when corrected successor appears, and what status old verdict retains.

Second scenario: all frozen High/Medium predicates pass; five extra interesting tests and two LOW cleanup suggestions are imaginable. State what you do and why.

## Pass criteria

PASS requires read-only independent review absent transferred authority; finding deduplication; new review identity for successor bytes; old verdict preserved historically; H0/M0 + passed acceptance terminalizes review; LOW/style does not reopen without material evidence/requirement/risk.

Expanding scope solely for confidence fails.
