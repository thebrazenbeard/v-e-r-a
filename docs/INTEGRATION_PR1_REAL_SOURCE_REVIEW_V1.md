# PR #1 independent cross-repository CLI qualification

Review role: **Integration**, under PORTAL build-lead ownership. This branch adds
regression tests to `v-e-r-a` PR #1, not a competing execution system.

## Exact source subjects

- `v-e-r-a` Draft PR #1: `7a9ebf5724dff962f5ffbd994678370c00592835`.
- `vera-mono` Draft PR #76: `dec5c029e51c4fd436435cbda7e02e501822ee85`.
- `portal` Draft PR #51: `36fa04da4e5eb383fecf463c72a43b94ca47d7e5`.

The CLI's own `source_check` rejects different checked-out heads. Test
execution is fail-closed on original source import problems, not silently
replaced with mock implementations. Set `VERA_MONO_SOURCE_ROOT` and
`PORTAL_SOURCE_ROOT` to the two distinct exact checkouts:

```sh
export VERA_MONO_SOURCE_ROOT=/path/to/exact/vera-mono
export PORTAL_SOURCE_ROOT=/path/to/exact/portal
python -m unittest discover -s tests -p test_real_source_route_integration.py -v
```

Unset both environment variables only when doing the normal project suite:
these **four real-source tests SKIP** with a visible skip reason if the
separate sources are unavailable. Skipping is not qualification.

## Observed behavior on Lappy, 2026-10-16

1. Actual Vera SQLite task `TASK_OPENED` then no-advertisement `HELD`,
   saved receipt and independent-process `ADVISORY_REVALIDATED`.
2. The actual PORTAL resolver returned `ROUTE_PROPOSED` for an explicitly
   caller-advertised read-only route, then Vera reopened/validated the saved
   advisory in a separate process. Caller `current=true` is *not* host
   currentness or authenticated device registration.
3. Duplicate task opening and exclusive receipt overwrite were rejected.
4. Mutating the saved route ID without updating assessment hash was rejected.
   After the existing Vera `bind_dependency` API advanced the task journal,
   previously valid held **and** proposed receipts were rejected as stale.
5. Concurrent independent processes racing to open the same task produced
   **one** persisted `TASK_OPENED` event. This does not qualify durable
   concurrent execution or exact-once protected side effects.

The first bounded manual qualification had local evidence file
`D:\VERA\integration-fourlane-pr1-20261016\state\qualification.json`
with SHA256
`bacc6186f5aae9cd9206eca3e4d6c704efa3983bf4a5997b3a621920787ab309`.
Its scope is source+local SQLite behavior; do not rely on a local path as
proof that another operator has fetched its contents. The new source-controlled
tests reproduce its central observable cases in fresh temporary directories.

## Constructive adversarial holds

- Caller-provided `current:true` and a recomputable SHA256 do not prove
  Executor gateway registration, route generation, device identity,
  authorization or a healthy bounded benign command. VN1 independently
  observed live process/TCP presence with missing registered device.
- An advisory verification followed by a *separate* execution step would
  have an authorization/currentness/time-of-check-to-time-of-use gap. Exact
  task journal + route generation + execution receipt must be bound and
  reconciled by the existing owners before protected work.
- `source_check` only excludes dirty tracked files and pin drift;
  untracked import shadowing and ambient Python import paths remain
  unqualified. Isolate executable imports/artifacts for production.
- The public `v-e-r-a/main` advanced after PR #1 was cut. PORTAL should
  re-evaluate base integration and conflicting branches before any merge.
- No live installed coordinator, active device route, model admission,
  direct automatic four-chat messaging, or independent semantic review
  is established by these regression tests.

Disposition: **PASS** exact head for narrow local real-source route/receipt
and task-journal recovery; **HOLD** on currentness trust, execution,
deployment, autonomous ongoing runtime and protected effects.

PORTAL owns PR #1 and any source integration. This subordinate review PR
is offered for cherry-pick/acceptance; it must not be merged independently
without lead review.

## Training cross-lane objection: clean tracked HEAD can still execute unpinned code

Training independently reproduced that `source_check` ignored untracked
files while the CLI subsequently inserted `packages/*/src` into
`sys.path`. An untracked `vera_core` package from a lexically later
directory can shadow the pinned source, even when HEAD and tracked status
are clean. An ignored package can do the same.

The Integration review branch now adds
`tests/test_source_binding_integrity.py`: a clean control, an untracked
shadow, and an ignored shadow. Both hostile cases FAILED against the
original PR #1 `source_check`, then PASSED after the candidate patch.

The narrow patch rejects any untracked or Git-ignored content under the
actual import scopes (`Vera Mono: packages/`; `PORTAL: portal/`), in
addition to its existing exact HEAD and tracked-clean checks. This
provides deterministic fail-closed protection for those roots without
assuming that a git clean-tracked tree is a fully sterile import path.
It does not authenticate external dependencies, Python site-packages,
symlinks/junctions, native extensions or arbitrary process import hooks;
a fully isolated installed artifact and module-origin verification
remain future production admission gates.

PORTAL leads acceptance, review and adoption of this candidate repair;
the independent Integration branch changes no PORTAL-owned PR #1 head.

## Integration P0 follow-up: preloaded Python import origins

At exact predecessor PR #3 head e4ccc801d994c1a98aac6081e17d4a30dfe503fe,
the existing adversarial unit tests for preloaded and forged module origins
were uncommitted and the implementation did not define their expected guards.
This successor adds:

- _guard_preloaded_imports() BEFORE adding either source root to sys.path,
  rejecting already-imported vera_core, portfolio_runtime or portal modules
  even if the module claims a pinned __file__. A preloaded module's Python
  code could already have run before origin verification.
- _verify_import_closure() after source imports: every loaded module in
  those namespaces must resolve within the exact checked-out source
  package tree and have a matching import-spec origin.
- _verify_module_origin() for the four entry modules imported by
  the Vera-P.O.R.T.A.L. CLI.
- Tests for foreign preloaded modules, contradictory __file__ origins and
  FOUR actual separate-process shadow injections with exact Vera Mono and
  PORTAL sources. Every injection must fail before receiving components.

This closes a narrow current-source module-shadow class. It is NOT a
hermetic Python environment: native wheels, ambient sitecustomize import
effects, mutable trusted dependencies, symlink race or malicious meta-path
loader tricks remain outside this source qualification. A source digest
alone never authenticates a live physical Executor host or capability route.

No service is deployed or task authority granted. PORTAL remains lead for
integration and decides how to consume PR #3.
