# V-E-R-A — local model interface and pinned-source workspace

**A Python reference application for running a bounded, response-only local-model chat interface and inspecting a pinned collection of independently maintained component sources.**

V-E-R-A contains two useful but deliberately separate tools:

1. A same-machine browser interface to a locally running **Ollama-compatible model service**. It discovers installed model names, sends bounded conversational requests, and displays returned text without executing model-proposed tools.
2. A Git source registry and worktree materializer for the project's component snapshot branches. It checks recorded commit pins, refuses to overwrite existing destinations, and distinguishes exact Git mirrors from intentionally sanitized or source-definition snapshots.

This repository is **not** a universal agent host, a multi-provider inference router, an autonomous task scheduler, or an authorization service. Its source snapshots do not install, connect, authorize, or qualify their upstream components.

## Requirements

- Python **3.10+** and Git for the source-registry workflow.
- Python 3.10+ and an independently installed, locally running Ollama-compatible HTTP service for the response-only interface.
- Optional encrypted transcript-vault dependencies in [`requirements-vault.txt`](requirements-vault.txt) if the operator explicitly enables local persistence.

The default interface uses the Python standard library and static browser assets; there is no frontend build step. See the [source registry](components.json), [interface code](interface/), and [source materializer](scripts/materialize.py).

## Run the local chat interface

From a checkout, after starting your own local model service:

```sh
python -m interface --port 8765 --ollama-url http://127.0.0.1:11434
```

Open `http://127.0.0.1:8765/` in a browser **on the same computer**. The model list comes from the live local service; no model is bundled or installed by this repository.

The HTTP gateway binds to loopback, validates Host/Origin and a fresh per-process browser-session token, bounds request bodies and replies, and refuses model tool calls. A browser-session token is **not** operating-system identity, person authentication, consent, or permission to act. The model service may log requests under its own policy. No remote host or external device is contacted by this interface.

The browser keeps ordinary conversation text in the current tab. Persistent transcripts are **off by default**. Operators can separately enable an encrypted local transcript vault using both `--memory-db` and `--memory-secret-file`; the optional `--memory-rollback-anchor` supplies a limited, separately protected witness against **database-only** rollback. This is not secure erasure, a durable identity system, or whole-device rollback protection. Read the [interface security and vault qualification](docs/VERA_INTERFACE_V1.md) before enabling persistence.

The interface can optionally display a **read-only, separately authenticated** Volition goal projection when an operator explicitly injects a qualified host provider and separate read token. That projection never grants effect authority, creates a task, or proves that a model independently formed a desire. See the [verified Volition adapter contract](docs/VERIFIED_VOLITION_HOST_ADAPTER.md).

## Inspect and assemble pinned source snapshots

[`components.json`](components.json) currently records **44 populated component branches**: **38 exact Git-tree mirrors**, **5 sanitized source snapshots**, and **1 source-definition provider snapshot**. These are historical, pinned source states, **not** a continuously synchronized monorepo or proof that any component is installed.

The registry and materializer are specifically bound to the V-E-R-A repository and its named component branches. Their checks are reusable as a pattern, but this script is **not** a generic arbitrary-GitHub repository mirror manager without code changes.

```sh
git clone https://github.com/thebrazenbeard/v-e-r-a.git
cd v-e-r-a

# Offline registry inventory; does not fetch or materialize components.
python scripts/materialize.py list

# Check that a selected published component branch still has its recorded pin.
python scripts/materialize.py check-origin --only portal

# Optional explicit checkout; create the destination first.
mkdir components
python scripts/materialize.py materialize --only portal
python scripts/materialize.py verify --only portal
```

`check-origin` and `materialize` contact the repository's remote Git origin. Materialization creates a **detached worktree at the recorded snapshot commit**, verifies that the branch did not move, and refuses an existing destination. `verify` checks commit and clean-state invariants after materialization. It does not compare that snapshot to a newer upstream `main` or test upstream runtime behavior.

For sanitized branches, a tracked `MIRROR_SOURCE_PROVENANCE.json` records omitted material; they are **not** byte-identical upstream mirrors. The provider snapshot contains schema/code definitions, not a restorable live service or customer records. The source repositories themselves remain authoritative for code changes, reviews, licenses, and deployments. Do not treat a mirror branch as a permission grant or as a substitute for its upstream security review.

## Interfaces and trust boundaries

| Surface | Implemented scope | Explicitly outside scope |
| --- | --- | --- |
| Local chat | Same-host installed-model inventory and bounded response-only chat | Model tool execution, remote inference fleet, external effects |
| Browser session | Same-origin session gating and HTML-safe text display | OS user identity or authorization against other local processes |
| Optional transcript vault | Operator-initiated encrypted save/restore/delete and limited rollback witness | Automatic long-term memory, forensic erasure, immutable host identity |
| Optional goal view | Source-pinned, authenticated **read-only** Volition state projection when host configured | Goal authorship proof, model-owned permission, task scheduling |
| Component registry | Pinned branch materialization and source-provenance classifications | Upstream ownership, live installation, current runtime qualification |

The [interface contract](docs/VERA_INTERFACE_V1.md) documents the intended future seams for memory, observation, advisory routing, and protected actions. Those are requirements for separately qualified host integrations, not capabilities silently activated by installing this package. Source labels, selected routes, a local session token, and a model response **cannot authorize a protected operation**. No coherent host-owned immutable authority or provider-binding service is provided here.

## Test and qualification

Run the included source and simulated local-gateway regressions:

```sh
python -m unittest discover -s tests -v
```

The tests use temporary Git repositories and a fake local model HTTP server. They cover registry pin and worktree behavior, session/Origin/Host guards, rejected tool calls, transcript-vault behavior, rollback limits, and selected optional goal-view policies. Tests requiring unavailable optional dependencies or operating-system facilities may skip. They do **not** demonstrate a real pretrained model, a deployed desktop host, actual upstream component installation, external-action authorization, or formal security verification.

## License and contribution status

This public repository does **not** currently track a root `LICENSE`, `COPYING`, or `CONTRIBUTING.md`. Public source visibility does not automatically grant third-party redistribution, commercial use, or derivative-work rights. Each upstream component retains its own terms; review those terms before reusing snapshots or bundling them into another product.

For additional implementation detail, start with the [interface design](docs/VERA_INTERFACE_V1.md), [verified goal-view adapter](docs/VERIFIED_VOLITION_HOST_ADAPTER.md), [local goal-view prototype](docs/VERA_VOLITION_READ_ONLY_VIEW_PROTOTYPE.md), and [source registry](components.json).
