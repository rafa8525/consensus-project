"""Research-only authorization preflight and bounded one-shot model proposal runner.

This module makes no HTTP/API calls itself. The only provider integration is via
an injected callable; CI uses a fake. Estimated token cost != enforceable billing.
"""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import hashlib
import json
import sqlite3
from pathlib import Path
from proposal_provider import validate_proposal

CALL_CAP=1
OUTPUT_TOKEN_CAP=1000
MAX_PROMPT_BYTES=2000
MIN_EXPECTED_INPUT_TOKENS=1

@dataclass(frozen=True)
class Approval:
    experiment_id: str
    model: str
    approved_by: str
    approved_spend_usd: str
    input_usd_per_million: str
    output_usd_per_million: str
    approved_api_project: str
    billing_cap_independently_confirmed: bool=False
    live_calls_approved: bool=False

def _money(text):
    if not isinstance(text,str):raise ValueError("Money value must be a decimal string")
    try: value=Decimal(text)
    except InvalidOperation as exc:raise ValueError("Invalid price") from exc
    if not value.is_finite() or value<0:raise ValueError("Invalid nonnegative price")
    return value

def preflight(approval, *, model, input_token_ceiling, output_token_ceiling, live=False):
    if type(approval) is not Approval:raise PermissionError("Approval record required")
    if any(not isinstance(v,str) or not v.strip() or len(v)>128 for v in (
        approval.experiment_id,approval.model,approval.approved_by,approval.approved_api_project)):
        raise PermissionError("Incomplete approval")
    if model!=approval.model:raise PermissionError("Model not approved")
    if type(input_token_ceiling) is not int or not MIN_EXPECTED_INPUT_TOKENS<=input_token_ceiling<=3000:
        raise ValueError("Input token estimate cap exceeded")
    if type(output_token_ceiling) is not int or not 200<=output_token_ceiling<=OUTPUT_TOKEN_CAP:
        raise ValueError("Output cap exceeded")
    ceiling=(
        _money(approval.input_usd_per_million)*input_token_ceiling+
        _money(approval.output_usd_per_million)*output_token_ceiling
    )/Decimal(1_000_000)
    amount=_money(approval.approved_spend_usd)
    if ceiling>amount:raise PermissionError("Estimated cost exceeds approved amount")
    if live and not (approval.live_calls_approved is True and
                     approval.billing_cap_independently_confirmed is True):
        raise PermissionError("Live API calls not approved")
    return {"experiment_id":approval.experiment_id,"model":model,
            "max_calls":CALL_CAP,"estimated_upper_usd":str(ceiling),
            "is_actual_billing_cap":False,
            "live_authorized":bool(live),
            "production_promotion_allowed":False}

def open_ledger(path):
    p=Path(path)
    if p.is_symlink() or not p.parent.is_dir():raise ValueError("Unsafe ledger path")
    con=sqlite3.connect(str(p),timeout=10,isolation_level=None)
    con.execute("PRAGMA busy_timeout=10000")
    con.execute("PRAGMA journal_mode=WAL")
    con.executescript("""CREATE TABLE IF NOT EXISTS requests(
      experiment_id TEXT PRIMARY KEY, model TEXT NOT NULL,
      status TEXT NOT NULL CHECK(status IN ('reserved','completed','failed')),
      proposal_sha TEXT);""")
    return con

def reserve(con,experiment_id,model):
    con.execute("BEGIN IMMEDIATE")
    try:
        con.execute("INSERT INTO requests(experiment_id,model,status) VALUES(?,?,'reserved')",
                    (experiment_id,model))
        con.execute("COMMIT")
    except BaseException:
        con.execute("ROLLBACK")
        raise

def finish(con,experiment_id,ok,proposal_sha=None):
    changed=con.execute("UPDATE requests SET status=?,proposal_sha=? WHERE experiment_id=? AND status='reserved'",
                ("completed" if ok else "failed",proposal_sha,experiment_id)).rowcount
    if changed!=1:raise ValueError("Reservation is not active")

def run_mocked_proposal(db,approval,transport,*,model,input_token_ceiling=500,output_token_ceiling=800):
    """Dry-run request ledger with supplied fake transport; no network implied."""
    admission=preflight(approval,model=model,input_token_ceiling=input_token_ceiling,
                       output_token_ceiling=output_token_ceiling,live=False)
    if not callable(transport):raise ValueError("Transport must be callable")
    con=open_ledger(db)
    try:
        reserve(con,approval.experiment_id,model)
        try:
            raw=transport()
            proposal=validate_proposal(raw)
            digest=hashlib.sha256(json.dumps(proposal,sort_keys=True).encode()).hexdigest()
            finish(con,approval.experiment_id,True,digest)
            return {"admission":admission,"proposal_sha256":digest,
                    "provider":"SIMULATED_NO_API","external_calls":0,
                    "actual_api_spend_usd":"0.00","promotion_approved":False}
        except BaseException:
            finish(con,approval.experiment_id,False)
            raise
    finally:
        con.close()
