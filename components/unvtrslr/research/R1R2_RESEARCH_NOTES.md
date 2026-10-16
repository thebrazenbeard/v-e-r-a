# R1/R2 Research Notes — Representation and Evaluation

Status: `RESEARCH_SYNTHESIS / 2026-09-07`

This note records outside research that materially changed or constrained the R1/R2 design. It is not itself a qualification result.

## 1. Predictive state representations motivate a genuinely non-symbolic rival

Littman, Sutton, and Singh's predictive-state-representation work shows that the state of a dynamical system can be represented through multi-step, action-conditional predictions of future observations rather than a hidden-state ontology.

Project consequence:

- UNVTRSLR should not assume that semantic mediation requires explicit object/event/relation graphs;
- PIS is included as a serious rival whose semantics are grounded in predictive/interventional consequences;
- if PIS passes the same semantic-transfer tests with less ontology, richer substrates must justify their complexity.

Boundary:

Predictive state representation research is about dynamical-state representation, not proof of semantic understanding. UNVTRSLR adds communication, grounding, cross-task transfer, non-equivalence, and adversarial private-code tests.

## 2. Communication metrics can look positive when communication has no causal effect

Lowe et al. show that intuitive emergent-communication measures can be misleading: messages can correlate with actions while not affecting the environment or other agent.

Project consequence:

- R2 separates signaling correlation from causal listening;
- E01 message ablation and E02 direct message intervention are critical gates;
- N02 is a required correlated-but-noncausal control.

## 3. Successful coordination can coexist with nonconceptual internal alignment

Bouchacourt & Baroni report agents that communicate successfully while their aligned visual representations fail to capture the conceptual properties a human evaluator might expect.

Project consequence:

- task reward cannot establish semantics;
- evaluator interventions must ask what external distinctions signals track;
- private/shared latent alignment is an explicit threat model rather than positive evidence.

## 4. Unsupervised representation recovery is not uniquely identifiable without inductive bias

Locatello et al. show that unsupervised disentanglement is fundamentally impossible without inductive biases on the model and data, and that apparent disentanglement properties can be difficult to identify without supervision.

Project consequence:

- UNVTRSLR must not claim that a representation can discover a unique true ontology from observations alone;
- R1 records each substrate's inductive biases explicitly;
- R2 evaluates operational invariants under interventions rather than uniqueness of internal coordinates;
- internal symbol permutations and other consequence-preserving transformations are treated as equivalent within tested scope.

This is one reason the project uses `GROUNDED_WITHIN_TESTED_SCOPE`, not `UNIVERSALLY_GROUNDED`.

## 5. Causal influence is a stronger communication criterion than mutual information alone

Jaques et al. use counterfactual reasoning to measure an agent's causal influence on another agent's behavior.

Project consequence:

- R2 uses controlled signal interventions;
- a signal must not merely predict listener actions but must causally influence them when the claimed semantics require listening;
- causal influence is still not sufficient by itself, because an action-plan code can causally control a receiver without representing reusable world semantics.

Thus R2 combines causal influence with cross-task, role, partner, and world-factor tests.

## 6. Compositionality and generalization are separable

Chaabouni et al. find that compositionality is not necessarily correlated with generalization in emergent languages, while compositional languages may be more readily transmitted to new learners.

Project consequence:

- R2 does not use one compositionality score as a semantic certificate;
- E06 compositional recombination and E09 third-party acquisition are separate dimensions;
- a system can generalize without earning a claim of compositional semantic structure.

Recent concept-best-matching work also reinforces that ordinary proxy metrics do not directly expose the correspondence between emergent symbols and evaluator concepts.

Project boundary:

UNVTRSLR does not require an emergent code to map neatly onto English concepts. External reconstructions are diagnostic and must remain grounded in evaluator interventions rather than English similarity.

## 7. The strongest adversary is not arbitrary notation; it is task-bound hidden common ground

A code can use arbitrary symbols and still be a genuine convention. Therefore an evaluator that rewards human-readable symbols or penalizes opaque notation would be anthropocentric.

R2 instead asks whether the convention survives removal of hidden common ground:

- fresh world identities;
- coordinate changes;
- different tasks;
- role reversal;
- independent partners;
- different sensors;
- direct world interventions;
- ontology mismatch.

If the convention survives those tests, its arbitrariness is not evidence against grounding.

## 8. Operational semantics is necessarily scope-bounded

No finite test suite can distinguish two hypotheses that agree on every tested observation and intervention but differ only outside the test distribution.

Project consequence:

- equivalence is always scoped;
- every grounding certificate binds the exact world/intervention family;
- new adversarial worlds can invalidate or narrow old certificates;
- discovering a new shortcut creates a new negative control rather than rewriting history.

## Sources added for R1/R2

### Littman, M. L., Sutton, R. S., & Singh, S. (2001/2002). “Predictive Representations of State.” NeurIPS 14.

https://proceedings.neurips.cc/paper_files/paper/2001/hash/1e4d36177d71bbb3558e43af9577d70e-Abstract.html

### Lowe, R., Foerster, J., Boureau, Y-L., Pineau, J., & Dauphin, Y. (2019). “On the Pitfalls of Measuring Emergent Communication.”

https://arxiv.org/abs/1903.05168

### Jaques, N., Lazaridou, A., Hughes, E., Gulcehre, C., Ortega, P., Strouse, D., Leibo, J. Z., & de Freitas, N. (2019). “Social Influence as Intrinsic Motivation for Multi-Agent Deep Reinforcement Learning.” ICML 2019.

https://proceedings.mlr.press/v97/jaques19a.html

### Locatello, F. et al. (2019). “Challenging Common Assumptions in the Unsupervised Learning of Disentangled Representations.” ICML 2019.

https://proceedings.mlr.press/v97/locatello19a.html

### Carmeli, B., Belinkov, Y., & Meir, R. (2024). “Concept-Best-Matching: Evaluating Compositionality In Emergent Communication.” Findings of ACL 2024.

https://aclanthology.org/2024.findings-acl.189/

## Current research conclusion

The literature supports the need for the R1/R2 split:

- representation choices carry inductive bias and should compete;
- task success and correlation are too weak;
- causal use is necessary but still not sufficient;
- transfer across tasks, partners, roles, and sensor regimes attacks task-private code;
- no finite evaluator provides ontology-independent metaphysical proof;
- a scoped, adversarial operational certificate is the defensible target.
