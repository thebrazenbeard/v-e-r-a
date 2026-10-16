from __future__ import annotations

import unittest

from tools.orgasm_optional_invocation_route import (
    COMMAND_ID,
    SCHEMA,
    RouteEvidenceInput,
    build_route_evidence,
    classify_availability,
    current_source_only_evidence,
)


class OrgasmOptionalInvocationRouteTests(unittest.TestCase):
    def test_source_only_state_fails_closed_as_unknown(self) -> None:
        evidence = current_source_only_evidence("source-only-test")
        self.assertEqual(evidence["schema"], SCHEMA)
        self.assertEqual(evidence["command_id"], COMMAND_ID)
        self.assertEqual(evidence["availability"], "UNKNOWN")
        self.assertEqual(evidence["install_state"], "UNKNOWN")
        self.assertEqual(evidence["route_state"], "UNKNOWN")
        self.assertEqual(evidence["runtime_consumption_state"], "UNKNOWN")
        self.assertEqual(evidence["adapter_state"], "UNKNOWN")
        self.assertEqual(evidence["qualification_state"], "UNKNOWN")

    def test_fully_current_qualified_route_is_available_qualified(self) -> None:
        value = RouteEvidenceInput(
            source_revision="qualified",
            install_state="CURRENT",
            route_state="ACTIVE_CURRENT",
            runtime_consumption_state="VERIFIED_CURRENT",
            adapter_state="CURRENT",
            qualification_state="QUALIFIED",
            observed_at="2026-09-20T22:00:00Z",
        )
        self.assertEqual(classify_availability(value), "AVAILABLE_QUALIFIED")

    def test_fully_current_test_route_is_available_test_only(self) -> None:
        value = RouteEvidenceInput(
            source_revision="test-only",
            install_state="CURRENT",
            route_state="ACTIVE_CURRENT",
            runtime_consumption_state="VERIFIED_CURRENT",
            adapter_state="CURRENT",
            qualification_state="TEST_ONLY",
            observed_at="2026-09-20T22:00:00Z",
        )
        self.assertEqual(classify_availability(value), "AVAILABLE_TEST_ONLY")

    def test_conflict_or_unknown_dominates(self) -> None:
        conflict = RouteEvidenceInput(
            source_revision="conflict",
            install_state="CURRENT",
            route_state="CONFLICT",
            runtime_consumption_state="VERIFIED_CURRENT",
            adapter_state="CURRENT",
            qualification_state="QUALIFIED",
        )
        unknown = RouteEvidenceInput(
            source_revision="unknown",
            install_state="UNKNOWN",
            route_state="ACTIVE_CURRENT",
            runtime_consumption_state="VERIFIED_CURRENT",
            adapter_state="CURRENT",
            qualification_state="QUALIFIED",
        )
        self.assertEqual(classify_availability(conflict), "UNKNOWN")
        self.assertEqual(classify_availability(unknown), "UNKNOWN")

    def test_authoritative_negative_axis_is_unavailable(self) -> None:
        value = RouteEvidenceInput(
            source_revision="negative",
            install_state="CURRENT",
            route_state="ACTIVE_CURRENT",
            runtime_consumption_state="NOT_VERIFIED",
            adapter_state="CURRENT",
            qualification_state="QUALIFIED",
        )
        self.assertEqual(classify_availability(value), "UNAVAILABLE")

    def test_evidence_id_is_deterministic_for_same_bound_material(self) -> None:
        value = RouteEvidenceInput(
            source_revision="same",
            install_state="CURRENT",
            route_state="ACTIVE_CURRENT",
            runtime_consumption_state="VERIFIED_CURRENT",
            adapter_state="CURRENT",
            qualification_state="TEST_ONLY",
            observed_at="2026-09-20T22:00:00Z",
        )
        first = build_route_evidence(value)
        second = build_route_evidence(value)
        self.assertEqual(first["evidence_id"], second["evidence_id"])
        self.assertEqual(len(first["evidence_id"]), 64)


if __name__ == "__main__":
    unittest.main()
