from meso_crct import (
    AllocationSample,
    AllocationWindow,
    CircuitState,
    GoalObligation,
    RewardState,
    SalienceState,
    TargetState,
    audit_allocation_window,
    audit_attention_budget,
    select_target,
)


def test_balanced_goal_allocation_passes():
    samples = [
        AllocationSample("goal:a", 0.8, "semantic_relevance"),
        AllocationSample("goal:b", 0.7, "epistemic_value"),
        AllocationSample("goal:a", 0.8, "semantic_relevance"),
        AllocationSample("goal:b", 0.7, "epistemic_value"),
    ]
    obligations = [
        GoalObligation("goal:a", 0.25),
        GoalObligation("goal:b", 0.25),
    ]
    audit = audit_attention_budget(samples, obligations)
    assert audit.passed
    assert audit.dominant_fraction == 0.5


def test_narrow_target_crowdout_is_flagged():
    samples = [
        AllocationSample("target:loop", 1.0, "incentive_salience")
        for _ in range(9)
    ] + [
        AllocationSample("goal:maintenance", 0.4, "semantic_relevance")
    ]
    obligations = [GoalObligation("goal:maintenance", 0.20)]
    audit = audit_attention_budget(samples, obligations)
    assert "goal_neglect" in audit.flags
    assert "target_crowd_out" in audit.flags
    assert "incentive_capture" in audit.flags
    assert audit.neglected_goals == ("goal:maintenance",)


def test_protective_emergency_does_not_count_as_ordinary_crowdout():
    samples = [
        AllocationSample(
            "hazard:fire",
            1.0,
            "hazard",
            protective=True,
        )
        for _ in range(20)
    ]
    obligations = [GoalObligation("goal:maintenance", 0.20)]
    audit = audit_attention_budget(samples, obligations)
    assert audit.passed
    assert audit.protective_samples == 20
    assert audit.nonprotective_samples == 0


def test_goal_threshold_is_user_supplied_not_equal_share_assumption():
    samples = [
        AllocationSample("goal:primary", 0.9, "semantic_relevance")
        for _ in range(8)
    ] + [
        AllocationSample("goal:background", 0.4, "semantic_relevance")
        for _ in range(2)
    ]
    obligations = [GoalObligation("goal:background", 0.10)]
    audit = audit_attention_budget(samples, obligations)
    assert "goal_neglect" not in audit.flags


def test_allocation_window_records_actual_selection_results():
    window = AllocationWindow()
    result = select_target([
        TargetState(
            "goal:a",
            CircuitState(
                salience=SalienceState(semantic_relevance=0.8),
            ),
        ),
        TargetState(
            "goal:b",
            CircuitState(
                salience=SalienceState(semantic_relevance=0.3),
            ),
        ),
    ])
    window = window.record(result)
    assert len(window.samples) == 1
    assert window.samples[0].target_id == "goal:a"
    assert window.no_selection_cycles == 0


def test_quiescent_selection_cycle_is_recorded_without_fake_sample():
    window = AllocationWindow().record(
        select_target([
            TargetState("one"),
            TargetState("two"),
        ])
    )
    assert window.samples == ()
    assert window.no_selection_cycles == 1


def test_real_local_selection_history_drives_crowdout_audit():
    window = AllocationWindow()

    for _ in range(9):
        result = select_target([
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
        ])
        window = window.record(result)

    maintenance_only = select_target([
        TargetState(
            "goal:maintenance",
            CircuitState(
                salience=SalienceState(semantic_relevance=0.4),
            ),
        )
    ])
    window = window.record(maintenance_only)

    audit = audit_allocation_window(
        window,
        [GoalObligation("goal:maintenance", 0.20)],
    )
    assert audit.dominant_target == "target:loop"
    assert "goal_neglect" in audit.flags
    assert "target_crowd_out" in audit.flags
    assert "incentive_capture" in audit.flags


def test_real_protective_selections_remain_exempt_from_ordinary_share():
    window = AllocationWindow()
    for _ in range(5):
        result = select_target([
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
        ])
        window = window.record(result)

    audit = audit_allocation_window(
        window,
        [GoalObligation("goal:maintenance", 0.20)],
    )
    assert audit.protective_samples == 5
    assert audit.nonprotective_samples == 0
    assert audit.passed
