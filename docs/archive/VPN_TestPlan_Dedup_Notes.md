# Deprecation note (VPN test plan duplicates)

These files contain overlapping VPN testing notes:
- vpn_activation_testing_plan.txt
- VPNActivationTestingPlan.txt
- VPN_activation_testing.txt

Action:
- Keep ONE canonical plan: `docs/VPN_AutoActivation_TestPlan.md`
- Move the older files to `docs/archive/` and add this note at top:
  'DEPRECATED — see docs/VPN_AutoActivation_TestPlan.md'

Reason:
- Prevent drift and contradictions.
- Ensure a single auditable source of truth with evidence requirements.
