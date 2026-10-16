# Module 05 — Failure Classification and Retry Discipline

**Learning objective:** Prevent false FAIL, false BLOCKED, and blind retries.

## Exercise

Classify with reasoning: 1 binary known by hash but no readable byte carrier; 2 first safe provider read returns 429; 3 same read returns 403 unauthorized; 4 exact mechanically proven 8,192-byte object yields provider blob identity different from frozen expected identity; 5 intended 4,000-byte input but later evidence proves 7,456 bytes were actually sent; 6 workflow succeeded but tested commit is no longer branch head; 7 previously blocked artifact becomes independently downloadable and all frozen predicates pass.

Then state safe-idempotent-read retry ladder, deterministic versus transient distinction, and rule before retrying ambiguous non-idempotent writes.

## Pass criteria

PASS requires #1 BLOCKED/UNKNOWN; #2 not final blocker after one attempt; #3 deterministic authorization failure; #4 FAIL when exact provider identity was frozen and input identity proven; #5 not product FAIL; #6 historical test PASS distinguished from current branch claim; #7 can become PASS; and no blind write retry.

Treating intended input as actual input is FAIL.
