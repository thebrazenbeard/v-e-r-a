import unittest
from decimal import Decimal

from vera_works.projections import available_balance, decision_queues, financial_ledger


def event(event_id, event_type, subject_type, subject_id, from_state, to_state, payload=None):
    return {
        "schema_version": "event-v1",
        "event_id": event_id,
        "event_type": event_type,
        "subject_type": subject_type,
        "subject_id": subject_id,
        "actor": "vera",
        "recorded_at": "2026-08-29T13:00:00Z",
        "correlation_id": "CORR-TEST",
        "causation_id": None,
        "idempotency_key": event_id.lower(),
        "from_state": from_state,
        "to_state": to_state,
        "payload": payload or {},
        "external_effect": False,
    }


class ProjectionTests(unittest.TestCase):
    def financial(self, event_id, subject_id, from_state, to_state, payload):
        return event(event_id, f"FINANCIAL_{to_state}", "financial", subject_id, from_state, to_state, payload)

    def hold(self, event_id, subject_id, kind):
        required = {"VERA_DECISION_REQUIRED": "vera", "PATRICK_ACTION_REQUIRED": "patrick", "PATRICK_DECISION_REQUIRED": "patrick", "AUTOMATION_EXCEPTION": "automation"}[kind]
        return event(event_id, kind, "hold", subject_id, None, "OPEN", {
            "hold_kind": kind,
            "problem": "test",
            "held_subject_type": "assignment",
            "held_subject_id": "A1",
            "held_state": "HELD",
            "required_from": required,
            "recommendation": "recommended action",
            "alternatives": ["alternate"],
            "consequences": ["consequence"],
            "inaction_effect": "remains held",
            "resume_event_type": "RESOLUTION_RECORDED",
        })

    def test_receivable_does_not_increase_available_balance(self):
        events = [self.financial("F0", "TX1", None, "EARNED", {"currency": "USD", "gross": "100.00"}), self.financial("F1", "TX1", "EARNED", "RECEIVABLE", {"currency": "USD", "gross": "100.00"})]
        self.assertEqual(available_balance(events), Decimal("0.00"))

    def test_received_increases_balance_by_net(self):
        events = [self.financial("F2", "TX1", None, "RECEIVED", {"currency": "USD", "gross": "100.00", "fees": "5.00", "tax_reserve": "10.00", "net": "85.00"})]
        self.assertEqual(available_balance(events), Decimal("85.00"))

    def test_spent_decreases_balance(self):
        events = [
            self.financial("F2", "TX1", None, "RECEIVED", {"currency": "USD", "gross": "100.00", "fees": "5.00", "tax_reserve": "10.00", "net": "85.00"}),
            self.financial("F3", "SP1", None, "SPENT", {"currency": "USD", "amount": "20.00", "purpose": "hosting"}),
        ]
        self.assertEqual(available_balance(events), Decimal("65.00"))

    def test_spent_cannot_exceed_available_vera_fund_balance(self):
        events = [
            self.financial("F2", "TX1", None, "RECEIVED", {"currency": "USD", "gross": "50.00", "fees": "0.00", "tax_reserve": "0.00", "net": "50.00"}),
            self.financial("F3", "SP1", None, "SPENT", {"currency": "USD", "amount": "60.00", "purpose": "too expensive"}),
        ]
        with self.assertRaisesRegex(ValueError, "financial SPENT F3 exceeds available Vera Fund balance"):
            available_balance(events)

    def test_refund_reverses_referenced_received_amount(self):
        events = [
            self.financial("F2", "TX1", None, "RECEIVED", {"currency": "USD", "gross": "100.00", "fees": "5.00", "tax_reserve": "10.00", "net": "85.00"}),
            self.financial("F4", "TX1", "RECEIVED", "REFUNDED", {"currency": "USD", "amount": "85.00", "reverses_event_id": "F2"}),
        ]
        self.assertEqual(available_balance(events), Decimal("0.00"))
        self.assertEqual(financial_ledger(events)[-1]["reference"], "F2")

    def test_refund_reference_must_point_to_prior_received_event(self):
        events = [
            self.financial("F2", "TX1", None, "RECEIVED", {"currency": "USD", "gross": "100.00", "fees": "0.00", "tax_reserve": "0.00", "net": "100.00"}),
            self.financial("F4", "TX1", "RECEIVED", "REFUNDED", {"currency": "USD", "amount": "100.00", "reverses_event_id": "NOT-A-RECEIPT"}),
        ]
        with self.assertRaisesRegex(ValueError, "financial REFUNDED F4 references unknown prior RECEIVED event NOT-A-RECEIPT"):
            financial_ledger(events)

    def test_financial_math_uses_decimal(self):
        events = [self.financial("F2", "TX1", None, "RECEIVED", {"currency": "USD", "gross": "0.30", "fees": "0.00", "tax_reserve": "0.00", "net": "0.30"}), self.financial("F3", "SP1", None, "SPENT", {"currency": "USD", "amount": "0.10", "purpose": "test"})]
        self.assertEqual(available_balance(events), Decimal("0.20"))
        self.assertIsInstance(available_balance(events), Decimal)

    def test_open_holds_project_to_four_queues(self):
        events = [self.hold("H1", "HOLD-1", "VERA_DECISION_REQUIRED"), self.hold("H2", "HOLD-2", "PATRICK_ACTION_REQUIRED"), self.hold("H3", "HOLD-3", "PATRICK_DECISION_REQUIRED"), self.hold("H4", "HOLD-4", "AUTOMATION_EXCEPTION")]
        queues = decision_queues(events)
        self.assertEqual([x["event_id"] for x in queues["vera_decisions"]], ["H1"])
        self.assertEqual([x["event_id"] for x in queues["patrick_actions"]], ["H2"])
        self.assertEqual([x["event_id"] for x in queues["patrick_decisions"]], ["H3"])
        self.assertEqual([x["event_id"] for x in queues["automation_exceptions"]], ["H4"])


if __name__ == "__main__":
    unittest.main()
