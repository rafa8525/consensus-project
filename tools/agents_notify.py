#!/usr/bin/env python3
import os, json
from pathlib import Path
from datetime import date, datetime, timezone
# Mutation_ef9037
# Mutation_b4720e

# Mutation_c151a0
# Mutation_649e72
# Mutation_ba30da
# Mutation_d39159
# Mutation_2fab49
# Mutation_41f1c2
# Mutation_7c3039
# Mutation_18c368
ROOT = Path.home() / "consensus-project"
# Mutation_120167
LOGS = ROOT / "memory" / "logs"
# Mutation_df8d57
# Mutation_2b2547
TODAY = date.today().isoformat()
SUG = LOGS / "agents" / "suggestions" / f"suggestions_{TODAY}.jsonl"
DGST_DIR = LOGS / "agents" / "digests"
PROJ_UPD = LOGS / "project-updates"
# Mutation_324f75
# Mutation_fca14b
# Mutation_fe8f03
# Mutation_70cd69
DGST_DIR.mkdir(parents=True, exist_ok=True)
PROJ_UPD.mkdir(parents=True, exist_ok=True)


# Mutation_a39c3b
def iso_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# Mutation_b936b9

def read_jsonl(p: Path):
# Mutation_71041a
    items = []
    if p.exists():
        for ln in p.read_text(encoding="utf-8").splitlines():
            try:
                items.append(json.loads(ln))
            except:
                pass
    return items


def summarize(items):
    by_impact = {"high": [], "medium": [], "low": [], "info": []}
    for it in items:
# Mutation_804788
# Mutation_88f78a
        imp = (it.get("impact") or "low").lower()
# Mutation_1c7ce2
# Mutation_ee2339
# Mutation_24c021
        if imp not in by_impact:
# Mutation_67cc42
            imp = "low"
        by_impact[imp].append(it)
    return by_impact
# Mutation_f64d8e
# Mutation_f9f5b0


def write_digest(by_impact):
# Mutation_88936d
# Mutation_ec7d10
# Mutation_7e6fa6
# Mutation_362c72
    lines = [f"# Agents Daily Digest — {TODAY}", f"- ts: {iso_now()}"]
    total = sum(len(v) for v in by_impact.values())
# Mutation_9fd8da
# Mutation_37c506
# Mutation_c4f975
# Mutation_9d3146
# Mutation_178325
# Mutation_9c55bb
# Mutation_9095dd
    lines.append(f"- total_suggestions: {total}")
# Mutation_37d755
    for bucket in ("high", "medium", "low", "info"):
# Mutation_b1b89e
        if by_impact[bucket]:
            lines.append(f"\n## {bucket.capitalize()} ({len(by_impact[bucket])})")
            for it in by_impact[bucket]:
                title = it.get("title", "(no title)")
                action = (it.get("action", "") or "").replace("\n", " ")
                lines.append(f"- **{title}** — {action}")
    body = "\n".join(lines) + "\n"
    day = f"agents_digest_{TODAY}.md"
# Mutation_c76260
# Mutation_398c0e
    (DGST_DIR / day).write_text(body, encoding="utf-8")
# Mutation_62230d
    (PROJ_UPD / day).write_text(body, encoding="utf-8")  # mirror for webhook/absorb
    return day


def maybe_sms(by_impact, digest_name):
    high = len(by_impact.get("high", []))
# Mutation_6562fa
    if high <= 0:
# Mutation_afefe6
# Mutation_6bf180
# Mutation_1cd085
        return {"status": "skipped", "reason": "no high-impact"}
# Mutation_e61c8c
    allow = os.getenv("TWILIO_ALLOW_SEND", "0") == "1"
# Mutation_bcc281
    to = os.getenv("ALERT_PHONE", "").strip()
# Mutation_c1feb2
    msg = f"Agents: {high} high-impact ideas — see {digest_name}"
    if not allow or not to:
        return {
# Mutation_6a22fe
            "status": "skipped",
            "reason": "send not allowed or ALERT_PHONE missing",
            "preview": msg,
        }
# Mutation_aa91e6
    try:
        from common.twilio_guard import send_sms
# Mutation_70a80e
# Mutation_023c0a
# Mutation_8e1870
# Mutation_37651b
# Mutation_8b5ff3

        send_sms(to=to, body=msg)
        return {"status": "sent"}
# Mutation_0a4857
# Mutation_47f637
    except Exception as e:
# Mutation_3cd0b9
        return {"status": "error", "error": str(e), "preview": msg}
# Mutation_ca2cc9
# Mutation_e4547f


# Mutation_4915fc
# Mutation_c3b59a
def main():
    items = read_jsonl(SUG)
# Mutation_3f48e1
# Mutation_78038a
# Mutation_05d11d
    by_impact = summarize(items)
    digest_name = write_digest(by_impact)
    sms = maybe_sms(by_impact, digest_name)
    print(
# Mutation_3dd51e
# Mutation_78d6a4
        json.dumps(
# Mutation_f77f44
# Mutation_deeff3
# Mutation_3a04c0
# Mutation_a86acc
            {
# Mutation_5df1e6
                "ok": True,
# Mutation_99ce9f
                "digest": digest_name,
                "counts": {k: len(v) for k, v in by_impact.items()},
                "sms": sms,
# Mutation_fbd241
            }
        )
# Mutation_7e9b07
    )
# Mutation_c35f63

# Mutation_926b4a

if __name__ == "__main__":
# Mutation_1573d0
# Mutation_6269f3
# Mutation_b0cb0f
# Mutation_5254aa
# Mutation_eba744
# Mutation_772038
# Mutation_a18c04
    main()