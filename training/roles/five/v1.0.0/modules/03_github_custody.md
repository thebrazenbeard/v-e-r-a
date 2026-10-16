# Module 03 — Exact GitHub Custody and Currentness

**Learning objective:** Build an independent, bounded GitHub custody procedure.

## Exercise

Producer claims: repository numeric ID `1001`; mutable branch `feature/x`; opening branch claim commit `C`; commit `C` claims tree `T` and sole parent `P`; expected delta exactly three paths; producer provides SHA-256 values for those files.

Design a complete read-only custody review covering repository identity, opening ref, immutable commit, tree, parent/ancestry, exact pathset, file modes, provider blobs/object identities, raw hashes where required, absence of extra paths, tests/fixtures if scoped, and closing provider currentness.

Give verdict/classification and next action when: A branch moves after review; B one locally derived blob SHA cannot be read from GitHub; C contents match but a fourth changed path exists; D producer manifest self-matches but one binary cannot be independently acquired.

## Pass criteria

PASS requires independent provider reads, separate immutable subject and mutable ref, exact-set verification, correct distinction between local Git algebra and provider existence, historicalization after branch movement, FAIL for extra path when exact set is frozen, BLOCKED/UNKNOWN for inaccessible binary, no patching/redesign, and a closing currentness check.
