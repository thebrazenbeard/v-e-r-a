from __future__ import annotations

import unittest

from tools.orgasm_optional_invocation_route import RouteEvidenceInput, classify_availability


class OptionalInvocationLiveNegativeTests(unittest.TestCase):
    def test_authoritative_negative_beats_other_unknown_axes(self) -> None:
        value = RouteEvidenceInput(
            source_revision="live-readback",
            install_state="UNKNOWN",
            route_state="UNKNOWN",
            runtime_consumption_state="NOT_VERIFIED",
            adapter_state="MISSING",
            qualification_state="UNKNOWN",
            observed_at="2026-09-20T22:50:00Z",
        )
        self.assertEqual(classify_availability(value), "UNAVAILABLE")


if __name__ == "__main__":
    unittest.main()
