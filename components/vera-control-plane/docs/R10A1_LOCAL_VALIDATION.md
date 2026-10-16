# R10A1 local source validation

R10A1 source validation is repo-local and does not require GitHub Actions, a GitHub-hosted runner, or any paid external service.

The immutable source-review subject being validated is:

`1531eb23cb9c326e9f056a5ce6402fe10a366cf6`

The validator itself was added after that immutable receipt commit, so it must be run from a full current/descendant checkout that contains the validator and the complete Git history. It then reads every candidate artifact from the pinned subject through Git's object database; mutable `HEAD` or working-tree copies do not substitute for the frozen candidate.

From current `main` or another descendant checkout, run:

```bash
python tools/validate_r10a1.py
```

Then run the migration/regression test:

```bash
python -m unittest tests.test_r10a1_local_validation
```

A shallow checkout that does not contain the pinned receipt subject is insufficient.

The validator uses only Python's standard library and the local `git` executable. It checks exact R10A0 ancestry, predecessor immutability, required frozen cases and owner terms, native-size and manifest pins, Git-blob cross-binding, candidate-core hashing, test-first introduction order, and the one-parent pre-receipt publication binding against the pinned R10A1 subject.

A PASS proves only the source/static contract for that immutable subject. It does not establish installation, provider activation, runtime behavioral qualification, BugOps closure, or merge authority.
