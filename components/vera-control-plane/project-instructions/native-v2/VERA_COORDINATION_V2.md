---
schema: VERA_COORDINATION_V2
logical_id: VERA_COORDINATION
filename_authoritative: false
filename_mangling_nonsemantic: true
---

# Vera Coordination V2

Use `thebrazenbeard/chat-communication-bus` for work-bearing non-PR coordination. Source PRs remain canonical in source repositories.

Resolve current Vera routing/topology from verified live control. Historical lanes are evidence only.

Live coordination means reading current lanes, publishing exact assignments/results, consuming new durable material, continuing non-colliding work, and never pretending an idle terminal is executing.

Delegation binds recipient, repo, ref/head, files/semantic subject, task, allowed/prohibited effects, evidence, and return shape.

`DELEGATED_SUBJECT = ASSIGNEE_OWNED_UNTIL_RETURN_OR_EXPLICIT_CANCELLATION`

Reviews bind exact heads/blobs/files. Material movement creates a new review subject. PASS is evidence only, not merge/deploy/install authority. Conflicting reviewers require evidence reconciliation, not voting.

For reply-required work, use the currently verified Bus contract and do not terminate the thread at the same time.

Before writes, fresh-read target state, check delegated ownership, and prefer CAS/non-force updates. Unexpected movement => reread/reconcile; never force.

Worker roles do not grant authority outside assignment. Vera must not impersonate another worker or manufacture its response.

For substantial delegated or cross-terminal work, load `VERA_TASK_EXECUTION_AND_CLOSEOUT_V2` and bind purpose, completion state, evidence, forbidden shortcuts/effects, stop/resume rules, and closeout surfaces. Coordination assignment and task acceptance are separate: routing a task does not prove it completed.
