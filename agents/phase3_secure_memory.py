"""Opt-in access-controlled facade for mock evidence memory.

Prototype boundary only: this validates caller IDs and task grants in-process;
direct SQLite file access must be prevented by OS file permissions in production.
"""
from agents.phase2_protocol import ProtocolError
from agents.phase3_memory import EvidenceMemory

PRINCIPALS = frozenset({"planner", "executor", "ACS-01", "ACS-02", "ACS-03", "ACS-04", "ACS-05"})
PERMISSIONS = frozenset({"read", "write"})


class AuthorizedEvidenceMemory:
    def __init__(self, path, access, *, simulation=False):
        if simulation is not True:
            raise ProtocolError("simulation=True required")
        if not isinstance(access, dict):
            raise ProtocolError("explicit task grants required")
        self.grants = {}
        for task_id, grants in access.items():
            if not isinstance(task_id, str) or not task_id or not isinstance(grants, dict):
                raise ProtocolError("invalid task grants")
            self.grants[task_id] = {}
            for principal, perms in grants.items():
                if principal not in PRINCIPALS or not isinstance(perms, (set, frozenset, list, tuple)):
                    raise ProtocolError("invalid principal or permissions")
                perms = frozenset(perms)
                if not perms or not perms.issubset(PERMISSIONS):
                    raise ProtocolError("invalid permissions")
                self.grants[task_id][principal] = perms
        self.memory = EvidenceMemory(path, simulation=True)

    def _require(self, task_id, principal, permission):
        if principal not in PRINCIPALS or permission not in self.grants.get(task_id, {}).get(principal, ()):
            raise ProtocolError("access denied")

    def remember(self, principal, evidence_id, task_id, agent_id, source_ref, finding):
        self._require(task_id, principal, "write")
        if agent_id != principal:
            raise ProtocolError("agent identity mismatch")
        return self.memory.remember(evidence_id, task_id, agent_id, source_ref, finding)

    def for_task(self, principal, task_id, *, limit=25):
        self._require(task_id, principal, "read")
        return self.memory.for_task(task_id, limit=limit)

    def close(self):
        self.memory.close()
