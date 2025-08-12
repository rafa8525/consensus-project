#!/usr/bin/env python3
import os, subprocess, json, platform
from pathlib import Path
from datetime import datetime, timedelta

SAFE_SSIDS = {s.strip() for s in os.getenv("SAFE_SSIDS", "Home,Work,PhoneHotspot").split(",") if s.strip()}
DRY_RUN = os.getenv("VPN_DRY_RUN", "1") == "1"
UP_CMD = os.getenv("VPN_UP_CMD", "")
STATUS_CMD = os.getenv("VPN_STATUS_CMD", "")
COOLDOWN_MIN = int(os.getenv("VPN_COOLDOWN_MIN", "10"))

BASE = Path("/home/rafa1215/consensus-project/memory/logs/security")
BASE.mkdir(parents=True, exist_ok=True)
STATE = BASE / ".state_vpn_autoconnect.json"
LOG = BASE / "vpn_autoconnect.log"

def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def log(msg):
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")

def load_state():
    try:
        return json.loads(STATE.read_text())
    except Exception:
        return {}

def save_state(d):
    STATE.write_text(json.dumps(d))

def current_ssid():
    sysname = platform.system().lower()
    if "windows" in sysname:
        out = sh("netsh wlan show interfaces").stdout
        for line in out.splitlines():
            if line.strip().lower().startswith("ssid") and "bssid" not in line.lower():
                return line.split(":",1)[1].strip()
    elif "darwin" in sysname:
        out = sh("/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I").stdout
        for line in out.splitlines():
            if " SSID:" in line:
                return line.split("SSID:",1)[1].strip()
    else:
        out = sh("nmcli -t -f active,ssid dev wifi | egrep '^yes' | cut -d: -f2").stdout.strip()
        if not out:
            out = sh("iwgetid -r").stdout.strip()
        return out or None
    return None

def vpn_status():
    if not STATUS_CMD:
        return "unknown"
    r = sh(STATUS_CMD)
    if r.returncode == 0 and r.stdout.strip():
        return r.stdout.strip()[:200]
    return f"rc={r.returncode} {r.stderr.strip()[:120]}"

def connect_vpn():
    if not UP_CMD:
        log("VPN_UP_CMD not set; cannot connect.")
        return {"ok": False, "reason": "no_cmd"}
    if DRY_RUN:
        log(f"DRY_RUN: would run: {UP_CMD}")
        return {"ok": True, "dry_run": True}
    r = sh(UP_CMD)
    ok = (r.returncode == 0)
    log(f"RUN: {UP_CMD} -> rc={r.returncode} out='{r.stdout.strip()[:200]}' err='{r.stderr.strip()[:200]}'")
    return {"ok": ok, "rc": r.returncode}

def main():
    ssid = current_ssid() or "<unknown>"
    st = load_state()
    last_ssid = st.get("last_ssid")
    last_when = datetime.fromisoformat(st["last_action"]) if st.get("last_action") else datetime.min

    public = (ssid not in SAFE_SSIDS)
    log(f"SSID='{ssid}' public={public} status='{vpn_status()}'")
    if public and (ssid != last_ssid or datetime.now() - last_when >= timedelta(minutes=COOLDOWN_MIN)):
        res = connect_vpn()
        st = {"last_ssid": ssid, "last_action": datetime.now().isoformat(), "last_result": res}
        save_state(st)
    else:
        st = {"last_ssid": ssid, "last_action": st.get("last_action"), "last_result": st.get("last_result")}
        save_state(st)

if __name__ == "__main__":
    main()
