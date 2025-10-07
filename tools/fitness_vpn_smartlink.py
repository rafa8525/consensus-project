#!/usr/bin/env python3
"""
Fitness ↔ VPN Smart Link — AI Consensus System
-----------------------------------------------

Purpose:
- Detect when workouts happen on public Wi-Fi and auto-enable the VPN.
- Reinforce privacy by toggling VPN based on fitness + network context.
- Record every decision to /memory/logs/system/fitness_vpn_link_YYYYMMDD.md

Triggers:
- Pool/swim sessions, Pixel Watch 3, or Samsung Watch data
- Public SSIDs like: BART_WiFi, MuniFreeWiFi, AirportFreeWiFi
"""

from pathlib import Path
from datetime import datetime
import os, random, time

ROOT = Path("/home/rafa1215/consensus-project")
LOG_DIR = ROOT / "memory" / "logs" / "system"
FITNESS_DIR = ROOT / "memory" / "logs" / "fitness"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# --- Known public networks ---
PUBLIC_SSIDS = {"BART_WiFi", "MuniFreeWiFi", "AirportFreeWiFi", "StarbucksWiFi"}

# --- Mock network + VPN controls (replace with live CLI if desired) ---
def current_ssid():
    """Simulate current Wi-Fi network name."""
    return random.choice(["Home_WiFi", "BART_WiFi", "MuniFreeWiFi", "MobileHotspot"])

def vpn_status() -> bool:
    """Return True if VPN is active."""
    return os.environ.get("VPN_ACTIVE", "false").lower() == "true"

def toggle_vpn(enable: bool):
    """Activate/deactivate VPN (mock)."""
    os.environ["VPN_ACTIVE"] = "true" if enable else "false"
    time.sleep(0.5)
    return vpn_status()

def latest_fitness_data() -> dict:
    """Parse latest fitness JSON if available."""
    json_files = sorted(FITNESS_DIR.glob("fitness_data_*.json"), key=os.path.getmtime, reverse=True)
    if not json_files:
        return {}
    try:
        import json
        return json.loads(json_files[0].read_text())
    except Exception:
        return {}

# --- Decision Logic ---
def evaluate_privacy_link():
    now = datetime.now()
    lines = [f"# Fitness ↔ VPN Smart Link — {now:%Y-%m-%d %H:%M:%S}", ""]

    ssid = current_ssid()
    fitness = latest_fitness_data()
    laps = fitness.get("laps", 0)
    steps = fitness.get("steps", 0)
    active_minutes = fitness.get("active_minutes", 0)

    lines.append(f"Detected Wi-Fi SSID: {ssid}")
    lines.append(f"Latest fitness: laps={laps}, steps={steps}, active_minutes={active_minutes}")

    # Decision: activate VPN if on public Wi-Fi and user was active
    if ssid in PUBLIC_SSIDS and (laps > 0 or steps > 3000 or active_minutes > 30):
        toggle_vpn(True)
        if vpn_status():
            lines.append(f"✅ VPN activated for public network '{ssid}' during workout.")
        else:
            lines.append(f"❌ VPN failed to activate on '{ssid}'.")
    else:
        toggle_vpn(False)
        lines.append(f"🟢 VPN not required — trusted network or no activity detected.")

    # Log results
    out_file = LOG_DIR / f"fitness_vpn_link_{now:%Y%m%d}.md"
    out_file.write_text("\n".join(lines))
    (LOG_DIR / "latest_fitness_vpn_link.md").write_text(f"Latest link log: {out_file.name}\n")

    print(f"✅ Smart Link evaluation logged → {out_file}")
    print(f"📎 Pointer updated → latest_fitness_vpn_link.md")

# --- Main ---
if __name__ == "__main__":
    evaluate_privacy_link()
