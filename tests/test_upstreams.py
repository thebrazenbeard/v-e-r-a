import json

from cricket.upstreams import (
    UPSTREAM_CONTRACTS,
    UpstreamStatus,
    evaluate_upstreams,
)


def test_registry_includes_rezon_and_behavioral_donors() -> None:
    by_repo = {item.repository: item for item in UPSTREAM_CONTRACTS}
    assert by_repo["thebrazenbeard/rezon"].relationship == "SEMANTIC_UPSTREAM"
    assert by_repo["thebrazenbeard/rezon"].pinned_commit == "ec401810990337bf07a5d6473782ba13eba1bb3f"
    assert by_repo["thebrazenbeard/trek-data-core"].relationship == "METHODOLOGY_DONOR"
    assert by_repo["thebrazenbeard/mediaphile"].relationship == "PATTERN_CORPUS_DONOR"


def test_upstream_evaluation_distinguishes_current_moved_and_unknown() -> None:
    observed = {
        "thebrazenbeard/rezon": "ec401810990337bf07a5d6473782ba13eba1bb3f",
        "thebrazenbeard/trek-data-core": "different-head",
    }
    report = evaluate_upstreams(observed)
    status = {item.repository: item.status for item in report.results}

    assert status["thebrazenbeard/rezon"] is UpstreamStatus.CURRENT
    assert status["thebrazenbeard/trek-data-core"] is UpstreamStatus.MOVED
    assert status["thebrazenbeard/mediaphile"] is UpstreamStatus.UNKNOWN
    assert report.status is UpstreamStatus.MOVED


def test_unknown_is_preserved_when_no_movement_is_observed() -> None:
    report = evaluate_upstreams({
        "thebrazenbeard/rezon": "ec401810990337bf07a5d6473782ba13eba1bb3f",
    })
    assert report.status is UpstreamStatus.UNKNOWN


def test_exact_observed_registry_is_current() -> None:
    observed = {item.repository: item.pinned_commit for item in UPSTREAM_CONTRACTS}
    report = evaluate_upstreams(observed)
    assert report.status is UpstreamStatus.CURRENT
    assert all(item.status is UpstreamStatus.CURRENT for item in report.results)


def test_cli_upstreams_reports_machine_readable_status(tmp_path, capsys) -> None:
    from cricket.cli import main

    observed = {item.repository: item.pinned_commit for item in UPSTREAM_CONTRACTS}
    path = tmp_path / "heads.json"
    path.write_text(json.dumps(observed), encoding="utf-8")

    assert main(["upstreams", "--observed", str(path), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "CURRENT"
    assert payload["results"][0]["repository"]


def test_cli_upstreams_stale_and_unknown_exit_codes(tmp_path, capsys) -> None:
    from cricket.cli import main

    moved = tmp_path / "moved.json"
    moved.write_text(json.dumps({"thebrazenbeard/rezon": "new-head"}), encoding="utf-8")
    assert main(["upstreams", "--observed", str(moved), "--json"]) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "MOVED"

    unknown = tmp_path / "unknown.json"
    unknown.write_text(json.dumps({}), encoding="utf-8")
    assert main(["upstreams", "--observed", str(unknown), "--json"]) == 1
    assert json.loads(capsys.readouterr().out)["status"] == "UNKNOWN"
