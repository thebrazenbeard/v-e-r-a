"""Typed source provenance for optional owner-provisioned Vera prompt behavior.

No private source is bundled. A pinned owner file is admitted by the separate
persona_profile module; these receipts cannot attest loaded model weights.
"""

from __future__ import annotations

import hashlib
import hmac
from pathlib import Path

from .persona_profile import (PersonaSeed, PROFILE_SCHEMA, SOURCE_COMMIT,
                              SOURCE_GIT_BLOB_SHA1, SOURCE_REPOSITORY,
                              SOURCE_SHA256)

PRESENTATION_GIT_BLOB_SHA = "887bfe1d6862d23550b224a00a60e32d197e8c1f"


def verify_presentation_file(path: str | Path) -> None:
    """Admit owner-provisioned canonical presentation bytes without bundling."""
    target = Path(path)
    with target.open("rb") as source:
        raw = source.read(16_385)
    if len(raw) > 16_384:
        raise ValueError("presentation source exceeds size limit")
    blob = b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
    if not hmac.compare_digest(hashlib.sha1(blob).hexdigest(),
                               PRESENTATION_GIT_BLOB_SHA):
        raise ValueError("presentation file differs from pinned canonical source")


def persona_source_receipt(seed: PersonaSeed | None,
                           presentation_verified: bool = False) -> dict:
    if seed is None:
        return {
            "kind": "not_connected",
            "qualification": "NOT_CONFIGURED",
            "prompt_layer": "none",
            "identity_attested": False,
            "trained_weights_modified": False,
        }
    receipt = {
        "kind": "behavior_configuration",
        "profile_id": PROFILE_SCHEMA,
        "profile_version": seed.profile_version,
        "repository": SOURCE_REPOSITORY,
        "profile_blob_sha": SOURCE_GIT_BLOB_SHA1,
        "source_commit": SOURCE_COMMIT,
        "source_sha256": SOURCE_SHA256,
        "source_classification": {
            "kind": "behavior_configuration",
            "origin": "explicit_owner_provisioned_pinned_profile",
            "imported_knowledge": False,
            "trained_weights_modified": False,
        },
        "qualification": "SOURCE_ONLY",
        "prompt_layer": "server_owned_system",
        "identity_attested": False,
        "trained_weights_modified": False,
    }
    if presentation_verified:
        receipt["presentation_blob_sha"] = PRESENTATION_GIT_BLOB_SHA
        receipt["presentation_implementation"] = "ADMITTED_SOURCE_REFERENCE_ONLY"
    return receipt
