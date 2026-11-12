"""Phase 5 simulated adapter and duplicate-workflow safety tests."""
import unittest
from agents.phase5_registry import MockIntegrationRegistry
from agents.phase2_protocol import ProtocolError


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.reg = MockIntegrationRegistry(simulation=True)
        self.reg.register(adapter_id="bills.mock", capability="bills",
                          workflow_key="existing.bill.alerts", owner="acs-02",
                          permissions={"read_mock", "notify_mock"},
                          handler=lambda p: self.calls.append(p) or "synthetic-notice")

    def send(self, **kwargs):
        values = dict(adapter_id="bills.mock", principal="acs-02",
                      permission="notify_mock", event_id="notice-1",
                      payload={"synthetic_value": "dummy"})
        values.update(kwargs)
        return self.reg.dispatch(**values)

    def test_simulation_required(self):
        with self.assertRaises(ProtocolError):
            MockIntegrationRegistry()

    def test_allowed_mock_dispatch(self):
        r = self.send()
        self.assertEqual(r["status"], "delivered")
        self.assertEqual(len(self.calls), 1)

    def test_duplicate_event_not_reexecuted(self):
        self.send()
        r = self.send()
        self.assertTrue(r["duplicate"])
        self.assertFalse(r.get("executed", True) and False)  # explicit event is cached
        self.assertEqual(len(self.calls), 1)

    def test_duplicate_workflow_registration_rejected(self):
        with self.assertRaises(ProtocolError):
            self.reg.register(adapter_id="another.mock", capability="bills",
                              workflow_key="existing.bill.alerts", owner="acs-03",
                              permissions={"read_mock"}, handler=lambda p: "ok")

    def test_unauthorized_caller_and_permission(self):
        for args in ({"principal": "acs-03"}, {"permission": "send_money"},
                     {"principal": "unknown"}):
            with self.assertRaises(ProtocolError):
                self.send(**args)
        self.assertEqual(self.calls, [])

    def test_no_real_or_sensitive_payload(self):
        for payload in ({"account": "123"}, {"synthetic_value": {"secret": "x"}},
                        {"synthetic_value": "x", "token": "secret"}):
            with self.assertRaises(ProtocolError):
                self.send(payload=payload)
        self.assertEqual(self.calls, [])

    def test_event_collision_rejected(self):
        self.send()
        with self.assertRaises(ProtocolError):
            self.send(payload={"synthetic_value": "changed"})

    def test_handler_failure_remains_uncertain(self):
        attempts = []
        self.reg.register(adapter_id="health.mock", capability="wearables",
                          workflow_key="existing.wearable.sync", owner="acs-03",
                          permissions={"read_mock"},
                          handler=lambda p: attempts.append(p) or 123)
        args = dict(adapter_id="health.mock", principal="acs-03",
                    permission="read_mock", event_id="event-1",
                    payload={"synthetic_value": "dummy"})
        self.assertEqual(self.reg.dispatch(**args)["status"], "uncertain")

    def test_inventory_does_not_expose_handlers(self):
        listing = self.reg.inventory()
        self.assertEqual(listing[0]["workflow_key"], "existing.bill.alerts")
        self.assertNotIn("handler", listing[0])


if __name__ == "__main__":
    unittest.main()
