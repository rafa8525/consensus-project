# System Health Snapshot

- Generated: 2025-12-10T07:03:29.856237+00:00
- Overall status: **OK**

## Subsystem Status Overview

| Subsystem | Status | Source | Notes |
|-----------|--------|--------|-------|
| weekly_auto_status | unknown | `memory/logs/status/weekly_status_auto.md` | file yes |
| absorption | ok | `memory/logs/status/absorption_status.md` | file yes |
| geofence_sms | ok | `memory/logs/status/geofence_sms_status.md` | file yes |
| gmail | ok | `memory/logs/status/gmail_status.md` | file yes |
| movie_list | unknown | `memory/logs/media/movie_list_status.md` | file yes |
| predictions | unknown | `memory/logs/system/predictions/prediction_feed_summary_latest.md` | file yes |

## Agent Run Results

### Agent: auto_status
- Result: **OK**

### Agent: prediction_summary
- Result: **OK**

### Agent: movie_detector
- Result: **OK**

### Agent: absorption_monitor
- Result: **OK**

### Agent: geofence_sms_monitor
- Result: **OK**

### Agent: gmail_monitor
- Result: **OK**

## Detailed Status Files

### weekly_auto_status
_Source: `memory/logs/status/weekly_status_auto.md`_

# Weekly Auto-Status Report

- Generated: 2025-12-10T07:03:22.849936+00:00

## VPN Health
- Checks in last 7 days: 168
- Public Wi-Fi failures: 0
- Success rate: 100.00%

**VPN KPI Notes:**
- ✅ Success rate meets target (100.00% ≥ 98%).
- ✅ Public failures 0 within limit 3.

## Fitness
- Days with metrics (last 7): 8/7
- Coverage: 114.29%
- Coaching events in last 7 days: 16

**Fitness KPI Notes:**
- ✅ Coverage meets target (114.29% ≥ 90%).
- ✅ Coaching events meet target (16 ≥ 1).

## Knowledge Base Maintenance
- Cleanup runs in last 7 days: 7

**KB KPI Notes:**
- ✅ Cleanup runs meet target (7 ≥ 3).

### absorption
_Source: `memory/logs/status/absorption_status.md`_

# Absorption / Heartbeat Status

- Generated: 2025-12-10T07:03:29.419338+00:00
- Lookback window: last 48 hours
- Cutoff timestamp: 2025-12-08T07:03:23.761168+00:00
- Overall status: **OK**
- Summary: 601 runs in 48h; average 300.50 runs/day meets target.

## Per-log event counts

- `memory/logs/system/absorb_memory.log`: 502 events in window
- `memory/logs/system/absorb_runner.log`: 99 events in window
- `memory/logs/system/heartbeat.log`: 0 events in window

## Totals

- Total absorption-related events: **601**

### geofence_sms
_Source: `memory/logs/status/geofence_sms_status.md`_

# Geofence / SMS Status

- Generated: 2025-12-10T07:03:29.605584+00:00
- Lookback window: last 48 hours
- Cutoff timestamp: 2025-12-08T07:03:29.591234+00:00
- Overall status: **OK**
- Summary: SMS / geofence ratio 2.02 meets or exceeds target 0.80.

## Totals

- Total geofence events: **47**
- Total SMS events: **95**
- SMS / geofence ratio: **2.02**

## Per-log geofence counts

- `memory/logs/transport/transit_log.md`: 0 events in window
- `memory/logs/system/sms_daemon/geofence_events.jsonl`: 47 events in window

## Per-log SMS counts

- `memory/logs/system/sms_daemon/sms_events.jsonl`: 47 events in window
- `memory/logs/system/sms_daemon/sms_daemon.log`: 47 events in window
- `memory/logs/system/voice_trigger_heartbeat.log`: 1 events in window

### gmail
_Source: `memory/logs/status/gmail_status.md`_

# Gmail Integration Status

- Generated: 2025-12-10T07:03:29.820328+00:00
- Lookback window: last 48 hours
- Cutoff timestamp: 2025-12-08T07:03:29.810831+00:00
- Overall status: **OK**
- Summary: 47 Gmail-related events in the window with no errors detected.

## Totals

- Total Gmail events: **47**
- Error events: **0**
- Error ratio: **0.00**

## Per-log breakdown

- `memory/logs/system/gmail_agent.log`: 0 events in window, 0 errors
- `memory/logs/system/gmail_alert_agent.log`: 0 events in window, 0 errors
- `memory/logs/system/gmail_voice_reader.log`: 0 events in window, 0 errors
- `memory/logs/gmail/gmail_activity.jsonl`: 47 events in window, 0 errors

### movie_list
_Source: `memory/logs/media/movie_list_status.md`_

# Movie List Status

- Generated: 2025-12-10T07:03:23.445451+00:00
- Source file: `memory/exports/movie_list_export.txt`
- Total movies tracked: **0**
- Initial load: yes
- New movies this run: 0

## All Movies (current snapshot)

_No movies found in the export file._

### predictions
_Source: `memory/logs/system/predictions/prediction_feed_summary_latest.md`_

# Prediction Feed Summary

- Generated: 2025-12-10T07:03:23.118528+00:00
- Source file: `memory/logs/system/predictions/prediction_feed_summary_latest.md`

## Overview
- Total predictions: 2
- High confidence: 0
- Medium confidence: 0
- Low confidence: 1
- High-alert items: 0
- Medium-alert items: 0
- Low-alert items: 0

## Predictions

1. **Overview**
   - Confidence: `0` (_low_)
   - Alert: `items: 0` (_unknown_)
   - Notes: - Total predictions: 4

2. **Predictions**
   - Confidence: ``unknown` (_unknown_)` (_unknown_)
   - Alert: ``none` (_none_)` (_unknown_)
   - Notes: 1. **Errands & Geofences**

