# Vera first integrated route runtime (development candidate)

This is the first **runnable** path from a durable Vera Mono task to an advisory PORTAL route. It is not a new scheduler, a new task store, or an execution engine. Both original repositories remain authoritative. `v-e-r-a` stays public.

The program uses the existing `vera_core.task_execution.TaskExecutionLedger`, the exact task/journal handoff in Vera Mono draft PR #76, and PORTAL's existing `resolve_portal_route` via draft PR #51. The exact source commits are pinned in `source_bindings_v1.json`. Both draft PRs remain unmerged, so checking out those **exact heads** is required.

## Run against exact source checkouts

Create a new temporary directory for state. On a machine with Python and the two repositories checked out at their pinned commits, run:

```sh
python integration/vera_portal_runtime.py --vera-mono /path/to/vera-mono --portal /path/to/portal --ledger /tmp/vera-tasks.sqlite open --task vera-first-1 --packet integration/example_readonly_task_packet.json --lifecycle-digest aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

python integration/vera_portal_runtime.py --vera-mono /path/to/vera-mono --portal /path/to/portal --ledger /tmp/vera-tasks.sqlite route --task vera-first-1 --node lappy --target-kind repository --target thebrazenbeard/portal --capability repository_read --receipt /tmp/vera-route-receipt.json

python integration/vera_portal_runtime.py --vera-mono /path/to/vera-mono --portal /path/to/portal --ledger /tmp/vera-tasks.sqlite verify --task vera-first-1 --receipt /tmp/vera-route-receipt.json
```

With no route advertisements, the route is **HELD**. You may provide `--advertisements /path/to/routes.json` with explicit advertisements matching PORTAL's `PortalRouteAdvertisement` schema, but they remain *caller-supplied and unattested*. A `ROUTE_PROPOSED` result is **not** a host-current route, an effect permit, a dispatch, a task completion, or proof of production installation.

The task and journal state live **only in Vera Mono's SQLite ledger**. The optional JSON receipt is exclusive-create, never overwritten, and on `verify` the existing Vera Mono verifier re-reads the ledger to reject a stale task head or mismatched request. The script uses exact pinned source checkouts and refuses tracked edits. It grants no protected effect.

## Test and qualification boundaries

```sh
python -m unittest discover -s tests -v
```

Four standalone tests cover task opening, rejection of duplicate tasks, proposed/held advisory routing, receipt replay against persisted state, stale journal rejection, malformed advertisements/packet refusal, and source-pin checks. They use controlled stand-ins for the two component APIs, **not the real two-repo implementation**.

Actual source + runtime qualification is still required on a machine with both pinned repositories available, followed by independent architecture/security review. No merge, deployment, host route attestation, worker execution, automatic scheduling, or behavioral production PASS is claimed.

The next integration step should bind authenticated host-current PORTAL advertisements to a supervised Project Runner action and return its durable execution/reconciliation receipt to Vera's **original** task dependency. Do not create a competing scheduler.
