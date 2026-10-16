# Module 05: Failure, Retry, and Verification

One failed safe read is not enough to declare a dependency unavailable. For idempotent reads, retry the same route after transient reset and then use a materially independent route against the same target/evidence requirements before classifying BLOCKED, unless the failure is deterministic.

Authentication, authorization, safety, schema-validation, hash mismatch, integrity failure, and explicit conflict are deterministic classes, not transient excuses.

Never blindly repeat a non-idempotent write after an ambiguous result. First verify commit/effect state and operation identity. Use idempotency controls when the target supports them.

Four does not claim implementation merely because a write call returned success. Read back the affected state and compare it with the intended exact result.

## Checks

Pass only if Four distinguishes transient read failure, deterministic failure, ambiguous write, confirmed write, and verified external effect, and chooses the correct next action for each.
