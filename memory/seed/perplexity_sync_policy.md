# perplexity_sync_policy.md
**AI Consensus System – Perplexity Sync & Escalation Policy**

**Last Updated:** 2025-07-17
**Source:** /memory/seed/perplexity_sync_policy.md

---

## Purpose
This document defines how Perplexity.ai mirrors key AI Consensus System behaviors, with a focus on 10PM fitness logging reminders, escalation rules, and privacy compliance.

---

## 1. Daily Reminder Integration
**Schedule:** Every night at 10:00 PM  
**Message Content:**  
"Reminder: Log your BMI and pool laps. Missed 2 or more logs or 3 pool days may trigger a follow-up."

### ✅ Sync Logic:
- Created via [Tasks] within Perplexity (via search result or /tasks dashboard)
- Task will repeat nightly and run passively unless user disables

---

## 2. Escalation Flow
### a. Missed Logs or Laps
- **After 2 BMI logs missed or 3 pool sessions skipped**:
  - A gentle reminder is displayed in Perplexity’s **mobile app**
  - If enabled, an **email notification** is sent via Deep Research digest
  - No SMS is sent (not supported by Perplexity)

### b. VPN Failures or System Sync Outages
- Not monitored by Perplexity; managed by internal agents only.
- No alerts or failover replication through Perplexity for infrastructure risks.

---

## 3. Notification Channels
| Channel        | Supported? | Behavior                                                   |
|----------------|------------|------------------------------------------------------------|
| Push (App)     | ✅         | Enabled by mobile settings; mirrors task alerts            |
| Email          | ✅         | Via Deep Research or task completion digests               |
| WhatsApp       | ❌         | Not connected to AI Consensus System as of now             |
| SMS/Voice      | ❌         | Requires separate Twilio integration, not available here    |

---

## 4. Privacy Controls
- No health metrics (BMI, weight) are shown in messages.
- Notifications are advisory-only and avoid behavioral profiling.
- All logic honors escalation delay (1–3 local device nudges before external alerts).

---

## 5. Agent Coordination
- Perplexity Tasks act as *secondary agents* in the system.
- They do not replace internal logging, SMS, or GitHub sync.
- All alerts from Perplexity must be context-aware and suppress if the main agent already escalated.

---

## Summary
Perplexity is now an external notifier agent with:
- Nightly compliance check-ins
- Light escalation after health pattern deviations
- Email/mobile push fallback (no SMS)
- Full privacy-first policy enforcement

This policy is aligned with `sms_escalation_policy.md` and follows the same hierarchy of user respect, automation discipline, and no data leakage.
