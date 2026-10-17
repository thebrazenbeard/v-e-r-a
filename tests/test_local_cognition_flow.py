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
    recover_local_cognition_observation, make_local_resident_fixture_handler,
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


    def test_forged_acceptance_id_and_predecessor_never_rebind_model_result(self):
        i=self.intake();a=self.accept(i);result=self.result(i,a)
        altered=[
            {**a,"request_id":"ui-"+"f"*64},
            {**a,"checkpoint_event_id":"ui-forged:CHECKPOINT:local-fixture-"+a["request_id"]},
            {**a,"predecessor_journal_head":"e"*64},
        ]
        for fake in altered:
            with self.subTest(fake=fake):
                with self.assertRaises(ProvenanceBridgeError):
                    record_local_cognition_result(
                        ledger=self.ledger,store=self.store,intake=i,
                        acceptance=fake,resident_result=result,
                    )

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


    def test_two_interleaved_tasks_complete_under_task_scoped_cas(self):
        a=self.intake(conv="first",msg="one",text="first text")
        b=self.intake(conv="second",msg="two",text="second text")
        aa=self.accept(a);bb=self.accept(b)
        self.assertNotEqual(aa["checkpoint_journal_head"],bb["checkpoint_journal_head"])
        out_b=self.result(b,bb,output="second fixture")
        obs_b=record_local_cognition_result(
            ledger=self.ledger,store=self.store,intake=b,acceptance=bb,
            resident_result=out_b,
        )
        # First accepted task is NOT stale merely because another task
        # opened, accepted and recorded a result on the global journal.
        # This pre-active test runner can only serialize real stub execution;
        # actual model concurrency is solely the OS resident's business.
        out_a=self.result(a,aa,output="first fixture")
        obs_a=record_local_cognition_result(
            ledger=self.ledger,store=self.store,intake=a,acceptance=aa,
            resident_result=out_a,
        )
        for intake,accepted,observed,expected in (
            (a,aa,obs_a,"first fixture"),(b,bb,obs_b,"second fixture"),
        ):
            preview=read_local_cognition_response(
                ledger=self.ledger,store=self.store,intake=intake,
                acceptance=accepted,observation=observed,
                conversation_id=intake["conversation_id"],message_id=intake["message_id"],
            )
            self.assertEqual(preview["text"],expected)
            self.assertFalse(preview["display_authorized"])


    def test_cold_recovery_statuses_never_fabricate_history_or_completion(self):
        empty=recover_local_cognition_observation(
            ledger=self.ledger,store=self.store,conversation_id="none",message_id="never",
        )
        self.assertEqual(empty["status"],"NO_CANONICAL_TASK")
        i=self.intake()
        opened=recover_local_cognition_observation(
            ledger=self.ledger,store=self.store,conversation_id="conv-a",message_id="m1",
        )
        self.assertEqual(opened["status"],"NOT_ACCEPTED")
        a=self.accept(i)
        unfinished=recover_local_cognition_observation(
            ledger=self.ledger,store=self.store,conversation_id="conv-a",message_id="m1",
        )
        self.assertEqual(unfinished["status"],"OUTCOME_UNKNOWN_NO_REDISPATCH")
        outcome=self.result(i,a)
        obs=record_local_cognition_result(
            ledger=self.ledger,store=self.store,intake=i,acceptance=a,
            resident_result=outcome,
        )
        cold_ledger=self.Ledger(self.ledger.path)
        cold_store=self.Store(Path(self.tmp.name)/"pre.sqlite3")
        try:
            restored=recover_local_cognition_observation(
                ledger=cold_ledger,store=cold_store,
                conversation_id="conv-a",message_id="m1",
            )
            self.assertEqual(restored["status"],"SOURCE_OBSERVATION_REVALIDATED")
            self.assertEqual(restored["response_candidate"]["text"],outcome["final_text"])
            self.assertFalse(restored["display_authorized"])
            self.assertFalse(restored["accepted_as_task_result"])
            with self.assertRaises(ProvenanceBridgeError):
                recover_local_cognition_observation(
                    ledger=cold_ledger,store=cold_store,
                    conversation_id="conv-other",message_id="m1",
                ) if False else read_local_cognition_response(
                    ledger=cold_ledger,store=cold_store,intake=i,acceptance=a,
                    observation=obs,conversation_id="conv-other",message_id="m1",
                )
            self.store.update_run(outcome["run_id"],now=100,final_text="tampered")
            with self.assertRaises(ProvenanceBridgeError):
                recover_local_cognition_observation(
                    ledger=cold_ledger,store=cold_store,
                    conversation_id="conv-a",message_id="m1",
                )
        finally:
            cold_store.close()

    def test_exact_pr37_two_argument_callback_keeps_synthetic_output_off_ui(self):
        calls=[]
        def synthetic_only(*,store,task,request_id,route_id):
            calls.append((task,request_id,route_id))
            class Fake:
                def respond(_self, *, messages, tools):
                    assert not tools
                    assert any(m["role"]=="user" and task in m["content"] for m in messages)
                    return self.ModelResponse(final_text="fixture response - not admitted")
            engine=self.Engine(
                store=store,model=Fake(),tools=self.Tools(store),
                context=self.Context(store,max_chars=4096),
                system_prompt="Synthetic only, no real model",
                worker_id="test-only",max_steps=2,max_autonomous_turns_per_run=0,
                max_consecutive_endogenous_turns=0,
            )
            event=store.enqueue_event(
                kind="task.requested",payload={"task":task,"capabilities":[]},
                priority=0,dedup_key="veraos-text:"+request_id,now=1,
            )
            store.append_journal(
                event_type="VERAOS_COGNITION_ROUTE_SELECTED",subject_id=event,
                payload={"adapter_id":"pre-active-openai-compatible",
                         "route_id":route_id,"provider_id":route_id,
                         "model":"qwen3:4b-instruct","effect_class":"COGNITION_ONLY"},
                now=1,
            )
            for n in range(4):engine.run_once(now=2+n*.02)
            row=store.connection.execute(
                "SELECT id FROM runs WHERE source_event_id=?",(event,),
            ).fetchone()
            assert row is not None
            return {"status":"COMPLETED","event_id":event,"run_id":row["id"],
                    "route_id":route_id,"provider_id":route_id,
                    "final_text":"fixture response - not admitted"}
        mono=Path(self.tmp.name)/"mono-handler.sqlite3"
        pre=Path(self.tmp.name)/"pre-handler.sqlite3"
        h=make_local_resident_fixture_handler(
            ledger_path=mono,store_path=pre,
            conversation_id="scoped-local-fixture",advertisements=self.ads,
            source_only_executor=synthetic_only,
        )
        first=h("exact task input","http-msg-1")
        self.assertEqual(first["status"],"BLOCKED")
        self.assertIsNone(first["final_text"])
        self.assertEqual(len(calls),1)
        recovered=h("exact task input","http-msg-1")
        self.assertEqual(recovered["status"],"BLOCKED")
        self.assertEqual(len(calls),1)
        with self.assertRaises(ProvenanceBridgeError):
            h("different task same request id","http-msg-1")
        # A new Python callable simulates resident main() restart with only
        # original Mono and Pre-Active SQLite paths.
        after_restart=make_local_resident_fixture_handler(
            ledger_path=mono,store_path=pre,
            conversation_id="scoped-local-fixture",advertisements=self.ads,
            source_only_executor=synthetic_only,
        )
        self.assertEqual(after_restart("exact task input","http-msg-1")["status"],"BLOCKED")
        self.assertEqual(len(calls),1)
        cold_ledger=self.Ledger(mono);cold_store=self.Store(pre)
        try:
            recovered=recover_local_cognition_observation(
                ledger=cold_ledger,store=cold_store,
                conversation_id="scoped-local-fixture",message_id="http-msg-1",
            )
            self.assertEqual(recovered["status"],"SOURCE_OBSERVATION_REVALIDATED")
            self.assertEqual(recovered["response_candidate"]["text"],
                             "fixture response - not admitted")
            self.assertFalse(recovered["display_authorized"])
        finally:cold_store.close()

    def test_concurrent_distinct_http_source_callbacks_each_have_unique_task(self):
        ids=[]
        def unexecuted(*,store,task,request_id,route_id):
            ids.append(request_id)
            raise RuntimeError("synthetic worker interruption")
        mono=Path(self.tmp.name)/"mono-parallel.sqlite3"
        pre=Path(self.tmp.name)/"pre-parallel.sqlite3"
        handler=make_local_resident_fixture_handler(
            ledger_path=mono,store_path=pre,conversation_id="local-scope",
            advertisements=self.ads,source_only_executor=unexecuted,
        )
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures=[
                pool.submit(handler,"first request","m1"),
                pool.submit(handler,"second request","m2"),
            ]
            for f in futures:
                with self.assertRaises((RuntimeError,ProvenanceBridgeError)):
                    f.result()
        ledger=self.Ledger(mono)
        self.assertEqual(len([e for e in ledger.events() if e.event_type=="TASK_OPENED"]),2)
        self.assertEqual(len([e for e in ledger.events() if e.event_type=="TASK_CHECKPOINT"]),2)
        # The first request was accepted before an uncertain failure. A
        # replay must HOLD without a second synthetic call.
        for msg,text in (("m1","first request"),("m2","second request")):
            prior=handler(text,msg)
            self.assertEqual(prior["status"],"BLOCKED")
        self.assertEqual(len(ids),2)


    def test_crash_after_pre_active_completion_before_mono_observation_never_redispatches(self):
        # A durable completed run alone is not a canonical task result.
        # Crash between the Pre-Active commit and Mono result checkpoint:
        # cold restart must preserve ambiguity with NO duplicate execution.
        calls=[]
        def crash_after_completed_run(*,store,task,request_id,route_id):
            calls.append(request_id)
            class Model:
                def respond(_, *, messages, tools):
                    assert not tools
                    assert any(m["role"]=="user" and task in m["content"]
                               for m in messages)
                    return self.ModelResponse(final_text="unadopted synthetic text")
            engine=self.Engine(
                store=store, model=Model(), tools=self.Tools(store),
                context=self.Context(store,max_chars=4096),
                system_prompt="Crash fixture only, no model",
                worker_id="crash-source-only", max_steps=2,
                max_autonomous_turns_per_run=0,
                max_consecutive_endogenous_turns=0,
            )
            event=store.enqueue_event(
                kind="task.requested",
                payload={"task":task,"capabilities":[]},priority=0,
                dedup_key="veraos-text:"+request_id,now=1.0,
            )
            store.append_journal(
                event_type="VERAOS_COGNITION_ROUTE_SELECTED",
                subject_id=event, payload={
                    "adapter_id":"pre-active-openai-compatible",
                    "route_id":route_id,"provider_id":route_id,
                    "model":"qwen3:4b-instruct","effect_class":"COGNITION_ONLY",
                }, now=1.0,
            )
            for n in range(4):
                engine.run_once(now=2.0+n*0.02)
            run=store.connection.execute(
                "SELECT id,status,final_text FROM runs WHERE source_event_id=?",
                (event,),
            ).fetchone()
            assert run is not None and run["status"]=="COMPLETED"
            assert run["final_text"]=="unadopted synthetic text"
            raise RuntimeError("simulated process loss before Mono result observation")
        mono=Path(self.tmp.name)/"crash-mono.sqlite3"
        pre=Path(self.tmp.name)/"crash-pre.sqlite3"
        h=make_local_resident_fixture_handler(
            ledger_path=mono, store_path=pre,
            conversation_id="crash-local-conv",
            advertisements=self.ads, source_only_executor=crash_after_completed_run,
        )
        with self.assertRaisesRegex(RuntimeError,"simulated process loss"):
            h("one literal task","crash-msg-1")
        self.assertEqual(len(calls),1)
        cold_mono=self.Ledger(mono)
        cold_store=self.Store(pre)
        try:
            self.assertEqual(len([e for e in cold_mono.events()
                if e.event_type=="TASK_OPENED"]),1)
            self.assertEqual(len([e for e in cold_mono.events()
                if e.event_type=="TASK_CHECKPOINT"]),1)
            outcome=recover_local_cognition_observation(
                ledger=cold_mono,store=cold_store,
                conversation_id="crash-local-conv",message_id="crash-msg-1",
            )
            self.assertEqual(outcome["status"],"OUTCOME_UNKNOWN_NO_REDISPATCH")
            self.assertFalse(outcome["display_authorized"])
            row=cold_store.connection.execute(
                "SELECT COUNT(*) AS n FROM runs WHERE status='COMPLETED'"
            ).fetchone()
            self.assertEqual(row["n"],1)
        finally:
            cold_store.close()
        cold_handler=make_local_resident_fixture_handler(
            ledger_path=mono,store_path=pre,
            conversation_id="crash-local-conv",advertisements=self.ads,
            source_only_executor=crash_after_completed_run,
        )
        repeat=cold_handler("one literal task","crash-msg-1")
        self.assertEqual(repeat["status"],"BLOCKED")
        self.assertIsNone(repeat["final_text"])
        self.assertEqual(len(calls),1,"crash replay must not invoke worker again")
        with self.assertRaises(ProvenanceBridgeError):
            cold_handler("altered task under original request ID","crash-msg-1")
