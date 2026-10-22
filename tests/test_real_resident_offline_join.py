"""Actual VeraOS PR37 source HTTP -> Mono task -> PORTAL -> offline PreActive.

No installed PID1, QEMU, live Qwen or authenticated GUI session. Real source
handler returns BLOCKED even after persisted deterministic source completion.
"""
import gc
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
import urllib.error
import urllib.request

MONO=os.environ.get("VERA_MONO_SOURCE_ROOT")
PORTAL=os.environ.get("PORTAL_SOURCE_ROOT")
PRE=os.environ.get("PRE_ACTIVE_SOURCE_ROOT")
OS=os.environ.get("VERAOS_SOURCE_ROOT")
STAGE=os.environ.get("VERAOS_COMPONENTS_ROOT")


@unittest.skipUnless(all((MONO,PORTAL,PRE,OS,STAGE)),
                     "pinned Mono/PORTAL/PreActive/VeraOS source roots required")
class ActualResidentSourceJoinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path[:0]=[str(p) for p in (Path(MONO)/"packages").glob("*/src")]
        sys.path.insert(0,PORTAL)
        sys.path.insert(0,str(Path(PRE)/"src"))
        sys.path.insert(0,OS)
        sys.path.insert(0,str(Path(OS)/"tests"))
        from portal.route_resolver import PortalRouteAdvertisement
        from vera_core import VeraStateDirectory
        from vera_core.task_execution import TaskExecutionLedger
        from pre_active.store import Store
        from veraos import resident,desktop
        from source_only_offline_fixture import make_offline_fixture
        from integration.veraos_evidence_bridge import (
            make_local_resident_fixture_handler,
            recover_local_cognition_observation,
            ProvenanceBridgeError,
        )
        cls.Ad=PortalRouteAdvertisement
        cls.State=VeraStateDirectory
        cls.Ledger=TaskExecutionLedger
        cls.Store=Store
        cls.resident=resident
        cls.desktop=desktop
        cls.fixture=staticmethod(make_offline_fixture)
        cls.make_handler=staticmethod(make_local_resident_fixture_handler)
        cls.recover=staticmethod(recover_local_cognition_observation)
        cls.BridgeError=ProvenanceBridgeError

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.addCleanup(gc.collect)
        self.state=Path(self.tmp.name)/"state"
        self.run=Path(self.tmp.name)/"run"
        self.db=self.state/"pre-active.sqlite3"
        self.ledger=self.State(
            self.state/"vera-state",project_id="veraos",identity_id="VERA",
        ).task_execution_ledger().path
        self.ad=(self.Ad(
            adapter_id="pre-active-offline-fixture",route_id="offline-fixture",
            node_id="veraos",target_kind="MODEL",target_id="offline-deterministic",
            capabilities=("text",),
            effect_capabilities=("NO_PROTECTED_EFFECT",),
            authorized_effects=("NO_PROTECTED_EFFECT",),
            available=True,attached=True,current=True,
        ),)

    def test_current_pr37_http_worker_joins_real_mono_and_pre_active(self):
        execute,calls=self.fixture("offline exact receipt")
        def source_only_executor(*,store,task,request_id,route_id):
            self.assertEqual(route_id,"offline-fixture")
            return execute(task,request_id,store)
        handler=self.make_handler(
            ledger_path=self.ledger,store_path=self.db,
            conversation_id="one-local-conversation",
            advertisements=self.ad,source_only_executor=source_only_executor,
            offline_route=True,
        )
        servers=[]
        responses=[]
        old_server=self.resident.open_loopback_server
        old_status=self.resident.serve_status

        def bind_local(status_provider,**kwargs):
            srv=self.desktop.open_loopback_server(
                status_provider,port=0,**kwargs,
            )
            servers.append(srv)
            return srv

        def submit(_root,status,_stop):
            base=f"http://127.0.0.1:{servers[-1].server_port}"
            payload={"task":"One exact governed source request",
                     "request_id":"message-1"}
            req=urllib.request.Request(base+"/api/conversation",
                data=json.dumps(payload).encode("utf8"),headers={
                    "Origin":base,"Content-Type":"application/json",
                })
            with urllib.request.urlopen(req,timeout=10) as out:
                responses.append((out.status,json.loads(out.read())))
            self.assertFalse(status["cognition_route_qualified"])
            self.assertFalse(status["protected_effect_authority"])

        try:
            self.resident.open_loopback_server=bind_local
            self.resident.serve_status=submit
            argv=["--components-root",str(STAGE),"--state-root",str(self.state),
                  "--run-root",str(self.run)]
            self.assertEqual(self.resident.main(
                argv,source_fixture_execute=handler),0)
            self.assertEqual(len(calls),1)
            # A second resident instance reuses the same Mono/PreActive roots.
            self.assertEqual(self.resident.main(
                argv,source_fixture_execute=handler),0)
            self.assertEqual(len(calls),1)
        finally:
            self.resident.open_loopback_server=old_server
            self.resident.serve_status=old_status
        self.assertEqual([code for code,_ in responses],[202,202])
        self.assertEqual([r["status"] for _,r in responses],["BLOCKED","BLOCKED"])
        self.assertTrue(all(r["final_text"] is None for _,r in responses))
        led=self.Ledger(self.ledger)
        store=self.Store(self.db)
        try:
            recovered=self.recover(
                ledger=led,store=store,
                conversation_id="one-local-conversation",message_id="message-1",
            )
            self.assertEqual(recovered["status"],"SOURCE_OBSERVATION_REVALIDATED")
            self.assertFalse(recovered["display_authorized"])
            self.assertEqual(
                recovered["response_candidate"]["text"],"offline exact receipt",
            )
            self.assertEqual(len([
                e for e in led.events(recovered["task_id"])
                if e.event_type=="TASK_OPENED"
            ]),1)
            self.assertEqual(len([
                e for e in led.events(recovered["task_id"])
                if e.event_type=="TASK_CHECKPOINT"
            ]),2)
        finally:
            store.close()

    def test_offline_mode_rejects_qwen_advert_and_effect_escalation(self):
        execute,_=self.fixture()
        bad=self.Ad(
            adapter_id="pre-active-openai-compatible",
            route_id="dev:virtio-qwen4b",node_id="veraos",
            target_kind="MODEL",target_id="qwen3:4b-instruct",
            capabilities=("text",),
            effect_capabilities=("NO_PROTECTED_EFFECT",),
            authorized_effects=("NO_PROTECTED_EFFECT",),
            available=True,attached=True,current=True,
        )
        for advertisements in (
            (bad,),
            (self.Ad(
                adapter_id="pre-active-offline-fixture",route_id="offline-fixture",
                node_id="veraos",target_kind="MODEL",
                target_id="offline-deterministic",capabilities=("text",),
                effect_capabilities=("COGNITION_TURN",),
                authorized_effects=("COGNITION_TURN",),
                available=True,attached=True,current=True,
            ),),
        ):
            handler=self.make_handler(
                ledger_path=self.ledger,store_path=self.db,
                conversation_id="deny-conversation",
                advertisements=advertisements,
                source_only_executor=lambda **kw:execute(
                    kw["task"],kw["request_id"],kw["store"]),
                offline_route=True,
            )
            with self.assertRaises(self.BridgeError):
                handler("do not run","msg-1")
