# MESO-CRCT Semantic Contract V1

Purpose: stop overloaded words from silently becoming architecture.

## Rule

No design, code, test, or downstream integration may use the naked term **salience** where the kind of salience materially affects behavior.

## Operational vocabulary

| Term | Operational meaning | Must not be treated as |
|---|---|---|
| perceptual salience | bottom-up conspicuity in input | meaning, reward, desire |
| semantic relevance | relevance due to meaning/context/model goals | pleasure, truth, permission |
| motivational salience | significance that biases action readiness | positive reward only |
| incentive salience | cue-triggered attraction / wanting toward an outcome | liking, learning, truth |
| epistemic value | expected learning progress / information value | pleasure, external reward |
| attentional priority | current allocation of processing resources | an intrinsic property of the stimulus |
| hedonic valence | bounded pleasantness/unpleasantness channel | importance, urgency, correctness |
| reward | a signal/event used to shape selection or learning | pleasure by definition |
| prediction error | difference between expected and obtained outcome | hedonic valence |
| value | context-dependent evaluation for a particular consumer | universal goodness |
| relevance | relation to a current question/model/goal | salience by itself |
| meaning | semantic/relational structure represented by the system | reward or motivation |
| novelty | departure from expectation/familiarity | usefulness or desirability |
| satiation | reduction of acquisition pressure after repeated/consummatory gain | punishment |
| hazard | estimated danger/damage | suffering |
| avoidance | protective action urgency | negative pleasure |

## Semantic invariants

1. `high_semantic_relevance != high_pleasure`
2. `high_incentive_salience != high_hedonic_impact`
3. `high_attention != high_desire`
4. `high_prediction_error != high_importance`
5. `high_hazard != deep_negative_valence`
6. `reward_signal != phenomenology`
7. `meaningful != true`
8. `salient != authorized`

## Why this matters

The same word is used differently across neuroscience, psychology, computer vision, machine learning, linguistics, economics, and ordinary speech. MESO-CRCT therefore treats semantics as part of the executable contract rather than a documentation nicety.

If a future module introduces a new meaning of one of these terms, it must either:

- map explicitly onto an existing operational term; or
- introduce a new typed term with a stated non-equivalence boundary.
