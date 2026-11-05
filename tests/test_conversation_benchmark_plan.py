"""Public smoke benchmark is a plan, never evidence of model behavior."""

import json
import unittest

from benchmarks.conversation_v1 import build_plan


class ConversationBenchmarkPlanTests(unittest.TestCase):
    def test_exact_nine_source_only_cells_with_no_implied_model_inference(self):
        plan = build_plan()
        self.assertEqual(plan["evidence_class"], "SOURCE_ONLY_PLAN")
        self.assertEqual(plan["model_identity_attested"], False)
        self.assertEqual(len(plan["cells"]), 9)
        self.assertEqual({(row["arm"], row["max_tokens"]) for row in plan["cells"]},
                         {(arm, cap) for arm in ("official_base", "base_plus_seed",
                                                 "base_plus_correct_r16_seed")
                          for cap in (64, 96, 128)})
        for row in plan["cells"]:
            self.assertEqual(row["status"], "NOT_RUN")
            self.assertEqual(row["model_response"], None)
            self.assertEqual(row["latency_ms"], None)
            self.assertEqual(row["human_score"], None)
            self.assertEqual(row["weight_sha256"], None)
            self.assertEqual(row["owner_lease_receipt"], None)
            self.assertEqual(row["evaluation_custody"], "UNQUALIFIED")
        self.assertEqual(len(plan["public_smoke_cases"]), 4)
        self.assertEqual({case["id"] for case in plan["public_smoke_cases"]},
                         {"self_identification", "corrected_name", "dry_humor",
                          "memory_uncertainty"})
        self.assertTrue(all(1 <= len(case["turns"]) <= 3
                            for case in plan["public_smoke_cases"]))
        self.assertNotIn("PRIVATE", json.dumps(plan))

    def test_plan_is_deterministic_without_host_or_private_profile(self):
        self.assertEqual(json.dumps(build_plan(), sort_keys=True),
                         json.dumps(build_plan(), sort_keys=True))
        self.assertEqual(build_plan()["cells"][0]["max_tokens"], 64)
        self.assertEqual(build_plan()["cells"][-1]["max_tokens"], 128)


if __name__ == "__main__":
    unittest.main()
