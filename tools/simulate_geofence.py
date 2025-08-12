#!/usr/bin/env python3
import time, argparse, subprocess
def sim(lat1,lon1,lat2,lon2,acc=30):
    # enter
    subprocess.check_call(["python3","tools/geofence_engine.py","--lat",str(lat1),"--lon",str(lon1),"--acc",str(acc),"--source","sim-enter"])
    time.sleep(2)
    # exit
    subprocess.check_call(["python3","tools/geofence_engine.py","--lat",str(lat2),"--lon",str(lon2),"--acc",str(acc),"--source","sim-exit"])
if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--enter", nargs=2, type=float, required=True); ap.add_argument("--exit", nargs=2, type=float, required=True); ap.add_argument("--acc", type=int, default=30)
    a=ap.parse_args(); sim(a.enter[0],a.enter[1],a.exit[0],a.exit[1],a.acc)
