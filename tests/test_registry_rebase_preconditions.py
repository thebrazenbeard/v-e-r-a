from pathlib import Path
import subprocess

from tools.on_theo_registry.rebase_preconditions import audit_rebase_preconditions


SUBJECT = "HEAD"


def test_divergent_extension_referential_preconditions_are_equivalent() -> None:
    root = Path(__file__).resolve().parents[1]

    historical_witness_registry = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "ls-tree",
            "--name-only",
            "c1f6df5ea1fee0c5ac8d84a7b5c2b81fb905fd3e",
            "--",
            "registry/witnesses.yaml",
        ],
        text=True,
        encoding="utf-8",
        errors="strict",
        capture_output=True,
        check=True,
    )
    assert historical_witness_registry.stdout.strip() == ""

    report = audit_rebase_preconditions(root, SUBJECT)

    assert report["extension_count"] == 50
    assert report["ancestor_extension_count"] == 11
    assert report["divergent_extension_count"] == 39
    assert report["divergent_unique_base_count"] == 36
    assert report["ancestor_extension_count"] + report["divergent_extension_count"] == report["extension_count"]
    assert report["referential_precondition_mismatch_count"] == 0, report["mismatches"]
    assert report["referential_preconditions_equivalent"] is True

    divergent = [
        item
        for item in report["extensions"]
        if item["relation"] == "DIVERGED_REBASE_EXCEPTION_REQUIRED"
    ]
    assert len(divergent) == 39
    assert all(item["mismatch_count"] == 0 for item in divergent)