#!/usr/bin/env python3
from __future__ import annotations
from mcl_v2.queue_worker import process_queue_once as _raw_pq_once


from mcl_v2.logging_setup import get_logger
from mcl_v2.queue_worker import process_queue_once as _raw_process_queue_once

# --- BEGIN: process_queue_once_safe (no monkey-patching) ---
def process_queue_once_safe(policy) -> bool:
    """
    Call the original queue worker once and normalize the result to bool.
    Never raises; logs and returns False on error.
    """
    logger = get_logger("MCLv2")
    try:
        r = _raw_process_queue_once(policy)
    except Exception as e:
        logger.error("queue loop error: %s", e, exc_info=True)
        return False
    try:
        if isinstance(r, tuple):
            return bool(r[0]) if r else False
        ok_attr = getattr(r, "ok", None)
        if ok_attr is not None:
            try:
                return bool(ok_attr)
            except Exception:
                return False
        return bool(r)
    except Exception as e:
        logger.error("queue loop normalize error: %s", e, exc_info=True)
        return False
# --- END: process_queue_once_safe ---
import mcl_v2.queue_worker as qw
from mcl_v2.queue_worker import process_queue_once as _raw_pq

import os
import time
import schedule

from mcl_v2.lockfile import acquire_or_exit

from mcl_v2.paths import ERR_LOG, LOCK
from mcl_v2.scheduler_setup import setup_schedules
from mcl_v2.queue_worker import process_queue_once as _process_queue_once_raw

def _process_queue_once_bool(policy):
    """Coerce historical return shapes (bool/tuple/.ok/other) to bool and catch exceptions."""
    try:
        r = _process_queue_once_raw(policy)
    except Exception as e:
        from mcl_v2.logging_setup import get_logger
        get_logger('MCLv2').error(f'queue loop error: {e}')
        return False
    if isinstance(r, tuple):
        return bool(r[0]) if r else False
    if hasattr(r, 'ok'):
        try:
            return bool(getattr(r, 'ok'))
        except Exception:
            pass
    return bool(r)

from mcl_v2.sms_policy import SmsPolicy
from mcl_v2.utils import now_iso, write_heartbeat

logger = get_logger("MCLv2")

def main() -> int:
    acquire_or_exit()
    logger.info("=== MCL v2 started ===")

    policy = SmsPolicy.from_env()
    setup_schedules()

    try:
        test_secs = int(os.environ.get("TEST_MODE_DURATION", "0"))
    except Exception:
        test_secs = 0
    deadline = time.time() + test_secs if test_secs > 0 else None

    write_heartbeat()

    while True:
        try:
            schedule.run_pending()
            _process_queue_once_bool(policy)
        except Exception as e:
            try:
                with open(ERR_LOG, "a", encoding="utf-8") as f:
                    f.write(f"[{now_iso()}] loop error: {e}\n")
            except Exception:
                pass
            logger.error("loop error: %s", e)
            time.sleep(1)
        else:
            time.sleep(1)

        if deadline and time.time() >= deadline:
            logger.info("TEST_MODE_DURATION reached; exiting 0")
            break

    try:
        if LOCK.exists():
            LOCK.unlink()
    except Exception:
        pass
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
