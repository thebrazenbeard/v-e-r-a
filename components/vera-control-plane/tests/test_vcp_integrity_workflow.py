from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "vcp-integrity.yml"
VALIDATOR = ROOT / "tools" / "validate_vcp_integrity.py"


def text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def validator_text() -> str:
    return VALIDATOR.read_text(encoding="utf-8")


def test_workflow_exists_and_is_read_only() -> None:
    data = text()
    assert "name: VCP integrity" in data
    assert "permissions:\n  contents: read" in data
    assert "persist-credentials: false" in data
    assert "timeout-minutes: 10" in data


def test_pull_requests_are_bound_to_exact_head_sha() -> None:
    data = text()
    assert "EXPECTED_SHA: ${{ github.event.pull_request.head.sha || github.sha }}" in data
    assert "ref: ${{ env.EXPECTED_SHA }}" in data
    assert 'test "$actual" = "$EXPECTED_SHA"' in data


def test_workflow_delegates_to_executable_validator() -> None:
    data = text()
    assert 'python -m pip install --disable-pip-version-check -r requirements/vcp-integrity.txt' in data
    assert 'python tools/validate_vcp_integrity.py --base-sha "$BASE_SHA"' in data
    assert "python -m unittest discover" not in data
    assert "build_native_project_successor_v2a1.py" not in data


def test_validator_contains_full_suite_and_native_package_gate() -> None:
    data = validator_text()
    assert '"pytest", "-q", "tests"' in data
    assert '"unittest", "discover"' not in data
    assert "build_nv2a1(output)" in data
    assert 'assert actual_sha == expected["sha256"]' in data
    assert "assert actual <= 8000" in data
    assert '"git", "diff", "--check"' in data


def test_workflow_runs_for_relevant_pr_main_and_manual_events() -> None:
    data = text()
    assert "pull_request:" in data
    assert "push:" in data
    assert "workflow_dispatch:" in data
    assert '"project-instructions/**"' in data
    assert '"tools/**"' in data
    assert '"tests/**"' in data
    assert '"requirements/**"' in data
