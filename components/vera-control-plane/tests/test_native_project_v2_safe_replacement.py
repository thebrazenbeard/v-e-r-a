from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECOVERY = ROOT / "project-instructions" / "native-v2" / "VERA_CURRENTNESS_AND_RECOVERY_V2.md"

def text():
    return RECOVERY.read_text(encoding="utf-8")

def test_replacement_requires_durable_predecessor_and_rollback_binding():
    value = text()
    assert "bind the exact predecessor subject" in value
    assert "required durable identity/state/recovery material" in value
    assert "rollback locator/digest" in value

def test_successor_must_be_staged_and_read_back_before_completion():
    value = text()
    assert "Stage the successor without deleting the predecessor" in value
    assert "install/registration and current-route readback" in value
    assert "verify those surfaces after the switch" in value

def test_cleanup_cannot_be_inferred_from_successor_start():
    value = text()
    assert "SUCCESSOR_STARTED != PREDECESSOR_SAFE_TO_DELETE" in value
    assert "Preserve reversible predecessor custody" in value

def test_ambiguous_or_regressed_successor_fails_closed():
    value = text()
    assert "If successor readback diverges" in value
    assert "fail closed" in value
    assert "preserve both subjects" in value

def test_external_patterns_remain_research_only():
    value = text()
    assert "DNSCrypt/dnscrypt-server-docker@1218e909" in value
    assert "hughhowey/neo@a2846ff" in value
    assert "research sources only" in value
    assert "grant no Vera authority" in value
