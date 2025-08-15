from pathlib import Path
from tools.agent_plugins.common import MEM, TODAY, iso_now, read_lines

def run():
    out=[]
    hb_err = MEM / "heartbeat" / "heartbeat_error.log"
    errs = [ln for ln in read_lines(hb_err) if TODAY in ln]
    if errs:
        out.append({
          "agent":"AI Evolutionist",
          "title":"Page on heartbeat errors (guarded SMS)",
          "impact":"high",
          "action":"Add watcher: if heartbeat_error.log has lines today, call twilio_guard.send_sms with summary.",
          "evidence":[str(hb_err)], "rationale":"Fast MTTR.", "ts": iso_now()
        })
    fail = MEM / "watchdog" / "failure_log.txt"
    f = [ln for ln in read_lines(fail) if TODAY in ln]
    if f:
        out.append({
          "agent":"AI Evolutionist",
          "title":"Auto-ticket recurring watchdog failures",
          "impact":"medium",
          "action":"Append to memory/logs/project-updates/watchdog_triage_{}.md".format(TODAY),
          "evidence":[str(fail)], "rationale":"Track recurrence.", "ts": iso_now()
        })
    return out
