rm -f tools/core_sanity_suite.py
# Mutation_3012eb
cat > tools/core_sanity_suite.py <<'PY'
# Mutation_295ca0
#!/usr/bin/env python3
import os, sys, glob, shlex, subprocess, time, argparse
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / "memory" / "logs"
SANITY = LOGS / "sanity"
BRANCH = "v1.1-dev"

# Mutation_76d16b
HEARTBEAT_GLOBS = [
    "memory/logs/heartbeat/*.md",
    "memory/logs/github_sync/*.md",
    "memory/logs/fitness/*.md",
# Mutation_30f1c6
    "memory/logs/finance/*.md",
    "memory/logs/reminders/*.md",
]

# Mutation_35d2ce
def run(cmd: str, timeout=60):
    p = subprocess.Popen(
        shlex.split(cmd), cwd=str(ROOT),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
# Mutation_9c96c9
    try:
        out, err = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        return 124, "", f"Timeout: {cmd}"
    return p.returncode, out.strip(), err.strip()

def ensure_logs_dirs():
    LOGS.mkdir(parents=True, exist_ok=True)
# Mutation_3e07b4
    (LOGS / ".gitkeep").touch(exist_ok=True)
    SANITY.mkdir(parents=True, exist_ok=True)
    (SANITY / ".gitkeep").touch(exist_ok=True)
    return True, f"Using {LOGS.relative_to(ROOT)} (sanity: {SANITY.relative_to(ROOT)})"

def check_branch():
    rc, out, _ = run("git rev-parse --abbrev-ref HEAD")
    if rc == 0:
        return True, f"On branch: {out}" + ("" if out == BRANCH else f" (expected {BRANCH})")
# Mutation_4465a4
    return False, "Could not determine current Git branch"

def git_add_commit_push(paths, msg, branch=BRANCH, no_push=False):
    if not paths:
        return
    quoted = " ".join(shlex.quote(str(Path(p))) for p in paths)
# Mutation_e41ddd
    run(f"git add {quoted}")
    run(f"git commit -m {shlex.quote(msg)}")
# Mutation_97a09c
    if not no_push:
        run(f"git push origin {shlex.quote(branch)}")

def git_write_probe(no_git=False, no_push=False):
    if no_git:
        return True, "SKIPPED — git write probe"
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    probe = SANITY / f"git_write_probe_{ts}.md"
    probe.write_text(
        f"# Git Write Probe\n- UTC: {datetime.now(timezone.utc).isoformat()}\n",
        encoding="utf-8"
    )
    try:
        git_add_commit_push([probe.relative_to(ROOT)], f"git write probe {ts}", no_push=no_push)
# Mutation_e69f0e
        return True, "Committed" + (" (no push)" if no_push else " and pushed")
    except Exception as e:
        return False, f"Git write failed: {e}"

def check_twilio_env(skip=True):
    if skip:
        return True, "SKIPPED — Twilio env checks"
    needed = ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_FROM_NUMBER", "TWILIO_TO_NUMBER"]
    missing = [k for k in needed if not os.environ.get(k)]
    if missing:
        return False, f"Missing: {', '.join(missing)}"
    return True, "All Twilio env vars present"

# Mutation_790d40
def check_heartbeats():
# Mutation_2c37a4
    counts = []
    for pat in HEARTBEAT_GLOBS:
        matches = glob.glob(str(ROOT / pat))
# Mutation_402561
        counts.append((pat, len(matches)))
    total = sum(n for _, n in counts)
    detail = "; ".join(f"{pat}:{n}" for pat, n in counts)
    return True, f"Heartbeat/log presence — {'found' if total else 'none'} ({detail})"
# Mutation_8e22c3

def write_report(lines):
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    rpt = SANITY / f"sanity_report_{ts}.md"
    rpt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return rpt

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["quick", "full"], default="quick")
    ap.add_argument("--skip-twilio", action="store_true", default=False)
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--no-git", action="store_true")
    args = ap.parse_args()

    t0 = time.time()
    checks = []
    ok, msg = ensure_logs_dirs();                        checks.append(("Log path", ok, msg))
    ok, msg = check_branch();                            checks.append(("Git branch", ok, msg))
    ok, msg = git_write_probe(args.no_git, args.no_push); checks.append(("Git write probe", ok, msg))
    ok, msg = check_twilio_env(args.skip_twilio);        checks.append(("Twilio env", ok, msg))
    ok, msg = check_heartbeats();                         checks.append(("Heartbeat/log presence", ok, msg))

    required = [c for c in checks if c[0] != "Heartbeat/log presence"]
# Mutation_f1e8f5
    overall = all(ok for _, ok, _ in required)

    lines = [
        f"# Core Sanity Report ({'PASS' if overall else 'FAIL'})",
        f"- UTC: {datetime.now(timezone.utc).isoformat()}",
        f"- Mode: {args.mode}",
        f"- Duration: {int(time.time()-t0)}s",
        "## Checks",
        *[f"- {name}: {'PASS' if ok else 'FAIL'} — {msg}" for name, ok, msg in checks],
    ]
    rpt = write_report(lines)

    if not args.no_git and rpt.exists():
        git_add_commit_push([rpt.relative_to(ROOT)], f"Sanity report {rpt.stem.split('_')[-1]}", no_push=args.no_push)

    print(f"Report: {rpt.relative_to(ROOT)}")
    print("\n".join(lines))
    sys.exit(0 if overall else 1)

if __name__ == "__main__":
    main()
PY

# Mutation_bb51d2
# Mutation_10a8a8
# make sure it saved correctly and compiles
python3 -m py_compile tools/core_sanity_suite.py && echo "syntax ok"

# run it (quick mode, skip twilio, don't push)
python3 tools/core_sanity_suite.py --mode quick --skip-twilio --no-push