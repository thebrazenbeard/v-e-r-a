# V-E-R-A

**The virtual environment for reciprocal agency.**

This public repository is the source collection and integration workspace for Vera's constituent systems. Its original repositories remain authoritative.

**The source collection is populated.** The 44 named component branches currently comprise **38 complete, Git-tree-verified repository snapshots** and **6 intentionally held placeholders**. Those branches contain actual source trees, not links or empty stubs. `main` contains the registry, workspace assembly tool, and regression tests needed to use them together.

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

To check out **all 38 public snapshots**, use `python scripts/materialize.py materialize` after creating the `components` directory. Each component is materialized as a detached Git worktree at the **exact commit recorded in [components.json](components.json)**, within `components/<name>/`. The tool verifies the remote branch still matches the pinned commit, refuses overwrites, and never silently substitutes a newer source revision.

To see whether the registry still agrees with the remote branches without changing local files:

```sh
python scripts/materialize.py check-origin
```

The `verify` command checks pinned commits and clean working-tree state **after** materialization. The materialized `components/` folder is ignored on `main`, so one working clone can contain multiple independently versioned systems without mixing their trees.

Run the included **offline Git integration tests**:

```sh
python -m unittest discover -s tests -v
```

These tests use temporary Git remotes and real worktrees. They exercise checkout, exact pin validation, drift detection, held branch rejection, and refusal to overwrite existing state. They do not qualify Vera's full autonomous runtime.

## Branch model

A branch named `portal` contains a snapshot of [thebrazenbeard/portal](https://github.com/thebrazenbeard/portal) and `vera-mono` a snapshot of [thebrazenbeard/vera-mono](https://github.com/thebrazenbeard/vera-mono). The same arrangement applies to the other populated components, including `intranel`, `pre-active`, `volition`, `lgcm`, and the remaining names in the registry.

**Held branches:** `mediaphile`, `orgasm`, `redworm`, `sexuality`, and `vera-works` have private upstream source that has not been approved for copying into this public repository. `vera-supabase` lacks a verified corresponding source. The registry makes these holds visible without disclosing private contents. Public status of `v-e-r-a` is preserved.

A mirror is a **point-in-time copy**, not an automatic synchronization promise. The original upstream repository and its independent PR/review/CI process own source decisions. Do not edit the mirror branch as if it were authoritative.

## Runtime integration

Source collection is not runtime integration. Vera needs one durable task owner and governed component interfaces, not another standalone task scheduler. Current executable integration development is in [Draft PR #1](https://github.com/thebrazenbeard/v-e-r-a/pull/1), paired with [Vera Mono PR #76](https://github.com/thebrazenbeard/vera-mono/pull/76) and [PORTAL PR #51](https://github.com/thebrazenbeard/portal/pull/51). These drafts propose an advisory task-to-route boundary; **they are not merged, installed, or qualified as a resident system**.

The next behavioral milestone is a single persistent Vera task that obtains a fresh, authorized PORTAL route, runs through the **existing** supervised execution mechanism, reconciles a durable receipt, and survives interruption. A selected route is not itself permission, completion, or model admission.

The public repository may expose architecture, source, and reproducible tests without exposing secrets, credentials, personal data, or private project contents.
