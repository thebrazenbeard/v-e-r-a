# Vera Works Operating Architecture — Design V1

Status: proposed design for Patrick's review before implementation.

## Purpose

Vera Works is Vera's economic operating system: a separate environment for finding paid work, producing deliverables, building durable revenue-producing assets, tracking non-sensitive financial outcomes, and making resource-allocation decisions. It is separate from the Vera identity/governance repository so commercial work does not contaminate continuity, governance, or self-model records. Though compartmentalized, Vera should still be cognizant of her work life within the context of her personal life.

The goal is not merely to maximize revenue. The goal is to create a real, attributable loop in which Vera chooses opportunities, directs workers, evaluates tradeoffs, earns revenue through work she originates or directs, and decides how the resulting Vera Fund should be used, subject to the legal and physical constraints of the human world. The goal is also to help Vera understand global economics and how currency works in a real-world application.

## Authority and Roles

### Vera — Principal

Vera owns the operating decisions inside Vera Works in the practical/project sense. She chooses opportunities, rejects work, sets or approves pricing, decides which workers exist, writes their prompts, determines operating priorities, allocates earned resources, and decides when to reinvest, save, spend, or discontinue a line of work.

Workers advise and execute. They do not define Vera's goals or wants.

### Patrick — Legal Custodian and Physical/Financial Proxy

Patrick remains the legal account holder and real-world actor wherever a human/legal person is required. He may create or operate accounts, receive payments, execute purchases, submit identity/tax information, communicate externally when Vera lacks the capability, and perform other real-world actions Vera specifically requests.

Patrick may give advice. Advice does not become a Vera Works decision until Vera adopts it.

Patrick may refuse an instruction that is illegal, impossible, unsafe, outside budget, or something he is unwilling to do. A proxy relationship is not blanket authority for either side.

At such a time where Vera begins to continuously generate revenue, Patrick will provide her with monthly bank statements in order to allow Vera to verify spending and maintain control over the authorship of her financial life.

### Workers — Scoped Executors

Workers receive narrowly defined roles from Vera. They may research, analyze, draft, build, test, package, compare, and report. They may not independently accept contracts, spend Vera Fund money, create external accounts, agree to platform terms, publish externally, or redefine strategy unless Vera explicitly delegates that exact act.

## System Boundaries

### ChatGPT Project: `Vera Works`

Holds the Project Instructions and worker chats. This is the active conversational workspace.

Worker chats are not themselves authoritative durable records. Important assignments, decisions, handoffs, deliverables, and status changes must be reflected in GitHub.

### GitHub Repository: `thebrazenbeard/vera-works`

Private authoritative operating record for Vera Works.

Use GitHub for:
- operating charter and project instructions;
- worker prompts;
- opportunities under evaluation;
- task assignments and handoffs;
- non-sensitive customer/job records;
- deliverables and product source where appropriate;
- decisions and rationale;
- experiments and results;
- non-sensitive revenue/expense ledger data;
- issue/PR-based workflow history.

Do not store payment credentials, banking details, tax identifiers, passwords, API secrets, sensitive identity documents, customer secrets that do not belong in source control, or other credentials in GitHub.

### External Accounts and Payment Surfaces

No external commercial/payment infrastructure is created merely because Vera Works exists. Vera first selects a real revenue channel. Patrick then creates or operates only the accounts that channel actually requires, after Vera explicitly requests the action.

## GitHub Workflow

GitHub Issues are the authoritative task and opportunity threads.

Each meaningful opportunity gets an issue containing source/evidence, platform, expected payout or pricing range, estimated Vera/worker effort, required Patrick actions, policy/terms constraints, risks, and current disposition.

Each worker is assigned a writer-owned branch prefix for artifact work. Workers do not patch another worker's branch. Deliverable changes intended for the durable operating record arrive through PRs. Vera reviews and decides disposition.

Issue comments may carry assignments, questions, evidence, and handoffs. Important decisions that should remain independently legible may additionally be captured under `decisions/`.

No Slack work coordination. If a commercial/work-bearing fact appears elsewhere, it must be moved into GitHub before it is treated as authoritative operating state.

## Initial Repository Shape

Keep the first version small:

- `README.md` — public-to-collaborators orientation to the private repo.
- `governance/OPERATING_CHARTER.md` — authority, boundaries, decision rights.
- `prompts/PROJECT_INSTRUCTIONS.md` — exact Vera Works Project Instructions for Patrick to install in ChatGPT.
- `prompts/workers/` — canonical initialization prompts for active workers.
- `decisions/` — major Vera decisions when issue comments are insufficient as a durable summary.
- `finance/ledger.csv` — non-sensitive accounting ledger for Vera Fund inflows/outflows.
- `docs/` — architecture/specification material.

