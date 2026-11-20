"""V2 offline proposal-to-evaluation pipeline; no live AI and no production access.

Uses V1 durable SQLite receipt logic and deterministic real model fitting.
"""
import argparse
import json
from pathlib import Path

from proposal_provider import OfflineProposalProvider, validate_proposal
from three_role_research_cycle import (
    ROLES, connect, digest, _get, _write_once, engineer,
    independent_review, snapshot
)
from local_inference import TRAIN
from model_improvement_experiment import VALIDATION

VERSION="3-role-provider-v2-offline"

def _plan(provider):
    if getattr(provider,"is_live_model",True) is not False:
        raise ValueError("Live AI providers are disabled")
    if getattr(provider,"external_calls",None)!=0 or getattr(provider,"api_cost_usd",None)!=0:
        raise ValueError("Paid or external providers are disabled")
    proposal=validate_proposal(provider.propose())
    return {
        "version":VERSION,
        "hypothesis":proposal["hypothesis"],
        "expected_falsifier":proposal["expected_falsifier"],
        "proposal_id":proposal["experiment_id"],
        "provider":"OFFLINE_RECORDED",
        "alternatives":proposal["alternatives"],
        "development_sha":digest({"train":TRAIN,"validation":VALIDATION}),
        "budget":proposal["compute_budget"],
        "selection":proposal["metric"],
        "retest_used_for_selection":False,
        "production_changes":False,
    }

def run(db,provider=None):
    provider=provider if provider is not None else OfflineProposalProvider()
    # validate the proposed plan before any writes or model fits.
    proposal_plan=_plan(provider)
    c=connect(db)
    try:
        planner=_write_once(c,ROLES[0],digest({"version":VERSION,
                        "proposal_id":proposal_plan["proposal_id"]}),proposal_plan)
        engineered=engineer(planner)
        engineer_receipt=_write_once(c,ROLES[1],planner["sha"],engineered)
        reviewed=independent_review(planner,engineer_receipt)
        evaluator_receipt=_write_once(c,ROLES[2],
               digest([planner["sha"],engineer_receipt["sha"]]),reviewed)
        output=snapshot(c)
        output["proposal_mode"]="OFFLINE_RECORDED_NOT_AI"
        output["model_proposals_executed"]=len(engineered["outcomes"])
        output["reproducible_evaluator_review"]=reviewed["recomputed_validation_matches"]
        output["independent_generalization_verified"]=False
        output["promotion_approved"]=False
        output["provider_calls"]=0
        output["api_cost_usd"]=0
        return output
    finally:
        c.close()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--db",type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(run(a.db),sort_keys=True,indent=2))

if __name__=="__main__":main()
