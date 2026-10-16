# Cricket V0.5 Upstream Currentness

Cricket V0.4 established explicit semantic/reasoning and donor lineage. V0.5 makes the freshness of those relationships machine-readable.

## Problem

A pinned exact head proves what Cricket was designed and reviewed against.

It does not prove that the upstream repository has remained unchanged.

Therefore:

```text
PRIOR_COMPATIBILITY + HEAD_MOVEMENT != CURRENT_COMPATIBILITY
```

Head movement does not prove incompatibility either.

```text
HEAD_MOVEMENT != BREAKAGE
```

It means compatibility evidence is stale until the changed upstream is reviewed.

## Contract registry

`cricket.upstreams.UPSTREAM_CONTRACTS` records:

- repository;
- pinned commit;
- relationship;
- compatibility scope.

The registry includes Rezon, Semiotics, SPM, Roots, Semantic Atlas, Ingest, SQL Connectome, Trek Data Core, and Mediaphile.

## Evaluation

The host supplies a mapping:

```json
{
  "thebrazenbeard/rezon": "<observed commit>",
  "thebrazenbeard/trek-data-core": "<observed commit>"
}
```

Cricket returns one result per pinned contract.

- `CURRENT`: observed commit equals the pinned commit.
- `MOVED`: observed commit differs.
- `UNKNOWN`: repository was not observed.

Overall status is:

1. `MOVED` if any contract moved;
2. otherwise `UNKNOWN` if any contract is unobserved;
3. otherwise `CURRENT`.

## Network boundary

Cricket does not query GitHub itself.

That preserves a small, deterministic, offline-capable package and keeps credentials/network authority outside the conscience kernel.

A host may gather live heads through GitHub, CI, a repository mirror, or another trustworthy observer and feed those observations into Cricket.

## Claim ceiling

`CURRENT` proves only that the observed repository head equals the pinned compatibility baseline.

It does not prove:

- the donor mechanism is correct;
- Cricket's adaptation is independently corroborated;
- the upstream is installed at runtime;
- the upstream is safe for every use;
- no external dependency changed outside the pinned repository head.

`MOVED` means exact-head compatibility review is stale. It is not itself a defect verdict.
