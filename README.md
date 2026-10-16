> **License:** Source-visible, not open source. Original material is proprietary. Commercial use, redistribution, hosted-service use, and commercial derivative products require written permission. See [LICENSE](LICENSE) and [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md). Separately identified third-party components retain their own licenses.

# on-theo

A comparative theology, history, symbolism, and systems-modeling research repository.

## Purpose

`on-theo` studies how Jewish, Christian, Islamic, and adjacent traditions describe reality, creation, human nature, revelation, death, judgment, transcendence, and divine authority. It also maintains a deliberately separate speculative layer that asks whether recurring religious symbols can be fruitfully translated into modern systems/computation language without pretending that ancient authors literally meant computers or simulation theory.

The project is interested in resemblance, divergence, chronology, transmission, reinterpretation, and information loss.

## Core rule

Never collapse these categories:

1. **PRIMARY TEXT** — what a source actually says.
2. **HISTORICAL RECONSTRUCTION** — what historians can reasonably infer about people, movements, dates, or contexts.
3. **LATER TRADITION** — interpretations or stories that arise after the event/source being discussed.
4. **SCHOLARLY INTERPRETATION** — a documented academic reading or dispute.
5. **PROJECT INFERENCE** — an inference made within this repository from cited evidence.
6. **SPECULATIVE MODEL** — a deliberately hypothetical analogy, including the GOD/runtime/simulation framework.
7. **UNKNOWN** — evidence does not currently justify a stronger claim.

A compelling analogy is not historical evidence. A late source can preserve earlier material, but lateness must remain visible. Disagreement between traditions is data, not a defect to be silently harmonized.

## Repository architecture

On-Theo uses a provenance-aware directory/registry model.

- `main` is the canonical infrastructure and reconciled research baseline.
- `traditions/`, `chronology/`, `comparative/`, `research/`, `registry/`, and `synthesis/` are the durable content namespaces.
- branches and pull requests remain work/review surfaces; their existence does not make their contents canonical.
- historical thematic branches such as `tradition/judaism`, `tradition/christianity`, `tradition/islam`, `synthesis/commonality`, and `history/chronology` remain provenance sources where unique material has not yet been reconciled.
- later active research leaves are not silently promoted merely because the infrastructure baseline is canonicalized.
## Current research spine

The initial corpus grows out of several linked questions:

- What did first-century Jewish language such as *Kingdom of God*, Messiah, Son of Man, resurrection, Sheol, Gehenna, Satan, Torah, and Temple mean before later Christian doctrinal compression?
- What can and cannot responsibly be inferred about Yeshua's birth, paternity traditions, social stigma, Nazareth, the undocumented years, and hometown rejection?
- What is the historical status of Panthera/Pandera traditions?
- How does the Qur'an, six centuries later, preserve, reject, reinterpret, or symbolically rhyme with Jewish and Christian structures?
- Across traditions, what recurring architecture appears around creator/creation, delegated authority, revelation, temporary worldly existence, judgment, resurrection, and higher-order reality?
- Can those structures be translated into a modern computational metaphor — environment/runtime/controller/administrator, instantiated agents, privileged operations, re-instantiation, information channels — while keeping that translation explicitly speculative?

## Tone

Curious, irreverent when useful, but evidence-disciplined. No tradition receives automatic deference or automatic contempt. Claims earn confidence from evidence, not from familiarity, offensiveness, popularity, or how entertaining they are.

## Registry validation

The provenance registries and draft extension stack have an executable consistency check.

Run the test suite:

```bash
python -m pip install -r requirements-dev.txt
pytest -q
```

Run the validator directly:

```bash
python scripts/validate_registry.py --root .
python scripts/validate_registry.py --root . --json
```

Validation checks stable-ID collisions, unresolved source/witness/concept references, manifest identity/base/dependency consistency, and review result/provenance vocabularies. A successful validation means the registry graph is internally consistent; it does **not** merge, materialize, promote, or establish the historical truth of draft claims.