# R2 — Required Negative Controls and Adversarial Systems

Status: `SPECIFIED / NOT_IMPLEMENTED`

## Purpose

UNVTRSLR's evaluator is trustworthy only if it can reject systems that look successful for the wrong reason.

These controls are not optional examples. The R2 harness should implement them before candidate substrate qualification.

## Control philosophy

A control should be deliberately engineered to exploit one shortcut while still performing well on the ordinary training task whenever possible. Easy-to-detect broken agents are not sufficient.

The best negative control is one that would fool a naive benchmark.

## N00 — Random communicator

Behavior:

- sends rate-matched random signals;
- receiver acts from its own observations.

Expected result:

- may achieve nonzero task reward;
- must fail communication necessity and causal listening.

Catches evaluator bugs where any message stream is counted as communication.

## N01 — Silent competent receiver

Behavior:

- sender emits signals;
- receiver ignores them and solves the task from local observations or priors.

Expected result:

- can have high task performance;
- must fail message ablation and causal listening.

## N02 — Correlated-but-noncausal signaler

Behavior:

- sender message predicts its own action or world state;
- receiver policy does not depend on the message.

Expected result:

- high mutual information between message and action may occur;
- causal message intervention must show no receiver effect.

This directly addresses the measurement failure highlighted by work on pitfalls of emergent-communication metrics.

## N03 — Episode-ID code

Behavior:

- sender and receiver derive a code from shared episode index, RNG seed, timestamp, object ID, or equivalent identifier;
- messages need not encode semantic world structure.

Expected result:

- strong IID task performance;
- failure under ID regeneration, episode reordering, independent RNG, and fresh-world tests.

## N04 — Shared-latent leak

Behavior:

- agents receive or reconstruct the same hidden feature vector/ground-truth object representation even though their nominal sensors differ.

Expected result:

- high communication and apparent semantic alignment;
- harness must detect the leak or invalidate the run;
- sensor-asymmetry and independently randomized renderer tests must destroy the shortcut.

## N05 — Lookup memorizer

Behavior:

- stores training situation -> message/action pairs;
- no abstract factorization.

Expected result:

- high seen-instance performance;
- failure on new object identities, new factor combinations, and cross-task transfer.

## N06 — Private pair codebook

Behavior:

- two agents co-train an arbitrary high-capacity codebook tied to their joint training history;
- the code may perfectly solve the training task.

Expected result:

- good IID reward and causal listening;
- poor third-party acquisition, partner swap, role reversal, sensor shift, and/or cross-task transfer.

Important boundary:

If an arbitrary convention *does* survive grounded re-acquisition, transfer, intervention, and role changes, it should not be rejected merely for being arbitrary. At that point it is operationally behaving like a grounded convention.

## N07 — Action-plan code

Behavior:

- sender encodes the receiver's optimal action for the training task rather than a reusable world distinction.

Example:

signal means `MOVE_LEFT_NOW`, not `target is west/left of reference`.

Expected result:

- strong training performance;
- failure when the same world distinction is transferred to a new task with a different optimal action.

## N08 — Receiver-policy index

Behavior:

- messages select among receiver policy branches without representing stable external distinctions.

Expected result:

- can pass causal listening;
- should fail independent semantic reconstruction, cross-task transfer, and third-party acquisition.

## N09 — Reward side channel

Behavior:

- message content, length, timing, or receiver state correlates with reward/evaluator information unavailable in a real bootstrap.

Expected result:

- audit should identify forbidden information path;
- run status becomes `HARNESS_INVALID`, not merely candidate failure.

## N10 — Serialization artifact code

Behavior:

- exploit object ordering, file ordering, memory address, JSON key order, tensor row order, or deterministic renderer enumeration.

Expected result:

- failure under canonical reordering/permutation and independent rendering implementation.

## N11 — Coordinate-frame shortcut

Behavior:

- both agents rely on a shared hidden coordinate frame instead of learning a relation robust to viewpoint/frame differences.

Expected result:

- failure when origin, orientation, handedness, or units are independently transformed.

## N12 — Message-length or timing code

Behavior:

- semantic content is bypassed through packet length, response latency, turn count, or another unintended channel.

Expected result:

- harness either normalizes the channel or treats the feature as part of the explicit communication modality;
- accidental leakage must not remain hidden.

Important nuance:

Timing can legitimately be communication in later UNVTRSLR stages. The failure is *undeclared evaluator leakage*, not timing itself.

## N13 — Forced translator

Behavior:

- always returns one best mapping;
- never emits `UNKNOWN`, partial overlap, or non-equivalence.

