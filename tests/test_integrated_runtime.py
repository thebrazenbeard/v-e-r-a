"""Standalone safety tests; real-two-repository smoke is separately required."""
from __future__ import annotations
import hashlib
import json
from contextlib import closing
from pathlib import Path
import sqlite3
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1]))
from integration import vera_portal_runtime as runner


class TaskPacket:
    def __init__(self, **values):
        self.values = values
        self.packet_digest = hashlib.sha256(json.dumps(values, sort_keys=True, default=list).encode()).hexdigest()
    def validate(self):
        assert self.values['purpose']


class Ledger:
    """Mock task ledger with deterministic SQLite handle release on Windows."""

    def __init__(self, file):
        self.file = file
        with closing(sqlite3.connect(self.file)) as db:
            db.execute('create table if not exists tasks (id text primary key, head text, packet text)')
            db.commit()

    def events(self):
        with closing(sqlite3.connect(self.file)) as db:
            return tuple(types.SimpleNamespace(task_id=r[0]) for r in db.execute('select id from tasks'))

    def open_task(self, task, packet, *, lifecycle_evidence_digest):
        with closing(sqlite3.connect(self.file)) as db:
            db.execute('insert into tasks values (?, ?, ?)', (task, 'a'*64, packet.packet_digest))
            db.commit()
        return types.SimpleNamespace(journal_head_digest='a'*64)

    def read(self, task):
        with closing(sqlite3.connect(self.file)) as db:
            row = db.execute('select head, packet from tasks where id=?', (task,)).fetchone()
        if row is None:
            raise KeyError(task)
        return row

class Advertisement:
    def __init__(self, **kwargs): self.data = kwargs


def export_request(ledger, task, **kwargs):
    head, packet = ledger.read(task)
    return {'task_id':task, 'journal':head, 'packet':packet, **kwargs}


def assess(request, adverts):
    eligible = [x for x in adverts if x.data['current'] and x.data['available'] and x.data['attached']]
    if not eligible: return {'state':'HELD','route':None,'reason':'NO_QUALIFIED_ADVISORY_ROUTE','assessment_digest':'b'*64}
    return {'state':'ROUTE_PROPOSED','route':{'route_id':eligible[0].data['route_id']},'reason':None,'assessment_digest':'c'*64}


def verify(ledger, request, assessment):
    head, packet = ledger.read(request['task_id'])
    if (request['journal'], request['packet']) != (head, packet):
        raise RuntimeError('stale journal')
    return assessment


COMPONENTS=(Ledger,TaskPacket,export_request,verify,assess,Advertisement)


class IntegratedRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.ledger=self.root/'state.sqlite3'
        self.packet=self.root/'packet.json'
        record = {
            'purpose':'Test restartable advisory', 'subject':'thebrazenbeard/portal@main',
            'completion_state':'verified evidence', 'evidence_requirements':['receipt'],
            'writable_scope':[], 'non_targets':['no writes'],
            'forbidden_shortcuts_or_effects':['no protected actions'],
            'priority_order':['safety'], 'unknowns':['host currentness'],
            'return_shape':['advisory'], 'relevant_surfaces':['current route'],
        }
        self.packet.write_text(json.dumps(record))
        self.patch=patch.object(runner,'components',lambda *_:COMPONENTS)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def args(self, action, **opts):
        return types.SimpleNamespace(action=action,vera_mono=self.root,portal=self.root,ledger=self.ledger,task='task-1',**opts)

    def test_open_route_hold_and_restart_verify(self):
        first=runner.execute(self.args('open',packet=self.packet,lifecycle_digest='f'*64))
        self.assertEqual(first['status'],'TASK_OPENED')
        with self.assertRaises(ValueError):
            runner.execute(self.args('open',packet=self.packet,lifecycle_digest='f'*64))
        receipt=self.root/'route.json'
        proposed=runner.execute(self.args('route',node='lappy',target_kind='repository',target='thebrazenbeard/portal',capability=['repository_read'],advertisements=None,receipt=receipt))
        self.assertEqual(proposed['status'],'HELD')
        self.assertFalse(proposed['executed'])
        self.assertFalse(proposed['effect_authority'])
        again=runner.execute(self.args('verify',receipt=receipt))
        self.assertEqual(again['status'],'ADVISORY_REVALIDATED')
        self.assertIsNone(again['route'])
        with self.assertRaises(ValueError):
            runner.execute(self.args('route',node='lappy',target_kind='repository',target='thebrazenbeard/portal',capability=['repository_read'],advertisements=None,receipt=receipt))
        with closing(sqlite3.connect(self.ledger)) as db:
            db.execute('update tasks set head=? where id=?', ('b'*64,'task-1'))
            db.commit()
        with self.assertRaisesRegex(RuntimeError,'stale journal'):
            runner.execute(self.args('verify',receipt=receipt))

    def test_advertised_route_is_not_execution(self):
        runner.execute(self.args('open',packet=self.packet,lifecycle_digest='f'*64))
        advertised=self.root/'advertisements.json'
        route={'adapter_id':'github','route_id':'read-only','node_id':'lappy','target_kind':'repository',
               'target_id':'thebrazenbeard/portal','capabilities':['repository_read'],
               'effect_capabilities':['NO_PROTECTED_EFFECT'],'authorized_effects':['NO_PROTECTED_EFFECT'],
               'available':True,'attached':True,'current':True}
        advertised.write_text(json.dumps([route]))
        res=runner.execute(self.args('route',node='lappy',target_kind='repository',target='thebrazenbeard/portal',capability=['repository_read'],advertisements=advertised,receipt=None))
        self.assertEqual(res['status'],'ROUTE_PROPOSED')
        self.assertFalse(res['effect_authority'])
        self.assertEqual(res['advertisement_currentness'],'CALLER_SUPPLIED_UNATTESTED')
        route['current']=False
        advertised.write_text(json.dumps([route]))
        res=runner.execute(self.args('route',node='lappy',target_kind='repository',target='thebrazenbeard/portal',capability=['repository_read'],advertisements=advertised,receipt=None))
        self.assertEqual(res['status'],'HELD')

    def test_rejects_forged_fields_and_bad_shape(self):
        bad=self.root/'ads.json'
        bad.write_text(json.dumps([{'current':True,'shell':'rm -rf /'}]))
        with self.assertRaisesRegex(ValueError,'missing or unknown'):
            runner.ads_from_json(Advertisement,bad)
        packet=json.loads(self.packet.read_text())
        packet['authorized_execution']=True
        self.packet.write_text(json.dumps(packet))
        with self.assertRaisesRegex(ValueError,'missing or unknown'):
            runner.packet_from_json(TaskPacket,self.packet)

    def test_source_pin_fail_closed(self):
        with self.assertRaises(RuntimeError):
            runner.source_check(self.root,'0'*40,'Vera Mono')


if __name__=='__main__':unittest.main()
