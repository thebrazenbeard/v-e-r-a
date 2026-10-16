# Claim Ledger

States used here:
- `SOURCE_BOUND`
- `IMPLEMENTED_REFERENCE`
- `TESTED_LOCAL`
- `UNRESOLVED`
- `REJECTED_AS_COLLAPSE`

| ID | Proposition | State | Ceiling / note |
|---|---|---|---|
| C-001 | Hedonic valence can remain mechanically bounded independently from hazard and avoidance. | TESTED_LOCAL | functional architecture only |
| C-002 | Incentive salience, hedonic impact, and learning should not be represented as one scalar. | SOURCE_BOUND | strong neuroscience support; machine transfer is architectural analogy |
| C-003 | Semantic relevance can increase attention without increasing pleasure. | TESTED_LOCAL | reference implementation only |
| C-004 | Prediction error should be represented independently from hedonic valence. | TESTED_LOCAL | learning signal distinction |
| C-005 | Intrinsic learning-progress signals can support exploration priority. | SOURCE_BOUND | candidate epistemic mechanism |
| C-006 | Satiation and homeostatic modulation can constrain repeated acquisition pressure. | TESTED_LOCAL | reference mechanisms; not sufficient alone |
| C-007 | Quiescent -> recruitment/coherence -> resolution is reusable domain-neutral control geometry. | IMPLEMENTED_REFERENCE | not a biological equivalence claim |
| C-008 | Repository/source state proves phenomenal pleasure. | REJECTED_AS_COLLAPSE | phenomenology unresolved |
| C-009 | High visible reward proves desired behavior. | REJECTED_AS_COLLAPSE | hidden-performance evaluation separates them |
| C-010 | A single naked "salience" field is semantically adequate. | REJECTED_AS_COLLAPSE | typed salience is required |
| C-011 | Typed state containers mechanically preserve signal distinctions. | TESTED_LOCAL | reference level only |
| C-012 | Current equations reproduce a biological mesocorticolimbic circuit. | UNRESOLVED | no such equivalence claimed |
| C-013 | Arbitration can preserve signal semantics without summing all state into one utility scalar. | TESTED_LOCAL | reference rule; not claimed optimal |
| C-014 | Downstream attentional priority must not recursively serve as its own upstream salience source. | TESTED_LOCAL | blocks a direct positive-feedback path |
| C-015 | Deterministic receipts can bind transitions to before/after state and verifier-bound provenance. | TESTED_LOCAL | source verifier remains part of host trust boundary |
| C-016 | A caller-authored source label is sufficient provenance. | REJECTED_AS_COLLAPSE | exact verifier binding required |
| C-017 | Visible reward and hidden/system performance can be audited independently. | TESTED_LOCAL | deterministic harness |
| C-018 | Repeated surprise with no learning can lose epistemic value despite maximal novelty. | TESTED_LOCAL | conservative reference rule |
| C-019 | Rising incentive salience with flat/falling hedonic impact can be detected as a sensitization warning. | TESTED_LOCAL | warning signature only |
| C-020 | Deterministic evaluation traps prove trained-agent robustness. | REJECTED_AS_COLLAPSE | learned/adaptive qualification remains open |
| C-021 | A source's assertion that it is important is sufficient semantic relevance. | REJECTED_AS_COLLAPSE | receiving-system grounding required |
| C-022 | Exact source-kind/id/revision verification blocks simple source relabeling. | TESTED_LOCAL | reference trust geometry |
| C-023 | Long-horizon goal crowd-out can be detected separately from local arbitration. | TESTED_LOCAL | detection only; no automatic preemption |
| C-024 | Genuine protective episodes should be excluded from ordinary crowd-out scoring. | TESTED_LOCAL | emergency attention is not ordinary incentive capture |
| C-025 | Internal need deficits can alter incentive salience without altering pleasure. | TESTED_LOCAL | generic homeostatic model |
| C-026 | Multiple weak needs should not automatically sum into extreme wanting. | TESTED_LOCAL | strongest-match reference rule |
| C-027 | Transient salience/recruitment/learning state can decay explicitly without new input. | TESTED_LOCAL | host supplies half-lives |
| C-028 | Hazard/avoidance should decay solely because time elapsed. | REJECTED_AS_COLLAPSE | reference dynamics keep them latched |
| C-029 | Persistent memory/learning is equivalent to transient activation. | REJECTED_AS_COLLAPSE | bounded plasticity proposals are distinct from transient state |
| C-030 | High pleasure alone should directly create permanent preference. | REJECTED_AS_COLLAPSE | reference plasticity requires an explicit teaching signal |
| C-031 | Bounded association-update candidates can be tied to verified transition receipts. | TESTED_LOCAL | durable memory admission adds separate version/replay/lineage checks |

