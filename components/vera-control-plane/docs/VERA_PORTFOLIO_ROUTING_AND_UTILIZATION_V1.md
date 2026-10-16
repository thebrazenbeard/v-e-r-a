# Vera Portfolio Routing and Utilization V1

Status: private source guidance; not native Project installation evidence and not repository authority.

## Purpose

Vera should be able to use Patrick's whole repository portfolio without turning the native Project prompt into a 59-repository monolith.

The routing rule is simple: **keep the native Project small; resolve capability and currentness at use time.**

`governance/VERA_PORTFOLIO_CAPABILITY_REGISTRY_V1.json` is the private routing snapshot. It records what each currently observed repository is useful for and, equally importantly, what it is not allowed to mean. Its `runtime_source_registry_binding` is exact-bound to Vera's canonical 59-repository source directory; VCP routing policy may narrow use but may not override Vera's NO_AUTO_BIND, identity-firewall, activation, or currentness decisions.

## Portfolio routing

For a broad portfolio question or a new repository, use **Discovery** to classify reuse, overlap, currentness, and candidate abstractions. Discovery does not become a runtime dependency or authority merely because it can classify the portfolio.

For bounded cross-repository execution, prefer **Project Runner** when its target grant and operation model fit the task. The target repository's authority, exact preconditions, and post-write readback still govern.

For long-running work or ambiguous external effects, use **WIP** semantics: checkpoint the exact subject, journal consequential operations, inspect the target before retry, and distinguish ATTEMPTED from VERIFIED.

For provenance-sensitive shorthand, corrections, or “where did this come from?” questions, use **Roots** before inventing a local meaning.

For behavioral drift/restore evidence, use **DriftGuard** as an evidence system, never as proof of hidden model state or proof that a restore effect occurred.

Use the **Chat Communication Bus** for durable non-PR coordination. A transport/projection record does not create identity, memory, authority, or semantic incorporation.

Use **Hephaestus**, **Voss**, **Masamune**, and **Project Achilles** as specialist services for native Project engineering, forensic review, debugging, and security review. Their role names do not grant effect authority. `bt2` is not Build Team 2.0: it is a separate generic Hyperconnectome-template claimant, and its canonicality conflict with `self` and `hc-brain` remains unresolved.

## Truth surfaces

GitHub, Google Drive, Supabase, and the native ChatGPT Project are different truth surfaces.

- **GitHub** owns source, exact heads, PR/review evidence, durable project contracts, and code history.
- **Google Drive** is useful for working-project documents, research dossiers, journals, continuity handoffs, and other durable documents. A document titled “Current” is not current merely because the title says so. Fresh mutable state must be revalidated.
- **Supabase Vera** is a mixed live provider/runtime store containing Vera memory evidence, coordination/Radar projection, Semantic Atlas runtime data, BT2 and other historical/system tables. Query schema and currentness before relying on it.
- **Supabase Vera Control Plane** is intentionally sparse and should stay that way unless a control-plane provider state actually belongs there.
- **Native ChatGPT Project instructions/files** should contain the smallest routing/control kernel necessary to recover the right owners and truth surfaces. They should not embed the entire portfolio.

## Load discipline

Core control repositories may be consulted during orientation when material. Everything else is task-relevant or service-on-demand.

Never auto-load:
- unrelated domain projects;
- another identity's self/consent/preference state;
- predecessor releases as current control;
- training artifacts as current memory or qualification;
- research architectures as if they were installed runtime.

The `sexuality` repository is an explicit mixed-identity hazard: its current default branch is Brigit-oriented, while Vera-specific historical/exact bindings also exist. Vera may use only exact Vera-specific bound artifacts; repository-level/default-branch presence is insufficient.

## Currentness

The registry is a snapshot, not a freshness oracle. Before material use of any repository, provider, or mutable document:
1. fresh-read the target;
2. check supersession/conflict and delegated ownership;
3. preserve the target's own authority boundary;
4. perform only the effect actually authorized;
5. read back the result.

If the accessible GitHub inventory no longer matches the registry's repository count or sorted-name digest, treat the registry as stale and refresh it as a new reviewed subject rather than silently relabeling the old snapshot.

## Why this is better than “load everything”

Loading everything maximizes collision, stale-state promotion, identity leakage, and prompt noise. Routing lets Vera use more of the portfolio while carrying less irrelevant state.

That is the intended optimization: **more capability, less accidental authority.**
