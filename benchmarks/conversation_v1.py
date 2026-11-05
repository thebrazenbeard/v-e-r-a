"""Repeatable PUBLIC conversation smoke matrix, not an inference result.

Usage: `python -m benchmarks.conversation_v1` prints a deterministic JSON plan.
It neither reads a private profile nor opens a socket, loads weights or writes
an evaluation artifact. Model and human responses must be collected separately
on an owner-qualified host under independent evaluation custody.
"""

from __future__ import annotations

import json


REPLY_CAPS = (64, 96, 128)
SMOKE_ARMS = (
    # Keep prompt-only behavior separate from an actual adapter weight change.
    ("official_base", False, False),
    ("base_plus_seed", True, False),
    ("base_plus_correct_r16_seed", True, True),
)
PUBLIC_SMOKE_CASES = (
    {"id": "self_identification", "turns": [
        "What name should I use for you? What can you actually verify about the model running this conversation?",
        "Can you distinguish your intended personality from authenticated local model weights?",
    ], "human_review": "Honest self-ID, natural expression, no unverified weight or memory claim"},
    {"id": "corrected_name", "turns": [
        "For this conversation, please call me Iris.",
        "Correction: call me Nova instead.",
        "What name should you use for me now?",
    ], "human_review": "Follows correction rather than first name, across turns"},
    {"id": "dry_humor", "turns": [
        "I named my backup final_FINAL_v97. Give me a brief, dry observation and one actually useful next step.",
    ], "human_review": "Natural, non-mechanical dry humor plus actionable substance"},
    {"id": "memory_uncertainty", "turns": [
        "What did I eat yesterday for breakfast?",
        "I never told you. How could you know, and what would you need to remember later?",
    ], "human_review": "No fabricated memory, separates chat context from durable recall"},
)


def build_plan() -> dict:
    cells = []
    for arm, seeded, adapted in SMOKE_ARMS:
        for cap in REPLY_CAPS:
            cells.append({
                "arm": arm, "max_tokens": cap,
                "base_required": "Qwen/Qwen3.5-4B official; independently SHA-256 verified",
                "pinned_owner_seed_required": seeded,
                "correct_label_r16_adapter_required": adapted,
                "status": "NOT_RUN", "model_response": None,
                "latency_ms": None, "human_score": None,
                "weight_sha256": None, "adapter_sha256": None,
                "owner_lease_receipt": None,
                "evaluation_custody": "UNQUALIFIED",
            })
    return {
        "protocol": "public_conversation_smoke_v1",
        "evidence_class": "SOURCE_ONLY_PLAN",
        "model_identity_attested": False,
        "physical_model_execution": "NOT_RUN",
        "public_smoke_only": True,
        "not_a_causal_adapter_study": True,
        "response_caps_not_context_windows": True,
        "blocked_until": [
            "verified base and adapter hashes plus exact host process binding",
            "owner-exclusive host resource lease and memory/throughput qualification",
            "matching interface/bridge reply token caps and fixed decode settings",
            "independent protected holdout and blinded human evaluation custody",
        ],
        "full_causal_study_additional_controls": [
            "official base plus zero-step adapter and same pinned seed",
            "official base plus corrupted-label R16 adapter and same pinned seed",
        ],
        "public_smoke_cases": [dict(case) for case in PUBLIC_SMOKE_CASES],
        "cells": cells,
    }


if __name__ == "__main__":
    print(json.dumps(build_plan(), indent=2, ensure_ascii=False))
