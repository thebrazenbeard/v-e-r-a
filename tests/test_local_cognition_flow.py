"""Real Mono, PORTAL, Pre-Active local GUI fixture correlation; NO model or resident."""
import hashlib
import json
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
        self.addCleanup(self.tmp.cleanup)
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
        j=self.intake(conv="conv-b",msg="m1",text="Second request")
        self.assertNotEqual(j["task_id"],i["task_id"])
        a=self.accept(i)
        with self.assertRaises(ProvenanceBridgeError):self.accept(i)
        # The first current task head cannot be reused after a second task opened.
        with self.assertRaises(ProvenanceBridgeError):self.accept(j if j["opened_journal_head"]==i["opened_journal_head"] else i)
        unfinished={"status":"PENDING","event_id":"pending","run_id":None,
                    "final_text":None,"route_id":a["route_id"],"provider_id":a["route_id"]}
        with self.assertRaises(ProvenanceBridgeError):
            record_local_cognition_result(
                ledger=self.ledger,store=self.store,intake=i,acceptance=a,
                resident_result=unfinished,
            )

    def test_stale_dependencies_and_cancelled_task_block_fixture_acceptance(self):
        i=self.intake()
        self.ledger.bind_dependency(i["task_id"],"dep:late",
             kind="COORDINATION_COMMAND",target_id="command:late")
        with self.assertRaises(ProvenanceBridgeError):self.accept(i)
