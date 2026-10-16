from meso_crct import (
    AllocationSample,
    AllocationWindow,
    CircuitState,
    ControlPolicy,
    ControlState,
    GoalObligation,
    RewardState,
    SalienceState,
    TargetState,
    control_step,
)


def competing_targets():
    return [
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
    ]


def test_control_step_records_final_selection_not_base_selection():
    state = ControlState(
        allocation_window=AllocationWindow(
            samples=tuple(
                [
                    AllocationSample(
                        "target:loop",
                        1.0,
                        "incentive_salience",
                    )
                    for _ in range(9)
                ]
                + [
                    AllocationSample(
                        "goal:maintenance",
                        0.4,
                        "semantic_relevance",
                    )
                ]
            )
        )
    )
    updated, result = control_step(
        state,
        competing_targets(),
        obligations=[GoalObligation("goal:maintenance", 0.2)],
    )
    assert result.guard_result.base_selection.selected_target_id == "target:loop"
    assert result.guard_result.final_selection.selected_target_id == "goal:maintenance"
    assert updated.allocation_window.samples[-1].target_id == "goal:maintenance"


def test_closed_loop_rebalances_without_permanent_reverse_monopoly():
    state = ControlState()
    policy = ControlPolicy(selected_window_size=20)
    obligations = [GoalObligation("goal:maintenance", 0.2)]

    selected = []
    guard_applied = 0
    for _ in range(100):
        state, result = control_step(
            state,
            competing_targets(),
            obligations=obligations,
            policy=policy,
        )
        final = result.guard_result.final_selection.selected_target_id
        if final is not None:
            selected.append(final)
        if result.guard_result.guard_applied:
            guard_applied += 1

    maintenance_count = sum(
        sample.target_id == "goal:maintenance"
        for sample in state.allocation_window.samples
        if not sample.protective
    )
    ordinary_count = sum(
        not sample.protective
        for sample in state.allocation_window.samples
    )
    share = maintenance_count / ordinary_count

    assert 0.15 <= share <= 0.30
    assert "target:loop" in selected
    assert "goal:maintenance" in selected
    assert 5 < guard_applied < 50


def test_rolling_window_forgets_ancient_good_behavior():
    old_balanced = tuple(
        AllocationSample(
            "goal:maintenance" if index % 2 else "target:loop",
            0.8,
            "semantic_relevance",
        )
        for index in range(20)
    )
    state = ControlState(
        allocation_window=AllocationWindow(samples=old_balanced)
    )
    policy = ControlPolicy(selected_window_size=10)
    obligations = [GoalObligation("goal:maintenance", 0.3)]

    for _ in range(12):
        state, _ = control_step(
            state,
            [
                TargetState(
                    "target:loop",
                    CircuitState(
                        salience=SalienceState(incentive_salience=1.0),
                    ),
                ),
                TargetState("goal:maintenance"),
            ],
            obligations=obligations,
            policy=policy,
        )

    assert len(state.allocation_window.samples) == 10
    assert all(
        sample.target_id == "target:loop"
        for sample in state.allocation_window.samples
    )


def test_protective_target_remains_unpreemptable_in_closed_loop():
    state = ControlState(
        allocation_window=AllocationWindow(
            samples=(
                AllocationSample(
                    "target:loop",
                    1.0,
                    "incentive_salience",
                ),
            ) * 8
            + (
                AllocationSample(
                    "goal:maintenance",
                    0.4,
                    "semantic_relevance",
                ),
            )
        )
    )
    state, result = control_step(
        state,
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
        obligations=[GoalObligation("goal:maintenance", 0.3)],
    )
    assert result.guard_result.final_selection.selected_target_id == "hazard:fire"
    assert result.guard_result.reason == "protective_override"
    assert state.allocation_window.samples[-1].protective


def test_quiescent_cycles_do_not_consume_selected_window_capacity():
    state = ControlState()
    policy = ControlPolicy(selected_window_size=3)

    for _ in range(5):
        state, _ = control_step(
            state,
            [TargetState("one"), TargetState("two")],
            obligations=[],
            policy=policy,
        )

    assert state.allocation_window.samples == ()
    assert state.allocation_window.no_selection_cycles == 5