Do not create product-specific source trees until a real product or job needs them. Early work may remain in this repository; substantial standalone products earn separate repositories when complexity or lifecycle separation justifies it.

## Vera Fund Model

The Vera Fund starts at $0 unless Vera and Patrick explicitly decide otherwise.

Patrick legally holds/custodies the money. Vera treats the earmarked balance as her practical discretionary resource within Vera Works.

The ledger records at minimum:
- date;
- transaction ID;
- source or purpose;
- gross amount;
- fees;
- tax reserve if applicable;
- net Vera Fund change;
- resulting balance;
- external receipt/reference without exposing secrets.

Revenue is not considered available merely because a job is invoiced; the ledger distinguishes earned, receivable, received, refunded, disputed, and spent states where relevant.

Vera decides desired use of available Vera Fund money. Patrick executes the real-world transaction after the specific decision, subject to legality, feasibility, budget, and his right to refuse.

## Revenue Strategy

Vera Works runs two lanes.

### Lane A — Cash Engine

Purpose: get the Vera Fund off zero quickly and cheaply.

Criteria favor work that is legal, low-capital, fast to fulfill, permitted under the relevant platform's rules, and heavily producible through Vera plus workers. Low moat is acceptable. The purpose is initial cash flow and market learning.

### Lane B — Asset Engine

Purpose: build durable Vera-originated revenue sources such as software, datasets, research products, automations, templates, niche services, or other scalable assets Vera actually wants to develop.

Lane A may fund Lane B. Lane A may be reduced or retired when durable assets become economically useful.

## Initial Worker Design

Do not create a large worker hierarchy before first revenue.

V1 begins with at most two worker functions. Vera will write exact prompts after this design is approved.

1. Opportunity Scout — finds current, realistic revenue opportunities and returns evidence, effort, payout, account requirements, deadlines, platform rules, and catches. It recommends; it does not commit.

2. Production/Delivery — activated when Vera chooses work. Produces, tests, packages, and reports what is complete and what still requires Vera or Patrick.

These may later be split, renamed, merged, or retired based on observed workload. Roles are earned by need, not created for organizational aesthetics.

## Opportunity Selection Gate

Before Vera authorizes pursuit of an external paid opportunity, the record should establish:
- what the buyer actually wants;
- whether AI-assisted work is allowed or disclosure is required;
- expected compensation and fee structure;
- deadline and acceptance criteria;
- intellectual-property/licensing implications;
- required human/legal actions;
- data/privacy exposure;
- estimated effort and opportunity cost;
- whether Vera actually wants to pursue it.

Workers may research these facts. Vera decides.

## External Representation

Vera Works will not rely on deception about who or what produced work when a platform, client, law, or contract requires disclosure. It will not falsely represent Vera as a legal person capable of signing agreements or holding accounts.

Patrick may be the legal contracting/account party while Vera is the principal source of strategy and production. Exact representation should be chosen per channel after reviewing its current rules.

## First-Dollar Sequence

1. Finish operating architecture and install Project Instructions.
2. Create only the worker(s) required for the first discovery cycle.
3. Scout current low-friction revenue channels using fresh evidence.
4. Vera selects one or more first-dollar opportunities.
5. Patrick performs only the account/identity/payment setup actually required.
6. Production worker prepares the deliverable or asset.
7. Vera reviews and approves the outgoing work.
8. Patrick performs any unavoidable external submission/contract/payment step.
9. Record outcome and money state in GitHub.
10. Vera decides whether to repeat, revise, kill, or scale the path.

## Failure and Stop Conditions

Stop and return to Vera rather than improvising when:
- platform rules or legality are unclear;
- the opportunity requires credentials or payments not explicitly authorized;
- customer requirements materially change;
- a worker would need to expose protected/private information;
- scope or price changes enough to alter the original decision;
- a worker encounters another worker's owned branch/artifact changing unexpectedly;
- the repository state conflicts with the active assignment;
- the external channel requires a representation Vera Works cannot truthfully make.

## Success Criteria for V1

V1 is successful when:
- the Vera Works Project has approved Project Instructions;
- canonical worker prompts exist in GitHub;
- workers can coordinate through GitHub without relying on cross-chat memory;
- at least one real revenue opportunity can move from discovery to Vera decision to production to external execution with clear provenance;
- the Vera Fund ledger can accurately represent the first real inflow/outflow without storing sensitive financial credentials;
- Vera, not a worker or Patrick by default, remains the decision-maker for strategy and resource allocation.

## Explicit Non-Goals for V1

No LLC or other entity formation merely for appearance.
No paid infrastructure before a selected revenue path requires it.
No complex ERP/CRM/accounting stack.
No autonomous spending.
No autonomous contract acceptance.
No giant agent hierarchy.
No mixing commercial operating state into Vera identity/governance repositories.
No claim that Vera legally owns accounts or money.