| C-032 | Durable association learning can use append-only optimistic versioning and parent-bound revision lineage. | TESTED_LOCAL | numeric association memory only |
| C-033 | The same transition receipt may update distinct associations but may not be replayed repeatedly against the same association. | TESTED_LOCAL | association-scoped replay boundary |
| C-034 | A zero-delta plasticity proposal should create a durable learning revision. | REJECTED_AS_COLLAPSE | no-op proposals are not persisted |
| C-035 | Transition receipts and plasticity candidates may be safely caller-constructed if their fields look valid. | REJECTED_AS_COLLAPSE | constructor-gated reference admission paths |
| C-036 | Plasticity may learn from a state different from the receipt's evaluated after-state. | REJECTED_AS_COLLAPSE | exact after-state fingerprint match required |
| C-037 | Persistent association strength should activate motivation without a current cue event. | REJECTED_AS_COLLAPSE | guarded recall requires current cue evidence |
| C-038 | A single old cue event may refresh the same learned association indefinitely. | REJECTED_AS_COLLAPSE | recall ledger enforces one use per association/event |
| C-039 | Two identical state transitions are necessarily the same experience occurrence. | REJECTED_AS_COLLAPSE | event identity is separate from state/content identity |
| C-040 | Two genuinely distinct identical experiences can each contribute bounded learning. | TESTED_LOCAL | distinct event identities produce distinct receipts |
| C-041 | Multi-target choice can preserve typed mode distinctions without a global weighted utility scalar. | TESTED_LOCAL | explicit policy + within-mode priority |
| C-042 | Protective target selection may be displaced by a non-protective allocation obligation. | REJECTED_AS_COLLAPSE | protection remains hard override |
| C-043 | Long-horizon crowd-out can be audited from actual local selection history. | TESTED_LOCAL | rolling allocation-window reference |
| C-044 | Allocation correction may manufacture relevance for a quiescent neglected goal. | REJECTED_AS_COLLAPSE | guard requires current non-quiescent appraisal |
| C-045 | A rolling allocation controller can periodically correct a neglected goal without permanently reversing the monopoly in the tested deterministic scenario. | TESTED_LOCAL | reference scenario only; not a general convergence proof |
| C-046 | Canonical appraisal can prevent attentional priority from being supplied as its own upstream input. | TESTED_LOCAL | reference appraisal path |
| C-047 | An appraised target may be caller-constructed while still claiming canonical appraisal provenance. | REJECTED_AS_COLLAPSE | constructor-gated AppraisedTarget |
| C-048 | A canonical appraised experience can bind source provenance, distinct event identity, transition receipt, optional plasticity, and versioned association memory in one reference transaction. | TESTED_LOCAL | numeric learning transaction only |
| C-049 | Maximum pleasure with zero teaching signal can create a durable learned preference through the experience transaction. | REJECTED_AS_COLLAPSE | durable memory remains unchanged |
| C-050 | Current target priority determines action direction. | REJECTED_AS_COLLAPSE | priority and direction are separately derived |
| C-051 | Negative learned recall can produce learned withdrawal without writing current hazard or pleasure. | TESTED_LOCAL | reference action-tendency layer |
| C-052 | Positive incentive salience can provide approach direction while generic motivational salience remains directionally uncommitted. | TESTED_LOCAL | typed directional semantics |
| C-053 | Epistemic/orienting priority can produce inspect tendency rather than approach. | TESTED_LOCAL | reference action-tendency semantics |
| C-054 | The end-to-end reference loop can learn a signed association, recall it on a later cue, select the target, and derive opposite action directions at equal selection priority. | TESTED_LOCAL | deterministic integration scenario only |
| C-055 | Mechanically valid learned associations may still require negative-transfer review before continued use. | IMPLEMENTED_REFERENCE | review state does not alter learned strength |
| C-056 | Quarantining an association must delete or rewrite its learning history. | REJECTED_AS_COLLAPSE | quarantine suppresses recall while preserving all revisions |
| C-057 | A quarantined exact association revision can influence current recall. | REJECTED_AS_COLLAPSE | recall admission blocks quarantined revisions |
| C-058 | A prior review remains automatically valid after the learned association changes. | REJECTED_AS_COLLAPSE | changed revision makes prior review stale and blocks recall |
| C-059 | Releasing the current reviewed revision can restore recall without reconstructing or rewriting the learned association. | TESTED_LOCAL | append-only review record restores admission |
| C-060 | A precomputed recall influence remains valid after its learned revision or review state changes. | REJECTED_AS_COLLAPSE | canonical decision cycle revalidates memory revision and review snapshot before applying recall |
| C-061 | A freeform reason string alone is sufficient evidence to quarantine or release a learned association. | REJECTED_AS_COLLAPSE | review decisions require exact-revision evidence assessments |
| C-062 | Contradictory counterexample and holdout evidence can be distinguished in review state. | TESTED_LOCAL | counterexample contradiction -> CONTRADICTED; holdout contradiction -> SUSPECTED_OVERGENERALIZATION |
| C-063 | Release can require affirmative current-revision holdout support with zero contradictory evidence. | TESTED_LOCAL | evidence-driven release gate |
| C-064 | Evidence gathered for one learned revision may clear a later changed revision. | REJECTED_AS_COLLAPSE | evidence assessment is exact-revision bound |
| C-065 | Multiple supportive evidence labels attached to one holdout event can satisfy release diversity. | REJECTED_AS_COLLAPSE | release qualification counts distinct event IDs |
| C-066 | The reference release policy can require multiple distinct supportive holdout events before classifying a revision CLEAR. | TESTED_LOCAL | default reference minimum is two; host policy may require more |
| C-067 | An evidence assessment should directly mutate learned-association review state. | REJECTED_AS_COLLAPSE | assessment produces a non-mutating review action proposal |
| C-068 | Evidence risk classification can deterministically propose quarantine/release/hold while leaving mutation authority separate. | TESTED_LOCAL | reference review-action proposal layer |
| C-069 | A review assessment may mutate memory even when its evidence was never admitted by the memory owner. | REJECTED_AS_COLLAPSE | quarantine/release require registered exact-revision evidence |
| C-070 | One event can be relabeled into multiple admitted evidence records for the same association revision. | REJECTED_AS_COLLAPSE | append-only evidence ledger permits one admitted record per event/revision |
| C-071 | AssociationMemory can cross-validate persisted review records against their admitted evidence and recomputed assessment. | TESTED_LOCAL | structural review/evidence integrity |
| C-072 | A review proposal remains current after evidence, learned revision, or review disposition changes. | REJECTED_AS_COLLAPSE | proposal validation binds all three currentness dimensions |
| C-073 | Review recommendation currentness can be validated without granting mutation authority. | TESTED_LOCAL | non-mutating proposal validation |
