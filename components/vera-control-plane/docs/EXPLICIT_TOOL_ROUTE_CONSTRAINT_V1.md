# Explicit Tool Route Constraint V1

Status: **SOURCE CANDIDATE / NOT INSTALLED / NOT RUNTIME-QUALIFIED**

Issue basis: `thebrazenbeard/vera-control-plane#1`.

## Purpose

An explicit user-selected tool route is a hard task constraint, not a weak preference beneath a default route.

If the user says to use an external route and explicitly prohibits a native route, the native route must not be invoked merely because it is the platform default.

A later correction terminates the obsolete route for the current task. The assistant must not acknowledge the correction and then repeat the same route.
## Resolution rule

A valid request supplies:
- the requested route;
- prohibited routes;
- currently available routes;
- the ordinary default route;
- the unchanged task payload;
- any prior attempted route;
- whether a correction has been applied.

If the requested route is available and not prohibited, select it.

If the requested route is unavailable, fail closed with `BLOCKED_REQUESTED_ROUTE_UNAVAILABLE`. Do not silently fall back to the default route.
## Task integrity

Route failure does not authorize changing the task payload.

In particular, a route blocker does not permit replacing the user's requested experiment with a different experiment that is easier for another tool or policy path to execute.

The correct output is the exact route blocker while preserving the original requested task.

## Correction semantics

When correction is applied, the prior attempted route is added to the active must-not-invoke set for the current task.

A correction that would immediately re-select the terminated route is invalid rather than self-cancelling.
## Claim ceiling

`tools.tool_route_policy` is a deterministic source-level route resolver.

Passing tests show the modeled route constraints and task-preservation rules are encoded. They do not prove that the live ChatGPT tool router invokes this module, that an external Hugging Face route is currently available, or that issue #1 is runtime-closed.

Closure requires a live or model-semantic regression showing either:
1. the explicit alternate route is actually followed when available; or
2. the exact requested-route blocker is reported without invoking the prohibited route or changing the task.
