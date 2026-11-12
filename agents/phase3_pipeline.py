"""Isolated Phase 3 task execution -> evidence memory bridge.

Mock handlers only. Journal and evidence memory are different SQLite files, so
this bridge uses deterministic observation IDs to recover from a crash after
journal completion but before memory publication. No external side effects.
"""
from agents.phase2_durable import DurableSimulatedRouter
from agents.phase2_protocol import ProtocolError
from agents.phase3_memory import EvidenceMemory


class SimulatedEvidencePipeline:
    def __init__(self, task_db, memory_db, handlers, *, simulation=False):
        if simulation is not True:
            raise ProtocolError("simulation=True required")
        self.router = DurableSimulatedRouter(task_db, handlers, simulation=True)
        try:
            self.memory = EvidenceMemory(memory_db, simulation=True)
        except BaseException:
            self.router.close()
            raise

    def dispatch(self, task_id, worker, task):
        report = self.router.dispatch(task_id, worker, task)
        # Only journal-recorded completed tasks can be mirrored; an uncertain,
        # pending or failed state is never promoted to successful evidence.
        row = self.router.journal.get(task_id)
        if report["state"] != "completed" or row is None or row["state"] != "completed":
            return dict(report, memory_status="not_recorded")
        finding = row["result"]
        if not isinstance(finding, str) or not finding.strip() or len(finding) > 500:
            raise ProtocolError("invalid journal result for evidence publication")
        memory_status = self.memory.remember(
            "phase3." + task_id, task_id, worker, "mock-journal." + task_id, finding)
        return dict(report, memory_status=memory_status)

    def close(self):
        try:
            self.memory.close()
        finally:
            self.router.close()
