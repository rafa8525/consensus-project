#!/usr/bin/env bash
# finalize_consensus.sh — one-touch consolidation for Consensus Project
# - Harden guard, logs-only (no SMS), wire Ride-Deals into status
# - Run one-shot health tasks, build today’s report, print proofs

# ---- Safe shell options (portable) ----
set -e
set -u
set -o pipefail 2>/dev/null || true

ROOT="$HOME/consensus-project"
TOOLS="$ROOT/tools"
LOGS="$HOME/memory/logs"
SYS="$LOGS/system"
REPORTS="$LOGS/reports"

say() { printf '%s\n' "$*"; }

mkdir -p "$SYS" "$REPORTS"

say "=== 0) Sanity: required tools present ==="
# (Keep this list minimal but sufficient)
REQ="mcl_guard.py ride_deals_scan.py security_suite.py morning_master.py status_postprocess.py publish_status_report.py vpn_test_runner.py"
missing=0
for f in $REQ; do
  if [ ! -s "$TOOLS/$f" ]; then
    say "MISSING: $TOOLS/$f"
    missing=1
  fi
done
if [ "$missing" -ne 0 ]; then
  say "❌ Missing files above. Aborting."
  exit 1
fi
chmod +x "$TOOLS/"*.py 2>/dev/null || true

say "=== 1) Enforce logs-only (no SMS) ==="
# Disable Twilio in .env if present
if [ -f "$HOME/reminder-api/.env" ]; then
  if grep -q '^SMS_ENABLED=' "$HOME/reminder-api/.env"; then
    sed -i 's/^SMS_ENABLED=.*/SMS_ENABLED=false/' "$HOME/reminder-api/.env"
  else
    printf '\nSMS_ENABLED=false\n' >> "$HOME/reminder-api/.env"
  fi
fi
# Comment out any SMS artifact vars (idempotent)
sed -i -E 's/^\s*(OUT_SMS\s*=.*)$/# SMS disabled: \1/' "$TOOLS/ride_deals_scan.py" 2>/dev/null || true
sed -i -E 's/^\s*(OUT_SMS\s*=.*)$/# SMS disabled: \1/' "$TOOLS/geofence_nudger.py" 2>/dev/null || true
sed -i -E 's/^\s*(SMS_ALERT\s*=.*)$/# SMS disabled: \1/' "$TOOLS/security_suite.py" 2>/dev/null || true
# Remove any old SMS trigger files
rm -f "$SYS"/*.sms "$SYS"/*_sms.txt 2>/dev/null || true

say "=== 2) Clear cadence markers (force fresh run) ==="
rm -f "$SYS"/.last_*.py 2>/dev/null || true

say "=== 3) Wire Ride-Deals into daily status (postprocess) ==="
python3 - <<'PY'
from pathlib import Path
p = Path("/home/rafa1215/consensus-project/tools/morning_master.py")
if p.exists():
    s = p.read_text(encoding="utf-8")
    hook = 'run(["python3", str(TOOLS / "status_postprocess.py")])'
    if hook not in s:
        s = s.replace(
            'run(["python3", str(TOOLS / "publish_status_report.py")])',
            'run(["python3", str(TOOLS / "publish_status_report.py")])\n    ' + hook
        )
        p.write_text(s, encoding="utf-8")
        print("morning_master: added status_postprocess hook")
    else:
        print("morning_master: hook already present")
else:
    print("morning_master.py missing (unexpected)")
PY

say "=== 4) One-shot guard (runs eligible tasks now) ==="
MCL_ONESHOT=true python3 "$TOOLS/mcl_guard.py" || true

say "=== 5) Morning summary (idempotent) ==="
python3 "$TOOLS/morning_master.py" || true

say "=== 6) Status report (today) + postprocess append ==="
python3 "$TOOLS/publish_status_report.py" || true
python3 "$TOOLS/status_postprocess.py" || true

say "=== 7) Doctor snapshot ==="
if [ -f "$ROOT/consensus_doctor.py" ]; then
  python3 "$ROOT/consensus_doctor.py" | tee -a "$SYS/consensus_doctor_history.log" || true
else
  say "consensus_doctor.py not found (skipping doctor snapshot)"
fi

say "=== 8) Proofs ==="
say "--- Heartbeat tail ---"
tail -n 10 "$SYS/mcl_guard_heartbeat.log" 2>/dev/null || say "(no heartbeat yet)"

say "--- Ride deals JSON (ts + counts) ---"
python3 - <<'PY'
import json, pathlib
j = pathlib.Path("/home/rafa1215/memory/logs/system/ride_deals.json")
if j.exists():
    try:
        d = json.loads(j.read_text() or "{}")
        print(d.get("ts", "<no ts>"))
        for it in d.get("sites", []):
            site = it.get("site", "?")
            cnt = len(it.get("hits", [])) if "hits" in it else "ERR"
            print(f"{site} -> {cnt}")
    except Exception as e:
        print(f"(parse error: {e})")
else:
    print("ride_deals.json missing")
PY

say "--- Status top (should include Ride Deals summary near end) ---"
STATUS_FILE="$REPORTS/project_status_$(date -u +%F).md"
if [ -f "$STATUS_FILE" ]; then
  sed -n '1,220p' "$STATUS_FILE"
else
  say "Project status for today not found: $STATUS_FILE"
fi

say "=== DONE: finalize_consensus OK ==="
