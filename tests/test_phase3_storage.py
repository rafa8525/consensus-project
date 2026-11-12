"""Durable ACL and SQLite backup/restore simulation tests."""
import os
import sqlite3
import tempfile
import unittest

from agents.phase2_protocol import ProtocolError
from agents.phase3_storage import DurableAuthorizedMemory, backup_sqlite, restore_sqlite


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.db = os.path.join(self.folder.name, "memory.db")
        self.backup = os.path.join(self.folder.name, "snapshot.db")
        self.restored = os.path.join(self.folder.name, "restored.db")

    def tearDown(self):
        self.folder.cleanup()

    def test_durable_grants_survive_restart(self):
        store = DurableAuthorizedMemory(self.db, simulation=True)
        store.grant("t1", "ACS-02", "write", bootstrap=True)
        store.grant("t1", "planner", "read", bootstrap=True)
        store.remember("ACS-02", "e1", "t1", "mock-proof", "synthetic")
        store.close()
        reopened = DurableAuthorizedMemory(self.db, simulation=True)
        self.assertEqual(reopened.for_task("planner", "t1")[0]["finding"], "synthetic")
        with self.assertRaises(ProtocolError):
            reopened.for_task("ACS-03", "t1")
        reopened.close()

    def test_default_deny_and_read_only(self):
        store = DurableAuthorizedMemory(self.db, simulation=True)
        with self.assertRaises(ProtocolError):
            store.for_task("planner", "t1")
        store.grant("t1", "planner", "read", bootstrap=True)
        with self.assertRaises(ProtocolError):
            store.remember("planner", "e1", "t1", "mock", "data")
        store.close()

    def test_revocation_persists(self):
        store = DurableAuthorizedMemory(self.db, simulation=True)
        store.grant("t1", "planner", "read", bootstrap=True)
        store.revoke("t1", "planner", "read", bootstrap=True)
        store.close()
        reopened = DurableAuthorizedMemory(self.db, simulation=True)
        with self.assertRaises(ProtocolError):
            reopened.for_task("planner", "t1")
        reopened.close()

    def test_bootstrap_required(self):
        store = DurableAuthorizedMemory(self.db, simulation=True)
        with self.assertRaises(ProtocolError):
            store.grant("t1", "planner", "read")
        with self.assertRaises(ProtocolError):
            store.revoke("t1", "planner", "read")
        store.close()

    def test_backup_restore_preserves_grants_and_memory(self):
        store = DurableAuthorizedMemory(self.db, simulation=True)
        store.grant("t1", "ACS-02", "write", bootstrap=True)
        store.grant("t1", "planner", "read", bootstrap=True)
        store.remember("ACS-02", "e1", "t1", "mock-proof", "synthetic")
        info = backup_sqlite(self.db, self.backup, simulation=True)
        self.assertEqual(info["integrity"], "ok")
        store.close()
        restore_sqlite(self.backup, self.restored, simulation=True,
                       expected_sha256=info["sha256"])
        reopened = DurableAuthorizedMemory(self.restored, simulation=True)
        self.assertEqual(reopened.for_task("planner", "t1")[0]["finding"], "synthetic")
        reopened.close()

    def test_restore_wrong_checksum_fails_closed(self):
        store = DurableAuthorizedMemory(self.db, simulation=True)
        store.close()
        backup_sqlite(self.db, self.backup, simulation=True)
        with self.assertRaises(ProtocolError):
            restore_sqlite(self.backup, self.restored, simulation=True,
                           expected_sha256="0" * 64)
        self.assertFalse(os.path.exists(self.restored))

    def test_cannot_overwrite_existing_target(self):
        store = DurableAuthorizedMemory(self.db, simulation=True)
        store.close()
        backup_sqlite(self.db, self.backup, simulation=True)
        with self.assertRaises(ProtocolError):
            backup_sqlite(self.db, self.backup, simulation=True)

    def test_simulation_guard(self):
        with self.assertRaises(ProtocolError):
            DurableAuthorizedMemory(self.db)
        store = DurableAuthorizedMemory(self.db, simulation=True)
        store.close()
        with self.assertRaises(ProtocolError):
            backup_sqlite(self.db, self.backup)
