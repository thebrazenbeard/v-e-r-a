import numpy as np

from unvtrslr.events import discover_candidate_units


SR = 16000


def tone(freq, seconds=0.5, amp=0.5):
    t = np.arange(int(SR * seconds)) / SR
    return amp * np.sin(2 * np.pi * freq * t)


def concat(*parts):
    return np.concatenate(parts)


def test_stationary_tone_is_single_candidate_event():
    result = discover_candidate_units(tone(220, 1.0), SR)
    assert len(result.events) == 1
    assert [u.unit_id for u in result.units] == ["u0"]


def test_large_frequency_change_creates_boundary_near_transition():
    x = concat(tone(160, 0.55), tone(320, 0.55))
    result = discover_candidate_units(x, SR)
    assert len(result.events) == 2
    assert 0.42 <= result.events[0].end_s <= 0.68
    assert result.units[0].unit_id != result.units[1].unit_id


def test_repeated_acoustic_state_reuses_candidate_unit_id():
    x = concat(tone(170, 0.42), tone(330, 0.42), tone(170, 0.42))
    result = discover_candidate_units(x, SR, min_event_s=0.18)
    assert len(result.events) == 3
    ids = [u.unit_id for u in result.units]
    assert ids[0] == ids[2]
    assert ids[0] != ids[1]


def test_global_amplitude_change_does_not_create_structure_by_itself():
    a = discover_candidate_units(tone(210, 1.0, amp=0.15), SR)
    b = discover_candidate_units(tone(210, 1.0, amp=0.75), SR)
    assert len(a.events) == 1
    assert len(b.events) == 1


def test_claim_ceiling_does_not_call_events_words_or_phonemes():
    result = discover_candidate_units(tone(200, 0.5), SR)
    assert result.claim_ceiling == "ACOUSTIC_EVENT_HYPOTHESES_ONLY_NO_LINGUISTIC_SEGMENTATION"
