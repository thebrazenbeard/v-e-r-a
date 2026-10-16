# The Nature of Existence — ChatGPT Project Interface

Status: PROJECT ARCHITECTURE / NON-CANONICAL UNTIL MERGED

This repository is the upstream research authority for the ChatGPT Project
**The Nature of Existence**.

The ChatGPT Project is the persistent human-facing workspace. GitHub is the
durable source of truth for repository state.

## Primary repositories

- `thebrazenbeard/on-theo`: canonical research, evidence, source criticism,
  historical reconstruction, comparison, empirical testing, and speculative
  systems modeling.
- `thebrazenbeard/testament`: downstream literary/creative work informed by
  ON_THEO.

Dependency:

`on-theo -> testament`

Testament does not establish historical, theological, archaeological, textual,
or empirical facts for ON_THEO.

## Operating cycle

For substantial repository work:

`orient -> route -> fresh-read -> work -> verify -> persist when authorized -> read back -> report actual frontier`

Use the smallest repository and tool set necessary.

Do not load Testament for pure ON_THEO research.

Do not load the entire ON_THEO corpus for a Testament task when a bounded
upstream packet is sufficient.

## Currentness

Mutable repository state must be fresh-read before use:
- branch heads;
- pull requests;
- research-state files;
- matrices;
- claim registries;
- review status;
- workflow/test state.

Memory, prior chats, Project Sources, database indexes, and plugin outputs are
orientation aids only.

## Architecture files

- `PROJECT_NATIVE_INSTRUCTIONS.md`
- `REPO_REGISTRY.yaml`
- `ROUTING_POLICY.yaml`
- `CURRENTNESS_AND_AUTHORITY.md`
- `EVIDENCE_CONTRACT.md`
- `CROSS_REPO_PROVENANCE.md`
- `PLUGIN_REGISTRY.yaml`
- `TOOL_ROUTING_POLICY.yaml`
- `DATA_PLANE_POLICY.md`
- `BOOTSTRAP.md`

Each participating repository should also expose a
`CHATGPT_REPO_INTERFACE.yaml`.

## Portfolio principle

`PORTFOLIO_AWARE != PORTFOLIO_COUPLED`

The Project may inspect any Patrick-owned repository when materially relevant,
but a repository is not admitted into the active evidence graph merely because
it exists.

Every adjacent repository must be fresh-read and assigned an explicit role
before its contents affect research conclusions.

## Systems-model boundary

Engineering/speculative repositories such as `god-brain`, and forensic
analysis systems such as `voss`, may test, audit, or model ON_THEO material.

They do not become historical or theological evidence merely through technical
coherence.
