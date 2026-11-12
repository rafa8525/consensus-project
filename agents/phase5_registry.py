"""Phase 5 mock-only integration registry, default-deny and no duplicate owners.

No imports of real connectors or network-capable modules. The registry holds
synthetic configuration; dispatch invokes explicitly supplied mock handlers.
"""
from agents.phase2_protocol import ProtocolError

CAPABILITIES = frozenset({"notifications", "wearables", "bills", "entertainment", "device_security"})
PERMISSIONS = frozenset({"read_mock", "notify_mock"})
_ID = set("abcdefghijklmnopqrstuvwxyz0123456789._-")


def _identifier(value):
    return isinstance(value, str) and 1 <= len(value) <= 80 and all(c in _ID for c in value)


class MockIntegrationRegistry:
    def __init__(self, *, simulation=False):
        if simulation is not True:
            raise ProtocolError("simulation=True required")
        self._adapters = {}
        self._owners = {}
        self._processed = {}

    def register(self, *, adapter_id, capability, workflow_key, owner, permissions,
                 handler, data_class="synthetic"):
        if not all(_identifier(x) for x in (adapter_id, workflow_key, owner)):
            raise ProtocolError("invalid identifier")
        if capability not in CAPABILITIES or data_class != "synthetic":
            raise ProtocolError("capability or data classification prohibited")
        if not isinstance(permissions, (set, frozenset)) or not permissions or not permissions <= PERMISSIONS:
            raise ProtocolError("invalid or excessive permissions")
        if not callable(handler):
            raise ProtocolError("mock handler required")
        if adapter_id in self._adapters:
            raise ProtocolError("duplicate adapter ID")
        if workflow_key in self._owners:
            raise ProtocolError("duplicate workflow owner")
        self._adapters[adapter_id] = {
            "capability": capability, "workflow_key": workflow_key,
            "owner": owner, "permissions": frozenset(permissions),
            "handler": handler}
        self._owners[workflow_key] = adapter_id

    def dispatch(self, *, adapter_id, principal, permission, event_id, payload):
        if not _identifier(event_id) or not _identifier(principal):
            raise ProtocolError("invalid caller or event ID")
        adapter = self._adapters.get(adapter_id)
        if adapter is None:
            raise ProtocolError("unregistered adapter")
        if principal != adapter["owner"] or permission not in adapter["permissions"]:
            raise ProtocolError("access denied")
        if not isinstance(payload, dict) or set(payload) != {"synthetic_value"}:
            raise ProtocolError("synthetic payload required")
        v = payload["synthetic_value"]
        if type(v) not in (str, int, float, bool) or type(v) is str and len(v) > 120:
            raise ProtocolError("invalid synthetic data")
        key = (adapter_id, event_id)
        if key in self._processed:
            prev_payload, report = self._processed[key]
            if prev_payload != payload:
                raise ProtocolError("event ID collision")
            return dict(report, duplicate=True)
        # Cache uncertain results: a mock handler may already have had effects.
        try:
            result = adapter["handler"](dict(payload))
        except Exception:
            report = {"adapter_id": adapter_id, "status": "uncertain",
                      "duplicate": False, "executed": True, "reason": "mock_handler_error"}
            self._processed[key] = (dict(payload), report)
            return dict(report)
        if not isinstance(result, str) or not result.strip() or len(result) > 160:
            report = {"adapter_id": adapter_id, "status": "uncertain",
                      "duplicate": False, "executed": True, "reason": "invalid_mock_result"}
            self._processed[key] = (dict(payload), report)
            return dict(report)
        report = {"adapter_id": adapter_id, "status": "delivered", "duplicate": False,
                  "executed": True, "result": result}
        self._processed[key] = (dict(payload), report)
        return dict(report)

    def inventory(self):
        return [
            {"adapter_id": key, "workflow_key": value["workflow_key"],
             "capability": value["capability"], "owner": value["owner"]}
            for key, value in sorted(self._adapters.items())
        ]
