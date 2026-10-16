from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from vera_works.claim_sources import (
    SourceReadState,
    automatic_read_queue,
    deferred_sources,
    load_source_registry,
)


class ClaimSourceTests(unittest.TestCase):
    def test_registry_only_schedules_ready_authoritative_noninteractive_reads(self):
        payload = {
            "sources": [
                {
                    "source_id": "ready",
                    "title": "Ready",
                    "jurisdiction": "X",
                    "source_class": "GOVERNMENT",
                    "discovery_mode": "DIRECT_FETCH",
                    "read_state": "READY",
                    "entrypoint": "https://example.gov/",
                    "authoritative": True,
                    "person_to_person_communication_required": False,
                    "claim_effect_requires_identity": False,
                    "notes": ""
                },
                {
                    "source_id": "turnstile",
                    "title": "Turnstile",
                    "jurisdiction": "X",
                    "source_class": "GOVERNMENT",
                    "discovery_mode": "INTERACTIVE_SEARCH",
                    "read_state": "INTERACTIVE_GATE",
                    "entrypoint": "https://example.gov/search",
                    "authoritative": True,
                    "person_to_person_communication_required": False,
                    "claim_effect_requires_identity": True,
                    "notes": ""
                },
                {
                    "source_id": "secondary",
                    "title": "Secondary",
                    "jurisdiction": "X",
                    "source_class": "SECONDARY",
                    "discovery_mode": "DIRECT_FETCH",
                    "read_state": "READY",
                    "entrypoint": "https://example.com/",
                    "authoritative": False,
                    "person_to_person_communication_required": False,
                    "claim_effect_requires_identity": False,
                    "notes": ""
                }
            ]
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sources.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            sources = load_source_registry(path)
        self.assertEqual([item.source_id for item in automatic_read_queue(sources)], ["ready"])
        self.assertEqual(
            [item.source_id for item in deferred_sources(sources)],
            ["turnstile", "secondary"],
        )
        self.assertEqual(sources[1].read_state, SourceReadState.INTERACTIVE_GATE)

    def test_duplicate_source_ids_fail_closed(self):
        source = {
            "source_id": "same",
            "title": "One",
            "jurisdiction": "X",
            "source_class": "GOVERNMENT",
            "discovery_mode": "DIRECT_FETCH",
            "read_state": "READY",
            "entrypoint": "https://example.gov/",
            "authoritative": True,
            "person_to_person_communication_required": False,
            "claim_effect_requires_identity": False,
            "notes": ""
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sources.json"
            path.write_text(json.dumps({"sources": [source, dict(source)]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_source_registry(path)


if __name__ == "__main__":
    unittest.main()
