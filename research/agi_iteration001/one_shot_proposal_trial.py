"""One-shot Responses API research transport; zero calls unless explicit LIVE mode.

Dry-run uses the existing fixed offline proposal; live mode requires a protected
manual GitHub Actions environment, a verified project, and a scoped secret.
This script is not a global spending cap or a reusable autonomous agent.
"""
from __future__ import annotations
import argparse
from decimal import Decimal
import hashlib
import json
import os
import re
import urllib.request
from types import SimpleNamespace

from openai_proposal_adapter import OpenAIProposalProvider
from proposal_provider import OfflineProposalProvider, validate_proposal
from safe_trial_diagnostics import safe_failure_record

MODEL="gpt-6-luna"
BRANCH="refs/heads/research/agi-iteration-001-20261119"
REPO="rafa8525/consensus-project"
MAX_OUTPUT=800
MAX_RESPONSE=32768
API_ENDPOINT="https://api.openai.com/v1/responses"
PROJECT_ID_PATTERN=re.compile(r"^proj_[A-Za-z0-9_-]{8,100}$")

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):
        raise RuntimeError("Unexpected redirect blocked")

class OnceHTTPClient:
    """Minimal one-request no-retry transport; never logs tokens or responses."""
    def __init__(self,key,project_id,*,opener=None):
        if not isinstance(key,str) or not key.startswith("sk-") or len(key)<20:
            raise ValueError("Invalid secret availability")
        if not isinstance(project_id,str) or not PROJECT_ID_PATTERN.fullmatch(project_id):
            raise ValueError("Invalid project ID")
        self._key=key
        self._project=project_id
        self._opener=opener or urllib.request.build_opener(NoRedirect())
        self.responses=self
        self.calls=0
    def create(self,**payload):
        if self.calls:raise PermissionError("Second call forbidden")
        if payload.get("model")!=MODEL or payload.get("max_output_tokens")!=MAX_OUTPUT:
            raise ValueError("Unexpected model or token budget")
        if payload.get("tools")!=[] or payload.get("store") is not False:
            raise ValueError("Tools and storage must be disabled")
        if set(payload)!={"model","instructions","input","max_output_tokens","tools","store","text"}:
            raise ValueError("Unexpected API request fields")
        if len(json.dumps(payload).encode("utf8"))>9000:
            raise ValueError("Request body too large")
        data=json.dumps(payload,separators=(",",":")).encode("utf8")
        req=urllib.request.Request(
            API_ENDPOINT,data=data,method="POST",
            headers={"Authorization":"Bearer "+self._key,
                     "OpenAI-Project":self._project,
                     "Content-Type":"application/json"})
        self.calls+=1  # increment before any network activity; never retry
        with self._opener.open(req,timeout=20) as res:
            if res.status!=200:raise RuntimeError("API returned non-success")
            raw=res.read(MAX_RESPONSE+1)
            if len(raw)>MAX_RESPONSE:raise RuntimeError("Response too large")
        obj=json.loads(raw)
        texts=[]
        for item in obj.get("output",[]):
            if item.get("type")=="message":
                for part in item.get("content",[]):
                    if part.get("type")=="output_text" and isinstance(part.get("text"),str):
                        texts.append(part["text"])
        return SimpleNamespace(status=obj.get("status"),
                               output_text="".join(texts) if texts else None,
                               id=obj.get("id"),
                               usage=obj.get("usage",{}))

def dry_run():
    proposal=validate_proposal(OfflineProposalProvider().propose())
    return {"status":"DRY_RUN_ONLY","external_calls":0,"model":MODEL,
            "proposal_sha256":hashlib.sha256(json.dumps(proposal,sort_keys=True).encode()).hexdigest(),
            "promotion_approved":False,"production_changes":False}

def verify_manual_context(env):
    exact={"GITHUB_EVENT_NAME":"workflow_dispatch",
           "GITHUB_REF":BRANCH,"GITHUB_REPOSITORY":REPO,
           "GITHUB_RUN_ATTEMPT":"1","AGI_EXPLICIT_ONE_SHOT":"YES-REVIEWED"}
    missing=[k for k,v in exact.items() if env.get(k)!=v]
    if missing:raise PermissionError("Manual protected workflow context unverified")
    if not PROJECT_ID_PATTERN.fullmatch(env.get("OPENAI_PROJECT_ID","")):
        raise PermissionError("Project scope missing")
    if not env.get("OPENAI_API_KEY","").startswith("sk-"):
        raise PermissionError("Encrypted environment key unavailable")

def live_once(env,*,transport=None):
    verify_manual_context(env)
    t=transport or OnceHTTPClient(env["OPENAI_API_KEY"],env["OPENAI_PROJECT_ID"])
    p=OpenAIProposalProvider(client=t,model=MODEL,enabled=True,
                             max_output_tokens=MAX_OUTPUT,max_requests=1)
    proposal=validate_proposal(p.propose())
    # Persist only non-secret, non-output digest; never execute proposed code.
    digest=hashlib.sha256(json.dumps(proposal,sort_keys=True).encode()).hexdigest()
    return {"status":"ONE_PROPOSAL_RECEIVED","external_calls":1,"model":MODEL,
            "proposal_sha256":digest,"promotion_approved":False,
            "production_changes":False,"actual_spend_usd":"NOT_VERIFIED"}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--dry-run",action="store_true")
    parser.add_argument("--live",action="store_true")
    a=parser.parse_args()
    if a.dry_run==a.live:raise SystemExit("Choose exactly one mode")
    if a.dry_run:
        result=dry_run()
    else:
        try: result=live_once(os.environ)
        except Exception as exc:
            # Only print allowlisted categories: no raw exception, API text or key.
            print(json.dumps(safe_failure_record(exc,attempted_request=True),sort_keys=True))
            raise SystemExit(1) from None
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
