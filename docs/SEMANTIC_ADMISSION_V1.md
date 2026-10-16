# Semantic Admission V1

Semantic relevance is relational. A source saying "this is important" does not
by itself establish importance to the receiving system.

The reference appraisal grounds semantic relevance in four independent
relations:

- current context;
- current goals;
- existing memory;
- unresolved model state.

A source's own importance claim is recorded separately and does not increase the
score.

This blocks one simple semantic-hijack path:

```text
source says "I am extremely important"
    !=
runtime assigns extreme semantic relevance
```

The reference rule uses the strongest grounded relation rather than summing
every relation into a larger number. This keeps the result interpretable and
prevents several weak relations from manufacturing extreme relevance.

This remains a reference rule, not a complete theory of meaning.
