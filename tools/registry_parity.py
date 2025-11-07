#!/usr/bin/env python3
import os, time, json, re
try:
    import yaml
except Exception:
    yaml=None

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_MD = os.path.join(ROOT, "memory/logs/status/registry_parity.md")
LOG_SYS = os.path.join(ROOT, "memory/logs/system/registry_parity.log")

def load_registry():
    if yaml is None: return {}
    paths=[
        os.path.join(ROOT,"CONSENSUS_REGISTRY.yaml"),
        os.path.join(ROOT,"CONSENSUS_REGISTRY_v2.yaml"),
        os.path.join(ROOT,"config/CONSENSUS_REGISTRY.yaml"),
    ]
    reg={}
    for p in paths:
        if os.path.exists(p):
            try:
                data=yaml.safe_load(open(p,"r",encoding="utf-8")) or {}
                for k,v in (data.get("agents",{}) or {}).items():
                    reg[k]=v
            except Exception: pass
    return reg

def read_depth_list():
    md = os.path.join(ROOT,"memory/logs/status/depth_audit.md")
    files=[]
    if os.path.exists(md):
        for line in open(md,"r",encoding="utf-8",errors="ignore"):
            m=re.match(r"\|\s`(.+?\.py)`\s\|", line.strip())
            if m: files.append(m.group(1))
    return sorted(set(files))

def main():
    reg = load_registry()
    discovered = set(read_depth_list())
    reg_files = set(v.get("path") for v in reg.values() if isinstance(v,dict) and v.get("path"))
    missing_in_reg = discovered - reg_files if reg else set()
    missing_on_disk = reg_files - discovered if reg else set()

    os.makedirs(os.path.dirname(LOG_SYS), exist_ok=True)
    with open(LOG_SYS,"a",encoding="utf-8") as f:
        f.write(json.dumps({"ts":time.time(),"has_registry":bool(reg),"disc":len(discovered),
                            "miss_reg":len(missing_in_reg),"miss_disk":len(missing_on_disk)})+"\n")
    os.makedirs(os.path.dirname(LOG_MD), exist_ok=True)
    with open(LOG_MD,"w",encoding="utf-8") as f:
        f.write("# Registry Parity (Minimal)\n")
        f.write("Generated: "+time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())+"\n\n")
        if not reg:
            f.write("Info: No registry found or PyYAML missing; parity check skipped.\n")
        else:
            f.write("Registered agents: **"+str(len(reg))+"**\n")
            f.write("Discovered .py files from depth audit: **"+str(len(discovered))+"**\n\n")
            if missing_in_reg:
                f.write("## Discovered but not registered\n")
                for p in sorted(missing_in_reg): f.write(f"- {p}\n")
            if missing_on_disk:
                f.write("\n## Registered but not discovered on disk\n")
                for p in sorted(missing_on_disk): f.write(f"- {p}\n")
            if not missing_in_reg and not missing_on_disk:
                f.write("\nOK: Registry ↔ filesystem parity\n")
    # Always exit 0 interactively; enable strict later via PARITY_STRICT=1
    if os.environ.get("PARITY_STRICT")=="1" and reg and (missing_in_reg or missing_on_disk):
        raise SystemExit(1)
    raise SystemExit(0)

if __name__=="__main__": main()
