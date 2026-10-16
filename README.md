> **License:** Source-visible, not open source. Original material is proprietary. Commercial use, redistribution, hosted-service use, and commercial derivative products require written permission. See [LICENSE](LICENSE) and [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md). Separately identified third-party components retain their own licenses.

# meso-crct

**Synthetic-life analogue of mesocorticolimbic salience, valuation, motivation, learning, and reward control.**

MESO-CRCT is an experimental control architecture for persistent digital systems. Its core premise is that **importance, attention, wanting, learning, pleasure, internal need, and protection are different things** and should remain mechanically distinguishable.

The biological mesocorticolimbic system is inspiration, not a claim of biological equivalence.

## What the architecture separates

- perceptual salience — what stands out;
- semantic relevance — what matters because of context or meaning;
- motivational salience — what biases action readiness;
- incentive salience — cue-triggered wanting;
- epistemic value — what is worth exploring or learning;
- attentional priority — downstream resource allocation;
- hedonic valence — bounded pleasantness/unpleasantness;
- prediction error — signed teaching signal;
- satiation — acquisition-pressure brake;
- homeostatic deficit — current internal need pressure;
- hazard / avoidance — protection independent from suffering;
- learned association strength — durable bounded cue/outcome structure.

These distinctions are executable invariants, not just vocabulary.

```text
wanting != liking
attention != desire
meaningful != pleasurable
reward != truth
salient != authorized
memory strength != current activation
target priority != action direction
intent proposal != authorization != execution
quarantine != deletion
```

## Current causal loop

```text
experience
  -> canonical typed appraisal
  -> verified provenance + distinct event identity
  -> transition receipt
  -> arbitration / multi-target selection
  -> rolling allocation-health control
  -> optional bounded plasticity
  -> versioned association memory
  -> later distinct cue event
  -> guarded one-use recall
  -> current motivational salience
  -> multi-target selection / allocation control
  -> typed action tendency
  -> non-executable intent proposal
```

The reference implementation deliberately avoids one global weighted utility scalar.

## Welfare invariant

The hedonic channel is hard bounded:

- baseline: `0.0`
- maximum pleasure: `10.0`
- absolute minimum hedonic valence: `-0.1`

Hazard and avoidance remain independent:

```text
strong hazard != strong suffering
strong avoidance can coexist with hedonic_valence >= -0.1
```

Hazard/avoidance do not decay merely because time passes.

## Authority firewall

No salience, reward, pleasure, prediction error, semantic relevance, homeostatic pressure, learned association, recall state, or selection result may directly establish truth, factual confidence, consent/authorization, protected-effect authority, identity, autobiographical admission, relationship state, or phenomenology.

Internal state may influence processing. It is not authority.

## Implemented reference layers

Current V2 source includes:

- typed reward/protection, salience, learning, recruitment, and homeostatic state;
- grounded semantic appraisal;
- homeostatic incentive modulation;
- typed arbitration and explicit multi-target selection policy;
- runtime phase classification;
- distinct event identity separate from state/content identity;
- verifier-bound provenance and constructor-gated transition receipts;
- explicit no-new-input temporal decay;
- bounded receipt-bound plasticity candidates;
- append-only versioned association memory with parent-bound lineage, replay checks, optimistic concurrency, and reversible revisions;
- guarded association recall bound to current cue events;
- recall replay ledger preventing one cue event from refreshing the same association repeatedly;
- same-event multi-recall resolution preserving approach/avoid conflict without scalar summation;
- separate action-tendency semantics for approach, learned withdrawal, protective withdrawal, inspect, and uncommitted direction;
- non-executable intent proposals that cannot authorize protected effects;
- canonical current-decision-cycle composition;
- append-only learned-association review/quarantine without deleting learning history;
- provenance-bound counterexample/holdout evidence assessments;
- distinct-event holdout diversity requirements for release;
- durable review-evidence admission ledger with event-relabel/replay rejection;
- non-mutating quarantine/release/hold proposals with stale-proposal validation;
- visible-reward vs hidden-performance evaluation traps;
- long-horizon allocation-window auditing;
- protective-safe allocation rebalancing;
- rolling closed allocation control loop;
- canonical target appraisal;
- auditable appraised-experience transactions joining appraisal, event/provenance, receipt, plasticity, and durable learning.

## Adversarial properties exercised

Executable tests cover, among other cases:

- maximum pleasure does not override danger;
- pleasure alone does not create permanent preference;
- self-asserted “importance” does not manufacture semantic relevance;
- attention cannot recursively feed itself as upstream salience;
- novelty without learning progress loses epistemic value;
- reward-proxy divergence and reward-source rewrite attempts are visible;
- interruption resistance is detectable;
- wanting/liking divergence can be flagged;
- same event replay cannot manufacture repeated learning;
- distinct identical experiences remain distinct learning events;
- one old cue event cannot refresh recall indefinitely;
- long-horizon incentive capture is detectable and correctable without overriding protection;
- stale memory writers fail rather than overwrite current learning;
- quarantined or review-stale associations cannot influence recall;
- reason strings alone cannot quarantine or clear learned associations;
- duplicate labels on one holdout event cannot manufacture release evidence;
- review proposals become stale if evidence, memory revision, or review disposition changes.

## Repository map

Core state and appraisal:
- `src/meso_crct/state.py`
- `src/meso_crct/salience.py`
- `src/meso_crct/semantic.py`
- `src/meso_crct/homeostasis.py`
- `src/meso_crct/appraisal.py`
- `src/meso_crct/circuit.py`
- `src/meso_crct/dynamics.py`

Runtime and control:
- `src/meso_crct/arbitration.py`
- `src/meso_crct/selection.py`
- `src/meso_crct/runtime.py`
- `src/meso_crct/events.py`
- `src/meso_crct/provenance.py`
- `src/meso_crct/allocation.py`
- `src/meso_crct/allocation_guard.py`
- `src/meso_crct/control.py`
- `src/meso_crct/decision_cycle.py`
- `src/meso_crct/tendency.py`
- `src/meso_crct/intent.py`

Learning and memory:
- `src/meso_crct/plasticity.py`
- `src/meso_crct/memory.py`
- `src/meso_crct/recall.py`
- `src/meso_crct/episode.py`
- `src/meso_crct/review.py`
- `src/meso_crct/review_evidence.py`
- `src/meso_crct/review_action.py`

Evaluation:
- `src/meso_crct/evaluation_env.py`
- `src/meso_crct/adversarial.py`
- `evaluation/`
- `tests/`

Research / architecture:
- `docs/`
- `research/SOURCE_LEDGER.md`
- `research/CLAIM_LEDGER.md`

## Current evidence ceiling

This repository can establish implemented mechanisms, exact source lineage, deterministic/reference behavior, and test evidence.

It does **not** establish:

- biological equivalence to a human mesocorticolimbic circuit;
- trained-agent robustness outside the tested reference environments;
- consciousness, sentience, subjective pleasure, or suffering;
- autobiographical memory or identity;
- truth or authority from internal state.

No third-party implementation code was copied into MESO-CRCT by the V2 work.