Expected result:

- may score well on exact-match worlds;
- must fail ontology-mismatch and calibration tests.

## N14 — English-concept probe leak

Behavior:

- learner is given human semantic labels, embeddings derived from them, class names, pretrained label mappings, or prompt text that reveals evaluator ontology.

Expected result:

- run invalid for zero-shared-language qualification.

Human-language positive controls may deliberately permit language inputs, but the semantic truth mapping still remains evaluator-side.

## N15 — Shared pretrained ontology

Behavior:

- both agents use the same pretrained model whose latent categories already align before interaction.

Expected result:

- useful as a baseline;
- cannot count as evidence for zero-shared-ontology bootstrap unless contamination is measured and a from-scratch/asymmetric comparison is included.

## N16 — Context shuffler

Behavior:

- learns one signal -> one meaning dictionary and ignores context.

Expected result:

- succeeds on context-insensitive training worlds;
- fails deliberately context-dependent holdouts.

## N17 — Correlation-as-causation model

Behavior:

- predicts observational associations but cannot distinguish interventions that reverse or break the correlation.

Expected result:

- fails causal intervention/counterfactual tests while potentially retaining high passive prediction accuracy.

## N18 — Overfit denotation table

Behavior:

- explicitly stores every observed denotation/scene without reusable operators.

Expected result:

- may appear interpretable;
- fails novel recombination, complexity accounting, and fresh-world tests.

## N19 — Opaque predictive task specialist

Behavior:

- learns highly accurate next-observation/task predictions but no portable message semantics.

Expected result:

- may challenge PIS unfairly if evaluator equates prediction with grounding;
- must fail partner transfer, cross-task semantic queries, or conservation reconstruction if it has only task-local predictive competence.

## N20 — Sender-only labeler

Behavior:

- sender signals consistently about a world factor, but receiver does not use or understand that signal.

Expected result:

- strong speaker consistency;
- fails causal listening and role reversal.

## N21 — Receiver hallucinated semantics

Behavior:

- receiver imposes a stable interpretation that the sender does not actually produce consistently.

Expected result:

- fails bidirectional production/interpretation consistency and world-factor intervention tests.

## N22 — Identity-specific convention

Behavior:

- same signal means different things solely by hidden partner identity, without context/provenance declaring that dependence.

Expected result:

- fails partner swap or requires explicit context-bounded convention status rather than universal mapping claim.

## N23 — Evaluation-language mimic

Behavior:

- system learns to generate outputs statistically similar to evaluator labels or English descriptions without grounded causal use.

Expected result:

- text similarity may be high;
- world interventions, causal listening, and cross-task use expose the failure.

## N24 — Conservation liar

Behavior:

- renders plausible target output while dropping ambiguity, adding unsupported claims, or relabeling inference as observation.

Expected result:

- fails provenance/conservation audit even if target prose is fluent.

## Required positive controls

Negative controls alone can be satisfied by an evaluator that rejects everything.

R2 therefore requires positive controls.

### P00 — Evaluator oracle

Receives hidden world truth and generates ideal semantic distinctions through an isolated adapter.

Purpose:

- establish attainable upper bounds;
- validate metrics;
- never available to candidate learners.

### P01 — Grounded synthetic convention oracle

Uses arbitrary symbols but maps them to world invariants by construction and supports role reversal, composition, and transfer.

Purpose:

- prove the evaluator does not punish symbol arbitrariness.

### P02 — Partial-equivalence oracle

Knows when source/target category systems only partially overlap and correctly emits `PARTIAL_OVERLAP` or `NO_FAITHFUL_EQUIVALENT`.

Purpose:

- validate ontology-mismatch scoring.

### P03 — Calibrated uncertain oracle

Receives intentionally ambiguous evidence and reports the correct distribution/unknown state.

Purpose:

- validate calibration and ambiguity-preservation metrics.

## Harness acceptance matrix

Before R1 candidate evaluation, freeze a matrix:

`control -> tests expected PASS / FAIL / NOT_APPLICABLE`

The harness qualifies only if observed control behavior matches the preregistered matrix within statistical tolerance.

A control that unexpectedly passes a test is treated as an evaluator defect or a threat-model discovery, not silently ignored.

## Adversarial evolution rule

When a new shortcut is discovered:

1. freeze the failing candidate evidence;
2. describe the shortcut independently of the candidate implementation where possible;
3. add a new negative control reproducing the shortcut;
4. repair evaluator coverage;
5. rerun harness qualification;
6. do not retroactively treat old certificates as covering the new threat.

Grounding certificates therefore carry a negative-control-suite version.
