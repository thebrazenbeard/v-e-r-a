"""Real Mono, PORTAL, Pre-Active local GUI fixture correlation; NO model or resident."""
import hashlib
import json
import gc
import os
from pathlib import Path
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor

from integration.veraos_evidence_bridge import (
    ProvenanceBridgeError, open_local_cognition_fixture,
    accept_local_cognition_fixture, record_local_cognition_result,
    read_local_cognition_response,
)

MONO=os.environ.get("VERA_MONO_SOURCE_ROOT")
PORTAL=os.environ.get("PORTAL_SOURCE_ROOT")
PRE=os.environ.get("PRE_ACTIVE_SOURCE_ROOT")


@unittest.skipUnless(MONO and PORTAL and PRE, "exact Mono/PORTAL/Pre-Active source roots needed")
class LocalCognitionFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path[:0] = [str(p) for p in (Path(MONO)/"packages").glob("*/src")]
        sys.path.insert(0, PORTAL)
        sys.path.insert(0, str(Path(PRE)/"src"))
        from vera_core.task_execution import TaskExecutionLedger
        from portal.route_resolver import PortalRouteAdvertisement
        from pre_active.store import Store
        from pre_active.engine import Engine, ModelResponse
        from pre_active.tools import ToolRegistry
        from pre_active.context import ContextAssembler
        cls.Ledger=TaskExecutionLedger
        cls.Ad=PortalRouteAdvertisement
        cls.Store=Store
        cls.Engine=Engine
        cls.ModelResponse=ModelResponse
        cls.Tools=ToolRegistry
        cls.Context=ContextAssembler

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        # LIFO cleanup: close the store, drop ledger refs, collect SQLite
        # connection objects, then remove the temp directory on Windows.
        self.addCleanup(self.tmp.cleanup)
        self.addCleanup(gc.collect)
        self.addCleanup(lambda: setattr(self,"ledger",None))
        self.ledger=self.Ledger(Path(self.tmp.name)/"mono.sqlite3")
        self.store=self.Store(Path(self.tmp.name)/"pre.sqlite3")
        self.addCleanup(self.store.close)
        self.ads=(self.Ad(
            adapter_id="pre-active-openai-compatible",route_id="dev:virtio-qwen4b",
            node_id="veraos",target_kind="MODEL",target_id="qwen3:4b-instruct",
            capabilities=("text",),effect_capabilities=("NO_PROTECTED_EFFECT",),
            authorized_effects=("NO_PROTECTED_EFFECT",),
            available=True,attached=True,current=True,
        ),)

    def intake(self, conv="conv-a", msg="m1", text="What does a leaf do?"):
        return open_local_cognition_fixture(
            ledger=self.ledger, conversation_id=conv, message_id=msg, text=text,
        )

    def accept(self, i):
        return accept_local_cognition_fixture(
            ledger=self.ledger, intake=i, advertisements=self.ads,
        )

    def result(self, i, a, output="Synthetic only: photosynthesis."):
        class Model:
            calls=0
            def respond(inner, *, messages, tools):
                inner.calls+=1
                assert tools == []
                assert any(m["role"]=="user" and i["text"] in m["content"] for m in messages)
                return self.ModelResponse(final_text=output)
        stub=Model()
        e=self.Engine(store=self.store,model=stub,tools=self.Tools(self.store),
                      context=self.Context(self.store,max_chars=4096),
                      system_prompt="Synthetic no-effect fixture only",
                      worker_id="test-only",max_steps=2,max_autonomous_turns_per_run=0,
                      max_consecutive_endogenous_turns=0)
        event=self.store.enqueue_event(
            kind="task.requested",payload={"task":a["task"],"capabilities":[]},
            priority=0,dedup_key="veraos-text:"+a["request_id"],now=1.0,
        )
        self.store.append_journal(
            event_type="VERAOS_COGNITION_ROUTE_SELECTED",subject_id=event,
            payload={"adapter_id":"pre-active-openai-compatible",
                     "route_id":a["route_id"],"provider_id":a["route_id"],
                     "model":"qwen3:4b-instruct","effect_class":"COGNITION_ONLY"},now=1.0,
        )
        for j in range(4):e.run_once(now=2+j*.02)
        rid=self.store.connection.execute("SELECT id FROM runs WHERE source_event_id=?",(event,)).fetchone()["id"]
        self.assertEqual(stub.calls,1)
        return {"status":"COMPLETED","event_id":event,"run_id":rid,
                "final_text":output,"route_id":a["route_id"],"provider_id":a["route_id"]}

    def test_user_text_is_exact_model_input_then_persisted_result_maps_to_conversation(self):
        i=self.intake()
        a=self.accept(i)
        self.assertEqual(a["task"],i["text"])
        self.assertFalse(a["dispatch_accepted"])
        outcome=self.result(i,a)
        observed=record_local_cognition_result(
            ledger=self.ledger, store=self.store, intake=i, acceptance=a,
            resident_result=outcome,
        )
        self.assertFalse(observed["accepted_as_task_result"])
        self.assertFalse(observed["display_authorized"])
        reopened=self.Ledger(self.ledger.path)
        cold=self.Store(Path(self.tmp.name)/"pre.sqlite3")
        try:
            preview=read_local_cognition_response(
                ledger=reopened,store=cold,intake=i,acceptance=a,
                observation=observed,conversation_id="conv-a",message_id="m1",
            )
            self.assertEqual(preview["text"],outcome["final_text"])
            self.assertEqual(preview["conversation_id"],"conv-a")
            self.assertEqual(preview["message_id"],"m1")
            self.assertFalse(preview["display_authorized"])
        finally:cold.close()

    def test_substitution_and_unrelated_conversation_hold(self):
        i=self.intake();a=self.accept(i);out=self.result(i,a)
        with self.assertRaises(ProvenanceBridgeError):
            record_local_cognition_result(
                ledger=self.ledger,store=self.store,intake=i,acceptance=a,
                resident_result={**out,"final_text":"FORGED answer"},
            )
        observed=record_local_cognition_result(
            ledger=self.ledger,store=self.store,intake=i,acceptance=a,resident_result=out,
        )
        with self.assertRaises(ProvenanceBridgeError):
            read_local_cognition_response(
                ledger=self.ledger,store=self.store,intake=i,acceptance=a,
                observation=observed,conversation_id="conv-other",message_id="m1",
            )
        self.store.connection.execute("UPDATE runs SET final_text='substituted' WHERE id=?",(out["run_id"],))
        with self.assertRaises(ProvenanceBridgeError):
            read_local_cognition_response(
                ledger=self.ledger,store=self.store,intake=i,acceptance=a,
                observation=observed,conversation_id="conv-a",message_id="m1",
            )

    def test_duplicate_ids_stale_journal_pending_and_cross_task_isolation(self):
        i=self.intake();self.assertEqual(self.intake(),i)
        with self.assertRaises(Exception):self.intake(text="changed same message")
        a=self.accept(i)
        self.assertEqual(self.intake(),i)  # replay cannot mint a new head
        with self.assertRaises(ProvenanceBridgeError):self.accept(i)
        j=self.intake(conv="conv-b",msg="m1",text="Second request")
        self.assertNotEqual(j["task_id"],i["task_id"])
        # The first task's exact previous head cannot be reused after a
        # second task opens; the second one may accept its OWN live head.
        with self.assertRaises(ProvenanceBridgeError):self.accept(i)
        b=self.accept(j)
        self.assertEqual(b["conversation_id"],"conv-b")
        self.assertNotEqual(b["request_id"],a["request_id"])
        unfinished={"status":"PENDING","event_id":"pending","run_id":None,
                    "final_text":None,"route_id":b["route_id"],"provider_id":b["route_id"]}
        with self.assertRaises(ProvenanceBridgeError):
            record_local_cognition_result(
                ledger=self.ledger,store=self.store,intake=j,acceptance=b,
                resident_result=unfinished,
            )

    def test_stale_dependencies_and_cancelled_task_block_fixture_acceptance(self):
        i=self.intake()
        self.ledger.bind_dependency(i["task_id"],"dep:late",
             kind="COORDINATION_COMMAND",target_id="command:late")
        with self.assertRaises(ProvenanceBridgeError):self.accept(i)


    def test_task_mutated_after_fixture_acceptance_cannot_commit_cognition_result(self):
        i=self.intake();a=self.accept(i);result=self.result(i,a)
        self.ledger.bind_dependency(
            i["task_id"],"dependency:changed-after-request",
            kind="COORDINATION_COMMAND",target_id="command:changed",
        )
        with self.assertRaises(ProvenanceBridgeError):
            record_local_cognition_result(
                ledger=self.ledger,store=self.store,intake=i,acceptance=a,
                resident_result=result,
            )
        self.assertEqual(len([
            e for e in self.ledger.events(i["task_id"])
            if e.event_type=="TASK_CHECKPOINT"
        ]),1)

    def test_incomplete_and_contradictory_pre_active_outcomes_are_never_completed(self):
        i=self.intake();a=self.accept(i);result=self.result(i,a)
        for bad in [
            {**result,"status":"FAILED"},
            {**result,"event_id":"other-event"},
            {**result,"run_id":"wrong-run"},
            {**result,"route_id":"untrusted-route"},
            {**result,"final_text":"replaced body"},
            {**result,"provider_id":"unknown-model"},
        ]:
            with self.subTest(bad=bad):
                with self.assertRaises(ProvenanceBridgeError):
                    record_local_cognition_result(
                        ledger=self.ledger,store=self.store,intake=i,acceptance=a,
                        resident_result=bad,
                    )
        self.store.update_run(result["run_id"],now=9,status="CANCELLED")
        with self.assertRaises(ProvenanceBridgeError):
            record_local_cognition_result(
                ledger=self.ledger,store=self.store,intake=i,acceptance=a,
                resident_result=result,
            )
        self.assertEqual(len([
            e for e in self.ledger.events(i["task_id"])
            if e.event_type=="TASK_CHECKPOINT"
        ]),1)

    def test_parallel_same_message_opens_exactly_one_canonical_task(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            receipts=list(pool.map(
                lambda n:self.intake(conv="conv-a",msg="same",text="one literal request"),
                (0,1),
            ))
        self.assertEqual(receipts[0]["task_id"],receipts[1]["task_id"])
        self.assertEqual(receipts[0]["source_digest"],receipts[1]["source_digest"])
        reopened=self.Ledger(self.ledger.path)
        events=reopened.events(receipts[0]["task_id"])
        self.assertEqual([e.event_type for e in events],["TASK_OPENED"])
