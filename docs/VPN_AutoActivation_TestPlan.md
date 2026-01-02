# VPN Auto-Activation — Canonical Test Plan (v1)

## Purpose
Validate that the system reliably **detects public Wi-Fi** and automatically **connects/disconnects VPN** with clear, auditable evidence.

## Scope
- Functional behavior (detect → connect, leave → disconnect)
- Reliability (false positives/negatives)
- Recovery (network drop, captive portal, VPN failure)
- Non-functional tests (load/stress/concurrency/endurance/failover)
- Evidence capture (logs + summary)

## Environments to test
- Home Wi-Fi (private / trusted SSID)
- At least 2 public Wi-Fi SSIDs (e.g., cafe, transit, guest network)
- Captive portal network (if available)
- Cellular hotspot (optional; treat as “private” unless configured otherwise)

## Required configuration
- SSID allow/deny lists (or “public detection rule”)
- VPN client command/connection method
- Logging enabled for:
  - Wi-Fi SSID changes
  - “public network” classification result
  - VPN connect/disconnect attempts
  - final VPN state after each attempt

## Functional test cases (must pass)
### F1 — Connect on public Wi-Fi
- Steps:
  1. Join a known public SSID
  2. Observe classification = public
  3. Observe VPN connect triggered
- Pass if:
  - VPN connects within **T seconds** (set T=30 unless you pick a different value)
  - Log shows: ssid → public → connect_attempt → connected

### F2 — Do NOT connect on trusted/private Wi-Fi
- Steps:
  1. Join trusted SSID
- Pass if:
  - Classification = private/trusted
  - VPN does not auto-connect (unless explicitly forced)
  - Log shows: ssid → private → no_connect

### F3 — Disconnect when leaving public Wi-Fi
- Steps:
  1. Start connected on public Wi-Fi with VPN on
  2. Switch to trusted SSID (or disconnect Wi-Fi entirely)
- Pass if:
  - VPN disconnects (or returns to your policy default)
  - Log shows: leave_public → disconnect_attempt → disconnected

### F4 — Captive portal handling (no “fake success”)
- Steps:
  1. Join a captive-portal SSID
- Pass if:
  - System does not record “connected” unless VPN is actually connected
  - Captive portal state is logged explicitly

### F5 — Failure + retry backoff
- Steps:
  1. Force a VPN connect failure (bad server, blocked port, etc.)
- Pass if:
  - A limited retry policy triggers (e.g., 2 retries)
  - Then backoff/diagnostic mode is entered
  - No alert spam

## Reliability tests (recommended)
- R1: 20 connect/disconnect cycles across 2 SSIDs (measure failure rate)
- R2: False positive test: networks that look public but are trusted (guest network)
- R3: False negative test: public SSID not in list (should still classify correctly if heuristic exists)

## Non-functional tests (run if the feature is daemonized / multi-agent)
- Load testing: repeated SSID transitions at expected daily volume
- Stress testing: rapid SSID flaps (on/off every few seconds)
- Concurrency testing: multiple agents emitting events simultaneously
- Endurance testing: keep monitoring active for 24–72 hours
- Failover testing: simulate watchdog restart mid-transition

## Evidence artifacts (required for audit)
Store under:
`memory/logs/evidence/vpn/<YYYY-MM-DD>/`

Minimum files:
- `vpn_test_run_<timestamp>.jsonl` (raw events)
- `vpn_test_summary_<YYYY-MM-DD>.md` (human-readable summary)
- Optional: screenshots / system outputs

## Pass/Fail gate (Definition of Done for VPN auto-activation)
- All Functional tests F1–F5 pass
- Reliability R1 completed with failure rate ≤ 5% (or your chosen threshold)
- Evidence artifacts saved and linked from the status index
