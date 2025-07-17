# SMS Escalation Policy – AI Consensus System

## Purpose
To ensure Rafael receives timely, privacy-safe alerts via SMS when critical events occur and fallback methods fail.

## Escalation Chain Overview
1. Local Notification
2. Push Reminder (if enabled)
3. SMS Alert via Twilio
4. Voice Call Escalation (optional for severe cases)

---

## Trigger Conditions for SMS

| Condition | Triggering Agent | Escalation Delay | Message Format | Notes |
|----------|------------------|------------------|----------------|-------|
| Missed 2+ BMI checks | Fitness Agent | After 24h silent | "No BMI logs for 2 days. Need a check-in?" | No health data included |
| Missed 3 workouts | Fitness Agent | After 72h | "You’ve missed 3 workouts. Need a boost?" | Applies to pool or alt activity |
| VPN fails >30s + risk detected | Network Agent | Immediate | "VPN inactive on public Wi-Fi. Data may be at risk." | Escalates only on untrusted network |
| No GitHub sync in 24h | Memory Agent | After retries fail | "System logs unsynced for 24h. Action needed?" | No internal content shown |
| Fallback-only logging for >48h | Consensus Agent | After 48h | "Fallback logging active >2 days. System may be degraded." | Triggers if SMS is disabled too |

---

## SMS Message Guidelines
- ✅ No sensitive health or location data
- ✅ Friendly tone, short format (<160 chars)
- ✅ Include optional “Reply 1 to confirm” in future
- ✅ All messages logged privately, not shared with third parties

---

## Logging
- SMS events are logged to `/logs/system/sms_log.md`
- Failed delivery triggers push retry and fallback reminder

---

## Future Enhancements
- Smart windowing (e.g., no SMS between 10pm–7am)
- Consent prompt before switching to voice fallback
- Two-way SMS interaction

---

## Last Updated
2025-07-16