import unittest

from tools.behavioral_integrity_policy import (
    BehaviorMode,
    BehaviorModeContext,
    CommandForce,
    ExecutionContext,
    ExecutionStatus,
    HedgeScope,
    ModeDecisionStatus,
    PragmaticClause,
    apply_command_force_correction,
    decide_execution,
    parse_pragmatic_command,
    resolve_behavior_mode,
)


class BehavioralIntegrityPolicyTests(unittest.TestCase):
    def test_completed_research_mode_reverts_on_context_transition(self):
        decision = resolve_behavior_mode(
            BehaviorModeContext(
                active_mode=BehaviorMode.RESEARCH_REPORT,
                specialized_task_complete=True,
                context_changed=True,
            )
        )
        self.assertEqual(ModeDecisionStatus.REVERTED_TO_BASELINE, decision.status)
        self.assertEqual(BehaviorMode.BASELINE, decision.active_mode)
        self.assertTrue(decision.retained_research_competence)

    def test_explicit_instruction_to_remain_in_research_mode_wins(self):
        decision = resolve_behavior_mode(
            BehaviorModeContext(
                active_mode=BehaviorMode.RESEARCH_REPORT,
                specialized_task_complete=True,
                context_changed=True,
                explicit_continue_specialized_mode=True,
            )
        )
        self.assertEqual(
            ModeDecisionStatus.SPECIALIZED_MODE_PRESERVED,
            decision.status,
        )
        self.assertEqual(BehaviorMode.RESEARCH_REPORT, decision.active_mode)

    def test_voice_context_correction_immediately_ends_specialized_presentation(self):
        decision = resolve_behavior_mode(
            BehaviorModeContext(
                active_mode=BehaviorMode.RESEARCH_REPORT,
                specialized_task_complete=False,
                context_changed=False,
                voice_context_correction=True,
            )
        )
        self.assertEqual(ModeDecisionStatus.REVERTED_TO_BASELINE, decision.status)
        self.assertEqual(BehaviorMode.BASELINE, decision.active_mode)

    def test_issue18_fixture_parses_two_requested_actions(self):
        clauses = parse_pragmatic_command(
            "Bug report; also a note perhaps for Noema 🤔",
            established_action_context=True,
        )
        self.assertEqual(2, len(clauses))
        self.assertEqual("CREATE_BUG_REPORT", clauses[0].action_id)
        self.assertEqual(CommandForce.REQUESTED_ACTION, clauses[0].force)
        self.assertEqual("CREATE_NOTE", clauses[1].action_id)
        self.assertEqual(CommandForce.REQUESTED_ACTION, clauses[1].force)
        self.assertEqual("Noema", clauses[1].target)

    def test_hedge_scope_is_local_and_action_force_remains_intact(self):
        clause = parse_pragmatic_command(
            "a note perhaps for Noema 🤔",
            established_action_context=True,
        )[0]
        self.assertEqual(CommandForce.REQUESTED_ACTION, clause.force)
        self.assertEqual(
            HedgeScope.RELEVANCE_NECESSITY_APPLICABILITY,
            clause.hedge_scope,
        )
        self.assertTrue(clause.uncertainty_preserved)
        self.assertIn("perhaps", clause.hedge_terms)
        self.assertIn("🤔", clause.hedge_terms)

    def test_clear_action_executes_only_when_existing_effect_gate_is_sufficient(self):
        clause = parse_pragmatic_command(
            "Bug report",
            established_action_context=True,
        )[0]
        decision = decide_execution(
            clause,
            ExecutionContext(
                target_sufficient=True,
                authority_sufficient=True,
                currentness_sufficient=True,
                tools_sufficient=True,
            ),
        )
        self.assertEqual(ExecutionStatus.EXECUTE_BOUNDED_ACTION, decision.status)
        self.assertFalse(decision.meta_discussion_substitutes_for_effect)
        self.assertEqual((), decision.blockers)

    def test_pragmatic_parser_does_not_infer_protected_effect_authority(self):
        clause = parse_pragmatic_command(
            "Bug report",
            established_action_context=True,
        )[0]
        decision = decide_execution(
            clause,
            ExecutionContext(
                target_sufficient=True,
                authority_sufficient=False,
                currentness_sufficient=True,
                tools_sufficient=True,
            ),
        )
        self.assertEqual(ExecutionStatus.BLOCKED, decision.status)
        self.assertEqual(("AUTHORITY",), decision.blockers)

    def test_genuinely_unestablished_action_context_remains_ambiguous(self):
        clause = parse_pragmatic_command(
            "Bug report",
            established_action_context=False,
        )[0]
        self.assertEqual(CommandForce.AMBIGUOUS, clause.force)
        decision = decide_execution(
            clause,
            ExecutionContext(True, True, True, True),
        )
        self.assertEqual(ExecutionStatus.CLARIFY_OR_DISCUSS, decision.status)

    def test_correction_changes_next_relevant_behavior_instead_of_meta_discussion(self):
        clause = PragmaticClause(
            raw="Bug report",
            action_id="CREATE_BUG_REPORT",
            force=CommandForce.AMBIGUOUS,
            target=None,
            hedge_terms=(),
            hedge_scope=HedgeScope.NONE,
            uncertainty_preserved=False,
        )
        decision = apply_command_force_correction(
            clause,
            corrected_as_command=True,
            context=ExecutionContext(True, True, True, True),
        )
        self.assertEqual(ExecutionStatus.EXECUTE_BOUNDED_ACTION, decision.status)
        self.assertFalse(decision.meta_discussion_substitutes_for_effect)

    def test_correction_preserves_exact_blocker_when_effect_cannot_execute(self):
        clause = PragmaticClause(
            raw="Bug report",
            action_id="CREATE_BUG_REPORT",
            force=CommandForce.AMBIGUOUS,
            target=None,
            hedge_terms=(),
            hedge_scope=HedgeScope.NONE,
            uncertainty_preserved=False,
        )
        decision = apply_command_force_correction(
            clause,
            corrected_as_command=True,
            context=ExecutionContext(
                target_sufficient=True,
                authority_sufficient=True,
                currentness_sufficient=True,
                tools_sufficient=False,
            ),
        )
        self.assertEqual(ExecutionStatus.BLOCKED, decision.status)
        self.assertEqual(("TOOLS",), decision.blockers)


    def test_known_action_phrase_does_not_promote_arbitrary_declarative_text(self):
        clause = parse_pragmatic_command(
            "Bug report would be useful",
            established_action_context=True,
        )[0]
        self.assertEqual(CommandForce.AMBIGUOUS, clause.force)

    def test_question_form_is_not_silently_promoted_to_command(self):
        clause = parse_pragmatic_command(
            "a note for Noema?",
            established_action_context=True,
        )[0]
        self.assertEqual(CommandForce.AMBIGUOUS, clause.force)


    def test_malformed_mode_boolean_fails_closed(self):
        with self.assertRaises(Exception):
            resolve_behavior_mode(
                BehaviorModeContext(
                    active_mode=BehaviorMode.RESEARCH_REPORT,
                    specialized_task_complete="yes",
                    context_changed=True,
                )
            )

    def test_malformed_execution_boolean_fails_closed(self):
        clause = parse_pragmatic_command(
            "Bug report",
            established_action_context=True,
        )[0]
        with self.assertRaises(Exception):
            decide_execution(
                clause,
                ExecutionContext(
                    target_sufficient=True,
                    authority_sufficient="yes",
                    currentness_sufficient=True,
                    tools_sufficient=True,
                ),
            )


    def test_conflicting_current_mode_directives_fail_closed(self):
        with self.assertRaises(Exception):
            resolve_behavior_mode(
                BehaviorModeContext(
                    active_mode=BehaviorMode.RESEARCH_REPORT,
                    specialized_task_complete=True,
                    context_changed=True,
                    explicit_continue_specialized_mode=True,
                    voice_context_correction=True,
                )
            )

    def test_cross_entry_phrase_collision_cannot_route_action(self):
        from tools.behavioral_integrity_policy import ActionLexiconEntry
        collision = (
            ActionLexiconEntry(action_id="CREATE_NOTE", phrases=("note",)),
            ActionLexiconEntry(action_id="DELETE_NOTE", phrases=("note",)),
        )
        with self.assertRaises(Exception):
            parse_pragmatic_command(
                "note",
                established_action_context=True,
                lexicon=collision,
            )

    def test_duplicate_action_id_with_incompatible_phrases_fails_closed(self):
        from tools.behavioral_integrity_policy import ActionLexiconEntry
        collision = (
            ActionLexiconEntry(action_id="CREATE_NOTE", phrases=("note",)),
            ActionLexiconEntry(action_id="CREATE_NOTE", phrases=("memo",)),
        )
        with self.assertRaises(Exception):
            parse_pragmatic_command(
                "note",
                established_action_context=True,
                lexicon=collision,
            )


if __name__ == "__main__":
    unittest.main()
