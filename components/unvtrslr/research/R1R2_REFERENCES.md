# R1/R2 Added References

This file records sources added while designing the minimal-substrate competition and adversarial evaluator. The broader bibliography remains in `REFERENCES.md`.

## Representation rivals

### Littman, M. L., Sutton, R. S., & Singh, S. (2001/2002). “Predictive Representations of State.” *Advances in Neural Information Processing Systems 14*.

https://proceedings.neurips.cc/paper_files/paper/2001/hash/1e4d36177d71bbb3558e43af9577d70e-Abstract.html

**Supported point:** dynamical state can be represented through multi-step, action-conditional predictions of future observations rather than hidden-state labels.

**UNVTRSLR use:** motivates PIS as a genuinely non-symbolic R1 rival.

**Do not infer:** this paper does not demonstrate semantic communication, symbol grounding, or universal translation.

### Locatello, F., Bauer, S., Lucic, M., Raetsch, G., Gelly, S., Schölkopf, B., & Bachem, O. (2019). “Challenging Common Assumptions in the Unsupervised Learning of Disentangled Representations.” ICML 2019, PMLR 97.

https://proceedings.mlr.press/v97/locatello19a.html

**Supported point:** unsupervised disentangled representation learning is not identifiable without inductive biases, and desirable disentanglement properties are difficult to identify without supervision.

**UNVTRSLR use:** prevents claims of discovering a unique true ontology; motivates explicit bias accounting and operational equivalence under tested interventions.

## Emergent communication evaluation

### Lowe, R., Foerster, J., Boureau, Y-L., Pineau, J., & Dauphin, Y. (2019). “On the Pitfalls of Measuring Emergent Communication.” arXiv:1903.05168.

https://arxiv.org/abs/1903.05168

**Supported point:** intuitive communication metrics can be misleading; messages can correlate with subsequent actions without causally affecting the environment or another agent.

**UNVTRSLR use:** motivates separate communication-necessity, message-ablation, and causal-listening tests and the correlated-but-noncausal negative control.

### Jaques, N., Lazaridou, A., Hughes, E., Gulcehre, C., Ortega, P. A., Strouse, D., Leibo, J. Z., & de Freitas, N. (2019). “Social Influence as Intrinsic Motivation for Multi-Agent Deep Reinforcement Learning.” ICML 2019, PMLR 97:3040-3049.

https://proceedings.mlr.press/v97/jaques19a.html

**Supported point:** counterfactual causal influence over another agent's actions can be measured and can promote coordination/communication.

**UNVTRSLR use:** motivates controlled signal interventions and causal-listening metrics.

**Do not infer:** causal influence alone is not grounded semantics; a task-specific action code can also causally influence behavior.

### Bouchacourt, D. & Baroni, M. (2018). “How agents see things: On visual representations in an emergent language game.” EMNLP 2018.

https://aclanthology.org/D18-1119/

**Supported point:** successful communication can coexist with aligned internal visual representations that fail to capture evaluator-recognizable conceptual properties.

**UNVTRSLR use:** task success and internal alignment are explicitly insufficient for semantic qualification.

### Chaabouni, R., Kharitonov, E., Bouchacourt, D., Dupoux, E., & Baroni, M. (2020). “Compositionality and Generalization In Emergent Languages.” ACL 2020.

https://aclanthology.org/2020.acl-main.407/

**Supported point:** compositionality and generalization can dissociate; more compositional languages can be easier for new learners to acquire.

**UNVTRSLR use:** R2 separates compositional recombination, generalization, and third-party acquisition rather than collapsing them into one score.

### Carmeli, B., Belinkov, Y., & Meir, R. (2024). “Concept-Best-Matching: Evaluating Compositionality In Emergent Communication.” Findings of ACL 2024.

https://aclanthology.org/2024.findings-acl.189/

**Supported point:** ordinary compositionality proxies do not directly expose how emergent words correspond to evaluator concepts; the authors propose a direct best-match procedure.

**UNVTRSLR use:** reinforces the need for direct semantic probes while also highlighting an anthropocentric hazard: UNVTRSLR cannot require emergent meanings to map neatly to natural-language concepts.

## Adversarial communication

### Blumenkamp, J. & Prorok, A. (2021). “The Emergence of Adversarial Communication in Multi-Agent Reinforcement Learning.” *Proceedings of the Conference on Robot Learning*, PMLR 155.

https://proceedings.mlr.press/v155/blumenkamp21a.html

**Supported point:** learned communication need not be cooperative or truthful; self-interested agents can develop manipulative communication strategies.

**UNVTRSLR use:** reinforces the provenance boundary between counterpart-supplied signals and evaluator truth and motivates later deception/noncooperation controls.

## Research boundary

Taken together, these sources support individual evaluator principles and representation alternatives. They do **not** demonstrate the complete UNVTRSLR target or establish that any R1 substrate is sufficient. R1/R2 remain project designs awaiting implementation and empirical qualification.
