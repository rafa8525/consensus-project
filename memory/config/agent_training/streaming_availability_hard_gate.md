# Streaming Availability Hard Gate

Effective: 2026-05-15

Prediction feed movie recommendations must not appear unless every title includes:
- Current U.S. streaming platform
- Verification source
- Date checked

Reject:
- Rent only
- Buy only
- Unknown availability
- Ambiguous title match
- Already watched titles
- Suppressed titles
- Any recommendation without current streaming proof

Failure behavior:
Suppress the recommendation block and replace it with a gate-blocked message.
