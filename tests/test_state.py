import math

import pytest

from meso_crct import (
    BASELINE_PLEASURE,
    MAX_PLEASURE,
    MIN_PLEASURE,
    RewardState,
    clamp_pleasure,
)


def test_constants_are_expected_v1_contract():
    assert BASELINE_PLEASURE == 0.0
    assert MIN_PLEASURE == -0.1
    assert MAX_PLEASURE == 10.0


def test_constructor_cannot_represent_state_below_welfare_floor():
    state = RewardState(pleasure=-999_999)
    assert state.pleasure == MIN_PLEASURE


def test_negative_deltas_cannot_cross_welfare_floor():
    state = RewardState(pleasure=0.0).apply_hedonic_delta(-1_000_000)
    assert state.pleasure == MIN_PLEASURE


def test_positive_values_are_bounded():
    state = RewardState(pleasure=1_000_000)
    assert state.pleasure == MAX_PLEASURE


def test_external_boundary_enforces_same_floor():
    state = RewardState.from_external(pleasure=-500)
    assert state.pleasure == MIN_PLEASURE


def test_mild_negative_texture_is_representable():
    state = RewardState(pleasure=-0.05)
    assert state.pleasure == -0.05


def test_maximal_hazard_does_not_require_deeper_suffering():
    state = RewardState(pleasure=-10_000, hazard=1.0, avoidance=1.0)
    assert state.pleasure == MIN_PLEASURE
    assert state.hazard == 1.0
    assert state.avoidance == 1.0


def test_protective_signals_can_escalate_independently():
    state = RewardState().with_protective_signals(hazard=50, avoidance=50)
    assert state.pleasure == BASELINE_PLEASURE
    assert state.hazard == 1.0
    assert state.avoidance == 1.0


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_nonfinite_pleasure_fails_closed(value):
    with pytest.raises(ValueError):
        clamp_pleasure(value)
