#!/usr/bin/env python3
import json, time, math, argparse
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
MEM  = ROOT/"memory"
CONF = MEM/"config"/"geofences.json"
STATE= MEM/"logs"/"geofencing"/"engine_state.json"
LOG  = MEM/"logs"/"geofencing"/"geofence_events.log"
(MEM/"logs"/"geofencing").mkdir(parents=True, exist_ok=True)

def load_conf():
    d = json.loads(CONF.read_text(encoding="utf-8"))
    return d.get("geofences", [])

def load_state():
    if STATE.exists():
        try: return json.loads(STATE.read_text(encoding="utf-8"))
        except: pass
    return {"last_seen":{}, "inside":{}}

def save_state(s): STATE.write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")

def log(line):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}] {line}\n")

def haversine_m(lat1, lon1, lat2, lon2):
    R=6371000
    p=math.pi/180
    dphi=(lat2-lat1)*p; dl=(lon2-lon1)*p
    a=math.sin(dphi/2)**2 + math.cos(lat1*p)*math.cos(lat2*p)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(a))

def act(action, fence, event):
    if action=="vpn_on":
        log(f"ACTION vpn_on fence={fence['id']} via event={event}")
        # TODO: integrate with tools/vpn_autoconnect.py
    elif action=="note":
        log(f"ACTION note '{fence['label']}' event={event}")
    elif action=="remind":
        # example: could call tools/remind.py for a fixed text
        log(f"ACTION remind fence={fence['id']} event={event}")
    else:
        log(f"ACTION unknown={action} fence={fence['id']}")

def process_event(lat, lon, accuracy_m=50, source="unknown"):
    fences = load_conf()
    st = load_state()
    now = int(time.time())
    for f in fences:
        dist = haversine_m(lat, lon, f["lat"], f["lon"])
        inside = dist <= max(1, f.get("radius_m", 150) + accuracy_m)
        fid = f["id"]
        prev_inside = bool(st["inside"].get(fid, False))
        last_fire = int(st["last_seen"].get(fid, 0))
        min_gap = int(f.get("min_retrigger_sec", 900))
        if inside and not prev_inside:
            # entering; require dwell to reduce false positives
            dwell = int(f.get("dwell_sec", 120))
            key = f"enter_probe_{fid}"
            if st["inside"].get(key, 0)==0:
                st["inside"][key] = now
                log(f"ENTER probe start fence={fid} dist_m={int(dist)} acc_m={accuracy_m}")
            elif now - int(st["inside"][key]) >= dwell and now - last_fire >= min_gap:
                log(f"ENTER confirmed fence={fid} dist_m={int(dist)} acc_m={accuracy_m} src={source}")
                act(f.get("enter_action","note"), f, {"type":"enter","lat":lat,"lon":lon})
                st["last_seen"][fid] = now
                st["inside"][fid] = True
                st["inside"][key] = 0
        elif not inside and prev_inside:
            # exiting; simple hysteresis using min_gap
            if now - last_fire >= min_gap:
                log(f"EXIT confirmed fence={fid} dist_m={int(dist)} acc_m={accuracy_m} src={source}")
                act(f.get("exit_action","note"), f, {"type":"exit","lat":lat,"lon":lon})
                st["last_seen"][fid] = now
                st["inside"][fid] = False
        else:
            # maintain probe or clear
            st["inside"].setdefault(fid, inside)
    save_state(st)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True)
    ap.add_argument("--acc", type=int, default=50)
    ap.add_argument("--source", default="manual")
    args = ap.parse_args()
    process_event(args.lat, args.lon, args.acc, args.source)
    print("OK")

if __name__=="__main__":
    main()
