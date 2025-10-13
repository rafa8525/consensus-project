from common import twilio_guard
from __future__ import annotations

import json
import os
import time
from pathlib import Path

from mcl_v2.paths import QUEUE, Q_PROC, Q_DONE
from mcl_v2.sms_policy import SmsPolicy
from mcl_v2.utils import jitter


def _load_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _twilio_send(policy: SmsPolicy, to: str, body: str, key: str) -> None:
    """Best-effort bounded delivery; record errors instead of raising."""
    try:
        from twilio.rest import Client  # type: ignore
    except Exception as e:
        policy.record("ERROR_NO_TWILIO", to, body, key=key, meta={"err": str(e)})
        return

    sid = os.getenv("TWILIO_ACCOUNT_SID", "")
    tok = os.getenv("TWILIO_AUTH_TOKEN", "")
    from_number = os.getenv("TWILIO_FROM_NUMBER", "")
    if not sid or not tok or not from_number or not to:
        policy.record(
            "ERROR_MISSING_ENV", to, body, key=key,
            meta={"need": ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_FROM_NUMBER"]},
        )
        return

    try:
        cli = Client(sid, tok)
        attempts, delivered, last_err = 0, False, None
        while attempts < 2 and not delivered:
            attempts += 1
            try:
                msg = clitwilio_guard.send_sms(client, to=to, from_=from_number, body=body)
                policy.record("DELIVERED", to, body, key=key, meta={"sid": getattr(msg, "sid", None)})
                delivered = True
            except Exception as e:
                last_err = str(e)
                time.sleep(jitter(2, 0.3))
        if not delivered:
            policy.record("ERROR_SEND", to, body, key=key, meta={"err": last_err})
    except Exception as e:  # pragma: no cover
        policy.record("ERROR_INIT", to, body, key=key, meta={"err": str(e)})


def process_queue_once(policy: SmsPolicy) -> None:
    """
    At-most-once: QUEUE/*.json -> Q_PROC/name (atomic rename) -> Q_DONE/name (finalize).
    Only handles {"type":"sms","to":...,"body":...,"key":optional}.
    """
    for job in sorted(QUEUE.glob("*.json")):
        proc = Q_PROC / job.name
        try:
            job.rename(proc)  # claim
        except FileNotFoundError:
            continue
        except Exception:
            continue

        try:
            data = _load_json(proc)
            if str(data.get("type", "")).lower() != "sms":
                Q_DONE.joinpath(proc.name).write_text(json.dumps(data), encoding="utf-8")
                policy.record("SKIP_UNKNOWN_JOB", data.get("to", ""), str(data)[:200], key="unknown", meta={"file": proc.name})
                continue

            to = str(data.get("to", "")).strip()
            body = str(data.get("body", "")).strip()
            key = str(data.get("key") or policy.stable_key(to, body))

            decision = policy.decide(to, key, body_preview=body[:60])
            if not decision:
                policy.record(decision.reason, to, body, key=key)
            else:
                _twilio_send(policy, to, body, key=key)
        finally:
            try:
                Q_DONE.joinpath(proc.name).write_text(proc.read_text(encoding="utf-8"), encoding="utf-8")
            except Exception:
                pass
            try:
                proc.unlink()
            except Exception:
                pass



def handle_sms_job(policy, job: dict):
    logger = get_logger("MCLv2")
    to   = job.get("to", "")
    body = job.get("body", "")
    key  = job.get("key") or policy.stable_key(to, body)

    status, meta = policy.decide(to, body)
    logger.info(f"sms decision: to={to} status={status} meta={meta}")

    if status != "ALLOW":
        policy.record(status, to, body, key=key, meta=meta)
        return True

    # Twilio not wired yet: record an error instead of sending
    policy.record("ERROR_NO_TWILIO", to, body, key=key, meta={"hint": "wire Twilio creds to send"})
    return True