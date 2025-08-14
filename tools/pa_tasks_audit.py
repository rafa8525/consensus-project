#!/usr/bin/env python3
import os, sys, requests, json
USER = os.environ.get("PA_USERNAME")
TOKEN = os.environ.get("PA_API_TOKEN")
if not USER or not TOKEN:
    print("Set PA_USERNAME and PA_API_TOKEN"); sys.exit(1)
BASE = f"https://www.pythonanywhere.com/api/v0/user/{USER}/"
def api(path, method="GET", data=None):
    h = {"Authorization": f"Token {TOKEN}"}
    url = BASE + path
    r = requests.request(method, url, headers=h, json=data)
    r.raise_for_status()
    return r.json() if r.text else {}
def main():
    tasks = api("schedule/").get("tasks", [])
    print("== Scheduled Tasks ==")
    for t in tasks: print(json.dumps(t, indent=2))
    disabled = []
    for t in tasks:
        cmd = (t.get("command") or "").lower()
        if any(k in cmd for k in ["twilio","sms","notify","reminder","watchdog","daily"]):
            api(f"schedule/{t['id']}/", method="POST", data={"enabled": False})
            disabled.append(t["id"])
    print(f"Disabled tasks: {disabled}")
if __name__ == "__main__": main()
