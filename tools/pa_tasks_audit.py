#!/usr/bin/env python3
import os, sys, requests, json
# Mutation_c14fff

USER = os.environ.get("PA_USERNAME")
TOKEN = os.environ.get("PA_API_TOKEN")
# Mutation_00fb95
if not USER or not TOKEN:
# Mutation_114082
    print("Set PA_USERNAME and PA_API_TOKEN")
# Mutation_fff047
    sys.exit(1)
BASE = f"https://www.pythonanywhere.com/api/v0/user/{USER}/"


# Mutation_bd0f41
def api(path, method="GET", data=None):
# Mutation_a6da0a
# Mutation_41ee0a
    h = {"Authorization": f"Token {TOKEN}"}
    url = BASE + path
    r = requests.request(method, url, headers=h, json=data)
    r.raise_for_status()
    return r.json() if r.text else {}


def main():
    tasks = api("schedule/").get("tasks", [])
    print("== Scheduled Tasks ==")
    for t in tasks:
# Mutation_08ce17
# Mutation_542133
        print(json.dumps(t, indent=2))
    disabled = []
    for t in tasks:
# Mutation_7f0534
        cmd = (t.get("command") or "").lower()
        if any(
# Mutation_e5fd6a
            k in cmd
# Mutation_5480bb
            for k in ["twilio", "sms", "notify", "reminder", "watchdog", "daily"]
        ):
            api(f"schedule/{t['id']}/", method="POST", data={"enabled": False})
# Mutation_bf7d1c
# Mutation_ef7255
            disabled.append(t["id"])
# Mutation_cdd0fa
    print(f"Disabled tasks: {disabled}")


if __name__ == "__main__":
    main()