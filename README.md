# V-E-R-A

**The virtual environment for reciprocal agency.**

This public repository is the source collection and integration workspace for Vera's constituent systems. Its original repositories remain authoritative.

**The source collection is populated.** All **44 named component branches are populated**: **38 exact Git-tree mirrors**, **5 security-sanitized GitHub source snapshots**, and **1 source-definition snapshot of the live Vera Supabase project**. No named branch remains at the original placeholder commit. Exact versus non-exact status is recorded in the source registry and each branch's provenance. `main` contains the registry, workspace assembly tool, and regression tests needed to use them together.

## Assemble a working source workspace

Git and Python 3.10+ are required. No global installation or model download is required.

```sh
git clone https://github.com/thebrazenbeard/v-e-r-a.git
cd v-e-r-a
python scripts/materialize.py list
mkdir components
python scripts/materialize.py materialize --only vera-mono --only portal --only intranel
python scripts/materialize.py verify --only vera-mono --only portal --only intranel
```

To check out **all 44 populated branches**, use `python scripts/materialize.py materialize` after creating the `components` directory. Each component is materialized as a detached Git worktree at the **pinned branch commit recorded in [components.json](components.json)**, within `components/<name>/`. A pinned commit is not automatically an exact copy of its upstream GitHub tree. The tool verifies the remote branch still matches the pinned commit, refuses overwrites, and never silently substitutes a newer source revision.

To see whether the registry still agrees with the remote branches without changing local files:

```sh
python scripts/materialize.py check-origin
```

The `verify` command checks pinned commits and clean working-tree state **after** materialization. The materialized `components/` folder is ignored on `main`, so one working clone can contain multiple independently versioned systems without mixing their trees.

Run the included **offline Git integration tests**:

```sh
python -m unittest discover -s tests -v
```

The included tests use temporary Git remotes and worktrees for checkout, pin validation, drift detection and refusal to overwrite state. New snapshot classifications on `main` have not yet received a fresh local regression-test PASS in this turn because remote execution was blocked; treat them as source-only until independently run. These tests do not qualify Vera's full autonomous runtime.

## Branch model

A branch named `portal` contains a snapshot of [thebrazenbeard/portal](https://github.com/thebrazenbeard/portal) and `vera-mono` a snapshot of [thebrazenbeard/vera-mono](https://github.com/thebrazenbeard/vera-mono). The same arrangement applies to the other populated components, including `intranel`, `pre-active`, `volition`, `lgcm`, and the remaining names in the registry.

**Security-sanitized GitHub branches:** `mediaphile`, `orgasm`, `redworm`, `sexuality`, and `vera-works` contain source snapshots derived from their pinned canonical GitHub `main` commits, but are **not byte-identical source trees**. Each branch contains `MIRROR_SOURCE_PROVENANCE.json` enumerating omitted files. Microsoft Defender quarantined `.vscode/tasks.json` as `Trojan:Script/MalTask.A` in all five local checkouts. A repeatedly flagged font was excluded; MediaPhile's local media-library SQLite database and Vera Works' wallet evidence and active-quarantine third-party patches were also excluded. The original private repositories were not changed.

**Vera Supabase branch:** [`vera-supabase`](../../tree/vera-supabase) is sourced from the actual Supabase project **Vera** (`klmbpaigzeguvnpccqzz`), not a missing GitHub repository. It contains generated types, six application-schema definitions, SQL routines, grants, row-level security policies, trigger definitions, 99 migration names/versions, and the live Edge Function source. No live table records, credentials, authentication records or vault data were copied. It is **not a restorable production database dump**; see its branch README.

A mirror is a **point-in-time copy**, not an automatic synchronization promise. The original upstream repository and its independent PR/review/CI process own source decisions. Do not edit the mirror branch as if it were authoritative.

## Runtime integration

Source collection is not runtime integration. Vera needs one durable task owner and governed component interfaces, not another standalone task scheduler. Current executable integration development is in [Draft PR #1](https://github.com/thebrazenbeard/v-e-r-a/pull/1), paired with [Vera Mono PR #76](https://github.com/thebrazenbeard/vera-mono/pull/76) and [PORTAL PR #51](https://github.com/thebrazenbeard/portal/pull/51). These drafts propose an advisory task-to-route boundary; **they are not merged, installed, or qualified as a resident system**.

The next behavioral milestone is a single persistent Vera task that obtains a fresh, authorized PORTAL route, runs through the **existing** supervised execution mechanism, reconciles a durable receipt, and survives interruption. A selected route is not itself permission, completion, or model admission.

The public repository exposes reviewed source snapshots and metadata while excluding quarantined code, known sensitive local records, and provider credentials. Distinguish snapshot availability from installed integration, authority, or runtime behavior.
