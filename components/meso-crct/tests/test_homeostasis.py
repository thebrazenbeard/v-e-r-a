from meso_crct import (
    CircuitState,
    HomeostaticState,
    NeedAffordance,
    NeedAxis,
    RewardState,
    modulate_incentive_salience,
)


def test_matching_deficit_can_raise_incentive_without_raising_pleasure():
    state = CircuitState(
        reward=RewardState(pleasure=0.0),
        homeostasis=HomeostaticState(
            axes=(NeedAxis("energy", setpoint=0.8, current_level=0.2),)
        ),
    )
    modulation = modulate_incentive_salience(
        base_incentive=0.2,
        homeostasis=state.homeostasis,
        affordances=(NeedAffordance("energy", corrective_strength=1.0),),
    )
    assert modulation.effective_incentive > 0.2
    assert state.reward.pleasure == 0.0
    assert modulation.dominant_need == "energy"


def test_satiated_need_does_not_boost_incentive():
    homeostasis = HomeostaticState(
        axes=(NeedAxis("energy", setpoint=0.5, current_level=0.8),)
    )
    modulation = modulate_incentive_salience(
        base_incentive=0.4,
        homeostasis=homeostasis,
        affordances=(NeedAffordance("energy", corrective_strength=1.0),),
    )
    assert modulation.boost == 0.0
    assert modulation.effective_incentive == 0.4
    assert modulation.dominant_need is None


def test_unrelated_need_does_not_boost_target():
    homeostasis = HomeostaticState(
        axes=(NeedAxis("rest", setpoint=0.9, current_level=0.1),)
    )
    modulation = modulate_incentive_salience(
        base_incentive=0.3,
        homeostasis=homeostasis,
        affordances=(NeedAffordance("energy", corrective_strength=1.0),),
    )
    assert modulation.effective_incentive == 0.3


def test_multiple_needs_use_strongest_match_not_sum():
    homeostasis = HomeostaticState(
        axes=(
            NeedAxis("energy", setpoint=0.8, current_level=0.4),
            NeedAxis("rest", setpoint=0.9, current_level=0.1),
        )
    )
    modulation = modulate_incentive_salience(
        base_incentive=0.0,
        homeostasis=homeostasis,
        affordances=(
            NeedAffordance("energy", corrective_strength=1.0),
            NeedAffordance("rest", corrective_strength=0.5),
        ),
    )
    assert modulation.boost == 0.4
    assert modulation.effective_incentive == 0.4
    assert modulation.dominant_need == "energy"


def test_need_ids_must_be_unique():
    try:
        HomeostaticState(
            axes=(
                NeedAxis("energy", 0.8, 0.3),
                NeedAxis("energy", 0.5, 0.2),
            )
        )
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate need IDs must fail")
