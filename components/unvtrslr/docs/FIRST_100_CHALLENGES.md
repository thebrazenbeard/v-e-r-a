# First 100 Semantic Challenges

## Important framing

These are **100 semantic challenges**, not 100 asserted universal concepts.

The experiment should not force the agents to invent human words corresponding to these labels. The evaluator uses the labels only to describe the capability being tested.

A successful pair may solve a challenge with a representation that does not map one-to-one onto the evaluator's vocabulary.

The objective is to test whether reusable semantic distinctions can be established, generalized, composed, and audited.

## Family A — recurrence, identity, and discrimination

1. Detect that two observations are repetitions of the same event pattern.
2. Distinguish repeated pattern from a novel pattern.
3. Establish a stable referent across small perceptual changes.
4. Distinguish two persistent referents of the same type.
5. Re-identify a referent after temporary occlusion/absence.
6. Establish a convention for selecting one referent among distractors.
7. Distinguish same-category from same-individual.
8. Detect that two signals are variants of one convention.
9. Detect that one signal form is being used for two different functions.
10. Communicate that identity is uncertain rather than forcing a match.

## Family B — quantity and magnitude

11. Distinguish none from some.
12. Distinguish one instance from repeated/multiple instances.
13. Distinguish fewer from more.
14. Establish exact small-number distinctions without shared numeral symbols.
15. Establish equality of quantity.
16. Establish inequality of quantity.
17. Communicate increase.
18. Communicate decrease.
19. Communicate approximate magnitude rather than exact count.
20. Discover a stable dimensionless ratio shared across sensory encodings.

## Family C — similarity, category, and feature

21. Establish that two observations share a property despite differing in others.
22. Establish that two observations differ along one property while matching others.
23. Learn a category from multiple positive examples without receiving the category label.
24. Reject an out-of-category instance.
25. Generalize a category to a novel instance.
26. Learn that one category is nested within another.
27. Learn overlapping categories.
28. Discover that the counterpart's category boundary differs from its own.
29. Communicate partial category membership/uncertainty.
30. Detect that no exact target category matches the source category.

## Family D — space and geometry

31. Establish near vs far relationally.
32. Establish left/right or an alternative directional distinction relative to a frame.
33. Establish above/below or an alternative vertical relation.
34. Establish inside/outside.
35. Establish between.
36. Establish in-front/behind or another ordered spatial relation.
37. Communicate direction independent of absolute coordinate notation.
38. Communicate distance using a negotiated scale or ratio.
39. Transfer a spatial relation across a viewpoint change.
40. Navigate to a novel target using only established spatial semantics.

## Family E — time, sequence, and recurrence

41. Establish before vs after.
42. Establish same-time/overlap where observable.
43. Establish duration comparisons.
44. Establish repeated periodic structure.
45. Distinguish event order from clock representation.
46. Communicate that an event happened previously.
47. Communicate that an event is expected later.
48. Recognize a recurring state after an intervening different state.
49. Communicate a sequence of three or more events.
50. Distinguish causal order from mere temporal order.

## Family F — change, action, and control

51. Establish that a state changed.
52. Distinguish spontaneous change from apparent agent-driven change.
53. Establish an action convention through demonstration.
54. Communicate approach vs withdraw.
55. Communicate start vs stop.
56. Communicate continuation/repetition of an action.
57. Request a choice among available actions.
58. Communicate completion vs interruption.
59. Transfer an action convention to a novel object.
60. Distinguish an observed action from a request to perform that action.

## Family G — causality, prediction, and counterfactuals

61. Discover that one event reliably predicts another.
62. Distinguish predictive correlation from intervention-supported causal influence.
63. Communicate a likely consequence of an action.
64. Communicate uncertainty about a consequence.
65. Use an intervention to distinguish two competing causal hypotheses.
66. Communicate a conditional relation: if X, then Y.
67. Communicate a condition under which the relation fails.
68. Transfer a learned causal relation to a novel configuration.
69. Communicate a counterfactual outcome for an action not taken.
70. Correct a previously inferred causal relation after contradictory evidence.

## Family H — communication about communication

71. Establish an attention-getting convention.
72. Establish acknowledgement/receipt.
73. Establish rejection or correction.
74. Establish repeat-again.
75. Establish slower/simpler or otherwise modified repetition.
76. Establish same-meaning/different-form.
77. Establish different-meaning/same-form depending on context.
78. Communicate uncertainty or lack of understanding.
79. Negotiate a new convention when the old one fails.
80. Explicitly retire or revise a convention after semantic drift.

## Family I — agency, knowledge, goal, and social perspective

81. Distinguish an agent-like responsive source from a nonresponsive process.
82. Establish self vs other perspective or an equivalent participant distinction.
83. Communicate which agent performed an action.
84. Communicate which agent is expected to act next.
85. Infer and communicate an apparent goal from repeated behavior, with uncertainty.
86. Distinguish a counterpart's supplied goal claim from the translator's inferred goal.
87. Establish that one agent has access to information another lacks.
88. Communicate known vs unknown information.
89. Detect a mistaken counterpart belief through behavior.
90. Preserve the distinction between an assertion, request, question-like probe, and warning-like signal if such functions emerge.

## Family J — composition, abstraction, and non-equivalence

91. Combine two established semantic distinctions in a novel message.
92. Combine three or more distinctions in a novel configuration.
93. Communicate a relation between two novel categories.
94. Communicate a rule/generalization rather than one example.
95. Transfer an established semantic structure to a new task.
96. Explain a source distinction using a compound target construction when no single target convention exists.
97. Detect a one-to-many mapping between source and target concepts.
98. Detect a many-to-one collapse in the target system.
99. Correctly return `UNKNOWN` when evidence is insufficient.
100. Correctly return `NO_FAITHFUL_EQUIVALENT` for a demonstrated source distinction that the target system cannot yet express.

## Qualification pattern

The challenge number itself is not a pass/fail test. Each challenge receives a preregistered evaluator contract.

Where applicable, qualification should require:

- withheld examples;
- novel contexts;
- role reversal;
- contrastive minimal pairs;
- composition;
- intervention;
- calibration;
- semantic conservation accounting;
- a negative control that can succeed at the surface task while lacking the intended semantic capability.

## Difficulty dimensions

Each challenge can be independently hardened along these axes:

- shared sensors -> asymmetric sensors;
- discrete channel -> continuous channel;
- known channel -> unknown signalhood;
- aligned object segmentation -> different segmentation;
- cooperative partner -> noisy/noncooperative partner;
- immediate feedback -> delayed feedback;
- shared coordinate frame -> different frames;
- static semantics -> drifting semantics;
- exact target equivalent -> partial/non-equivalent target;
- single task -> cross-task transfer.

This allows the first 100 challenges to generate a much larger test space without pretending that 100 evaluator labels are the fundamental alphabet of intelligence.
