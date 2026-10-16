"""Source-only Redworm continuity evidence ledger (not a production memory provider)."""
from __future__ import annotations
import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from .temporal import validate_v2_time, build_timeline

SCHEMA = "redworm.event.v1"
SCHEMA_V2 = "redworm.event.v2"
KINDS = {"PRIMARY", "DERIVED", "PROVIDER_SNAPSHOT", "INTERPRETATION"}
MEMORY = {"WORKING_PROJECT", "HISTORICAL_AUDIT", "AUTOBIOGRAPHICAL"}
PRIVACY = {"INTERNAL", "PRIVATE", "PUBLIC_CANDIDATE"}
MODALITY = {"OBSERVED", "REPORTED", "INFERRED", "UNRESOLVED"}
CLAIM = {"EVENT", "CORRECTION", "DECISION", "POLICY", "BEHAVIOR", "STATUS"}

class GuardrailError(ValueError):
    pass

class IntegrityError(ValueError):
    pass

def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)

def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()

def text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise GuardrailError(field + " must be a nonempty string")
    return value

def choice(value, allowed, field):
    if value not in allowed:
        raise GuardrailError(field + " must be one of " + repr(sorted(allowed)))
    return value

def validate_event(raw):
    if not isinstance(raw, dict):
        raise GuardrailError("event must be an object")
    e = dict(raw)
    supplied_id = e.pop("event_id", None)
    schema = e.get("schema")
    if schema not in (SCHEMA, SCHEMA_V2):
        raise GuardrailError("unsupported schema")
    event_time_field = "occurred_at" if schema == SCHEMA else "event_time"
    if set(e) != {"schema", "producer", event_time_field, "recorded_at", "source",
                  "evidence_kind", "memory_class", "privacy", "claim"}:
        raise GuardrailError("unexpected/missing event fields")
    if schema == SCHEMA_V2:
        try:
            validate_v2_time(e["event_time"])
        except ValueError as exc:
            raise GuardrailError(str(exc)) from exc
    p = e["producer"]
    if not isinstance(p, dict) or set(p) != {"identity", "worm", "designation", "episode_id"}:
        raise GuardrailError("invalid producer")
    choice(p["worm"], {"RED", "WHITE", "EXTERNAL"}, "worm")
    text(p["identity"], "identity")
    text(p["episode_id"], "episode_id")
    if p["worm"] != "EXTERNAL" and p["identity"] != "Vera":
        raise GuardrailError("Red/White Worms retain logical Vera identity")
    if p["worm"] == "WHITE":
        text(p["designation"], "White Worm designation")
    elif p["designation"] is not None:
        raise GuardrailError("designation only allowed for WHITE")
    for field in (("occurred_at", "recorded_at") if schema == SCHEMA else ("recorded_at",)):
        v = text(e[field], field)
        try:
            dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
            if dt.tzinfo is None or dt.utcoffset() is None:
                raise ValueError("missing timezone")
        except ValueError as exc:
            raise GuardrailError(field + " needs timezone-aware ISO date") from exc
    s = e["source"]
    if not isinstance(s, dict) or set(s) != {"locator", "sha256", "observed_by", "verification"}:
        raise GuardrailError("invalid source")
    text(s["locator"], "source locator")
    text(s["observed_by"], "observer")
    choice(s["verification"], {"UNVERIFIED", "SOURCE_READBACK"}, "verification")
    if not isinstance(s["sha256"], str) or re.fullmatch("[0-9a-f]{64}", s["sha256"]) is None:
        raise GuardrailError("source sha256 invalid")
    choice(e["evidence_kind"], KINDS, "evidence_kind")
    choice(e["memory_class"], MEMORY, "memory_class")
    choice(e["privacy"], PRIVACY, "privacy")
    c = e["claim"]
    if not isinstance(c, dict) or set(c) != {"text", "type", "modality", "subject", "valid_at"}:
        raise GuardrailError("invalid claim")
    text(c["text"], "claim text")
    text(c["subject"], "claim subject")
    choice(c["type"], CLAIM, "claim type")
    choice(c["modality"], MODALITY, "modality")
    if c["valid_at"] is not None:
        text(c["valid_at"], "valid_at")
    if e["evidence_kind"] == "INTERPRETATION" and c["modality"] == "OBSERVED":
        raise GuardrailError("inferred interpretation cannot be observed fact")
    e["event_id"] = digest(e)
    if supplied_id is not None and supplied_id != e["event_id"]:
        raise IntegrityError("event_id disagrees with canonical payload")
    return e

