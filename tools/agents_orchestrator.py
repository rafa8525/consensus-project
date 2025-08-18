#!/usr/bin/env python3
import sys, json, re, argparse, importlib.util
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path.home()/ "consensus-project"
REG  = ROOT / "registry" / "agents.yaml"
SUG  = ROOT / "memory" / "logs" / "agents" / "suggestions"
OUT_MD_DIR = ROOT / "memory" / "logs" / "agents"
TODAY = date.today().isoformat()

def iso_now(): 
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def parse_registry():
    txt = REG.read_text(encoding="utf-8")
    # minimal YAML parse with regex
    m = re.search(r'min_suggestions_per_day:\s*(\d+)', txt)
    min_sugg = int(m.group(1)) if m else 6
    plugins = re.findall(r'plugin:\s*([a-zA-Z0-9_]+)', txt)
    return min_sugg, plugins
def run_plugin(plugin_name):
    mod_path = ROOT / "tools" / "agent_plugins" / f"{plugin_name}.py"
    if not mod_path.exists():
        return [{
          "agent":"orchestrator",
          "title":f"Plugin missing: {plugin_name}",
          "impact":"low",
          "action":f"Add file tools/agent_plugins/{plugin_name}.py",
          "evidence":[str(mod_path)],
          "rationale":"Registry references it.",
          "ts": iso_now()
        }]
    try:
        spec = importlib.util.spec_from_file_location(plugin_name, str(mod_path))
        mod  = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)  # type: ignore
        res = mod.run() if hasattr(mod, "run") else []
        out=[]
        for r in (res or []):
            out.append({
              "agent":    r.get("agent", plugin_name),
              "title":    r.get("title","(no title)").strip(),
              "impact":   r.get("impact","info"),
              "action":   r.get("action","").strip(),
              "evidence": r.get("evidence",[]),
              "rationale":r.get("rationale",""),
              "ts":       r.get("ts", iso_now())
            })
        return out
    except Exception as e:
        return [{
          "agent":plugin_name,
          "title":"Plugin error",
          "impact":"low",
          "action":"Inspect plugin code; see JSONL for traceback summary.",
          "evidence":[str(mod_path)],
          "rationale":str(e),
          "ts": iso_now()
        }]
def write_jsonl(day, items):
    SUG.mkdir(parents=True, exist_ok=True)
    p = SUG / f"suggestions_{day}.jsonl"
    with p.open("a", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    return p

def merge_into_self_improvement(day, items):
    md = OUT_MD_DIR / f"self_improvement_{day}.md"
    header = "# Self-improvement suggestions"
    if md.exists():
        lines = md.read_text(encoding="utf-8").splitlines()
        if not lines or lines[0].strip() != header:
            lines = [header] + [ln for ln in lines if not ln.startswith("# ")]
    else:
        lines = [header]
    # dedupe by bullet text
    seen = {ln.strip().lower() for ln in lines if ln.startswith("- ")}
    for it in items:
        if not it.get("action"): 
            continue
        bullet = f"- {it['title']}: {it['action']}".strip()
        key = bullet.lower()
        if key not in seen:
            lines.append(bullet); seen.add(key)
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return md
def ensure_minimum(day, items, min_sugg):
    items = list(items)
    while len([i for i in items if i.get("action")]) < min_sugg:
        items.append({
          "agent":"orchestrator",
          "title":"Backfill suggestion",
          "impact":"low",
          "action":"Run agents_daily_improvement.py and add one concrete test or alert idea.",
          "evidence":[],
          "rationale":"Keep daily momentum.",
          "ts": iso_now()
        })
    return items

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="YYYY-MM-DD (default: today)")
    args = ap.parse_args()
    day = args.date or TODAY
    min_sugg, plugins = parse_registry()
    all_items=[]
    for name in plugins:
        all_items.extend(run_plugin(name))
    all_items = ensure_minimum(day, all_items, min_sugg)
    jl_path = write_jsonl(day, all_items)
    md_path = merge_into_self_improvement(day, all_items)
    print(f"Suggestions: {len(all_items)} → {jl_path.name}, updated {md_path.name}")

if __name__ == "__main__":
    sys.exit(main() or 0)
