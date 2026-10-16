# Claim Harvester

Status: **V1 SOURCE IMPLEMENTATION / NO CLAIM EFFECT AUTHORIZED**

Objective: continuously reduce the internet-sized search space of "free money" into a small queue of defensible, positive-value entitlement candidates that require no person-to-person sales or customer communication.

Current implementation:

- deterministic candidate/eligibility evaluator: `vera_works/claim_harvester.py`;
- runtime-only wallet configuration: `config.example.json`;
- architecture/effect boundary: `docs/CLAIM_HARVESTER_V1.md`;
- hostile unit tests: `tests/test_claim_harvester.py`.

Initial runtime aliases:

- `vera-fund-btc`
- `vera-fund-evm`

The actual public addresses are intentionally not committed. They are supplied at runtime through environment variables.

## Next frontier

1. Bind an Ingest-backed authoritative-source acquisition adapter.
2. Add source adapters for government/court redress and official crypto protocol claim APIs.
3. Feed normalized candidates through Lou-Pole + Voss/Cricket review when eligibility is not mechanically exact.
4. Add Project Runner scheduling and WIP checkpoints.
5. Add Pre-Active observation only after the installed runtime/daemon is independently verified.
6. Run read-only wallet entitlement/history scans.
7. For every positive candidate, create the appropriate Vera Works hold/effect packet rather than signing/submitting automatically.

No private key, seed phrase, password, signing credential, account credential, identity document, or unrelated transaction history belongs in this workstream.
