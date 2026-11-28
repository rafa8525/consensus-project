"""Sanitized scientific receipt for a fully validated bounded model proposal.

No model prose, request identifiers, credentials, raw API responses or secret
project IDs are emitted. Fixed research fields permit reproducible comparison.
"""
from __future__ import annotations
import hashlib
import json
from proposal_provider import validate_proposal, MODEL_CATALOG, DATASET_IDS, BUDGET

def proposal_evidence(proposal,*,origin="offline_mock"):
    obj=validate_proposal(proposal)
    if origin not in ("offline_mock","live_api"):
        raise ValueError("Unrecognized evidence origin")
    digest=lambda x: hashlib.sha256(x.encode("utf-8")).hexdigest()
    canonical=json.dumps(obj,sort_keys=True)
    return {
        "evidence_schema":"agi-bounded-proposal-v1",
        "origin":origin,
        "proposal_sha256":digest(canonical),
        "hypothesis_sha256":digest(obj["hypothesis"]),
        "expected_falsifier_sha256":digest(obj["expected_falsifier"]),
        "metric":"validation_macro_f1",
        "dataset_ids":list(DATASET_IDS),
        "compute_budget":dict(BUDGET),
        "candidate_models":[dict(v) for v in MODEL_CATALOG],
        "proposal_validated":True,
        "experiment_executed":False,
        "measured_improvement":False,
        "promotion_approved":False,
        "production_changes":False,
        "review_required_for_full_model_text":True,
    }
