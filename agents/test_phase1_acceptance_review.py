#!/usr/bin/env python3
"""Isolated regression checks; no network, Git changes or production execution."""
import copy
import hashlib
import tempfile
from pathlib import Path
import unittest
from datetime import datetime, timedelta, timezone
import phase1_acceptance_review as gate

NOW = datetime(2026, 10, 31, 18, 3, tzinfo=timezone.utc)
def iso(time):
    return time.isoformat()
def fixture():
    return {
        "generated_at_utc": iso(NOW),
        "agents": {n: {"status":"current", "verified":True,
                        "health_status":"healthy", "last_execution_utc":iso(NOW)}
                   for n in gate.AGENTS},
        "pythonanywhere_schedule":{"available":True,"acs01_task":{"enabled":True},
                                   "health_task":{"enabled":False}},
        "git":{"origin_reachable":{"ok":True}, "unresolved_merge_conflict":False,
               "status":{"tracked_changes_count":22}},
        "self_heal":{"branch_sync":{"ok":True,"ahead_after":0,"behind_after":0},
                     "recovery_proof":{"verified":True}}
    }
def proof():
    tests = {}
    for key in ("failure_detection", "automatic_retry", "recovery_verified", "bounded_escalation"):
        payload = ("PASS: " + key + "\\n").encode()
        filename = key + ".log"
        (gate.ROOT / "evidence" / filename).write_bytes(payload)
        tests[key] = {"passed": True, "artifact_path": filename,
                      "artifact_sha256": hashlib.sha256(payload).hexdigest(),
                      "executed_at_utc": iso(NOW), "execution_scope": "production"}
    return {"tests": tests}

class Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.old_root = gate.ROOT
        gate.ROOT = Path(self.temp.name)
        (gate.ROOT / "evidence").mkdir()
    def tearDown(self):
        gate.ROOT = self.old_root
        self.temp.cleanup()
    def test_local_proof_cannot_override_unverified_published_recovery(self):
        r = fixture()
        r["self_heal"]["recovery_proof"]["verified"] = False
        self.assertFalse(
            gate.evaluate(r, proof(), NOW)["published_recovery_verified"]
        )
        checks, reports, completed = gate.advance(r, proof(), {}, NOW)
        self.assertFalse(completed)
        self.assertEqual(reports, [])

    def test_missing_or_malformed_published_recovery_fails_closed(self):
        for value in (None, {}, {"verified": "true"}, {"verified": 1}):
            with self.subTest(value=value):
                r = fixture()
                r["self_heal"]["recovery_proof"] = value
                self.assertFalse(
                    gate.evaluate(r, proof(), NOW)["published_recovery_verified"]
                )

    def test_simulation_never_counts_as_production(self):
        p = proof()
        p["tests"]["recovery_verified"]["execution_scope"] = "isolated_simulation"
        self.assertFalse(gate.evaluate(fixture(), p, NOW)["proof_recovery_verified"])
    def test_tampered_or_fake_artifacts_fail(self):
        p = proof()
        p["tests"]["automatic_retry"]["artifact_sha256"] = "0" * 64
        self.assertFalse(gate.evaluate(fixture(), p, NOW)["proof_automatic_retry"])
        p = proof()
        p["tests"]["automatic_retry"]["artifact_path"] = "../other.log"
        self.assertFalse(gate.evaluate(fixture(), p, NOW)["proof_automatic_retry"])
        p = proof()
        (gate.ROOT / "evidence" / "automatic_retry.log").write_text("PASS: something else")
        self.assertFalse(gate.evaluate(fixture(), p, NOW)["proof_automatic_retry"])
    def test_healthy_parent_architecture(self):
        self.assertTrue(all(gate.evaluate(fixture(), proof(), NOW).values()))
    def test_each_agent_unhealthy(self):
        for n in gate.AGENTS:
            for field,value in (("verified",False),("status","stale"),
                                ("last_execution_utc","2020-01-01T00:00:00+00:00")):
                r=fixture()
                r["agents"][n][field]=value
                self.assertFalse(all(gate.evaluate(r, proof(), NOW).values()))
    def test_malformed_agent_data(self):
        for malformed in (None, [], "bad", 1):
            r=fixture()
            r["agents"]["ACS-04"]=malformed
            self.assertFalse(all(gate.evaluate(r, proof(), NOW).values()))
    def test_missing_proof(self):
        for k in proof()["tests"]:
            p=proof()
            del p["tests"][k]
            self.assertFalse(all(gate.evaluate(fixture(), p, NOW).values()))
    def test_old_and_future_report(self):
        for t in (NOW-timedelta(days=3), NOW+timedelta(seconds=1)):
            r=fixture()
            r["generated_at_utc"]=iso(t)
            self.assertFalse(all(gate.evaluate(r, proof(), NOW).values()))
    def test_documented_report_freshness_boundary(self):
        # Production report TTL is 30 hours, not the separate 36-hour agent horizon.
        for hours, accepted in ((29, True), (30, True), (31, False), (35, False)):
            with self.subTest(report_age_hours=hours):
                r = fixture()
                r["generated_at_utc"] = iso(NOW - timedelta(hours=hours))
                checks = gate.evaluate(r, proof(), NOW)
                self.assertIs(checks["report_fresh"], accepted)

    def test_old_report_cannot_advance_passing_streak(self):
        r = fixture()
        r["generated_at_utc"] = iso(NOW - timedelta(hours=31))
        checks, reports, complete = gate.advance(r, proof(), {}, NOW)
        self.assertFalse(checks["report_fresh"])
        self.assertEqual(reports, [])
        self.assertFalse(complete)

    def test_scheduler_and_remote_sync(self):
        for field in ("scheduler", "sync", "remote"):
            r=fixture()
            if field=="scheduler":r["pythonanywhere_schedule"]["acs01_task"]["enabled"]=False
            if field=="sync":r["self_heal"]["branch_sync"]["behind_after"]=1
            if field=="remote":r["git"]["origin_reachable"]["ok"]=False
            self.assertFalse(all(gate.evaluate(r, proof(), NOW).values()))
    def test_unique_cycle_and_replay(self):
        history={}
        for i in range(3):
            t=NOW+timedelta(days=i)
            r=fixture()
            r["generated_at_utc"]=iso(t)
            r["agents"]={n:{**a,"last_execution_utc":iso(t)} for n,a in r["agents"].items()}
            p=proof()
            checks,cycles,completed=gate.advance(r,p,history,t)
            self.assertEqual(len(cycles),i+1)
            self.assertEqual(completed,i==2)
            history={"passing_reports":cycles}
        checks,cycles,completed=gate.advance(r,p,history,t)
        self.assertEqual(len(cycles),3)
        self.assertTrue(completed)
        r["agents"]["ACS-02"]["verified"]=False
        _,cycles,completed=gate.advance(r,p,history,t)
        self.assertEqual(cycles,[])
        self.assertFalse(completed)

if __name__=="__main__":
    unittest.main()
