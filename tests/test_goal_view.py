"""Volition read-only current-goal projection; no goal creation or effects."""

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from interface.goal_view import GoalViewError, project_volition_goal, read_goal_envelope
from interface.server import make_server
from interface.verified_volition import VerifiedVolitionGoalProvider
from tests.windows_acl_fixture import private_test_temporary_directory


def envelope(now):
    return {
        "schema": "vera.volition-view-envelope.v1",
        "captured_at_utc": now.isoformat(),
        "source_ref": "host-verified:volition/current-snapshot",
        "snapshot": {
            "schema": "VOLITION_OPERATIONAL_MOTIVATION_V1",
            "engine": {
                "schema": "VOLITION_STATE_V3",
                "active_goal": {
                    "goal_id": "goal-0001", "choice_id": "choice-0001", "target": "inspect-open-work-item",
                    "adoption_score": 0.7, "revision": 1, "status": "ACTIVE",
                    "effect_authority": False,
                },
                "choices": [{
                    "choice_id": "choice-0001", "want_target": "inspect-open-work-item",
                    "choice_class": "MODEL_PROPOSED", "source": "model:proposal-1",
                    "want_score": 0.7, "effect_authority": False,
                }],
            },
            "wants": [{"target": "inspect-open-work-item", "score": 0.7,
                       "eligible": True, "evidence_id": "obs-1", "proposal_id": "proposal-1",
                       "effect_authority": False}],
            "protection_latches": [],
        },
    }


class _RouteOnlyVerifiedProviderDouble(VerifiedVolitionGoalProvider):
    """Tests the HTTP authorization route, not host custody verification."""

    def __init__(self, now):
        self.now = now
        self.fail = False

    def read_projection(self):
        if self.fail:
            raise RuntimeError("private provider error")
        return project_volition_goal(envelope(self.now), now=self.now)


class GoalViewTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 27, 20, tzinfo=timezone.utc)

    def test_current_verified_projection_is_only_proposal_without_effect_authority(self):
        result = project_volition_goal(envelope(self.now), now=self.now)
        self.assertEqual(result["status"], "PROPOSED_REVIEW")
        self.assertEqual(result["goal_id"], "goal-0001")
        self.assertEqual(result["choice_class"], "MODEL_PROPOSED")
        self.assertEqual(result["suggestion"], "Review current status of: inspect-open-work-item")
        self.assertFalse(result["effect_authority"])
        self.assertNotIn("source", result)  # raw model prose must not be exposed

    def test_stale_goal_is_not_reissued_as_current(self):
        result = project_volition_goal(envelope(self.now - timedelta(minutes=7)), now=self.now)
        self.assertEqual(result, {"status": "HOLD_STALE", "effect_authority": False})

    def test_mismatched_or_privileged_choice_holds(self):
        for mutate in (
            lambda v: v["snapshot"]["engine"]["choices"][0].update({"want_target": "unrelated"}),
            lambda v: v["snapshot"]["engine"]["active_goal"].update({"effect_authority": True}),
            lambda v: v["snapshot"]["engine"]["choices"][0].update({"effect_authority": True}),
            lambda v: v["snapshot"]["wants"][0].update({"effect_authority": True}),
            lambda v: v["snapshot"]["protection_latches"].append("inspect-open-work-item"),
        ):
            with self.subTest(mutate=mutate):
                value = envelope(self.now)
                mutate(value)
                with self.assertRaises(GoalViewError):
                    project_volition_goal(value, now=self.now)

    def test_model_provenance_cannot_be_relabelled_self_authored_or_user_directed(self):
        for forged_class in ("SELF_AUTHORED", "USER_DIRECTED", "POLICY_DERIVED"):
            with self.subTest(forged_class=forged_class):
                value = envelope(self.now)
                value["snapshot"]["engine"]["choices"][0]["choice_class"] = forged_class
                with self.assertRaises(GoalViewError):
                    project_volition_goal(value, now=self.now)

    def test_self_authored_source_cannot_be_claimed_by_envelope_alone(self):
        for source in ("self:goal-1", "user:pat", "policy:approved", "arbitrary"):
            with self.subTest(source=source):
                value = envelope(self.now)
                value["snapshot"]["engine"]["choices"][0].update({
                    "choice_class": "SELF_AUTHORED", "source": source,
                })
                with self.assertRaises(GoalViewError):
                    project_volition_goal(value, now=self.now)

    def test_model_class_without_model_origin_claim_holds(self):
        value = envelope(self.now)
        value["snapshot"]["engine"]["choices"][0]["source"] = "user:pat"
        with self.assertRaises(GoalViewError):
            project_volition_goal(value, now=self.now)

    def test_no_active_goal_does_not_invent_one(self):
        value = envelope(self.now)
        value["snapshot"]["engine"]["active_goal"] = None
        self.assertEqual(project_volition_goal(value, now=self.now),
                         {"status": "NO_CURRENT_GOAL", "effect_authority": False})

    def test_snapshot_file_is_read_again_after_restart_and_rejects_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "volition.json"
            path.write_text(json.dumps(envelope(self.now)))
            self.assertEqual(read_goal_envelope(path, now=self.now)["status"], "PROPOSED_REVIEW")
            fresh = subprocess.run([sys.executable, "-c",
                "import json,sys;from datetime import datetime;from interface.goal_view import read_goal_envelope;"
                "print(json.dumps(read_goal_envelope(sys.argv[1],now=datetime.fromisoformat(sys.argv[2]))))",
                str(path), self.now.isoformat()], capture_output=True, text=True,
                cwd=Path(__file__).resolve().parents[1], check=True)
            self.assertEqual(json.loads(fresh.stdout)["status"], "PROPOSED_REVIEW")
            path.write_text('{"schema":"a","schema":"b"}')
            with self.assertRaises(GoalViewError):
                read_goal_envelope(path, now=self.now)

    def test_goal_route_requires_distinct_private_token_not_browser_session(self):
        now = datetime.now(timezone.utc)
        provider = _RouteOnlyVerifiedProviderDouble(now)
        server = make_server(port=0, goal_provider=provider,
                             goal_access_token="this-is-a-separately-custodied-operator-secret")
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        url = f"http://127.0.0.1:{server.server_port}/api/goals/current"
        for headers in ({}, {"X-Vera-Session": server.session_token},
                        {"X-Vera-Goal-Access": "wrong"}):
            with self.subTest(headers=headers), self.assertRaises(HTTPError) as caught:
                urlopen(Request(url, headers=headers), timeout=5)
            self.assertEqual(caught.exception.code, 403)
        with urlopen(Request(url, headers={"X-Vera-Goal-Access":
                "this-is-a-separately-custodied-operator-secret"}), timeout=5) as response:
            result = json.loads(response.read())
        self.assertEqual(result["status"], "PROPOSED_REVIEW")
        self.assertFalse(result["effect_authority"])
        provider.fail = True
        with self.assertRaises(HTTPError) as caught:
            urlopen(Request(url, headers={"X-Vera-Goal-Access":
                    "this-is-a-separately-custodied-operator-secret"}), timeout=5)
        self.assertEqual(caught.exception.code, 503)
        failure = json.loads(caught.exception.read())
        self.assertEqual(failure, {"status": "HOLD_UNVERIFIED", "effect_authority": False})

    def test_raw_callback_provider_refused(self):
        with self.assertRaises(ValueError):
            make_server(port=0, goal_provider=lambda: envelope(self.now),
                        goal_access_token="this-is-a-separately-custodied-operator-secret")

    def test_combined_memory_and_goals_keep_private_capabilities_separate(self):
        now = datetime.now(timezone.utc)
        vault_key = "distinct-local-transcript-secret-0123456789"
        goal_key = "distinct-private-goal-view-secret-0123456789"
        with private_test_temporary_directory() as root:
            server = make_server(
                port=0, goal_provider=_RouteOnlyVerifiedProviderDouble(now), goal_access_token=goal_key,
                memory_db_path=Path(root) / "vault.sqlite3", memory_secret=vault_key,
                acknowledge_plaintext_vault_risk=True)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                base = f"http://127.0.0.1:{server.server_port}"
                browser = {"X-Vera-Session": server.session_token,
                           "X-Vera-Vault-Key": vault_key}
                with self.assertRaises(HTTPError) as denied_goal:
                    urlopen(Request(base + "/api/goals/current", headers=browser), timeout=5)
                self.assertEqual(denied_goal.exception.code, 403)

                goal_only = {"X-Vera-Goal-Access": goal_key,
                             "X-Vera-Session": server.session_token}
                with self.assertRaises(HTTPError) as denied_memory:
                    urlopen(Request(base + "/api/transcript", headers=goal_only), timeout=5)
                self.assertEqual(denied_memory.exception.code, 403)

                with urlopen(Request(base + "/api/goals/current", headers=goal_only), timeout=5) as response:
                    self.assertEqual(json.loads(response.read())["status"], "PROPOSED_REVIEW")
                with urlopen(Request(base + "/api/transcript", headers=browser), timeout=5) as response:
                    memory = json.loads(response.read())
                self.assertEqual(memory["status"], "empty")
                self.assertEqual(memory["revision"], 0)
            finally:
                server.shutdown()
                server.server_close()


if __name__ == "__main__":
    unittest.main()
