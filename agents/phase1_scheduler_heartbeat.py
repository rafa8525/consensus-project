#!/usr/bin/env python3
"""Opt-in external dead-man heartbeat for the existing ACS-01 GitHub guard.

Runs after scheduled executions only. Never modifies a scheduler or agent.
The shared ping URL is a GitHub Actions *secret*; do not log or save it.
No URL = no network access. External monitoring errors do not alter guard status.
"""
import os
import re
import sys
import urllib.request
from urllib.parse import urlsplit


def parse_ping_url(raw):
    if not raw:
        return None
    try:
        url = urlsplit(raw)
    except ValueError:
        return None
    if (url.scheme != "https" or url.hostname != "hc-ping.com"
            or url.port not in (None, 443) or url.username or url.password
            or url.query or url.fragment
            or not re.fullmatch(r"/[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}/?", url.path)):
        return None
    return raw.rstrip("/")


def ping(raw, *, scheduled, guard_outcome, preflight_outcome, opener=None):
    if not scheduled:
        return "skipped_non_scheduled_event"
    if not raw:
        return "not_configured"
    url = parse_ping_url(raw)
    if url is None:
        return "invalid_monitor_configuration"
    ok = guard_outcome == "success" and preflight_outcome == "success"
    endpoint = url if ok else url + "/fail"
    try:
        request = urllib.request.Request(
            endpoint, method="POST",
            headers={"User-Agent": "ACS01-Scheduled-Guard-Heartbeat/1.0"})
        with (opener or urllib.request.urlopen)(request, timeout=8) as response:
            if response.status < 200 or response.status >= 300:
                return "external_monitor_unavailable"
    except (OSError, ValueError):
        return "external_monitor_unavailable"
    return "scheduled_success_reported" if ok else "scheduled_failure_reported"


def main():
    result = ping(os.environ.get("ACS01_GUARD_HEARTBEAT_URL"),
                  scheduled=os.environ.get("GITHUB_EVENT_NAME") == "schedule",
                  guard_outcome=os.environ.get("GUARD_OUTCOME"),
                  preflight_outcome=os.environ.get("PRECHECK_OUTCOME"))
    print("External heartbeat:", result)
    # A failed or missing external monitoring service must not re-run ACS-01,
    # change production, or hide the original guard job outcome.
    return 0


if __name__ == "__main__":
    sys.exit(main())
