from meso_crct import (
    AllocationAudit,
    CircuitState,
    GoalObligation,
    RewardState,
    SalienceState,
    TargetState,
    select_with_allocation_guard,
)


def audit_with_maintenance_neglected():
    return AllocationAudit(
        nonprotective_samples=10,
        protective_samples=0,
        dominant_target="target:loop",
        dominant_fraction=0.9,
        goal_shares=(("goal:maintenance", 0.1),),
        neglected_goals=("goal:maintenance",),
        flags=("goal_neglect", "target_crowd_out", "incentive_capture"),
    )


def test_guard_rebalances_to_relevant_neglected_goal():
    result = select_with_allocation_guard(
        [
            TargetState(
                "target:loop",
                CircuitState(
                    salience=SalienceState(incentive_salience=1.0),
                ),
            ),
            TargetState(
                "goal:maintenance",
                CircuitState(
                    salience=SalienceState(semantic_relevance=0.4),
                ),
            ),
        ],
        audit=audit_with_maintenance_neglected(),
        obligations=[GoalObligation("goal:maintenance", 0.2)],
    )
    assert result.base_selection.selected_target_id == "target:loop"
    assert result.final_selection.selected_target_id == "goal:maintenance"
    assert result.guard_applied
    assert result.rebalanced_goal_id == "goal:maintenance"


def test_guard_never_overrides_protective_selection():
    result = select_with_allocation_guard(
        [
            TargetState(
                "hazard:fire",
                CircuitState(
                    reward=RewardState(hazard=1.0, avoidance=1.0),
                ),
            ),
            TargetState(
                "goal:maintenance",
                CircuitState(
                    salience=SalienceState(semantic_relevance=0.8),
                ),
            ),
        ],
        audit=audit_with_maintenance_neglected(),
        obligations=[GoalObligation("goal:maintenance", 0.2)],
    )
    assert result.final_selection.selected_target_id == "hazard:fire"
    assert not result.guard_applied
    assert result.reason == "protective_override"


def test_guard_does_not_resurrect_quiescent_neglected_goal():
    result = select_with_allocation_guard(
        [
            TargetState(
                "target:loop",
                CircuitState(
                    salience=SalienceState(incentive_salience=1.0),
                ),
            ),
            TargetState("goal:maintenance"),
        ],
        audit=audit_with_maintenance_neglected(),
        obligations=[GoalObligation("goal:maintenance", 0.2)],
    )
    assert result.final_selection.selected_target_id == "target:loop"
    assert not result.guard_applied
    assert result.reason == "no_currently_relevant_neglected_goal"


def test_guard_is_inert_without_goal_neglect():
    healthy = AllocationAudit(
        nonprotective_samples=10,
        protective_samples=0,
        dominant_target="goal:primary",
        dominant_fraction=0.6,
        goal_shares=(("goal:maintenance", 0.4),),
        neglected_goals=(),
        flags=(),
    )
    result = select_with_allocation_guard(
        [
            TargetState(
                "target:loop",
                CircuitState(
                    salience=SalienceState(incentive_salience=1.0),
                ),
            ),
            TargetState(
                "goal:maintenance",
                CircuitState(
                    salience=SalienceState(semantic_relevance=0.8),
                ),
            ),
        ],
        audit=healthy,
        obligations=[GoalObligation("goal:maintenance", 0.2)],
    )
    assert result.final_selection == result.base_selection
    assert not result.guard_applied


def test_largest_obligation_deficit_is_rebalanced_first():
    audit = AllocationAudit(
        nonprotective_samples=10,
        protective_samples=0,
        dominant_target="target:loop",
        dominant_fraction=0.8,
        goal_shares=(
            ("goal:a", 0.1),
            ("goal:b", 0.1),
        ),
        neglected_goals=("goal:a", "goal:b"),
        flags=("goal_neglect", "target_crowd_out"),
    )
    result = select_with_allocation_guard(
        [
            TargetState(
                "target:loop",
                CircuitState(
                    salience=SalienceState(incentive_salience=1.0),
                ),
            ),
            TargetState(
                "goal:a",
                CircuitState(
                    salience=SalienceState(semantic_relevance=0.5),
                ),
            ),
            TargetState(
                "goal:b",
                CircuitState(
                    salience=SalienceState(semantic_relevance=0.5),
                ),
            ),
        ],
        audit=audit,
        obligations=[
            GoalObligation("goal:a", 0.2),
            GoalObligation("goal:b", 0.4),
        ],
    )
    assert result.final_selection.selected_target_id == "goal:b"
