"""Pre-flight readiness checks for one bounded paid proposal trial.

This module does NOT access API projects, secrets, billing, or network.
All attestations are untrusted until confirmed through a connected platform
integration or human inspection of actual project settings.
"""
from dataclasses import dataclass
from decimal import Decimal
from api_call_admission import Approval, preflight

@dataclass(frozen=True)
class ReadinessEvidence:
    project_verified: bool = False
    api_credential_scoped_to_project_verified: bool = False
    hard_limit_enabled_verified: bool = False
    project_limit_usd: str = ""
    existing_monthly_usage_usd: str = ""
    model_access_verified: bool = False
    input_rate_per_million_usd: str = ""
    output_rate_per_million_usd: str = ""
    model: str = ""
    verified_by: str = ""
    # No credential or secret may be represented here.

def readiness(evidence, *, approved_usd="1.00", input_tokens=500, output_tokens=800):
    if type(evidence) is not ReadinessEvidence:
        raise PermissionError("Verified readiness record required")
    failed=[]
    checks={
       "project_verified":evidence.project_verified,
       "scoped_credential_verified":evidence.api_credential_scoped_to_project_verified,
       "project_hard_limit_enabled":evidence.hard_limit_enabled_verified,
       "model_access_verified":evidence.model_access_verified,
    }
    for key, value in checks.items():
        if value is not True:failed.append(key)
    if not evidence.verified_by or len(evidence.verified_by)>128:
        failed.append("named_reviewer")
    try:
        cap=Decimal(evidence.project_limit_usd)
        spent=Decimal(evidence.existing_monthly_usage_usd)
        authorized=Decimal(approved_usd)
        if not all(x.is_finite() for x in (cap,spent,authorized)):
            raise ValueError
        if authorized<=0 or authorized>Decimal("1.00") or cap<=0 or cap>Decimal("1.00"):
            failed.append("project_limit_at_most_1_usd")
        if spent<0 or spent>=cap:
            failed.append("project_budget_has_room")
        if cap-spent<authorized:
            failed.append("project_remaining_spend_at_least_authorization")
    except (ValueError,ArithmeticError):
        failed.append("project_billing_values")
    if not evidence.model:
        failed.append("model_selected")
    try:
        a=Approval(experiment_id="agi-one-shot-m25",model=evidence.model,
               approved_by=evidence.verified_by,approved_spend_usd=approved_usd,
               input_usd_per_million=evidence.input_rate_per_million_usd,
               output_usd_per_million=evidence.output_rate_per_million_usd,
               approved_api_project="verified-project",
               live_calls_approved=True,
               billing_cap_independently_confirmed=True)
        cost=preflight(a,model=evidence.model,input_token_ceiling=input_tokens,
                       output_token_ceiling=output_tokens,live=True)
    except (ValueError,PermissionError) as exc:
        failed.append("token_cost_estimate")
        cost=None
    # The bool fields here are *claims*, never remotely corroborated by code.
    # This is not a permit to invoke an API! A separate secure credential
    # environment and authenticated project/billing checks are still necessary.
    return {"status":"READY_FOR_MANUAL_VERIFICATION" if not failed else "BLOCKED",
            "unverified_attestations":True,"missing":failed,
            "proposal_api_call_permitted":False,
            "max_requests":1,"estimated_token_cost":cost,
            "price_or_billing_guarantee":False,
            "actual_spend_usd":"0.00",
            "production_changes":False}

if __name__=="__main__":
    import json
    print(json.dumps(readiness(ReadinessEvidence()),indent=2,sort_keys=True))
