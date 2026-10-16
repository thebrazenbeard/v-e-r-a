# Component source-preview export V1

V-E-R-A is intended as the source/build/qualification scaffold for VeraOS, not its selected runtime. The 44 components/ folders are navigable, **filtered source previews**, not runnable packages and not automatic runtime dependencies.

The original named branch commit, original source tree, original MIRRORED/SANITIZED/PROJECT_SNAPSHOT state, complete omitted paths (with blob IDs and reasons) and the exported subtree are recorded in component-exports.json. Filtered folders MUST NOT be advertised as exact upstream mirrors.

The preview excludes all .vscode/.idea/.devcontainer/.husky entries, nested .github/workflows, executable CI/workspace configs, font binaries (.woff/.woff2/.ttf/.otf/.eot), symlinks and gitlinks. Defender previously flagged workspace tasks and a font-disguised execution path in source mirrors. The excluded bytes remain available in the existing public named source branches. We do NOT read blocked content, bypass antivirus or execute source hooks.

**Hostile review: ACCEPTED.** Path-based filtering is not a malware clearance or a source-closure attestation; malicious payloads can exist in any retained ordinary source file. Do not run package scripts, install dependencies or load binary assets from these folders. A clean clone verifying tree hashes only establishes Git source integrity, not behavioral security.

To check exported folder trees (no source execution): python scripts/verify_safe_components.py --tree HEAD. For **strict original source blob/mode/omission verification**, append --verify-source-objects; the original pinned branch objects must be available, otherwise verification fails closed. The original detached worktree materializer remains available under .worktrees/components, and retrieves original pinned branches, which require their own security controls.

Before promotion to main: independent Integration security/import-origin review, independent Training provenance review, clean-clone tests and security review of retained paths. Source presence does not establish VeraOS build, install, selected route, runtime consumption or qualified behavior.
