"""Fail-closed funding gate for the AGI one-shot experiment.

The user declined API credit purchases on Nov 20, 2026. API usage approval
(up to $1) is NOT permission to buy prepaid credits. No external calls here.
"""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

@dataclass(frozen=True)
class FundingState:
    user_approved_credit_purchase: bool = False
    organization_available_credit_usd: str = "0.00"
    auto_reload_enabled: bool = False
    project_hard_limit_verified: bool = True
    project_limit_usd: str = "1.00"
    # Human-observed screenshot values; not live attestation.

def assessment(state):
    if type(state) is not FundingState:raise TypeError("Invalid funding state")
    try:
        credit=Decimal(state.organization_available_credit_usd)
        cap=Decimal(state.project_limit_usd)
        if not credit.is_finite() or not cap.is_finite() or credit<0 or cap<=0:
            raise ValueError("Invalid credit or cap")
    except (InvalidOperation,ValueError,TypeError):
        return {"status":"BLOCKED","reason":"INVALID_BILLING_EVIDENCE",
                "credit_purchase_permitted":False,"api_call_permitted":False}
    # An API spend budget and a credit *purchase* are distinct permissions.
    # Never trigger a purchase here even if an authorization flag changes.
    if credit==0:
        reason="NO_PREPAID_CREDITS"
    elif not state.project_hard_limit_verified or cap>Decimal("1.00"):
        reason="PROJECT_HARD_LIMIT_UNVERIFIED"
    elif state.auto_reload_enabled:
        reason="AUTO_RELOAD_MUST_BE_OFF"
    else:
        reason="FUNDING_PRESENT_STILL_REQUIRES_ACCOUNT_VERIFICATION"
    return {"status":"BLOCKED","reason":reason,
            "credit_purchase_permitted":False,"api_call_permitted":False,
            "project_spend_ceiling_usd":str(cap),
            "reported_credit_usd":str(credit),"external_api_calls":0,
            "purchase_attempts":0}

if __name__=="__main__":
    import json
    print(json.dumps(assessment(FundingState()),indent=2,sort_keys=True))
