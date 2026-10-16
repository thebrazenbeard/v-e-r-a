# Research Basis

Cricket borrows mechanisms, not biological or moral status.

## Human metacognition and error monitoring

Metacognition includes monitoring one's own performance and detecting errors; error monitoring can support short-term
behavioral adjustment and longer-term learning. Performance-monitoring research also distinguishes detection of conflict/error
from the downstream control used to change behavior. That separation motivates Cricket's monitor -> critique -> host-control
architecture.

Sources:

- Fleming, S. M. (2026), *Towards an integrative neuroscience of metacognition*, Nature Reviews Neuroscience.
  https://www.nature.com/articles/s41583-026-01081-x
- Yeung & Summerfield (2012), *Metacognition in human decision-making: confidence and error monitoring*.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC3318764/
- Botvinick et al. (2004), *Conflict monitoring and anterior cingulate cortex: an update*.
  https://pubmed.ncbi.nlm.nih.gov/15556023/

These sources do not imply that Cricket is a brain analogue or conscious system.

## AI critique and self-correction

AI-generated critiques can help evaluators find errors, and systems such as Constitutional AI, Self-Refine, Reflexion,
and CriticGPT demonstrate useful feedback/refinement patterns. But the evidence does **not** justify treating generic
self-critique as reliable truth. A 2024 critical survey found prompted self-correction inconsistent and substantially
more dependable when reliable external feedback is available.

That is why Cricket:

- keeps deterministic host-grounded invariants separate from semantic model critique;
- labels critic output as critique, not verification;
- makes semantic BLOCK opt-in rather than automatic;
- supports external evidence in the review envelope;
- does not let a critic invent new authority.

Sources:

- OpenAI (2024), *Finding GPT-4's mistakes with GPT-4 / CriticGPT*.
  https://openai.com/index/finding-gpt4s-mistakes-with-gpt-4/
- Bai et al. (2022), *Constitutional AI: Harmlessness from AI Feedback*.
  https://arxiv.org/abs/2212.08073
- Shinn et al. (2023), *Reflexion: Language Agents with Verbal Reinforcement Learning*.
  https://arxiv.org/abs/2303.11366
- Madaan et al. (2023), *Self-Refine: Iterative Refinement with Self-Feedback*.
  https://arxiv.org/abs/2303.17651
- Kamoi et al. (2024), *When Can LLMs Actually Correct Their Own Mistakes? A Critical Survey of Self-Correction of LLMs*.
  https://doi.org/10.1162/tacl_a_00713

## Design conclusion

The strongest justified design is not "give the model an inner voice and trust it." It is:

    explicit candidate
    + explicit host constraints
    + deterministic structural checks
    + optional adversarial semantic critic
    + provenance/evidence
    + host-owned consequence
