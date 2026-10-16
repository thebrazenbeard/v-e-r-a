from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "project-instructions" / "native-v2"
TASK = BASE / "VERA_TASK_EXECUTION_AND_CLOSEOUT_V2.md"
INTERFACE = BASE / "VERA_NATIVE_PROJECT_INTERFACE_V2.yaml"
COORD = BASE / "VERA_COORDINATION_V2.md"

def test_task_contract_is_native_source():
    interface = INTERFACE.read_text(encoding="utf-8")
    assert "logical_id: VERA_TASK_EXECUTION_AND_CLOSEOUT" in interface
    assert "schema: VERA_TASK_EXECUTION_AND_CLOSEOUT_V2" in interface

def test_task_packet_binds_completion_evidence_and_forbidden_shortcuts():
    text = TASK.read_text(encoding="utf-8")
    for phrase in (
        "**completion state**",
        "**evidence**",
        "**forbidden shortcuts/effects**",
        "**unknowns**",
        "**return shape**",
    ):
        assert phrase in text

def test_closeout_surfaces_cannot_collapse():
    text = TASK.read_text(encoding="utf-8")
    for surface in (
        "**source**",
        "**build/package**",
        "**install/registration**",
        "**current route**",
        "**runtime consumption**",
        "**behavior/effect**",
        "**docs/rules**",
        "**memory/privacy**",
        "**workspace/coordination**",
    ):
        assert surface in text
    assert (
        "SOURCE_PASS != INSTALL_PASS != ROUTE_PASS != RUNTIME_PASS "
        "!= BEHAVIOR_PASS != EFFECT_PASS"
    ) in text

def test_no_run_and_exact_subject_semantics_are_explicit():
    text = TASK.read_text(encoding="utf-8")
    assert "NO_RUN, not PASS or FAIL" in text
    assert "Material movement creates a new review subject" not in text
    assert "movement creates a new subject" in text

def test_coordination_points_to_task_closeout_without_authority_expansion():
    text = COORD.read_text(encoding="utf-8")
    assert "VERA_TASK_EXECUTION_AND_CLOSEOUT_V2" in text
    task = TASK.read_text(encoding="utf-8")
    assert "never grants more authority" in task

def test_cleanup_remains_separate_and_reversible_first():
    text = TASK.read_text(encoding="utf-8")
    assert "Destructive cleanup is separate" in text
    assert "Prefer reversible custody" in text
