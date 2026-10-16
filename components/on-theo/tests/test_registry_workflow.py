from pathlib import Path


def test_registry_workflow_runs_tests_and_direct_validation() -> None:
    root = Path(__file__).resolve().parents[1]
    path = root / ".github/workflows/validate-registries.yml"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "pytest -q" in text
    assert "python scripts/validate_registry.py --root . --json" in text
    assert "requirements-dev.txt" in text
    assert "fetch-depth: 0" in text
    assert "python scripts/audit_rebase_preconditions.py --root . --subject HEAD" in text
