"""Fail-closed, redacted, opt-in heartbeat checks (no real HTTP)."""
import unittest
from unittest.mock import patch
import phase1_scheduler_heartbeat as hb

URL="https://hc-ping.com/01234567-89ab-cdef-0123-456789abcdef"

class Response:
    status=200
    def __enter__(self): return self
    def __exit__(self,*args): return False

class HeartbeatTests(unittest.TestCase):
    def test_no_heartbeat_for_manual_push_or_pr_even_when_configured(self):
        def unexpected(*a,**kw): self.fail("No request allowed")
        for result in ("push","workflow_dispatch","pull_request"):
            with self.subTest(result=result):
                self.assertEqual(hb.ping(URL,scheduled=False,
                                         guard_outcome="success",
                                         preflight_outcome="success",
                                         opener=unexpected),
                                 "skipped_non_scheduled_event")

    def test_no_url_never_phones_home(self):
        with patch.object(hb.urllib.request, "urlopen",
                          side_effect=AssertionError("unexpected HTTP")):
            self.assertEqual(hb.ping(None,scheduled=True,
                                     guard_outcome="success",
                                     preflight_outcome="success"),
                             "not_configured")

    def test_only_exact_https_healthchecks_uuid_allowed(self):
        invalid=["http://hc-ping.com/01234567-89ab-cdef-0123-456789abcdef",
                 "https://hc-ping.com.evil.test/01234567-89ab-cdef-0123-456789abcdef",
                 "https://evil.test/01234567-89ab-cdef-0123-456789abcdef",
                 "https://hc-ping.com/01234567-89ab-cdef-0123-456789abcdef?token=1",
                 "https://hc-ping.com/foo", "https://hc-ping.com:444/01234567-89ab-cdef-0123-456789abcdef",
                 "https://name:pw@hc-ping.com/01234567-89ab-cdef-0123-456789abcdef"]
        for url in invalid:
            with self.subTest(url=url):
                self.assertIsNone(hb.parse_ping_url(url))
        self.assertEqual(hb.parse_ping_url(URL),URL)

    def test_success_ping_scheduled_and_both_steps_success(self):
        calls=[]
        def fake(request,timeout):
            calls.append((request.full_url,request.get_method(),timeout))
            return Response()
        status=hb.ping(URL,scheduled=True,guard_outcome="success",
                       preflight_outcome="success",opener=fake)
        self.assertEqual(status,"scheduled_success_reported")
        self.assertEqual(calls,[(URL,"POST",8)])

    def test_failed_guard_or_preflight_signals_failure_not_success(self):
        for pre,guard in (("success","failure"),("failure","skipped"),
                          ("skipped","success"),(None,None)):
            calls=[]
            def fake(request,timeout):
                calls.append(request.full_url)
                return Response()
            status=hb.ping(URL,scheduled=True,guard_outcome=guard,
                           preflight_outcome=pre,opener=fake)
            self.assertEqual(status,"scheduled_failure_reported")
            self.assertEqual(calls,[URL+"/fail"])

    def test_external_network_error_does_not_reveal_url_or_interrupt_guard(self):
        def bad(*args,**kwargs):raise OSError("secret would appear in exception")
        result=hb.ping(URL,scheduled=True,guard_outcome="success",
                       preflight_outcome="success",opener=bad)
        self.assertEqual(result,"external_monitor_unavailable")
        self.assertNotIn(URL,result)

if __name__=="__main__":
    unittest.main()
