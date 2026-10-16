# Interpretation relations

Relations make disagreements and dependencies explicit without changing the
deterministic matching algorithm.

Each relation has:

- id: stable relation identifier;
- left_id and right_id: existing interpretation IDs;
- kind: one of contrasts_with, contradicts, supports, or refines;
- source_id: the registered source supporting the relation claim.

Both endpoints must exist and be distinct. The relation source must exist.

## Semantics

contrasts_with records a source-backed difference between two readings without
asserting that they cannot both be useful or true.

contradicts is reserved for a source-backed claim that two readings are
incompatible. Merely belonging to different schools or frameworks is not enough.

supports is directional: left_id is the interpretation described by the source
as supporting right_id. It does not turn either endpoint into verified truth.

refines is directional: left_id is the interpretation described by the source
as refining or elaborating right_id.

contrasts_with and contradicts are stored with left/right endpoints for stable
serialization, but the engine does not infer an inverse edge or otherwise treat
the stored orientation as an additional claim.

Relations are metadata. They do not alter context matching, specificity,
ordering, revision status, or source authority. The engine performs no symmetry,
transitivity, contradiction propagation, or relation inference.

Queries expose relations attached to returned interpretations. A relation may
refer to an interpretation that did not itself match the query; that preserves
the registered relation without expanding the result set.
