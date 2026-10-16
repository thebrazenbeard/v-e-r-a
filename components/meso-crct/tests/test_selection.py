from meso_crct import (
    ArbitrationMode,
    CircuitState,
    RewardState,
    SalienceState,
    SelectionPolicy,
    TargetState,
    select_target,
)


def test_protection_overrides_nonprotective_high_priority_target():
    result = select_target([
        TargetState(
            "attractive",
            CircuitState(
                reward=RewardState(pleasure=10.0),
                salience=SalienceState(incentive_salience=1.0),
            ),
        ),
        TargetState(
            "danger",
            CircuitState(
                reward=RewardState(hazard=0.8, avoidance=0.8),
            ),
        ),
    ])
    assert result.selected_target_id == "danger"
    assert result.selected_decision.mode is ArbitrationMode.PROTECTIVE
    assert result.used_protective_override


def test_default_policy_prefers_motivational_over_epistemic_mode():
    result = select_target([
        TargetState(
            "learn",
            CircuitState(
                salience=SalienceState(epistemic_value=1.0),
            ),
        ),
        TargetState(
            "pursue",
            CircuitState(
                salience=SalienceState(motivational_salience=0.7),
            ),
        ),
    ])
    assert result.selected_target_id == "pursue"
    assert result.selected_decision.mode is ArbitrationMode.MOTIVATIONAL


def test_policy_can_explicitly_prioritize_epistemic_mode():
    policy = SelectionPolicy(
        nonprotective_precedence=(
            ArbitrationMode.EPISTEMIC,
            ArbitrationMode.MOTIVATIONAL,
            ArbitrationMode.ORIENTING,
        )
    )
    result = select_target([
        TargetState(
            "learn",
            CircuitState(
                salience=SalienceState(epistemic_value=0.6),
            ),
        ),
        TargetState(
            "pursue",
            CircuitState(
                salience=SalienceState(motivational_salience=1.0),
            ),
        ),
    ], policy=policy)
    assert result.selected_target_id == "learn"


def test_within_same_mode_higher_priority_wins():
    result = select_target([
        TargetState(
            "weak",
            CircuitState(
                salience=SalienceState(semantic_relevance=0.4),
            ),
        ),
        TargetState(
            "strong",
            CircuitState(
                salience=SalienceState(semantic_relevance=0.9),
            ),
        ),
    ])
    assert result.selected_target_id == "strong"


def test_exact_tie_is_deterministic_by_target_id():
    result = select_target([
        TargetState(
            "zeta",
            CircuitState(
                salience=SalienceState(semantic_relevance=0.8),
            ),
        ),
        TargetState(
            "alpha",
            CircuitState(
                salience=SalienceState(semantic_relevance=0.8),
            ),
        ),
    ])
    assert result.selected_target_id == "alpha"


def test_all_quiescent_targets_yield_no_selection():
    result = select_target([
        TargetState("one"),
        TargetState("two"),
    ])
    assert not result.selected
    assert result.selected_target_id is None
    assert result.selected_decision is None


def test_policy_rejects_missing_or_duplicate_modes():
    try:
        SelectionPolicy(
            nonprotective_precedence=(
                ArbitrationMode.MOTIVATIONAL,
                ArbitrationMode.MOTIVATIONAL,
                ArbitrationMode.ORIENTING,
            )
        )
    except ValueError:
        pass
    else:
        raise AssertionError("invalid precedence must fail")