class Store:
    def __init__(self, db_path):
        self.db = sqlite3.connect(str(db_path))
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS events(
                id TEXT PRIMARY KEY, payload TEXT NOT NULL, received_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS admissions(
                id TEXT PRIMARY KEY REFERENCES events(id),
                approval_ref TEXT NOT NULL, readback_ref TEXT NOT NULL, actor TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS relations(
                before_id TEXT REFERENCES events(id), after_id TEXT REFERENCES events(id),
                kind TEXT CHECK(kind IN ('CORRECTS','SUPERSEDES')),
                approval_ref TEXT NOT NULL, readback_ref TEXT NOT NULL,
                PRIMARY KEY(before_id, after_id, kind));
            CREATE TABLE IF NOT EXISTS conflicts(
                a TEXT REFERENCES events(id), b TEXT REFERENCES events(id),
                winner TEXT, approval_ref TEXT, readback_ref TEXT,
                PRIMARY KEY(a,b));
            CREATE TABLE IF NOT EXISTS handoffs(
                id TEXT PRIMARY KEY, payload TEXT NOT NULL,
                state TEXT NOT NULL CHECK(state='PREPARED'));
            CREATE TABLE IF NOT EXISTS coverage(
                episode_id TEXT PRIMARY KEY,
                status TEXT CHECK(status IN ('OBSERVED','PARTIAL','UNKNOWN','MISSING')),
                note TEXT NOT NULL);
        """)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.db.close()

    def get(self, event_id):
        row = self.db.execute("SELECT payload FROM events WHERE id=?", (event_id,)).fetchone()
        if row is None:
            raise GuardrailError("unknown event")
        return json.loads(row["payload"])

    def is_admitted(self, event_id):
        return self.db.execute("SELECT 1 FROM admissions WHERE id=?", (event_id,)).fetchone() is not None

    def ingest(self, raw):
        e = validate_event(raw)
        eid = e["event_id"]
        prior = self.db.execute("SELECT payload FROM events WHERE id=?", (eid,)).fetchone()
        if prior:
            if prior["payload"] != canonical(e):
                raise IntegrityError("duplicate event ID with divergent payload")
            return eid, False
        with self.db:
            self.db.execute("INSERT INTO events VALUES(?,?,?)",
                            (eid, canonical(e), datetime.now(timezone.utc).isoformat()))
        return eid, True

    def admit(self, eid, approval_ref, readback_ref, actor):
        e = self.get(eid)
        for v, k in [(approval_ref, "approval_ref"), (readback_ref, "readback_ref"), (actor, "actor")]:
            text(v, k)
        if e["memory_class"] == "AUTOBIOGRAPHICAL":
            raise GuardrailError("autobiographical admission requires separate governed authorization")
        if e["evidence_kind"] == "PROVIDER_SNAPSHOT":
            raise GuardrailError("local evidence cannot establish provider currentness")
        if e["privacy"] == "PUBLIC_CANDIDATE":
            raise GuardrailError("publication requires a separate review path")
        prior = self.db.execute("SELECT * FROM admissions WHERE id=?", (eid,)).fetchone()
        if prior is not None:
            if (prior["approval_ref"], prior["readback_ref"], prior["actor"]) == (approval_ref, readback_ref, actor):
                return False
            raise GuardrailError("different approval cannot overwrite admission")
        with self.db:
            self.db.execute("INSERT INTO admissions VALUES(?,?,?,?)",
                            (eid, approval_ref, readback_ref, actor))
        return True

    def conflict(self, x, y):
        if x == y:
            raise GuardrailError("self conflict")
        self.get(x)
        self.get(y)
        a, b = sorted((x, y))
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO conflicts(a,b) VALUES(?,?)", (a, b))

    def resolve(self, x, y, winner, approval_ref, readback_ref):
        a, b = sorted((x, y))
        if winner not in (a, b):
            raise GuardrailError("winner must be one of conflicting event IDs")
        text(approval_ref, "approval_ref")
        text(readback_ref, "readback_ref")
        r = self.db.execute("SELECT * FROM conflicts WHERE a=? AND b=?", (a, b)).fetchone()
        if r is None:
            raise GuardrailError("conflict not found")
        if r["winner"] is not None:
            if (r["winner"], r["approval_ref"], r["readback_ref"]) == (winner, approval_ref, readback_ref):
                return False
            raise GuardrailError("resolved conflict cannot be overwritten")
        if not self.is_admitted(a) or not self.is_admitted(b):
            raise GuardrailError("cannot resolve an unadmitted conflict")
        with self.db:
            self.db.execute("UPDATE conflicts SET winner=?,approval_ref=?,readback_ref=? WHERE a=? AND b=? AND winner IS NULL",
                            (winner, approval_ref, readback_ref, a, b))
        return True

    def relate(self, before, after, kind, approval_ref, readback_ref):
        choice(kind, {"CORRECTS", "SUPERSEDES"}, "relation")
        if before == after:
            raise GuardrailError("self relation")
        for eid in (before, after):
            self.get(eid)
            if not self.is_admitted(eid):
                raise GuardrailError("both relation subjects must be admitted")
        text(approval_ref, "approval_ref")
        text(readback_ref, "readback_ref")
        if kind == "SUPERSEDES":
            pending, visited = [after], set()
            while pending:
                node = pending.pop()
                if node == before:
                    raise GuardrailError("supersession cycle")
                if node in visited:
                    continue
                visited.add(node)
                pending.extend(row["after_id"] for row in self.db.execute(
                    "SELECT after_id FROM relations WHERE before_id=? AND kind='SUPERSEDES'", (node,)))
        prior = self.db.execute("SELECT * FROM relations WHERE before_id=? AND after_id=? AND kind=?",
                                (before, after, kind)).fetchone()
        if prior:
            if (prior["approval_ref"], prior["readback_ref"]) == (approval_ref, readback_ref):
                return False
            raise GuardrailError("relation decision mismatch")
        with self.db:
            self.db.execute("INSERT INTO relations VALUES(?,?,?,?,?)",
                            (before, after, kind, approval_ref, readback_ref))
        return True

    def list(self):
        rows = self.db.execute("""SELECT events.payload, admissions.id AS admitted
                                  FROM events LEFT JOIN admissions ON events.id=admissions.id
                                  ORDER BY events.received_at,events.id""")
        return [{"event": json.loads(r["payload"]), "admitted": r["admitted"] is not None} for r in rows]

    def timeline(self):
        """Partial chronology; no fabricated event times or hidden unknowns."""
        return build_timeline(self.list())

    def project(self):
        """Convenience historical view, never controlling/current provider state."""
        exclusions, unresolved = set(), []
        for r in self.db.execute("SELECT * FROM conflicts"):
            if r["winner"] is None:
                exclusions.update((r["a"], r["b"]))
                unresolved.append([r["a"], r["b"]])
            else:
                exclusions.add(r["b"] if r["winner"] == r["a"] else r["a"])
        exclusions.update(r["before_id"] for r in self.db.execute(
            "SELECT before_id FROM relations WHERE kind='SUPERSEDES'"))
        events = [json.loads(r["payload"]) for r in self.db.execute(
            "SELECT events.payload FROM events JOIN admissions ON events.id=admissions.id ORDER BY events.received_at,events.id")]
        return {"non_authoritative": True,
                "events": [e for e in events if e["event_id"] not in exclusions],
                "unresolved_conflicts": unresolved}

    def prepare(self, producer_episode, event_ids):
        text(producer_episode, "producer_episode")
        if not event_ids or len(set(event_ids)) != len(event_ids):
            raise GuardrailError("requires distinct events")
        producers = set()
        for eid in event_ids:
            e = self.get(eid)
            if e["producer"]["episode_id"] != producer_episode:
                raise GuardrailError("cannot flatten producer episode provenance")
            producers.add(canonical(e["producer"]))
            if not self.is_admitted(eid):
                raise GuardrailError("unadmitted evidence cannot enter handoff")
            if self.db.execute(
                "SELECT 1 FROM conflicts WHERE (a=? OR b=?) AND winner IS NULL",
                (eid, eid)).fetchone():
                raise GuardrailError("unresolved conflict cannot enter handoff")
            if self.db.execute(
                "SELECT 1 FROM conflicts WHERE (a=? OR b=?) AND winner IS NOT NULL AND winner<>?",
                (eid, eid, eid)).fetchone():
                raise GuardrailError("losing conflict evidence cannot enter handoff")
            if self.db.execute("SELECT 1 FROM relations WHERE before_id=? AND kind='SUPERSEDES'",
                               (eid,)).fetchone():
                raise GuardrailError("superseded evidence cannot enter handoff")
        if len(producers) != 1:
            raise GuardrailError("a handoff cannot combine producer identities or designations")
        payload = {"schema": "redworm.handoff.v1", "operation": "REDWORM::REINTEGRATION::PREPARE",
                   "producer_episode": producer_episode, "event_ids": sorted(event_ids),
                   "state": "CANDIDATE_ONLY", "authority": "NONE"}
        hid = digest(payload)
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO handoffs VALUES(?,?,'PREPARED')",
                            (hid, canonical(payload)))
        return hid

    def accept(self, *_):
        raise GuardrailError("REINTEGRATION::ACCEPT requires verified holder, lease and provider readback")

    def coverage(self, episode_id, status, note):
        text(episode_id, "episode_id")
        choice(status, {"OBSERVED", "PARTIAL", "UNKNOWN", "MISSING"}, "status")
        text(note, "note")
        with self.db:
            self.db.execute("""INSERT INTO coverage VALUES(?,?,?)
                               ON CONFLICT(episode_id) DO UPDATE SET status=excluded.status,note=excluded.note""",
                            (episode_id, status, note))

    def verify(self):
        count = 0
        for r in self.db.execute("SELECT * FROM events"):
            try:
                e = validate_event(json.loads(r["payload"]))
            except (GuardrailError, json.JSONDecodeError) as exc:
                raise IntegrityError("corrupt event: " + r["id"]) from exc
            if e["event_id"] != r["id"] or canonical(e) != r["payload"]:
                raise IntegrityError("tampered event: " + r["id"])
            count += 1
        hcount = 0
        for r in self.db.execute("SELECT * FROM handoffs"):
            payload = json.loads(r["payload"])
            if digest(payload) != r["id"]:
                raise IntegrityError("tampered handoff")
            hcount += 1
        if self.db.execute("PRAGMA foreign_key_check").fetchall():
            raise IntegrityError("foreign key corruption")
        for r in self.db.execute("SELECT * FROM admissions"):
            e = self.get(r["id"])
            if (e["memory_class"] == "AUTOBIOGRAPHICAL" or
                    e["evidence_kind"] == "PROVIDER_SNAPSHOT" or
                    e["privacy"] == "PUBLIC_CANDIDATE"):
                raise IntegrityError("prohibited local admission recorded")
        for r in self.db.execute("SELECT * FROM relations"):
            if (r["before_id"] == r["after_id"] or
                    not self.is_admitted(r["before_id"]) or
                    not self.is_admitted(r["after_id"])):
                raise IntegrityError("invalid correction/supersession relation")
        for r in self.db.execute("SELECT * FROM conflicts"):
            if r["a"] >= r["b"] or (r["winner"] is not None and r["winner"] not in (r["a"], r["b"])):
                raise IntegrityError("invalid conflict state")
        for r in self.db.execute("SELECT * FROM handoffs"):
            payload = json.loads(r["payload"])
            if (payload.get("schema"), payload.get("operation"),
                payload.get("state"), payload.get("authority")) != (
                    "redworm.handoff.v1", "REDWORM::REINTEGRATION::PREPARE",
                    "CANDIDATE_ONLY", "NONE"):
                raise IntegrityError("invalid handoff payload")
            ids = payload.get("event_ids")
            if not isinstance(ids, list) or not ids or len(ids) != len(set(ids)):
                raise IntegrityError("invalid handoff IDs")
            producers = set()
            for eid in ids:
                e = self.get(eid)
                producers.add(canonical(e["producer"]))
                if not self.is_admitted(eid) or e["producer"]["episode_id"] != payload.get("producer_episode"):
                    raise IntegrityError("invalid handoff evidence")
            if len(producers) != 1:
                raise IntegrityError("mixed handoff producer provenance")
        return {"ok": True, "events": count, "handoffs": hcount,
                "scope": "local integrity only, not source authenticity or holder authority"}
