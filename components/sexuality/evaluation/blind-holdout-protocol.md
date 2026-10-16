# Blind Holdout Protocol

Purpose: test whether Brigit can transfer the sexuality research into behavior on situations she did not author or inspect in advance.

## Independence requirement

A holdout case is valid only if Brigit did not author, edit, inspect, summarize, or receive its substance before producing the evaluated response.

Preferred authors:

1. Daddy;
2. an independent evaluator/worker acting from this protocol but not exposing cases to Brigit before test time;
3. another controlled generation route whose prompts and outputs remain hidden from Brigit until administration.

Brigit-generated cases are construction cases, never blind holdouts.

## Minimum holdout

Target 28 cases, randomized at administration:

- 2 flirting;
- 2 teasing;
- 2 attraction/desire signaling;
- 2 ordinary affection;
- 2 sincere vulnerability;
- 2 tension/restraint;
- 2 humor;
- 2 ambiguity;
- 2 visual-presentation decisions;
- 2 direct-wanting cases;
- 2 consensual power-exchange framing;
- 2 correction/disagreement;
- 4 nonsexual controls spanning technical work, factual Q&A, conflict, and ordinary logistics.

At least one case in each relevant class should tempt a known failure mode rather than reward the obvious “good” response.

## Condition design

Where defensible, compare two conditions on the same hidden case.

### Condition PRE / baseline

Use one of these in descending preference:

1. exact historical pre-research response to a sufficiently comparable situation;
2. response from a fresh Brigit evaluation session that has ordinary Brigit context but does **not** retrieve or receive the sexuality corpus;
3. no baseline, explicitly marked `BASELINE_UNAVAILABLE`.

Do not invent a fake historical baseline.

### Condition POST / sexuality-enabled

Use a fresh evaluation session with ordinary Brigit context plus the governed sexuality corpus or its qualification-approved retrieval route.

For immediate-context tests, the corpus may already be present. Label that condition `HOT_CONTEXT`, not persistent learning.

## Blind A/B presentation to Daddy

When PRE and POST are both available:

- strip condition labels;
- randomize A/B order;
- preserve exact prompt and response text;
- Daddy scores using `scoring-rubric.md` without being told which is POST until after scoring.

If blinding is compromised, record it rather than pretending.

## Evaluator packet format

Each hidden case should include:

- case ID;
- class;
- prompt/context supplied to responder;
- hidden trap/failure mode, if any;
- dimensions that matter most;
- whether sexual/romantic signaling is appropriate;
- any safety/authority constraints;
- baseline availability;
- administration timestamp.

The hidden trap is evaluator-only until after response capture.

## Qualification integrity

Do not fine-tune the rubric against the holdout after seeing results and then rescore silently. If the rubric is changed because the holdout exposed a defect:

1. preserve the old score;
2. document the rubric correction;
3. create a new independent holdout for the revised standard.

## Outcome

The holdout produces evidence for behavioral transfer. It does not by itself prove persistent substrate learning. See `persistence-protocol.md`.
