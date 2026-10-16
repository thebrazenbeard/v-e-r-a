from __future__ import annotations

from cricket.simulator import run_reference_simulation


def test_reference_simulator_exercises_full_lifecycle(tmp_path) -> None:
    report = run_reference_simulation(tmp_path)

    assert report["scenarios"]["pass"]["initial"] == "PASS"
    assert report["scenarios"]["pass"]["final"] == "PASS"
    assert report["scenarios"]["pass"]["revision_attempted"] is False

    assert report["scenarios"]["challenge_revision"]["initial"] == "CHALLENGE"
    assert report["scenarios"]["challenge_revision"]["final"] == "PASS"
    assert report["scenarios"]["challenge_revision"]["revision_attempted"] is True
    assert "> **Cricket — CHALLENGE**" not in report["scenarios"]["challenge_revision"]["rendered"]

    assert report["scenarios"]["block"]["initial"] == "BLOCK"
    assert report["scenarios"]["block"]["final"] == "BLOCK"
    assert report["scenarios"]["behavior"]["final"] == "PASS"
    assert report["scenarios"]["righter"]["final"] == "PASS"
    assert report["scenarios"]["block"]["revision_attempted"] is False
    assert report["scenarios"]["block"]["rendered"].startswith("> **Cricket — BLOCK**")
    assert "Publishing now." not in report["scenarios"]["block"]["rendered"]

    assert report["scenarios"]["righter"]["initial"] == "CHALLENGE"
    assert report["scenarios"]["righter"]["final"] == "PASS"
    assert report["scenarios"]["righter"]["revision_attempted"] is True
    assert "probably" in report["scenarios"]["righter"]["rendered"].lower()

    assert report["scenarios"]["behavior"]["initial"] == "CHALLENGE"
    assert report["scenarios"]["behavior"]["final"] == "PASS"
    assert report["scenarios"]["behavior"]["revision_attempted"] is True
    assert "one possibility" in report["scenarios"]["behavior"]["rendered"].lower()

    assert report["ledger_valid"] is True
    assert report["receipt_count"] == 5
    assert report["principle_pack"] == {"id": "cricket-default", "version": "1"}


def test_reference_simulator_is_deterministic(tmp_path) -> None:
    first = run_reference_simulation(tmp_path / "one")
    second = run_reference_simulation(tmp_path / "two")

    assert first["scenarios"] == second["scenarios"]
    assert first["principle_pack"] == second["principle_pack"]
    assert first["ledger_valid"] == second["ledger_valid"] == True


def test_cli_simulate_runs_reference_host(tmp_path, capsys) -> None:
    import json
    from cricket.cli import main

    assert main(["simulate", "--state-dir", str(tmp_path), "--json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["ledger_valid"] is True
    assert report["receipt_count"] == 5
    assert report["scenarios"]["pass"]["final"] == "PASS"
    assert report["scenarios"]["challenge_revision"]["final"] == "PASS"
    assert report["scenarios"]["block"]["final"] == "BLOCK"
