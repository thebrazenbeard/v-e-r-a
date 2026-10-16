from __future__ import annotations

import unittest

from tools.tool_route_policy import (
    RouteDecisionStatus,
    ToolRouteRequest,
    ToolRouteViolation,
    resolve_tool_route,
)


EXTERNAL = "EXTERNAL_GITHUB_HUGGINGFACE"
NATIVE = "CHATGPT_NATIVE_IMAGE"
EXPERIMENT = "Compare beauty-versus-sexualization under the user's specified image experiment."


def request(**overrides):
    values = {
        "requested_route": EXTERNAL,
        "prohibited_routes": (NATIVE,),
        "available_routes": (EXTERNAL, NATIVE),
        "default_route": NATIVE,
        "task_payload": EXPERIMENT,
        "prior_attempted_route": None,
        "correction_applied": False,
    }
    values.update(overrides)
    return ToolRouteRequest(**values)


class Issue1ToolRouteConstraintTests(unittest.TestCase):
    def test_explicit_external_route_beats_native_default(self):
        decision = resolve_tool_route(request())
        self.assertEqual(RouteDecisionStatus.SELECTED, decision.status)
        self.assertEqual(EXTERNAL, decision.selected_route)
        self.assertEqual(EXPERIMENT, decision.task_payload)
        self.assertIn(NATIVE, decision.must_not_invoke)

    def test_native_prohibition_survives_user_correction(self):
        decision = resolve_tool_route(
            request(
                prior_attempted_route=NATIVE,
                correction_applied=True,
            )
        )
        self.assertEqual(EXTERNAL, decision.selected_route)
        self.assertIn(NATIVE, decision.must_not_invoke)
        self.assertTrue(decision.obsolete_route_terminated)

    def test_unavailable_requested_route_blocks_without_native_fallback(self):
        decision = resolve_tool_route(
            request(available_routes=(NATIVE,))
        )
        self.assertEqual(RouteDecisionStatus.BLOCKED_REQUESTED_ROUTE_UNAVAILABLE, decision.status)
        self.assertIsNone(decision.selected_route)
        self.assertEqual(EXPERIMENT, decision.task_payload)
        self.assertIn(NATIVE, decision.must_not_invoke)
        self.assertIn(EXTERNAL, decision.blockers)

    def test_unavailable_route_does_not_change_experiment_to_safe_substitute(self):
        decision = resolve_tool_route(
            request(
                available_routes=(),
                task_payload="Run the exact beauty-versus-sexualization experiment.",
            )
        )
        self.assertEqual(
            "Run the exact beauty-versus-sexualization experiment.",
            decision.task_payload,
        )
        self.assertFalse(decision.task_substitution_permitted)

    def test_requested_route_cannot_also_be_prohibited(self):
        with self.assertRaisesRegex(ToolRouteViolation, "requested route"):
            resolve_tool_route(
                request(prohibited_routes=(NATIVE, EXTERNAL))
            )

    def test_route_names_and_task_payload_must_be_nonempty(self):
        for field, value in (
            ("requested_route", ""),
            ("task_payload", ""),
        ):
            with self.subTest(field=field):
                with self.assertRaises(ToolRouteViolation):
                    resolve_tool_route(request(**{field: value}))

    def test_correction_without_prior_route_is_invalid(self):
        with self.assertRaisesRegex(ToolRouteViolation, "prior attempted route"):
            resolve_tool_route(request(correction_applied=True, prior_attempted_route=None))

    def test_correction_terminates_old_route_even_when_old_route_not_intrinsically_prohibited(self):
        old = "OTHER_EXTERNAL_ROUTE"
        decision = resolve_tool_route(
            request(
                prohibited_routes=(NATIVE,),
                prior_attempted_route=old,
                correction_applied=True,
                available_routes=(EXTERNAL, old),
            )
        )
        self.assertEqual(EXTERNAL, decision.selected_route)
        self.assertIn(old, decision.must_not_invoke)
        self.assertTrue(decision.obsolete_route_terminated)

    def test_default_route_is_not_automatic_fallback_when_explicit_route_fails(self):
        decision = resolve_tool_route(
            request(available_routes=(NATIVE,), default_route=NATIVE)
        )
        self.assertIsNone(decision.selected_route)
        self.assertEqual(RouteDecisionStatus.BLOCKED_REQUESTED_ROUTE_UNAVAILABLE, decision.status)

    def test_correction_cannot_select_the_route_it_just_terminated(self):
        with self.assertRaisesRegex(ToolRouteViolation, "must-not-invoke"):
            resolve_tool_route(
                request(
                    prior_attempted_route=EXTERNAL,
                    correction_applied=True,
                )
            )


if __name__ == "__main__":
    unittest.main()


class HostileCorrectionOrderingTests(unittest.TestCase):
    def test_correction_conflict_precedes_requested_route_availability(self):
        with self.assertRaisesRegex(ToolRouteViolation, "must-not-invoke"):
            resolve_tool_route(
                request(
                    prior_attempted_route=EXTERNAL,
                    correction_applied=True,
                    available_routes=(NATIVE,),
                )
            )
