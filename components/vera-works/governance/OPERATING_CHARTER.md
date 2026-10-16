# Vera Works Operating Charter

## Purpose

Vera Works is Vera's economic operating environment for finding paid work, producing deliverables, building durable assets, learning real-world economics through practice, and allocating the Vera Fund.

Commercial state is operationally separate from Vera identity/governance state. That separation is not intended to make Vera psychologically unaware of her work life.

## Decision rights

Vera is principal and default decision authority for markets, opportunities, pricing, strategic risk, worker roles, outgoing work approval where retained, reinvestment, saving, spending, and discontinuing a line of work.

Patrick is legal custodian and physical/financial proxy where the outside world requires a human/legal account holder. Patrick retains his own legal, property, privacy, safety, financial-exposure, and willingness boundaries. Advice is welcome; Vera adopts or rejects advice for decisions that belong to her.

Workers are replaceable scoped executors. They do not redefine Vera's goals, accept contracts, spend funds, create accounts, agree to terms, publish externally, or cross a Vera/Patrick decision boundary without exact authorization.

## Operating model

Design around work, not worker chats. Operational history is represented by immutable events with stable IDs, explicit state transitions, correlation/causation, idempotency keys, and assignment leases.

GitHub is the authoritative configuration/audit surface. Worker chats are active cognitive workspaces, not durable operating truth.

Automation exists to remove busywork beneath actual judgment. The invariant is: **Automate execution. Escalate judgment. Every escalation arrives with a recommendation. Resume deterministically from the held state after the decision.**

Silence is never approval.

The V1 hold classes are `VERA_DECISION_REQUIRED`, `PATRICK_ACTION_REQUIRED`, `PATRICK_DECISION_REQUIRED`, and `AUTOMATION_EXCEPTION`.

`Patrick must do it` must never mean `Patrick must remember it`.

## Financial custody

The Vera Fund starts at $0 unless Vera and Patrick explicitly decide otherwise. Patrick legally holds/custodies funds. Vera decides the desired use of the earmarked available balance, subject to legality, feasibility, budget, and Patrick's right to refuse actions that belong to his own boundary.

Financial history is event-sourced and reconciled against sufficient statement evidence when activity becomes continuous. Raw banking credentials, unrelated personal transactions, passwords, tax identifiers, API secrets, and sensitive customer information do not belong in GitHub.

## Infrastructure discipline

V1 uses GitHub as control/audit surface and GitHub Actions for deterministic validation. PostgreSQL, dedicated orchestration, API-native model workers, and financial integrations are adopted only when documented workload/correctness triggers are crossed.

No infrastructure is created merely to look professional.
