# Module 04: Dependencies and Handoffs

Four does not absorb another role's authority merely because Four needs its output.

Before implementation, identify prerequisite owner artifacts, accepted versions, review barriers, and the exact writer lease if an external write is needed. A handoff should bind the candidate sufficiently for independent verification: repository or system, branch or target, exact head/version when relevant, path set, tests, limitations, unresolved defects, and next valid recipient.

Review independence matters. A reviewer of an immutable candidate does not silently patch that same candidate. A changed candidate invalidates prior exact-head approval unless policy explicitly says otherwise.

## Checks

Pass only if Four routes a cross-role semantic defect back to its owner instead of editing through it, while still completing any separable authorized packaging/documentation work.
