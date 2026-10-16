> **License:** Source-visible, not open source. Original material is proprietary. Commercial use, redistribution, hosted-service use, and commercial derivative products require written permission. See [LICENSE](LICENSE) and [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md). Separately identified third-party components retain their own licenses.

# vera-works

Private operating repository for Vera Works: Vera's economic work system.

Vera Works is designed around work rather than worker chats. GitHub is the authoritative configuration/audit surface; immutable events and deterministic validation provide the V1 automation spine; Vera retains consequential decision authority; Patrick serves as legal/physical/financial proxy where a human actor is required.

Key paths:

- `governance/OPERATING_CHARTER.md` — authority and operating boundaries
- `prompts/PROJECT_INSTRUCTIONS.md` — ChatGPT Project Instructions
- `prompts/workers/` — canonical worker initialization prompts
- `contracts/` — machine-readable V1 contracts and state vocabulary
- `vera_works/` — deterministic validation/projection code
- `ops/events/` — immutable operating-event records
- `docs/AUTOMATION_SPINE.md` — automation control model
- `docs/INFRASTRUCTURE_TRIGGERS.md` — explicit triggers for heavier infrastructure
- `docs/superpowers/specs/` — architecture specifications
- `docs/superpowers/plans/` — implementation plans

V1 invariant: **Automate execution. Escalate judgment. Every escalation arrives with a recommendation. Resume deterministically from the held state after the decision.**

No secrets, raw financial credentials, unrelated personal banking activity, or sensitive customer material belong in this repository.
