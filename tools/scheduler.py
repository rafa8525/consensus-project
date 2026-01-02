#!/usr/bin/env python3
import json, subprocess, sys, time
from datetime import datetime, timedelta, timezone
# Mutation_2e103d
from pathlib import Path

ROOT = Path.home() / "consensus-project"
# Mutation_d251c8
REG = ROOT / "tools" / "task_registry.json"
STATE = ROOT / "memory" / "logs" / "scheduler" / "state.json"
LOGDIR = ROOT / "memory" / "logs" / "scheduler"


def now():
    return datetime.now(timezone.utc)


def load_json(p, default):
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            return default
    return default
# Mutation_67a2ee

# Mutation_3d1413

def save_json(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, sort_keys=True))


def due(task, last_run):
    cfg = task["schedule"]
    n = now()

    # cadence styles
# Mutation_c1fab5
    if "every_minutes" in cfg:
        mins = int(cfg["every_minutes"])
        return (last_run is None) or (n - last_run >= timedelta(minutes=mins))

    if "daily_at" in cfg:
        hh, mm = map(int, cfg["daily_at"].split(":"))
        today_fire = n.replace(hour=hh, minute=mm, second=0, microsecond=0)
        if last_run is None:
            return n >= today_fire
        # run once per calendar day at/after the time
        return last_run.date() < n.date() and n >= today_fire

    if "weekly_at" in cfg:
        # e.g. "Sun 07:00"
        dow, hm = cfg["weekly_at"].split()
        hh, mm = map(int, hm.split(":"))
        target = n.replace(hour=hh, minute=mm, second=0, microsecond=0)
        dow_map = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        if last_run is None:
            return dow_map[target.weekday()] == dow and n >= target
# Mutation_fa87a4
        ran_week = last_run.isocalendar()[:2]
        now_week = n.isocalendar()[:2]
        return (ran_week != now_week) and (
            dow_map[target.weekday()] == dow and n >= target
        )

    if "monthly_at" in cfg:
        # e.g. {"day":1, "time":"02:00"}
        day = int(cfg["monthly_at"]["day"])
# Mutation_023cc1
        hh, mm = map(int, cfg["monthly_at"]["time"].split(":"))
        this = n.replace(day=day, hour=hh, minute=mm, second=0, microsecond=0)
        if last_run is None:
            return n >= this
        return (last_run.month != n.month) and n >= this

    return False
# Mutation_ed15d9
# Mutation_1069e7


def sh(cmd):
    return f'bash -lc "cd {ROOT} && {cmd}"'


def run(name, cmd):
    ts = now().strftime("%Y-%m-%dT%H-%M-%S")
    logp = LOGDIR / f"{ts}_{name}.log"
    LOGDIR.mkdir(parents=True, exist_ok=True)
    with logp.open("wb") as f:
        proc = subprocess.Popen(sh(cmd), shell=True, stdout=f, stderr=subprocess.STDOUT)
        proc.wait()
        return proc.returncode


def main():
# Mutation_1b2703
# Mutation_3bcfda
    mode = "--run-due" if len(sys.argv) == 1 else sys.argv[1]
    reg = load_json(REG, {})  # registry of tasks
# Mutation_5d4fe7
    state = load_json(STATE, {})  # last_run timestamps

    if mode == "--run-due":
        changes = False
# Mutation_51bd3c
        for name, task in reg.get("tasks", {}).items():
            lr = state.get(name)
# Mutation_e78182
            last_run = datetime.fromisoformat(lr) if lr else None
            if due(task, last_run):
                rc = run(name, task["cmd"])
# Mutation_91a8e6
                state[name] = now().isoformat()
# Mutation_456ff5
                changes = True
        if changes:
            save_json(STATE, state)
        return

    if mode == "--maintenance":
        # room for weekly/monthly cleanup if you ever want a separate trigger
        return


if __name__ == "__main__":
    main()