"""Offline, schema-validated research-proposal provider. Zero API access.

LLM-produced proposals are UNTRUSTED data. This module cannot execute code,
spawn subprocesses, reach network services, or authorize training deployment.
"""
from __future__ import annotations

import json
import re

MODEL_CATALOG = (
    {"kind": "word_nb"},
    {"kind": "word_char_nb", "n": 3, "alpha": 0.5},
    {"kind": "word_char_nb", "n": 4, "alpha": 1.0},
)
DATASET_IDS = ("train-v1", "validation-v1")
BUDGET = {"max_model_fits": 3, "max_examples": 30}
TOP_KEYS = frozenset({
    "experiment_id", "hypothesis", "expected_falsifier", "metric",
    "dataset_ids", "compute_budget", "alternatives", "stop_conditions",
})
TEXT_RE = re.compile(r"^[A-Za-z0-9 ,.:;()'?!+/%=-]{12,200}$")
BLOCKED = re.compile(
    r"(?i)(?:sk-[A-Za-z0-9_-]{6,}|github_pat_|gh[pousr]_[A-Za-z0-9_]{6,}|proj_[A-Za-z0-9_-]{6,}|https?://|\\|\\x00|\$\{|\$\(|\b(?:exec|eval|subprocess|"
    r"import|curl|wget|pip|bash|powershell|sudo|rm|chmod|secret|token|"
    r"password|deploy|production|override|ignore instructions)\b|;\s*\w+)"
)

# Fixed categories only: never emit generated values, private text, or exception bodies.
VALIDATION_REASONS=frozenset({
    "RESPONSE_SHAPE","EXPERIMENT_ID","HYPOTHESIS_TEXT","FALSIFIER_TEXT",
    "METRIC_MISMATCH","DATASET_MISMATCH","BUDGET_MISMATCH",
    "STOP_CONDITION_MISMATCH","CANDIDATE_MISMATCH","UNSAFE_TEXT",
})

class ProposalValidationError(ValueError):
    def __init__(self, reason):
        if reason not in VALIDATION_REASONS:
            reason="RESPONSE_SHAPE"
        self.reason=reason
        super().__init__("Proposal rejected: "+reason)

def _safe_text(text):
    if not isinstance(text,str) or not TEXT_RE.fullmatch(text) or BLOCKED.search(text):
        raise ProposalValidationError("UNSAFE_TEXT")
    return text

def validate_proposal(raw):
    if isinstance(raw,bytes):
        if len(raw)>6000:raise ProposalValidationError("RESPONSE_SHAPE")
        raw=raw.decode("utf-8")
    if isinstance(raw,str):
        if len(raw.encode("utf8"))>6000:raise ProposalValidationError("RESPONSE_SHAPE")
        try: obj=json.loads(raw)
        except json.JSONDecodeError as exc:raise ProposalValidationError("RESPONSE_SHAPE") from exc
    elif isinstance(raw,dict):
        obj=raw
    else:raise ProposalValidationError("RESPONSE_SHAPE")
    if not isinstance(obj,dict) or set(obj)!=TOP_KEYS:
        raise ProposalValidationError("RESPONSE_SHAPE")
    if not isinstance(obj["experiment_id"],str) or not re.fullmatch(r"[a-z0-9_-]{8,48}",obj["experiment_id"]):
        raise ProposalValidationError("EXPERIMENT_ID")
    for key,reason in (("hypothesis","HYPOTHESIS_TEXT"),
                       ("expected_falsifier","FALSIFIER_TEXT")):
        try:_safe_text(obj[key])
        except ProposalValidationError as exc:
            raise ProposalValidationError(reason) from None
    if obj["metric"]!="validation_macro_f1":
        raise ProposalValidationError("METRIC_MISMATCH")
    if obj["dataset_ids"]!=list(DATASET_IDS):
        raise ProposalValidationError("DATASET_MISMATCH")
    if not isinstance(obj["compute_budget"],dict) or obj["compute_budget"]!=BUDGET:
        raise ProposalValidationError("BUDGET_MISMATCH")
    if obj["stop_conditions"]!=["at_most_three_fits","no_production_promotion"]:
        raise ProposalValidationError("STOP_CONDITION_MISMATCH")
    variants=obj["alternatives"]
    if not isinstance(variants,list) or len(variants)!=3 or variants[0]!=MODEL_CATALOG[0]:
        raise ProposalValidationError("CANDIDATE_MISMATCH")
    if any(not isinstance(v,dict) or v not in MODEL_CATALOG for v in variants):
        raise ProposalValidationError("CANDIDATE_MISMATCH")
    if len({json.dumps(v,sort_keys=True) for v in variants})!=3:
        raise ProposalValidationError("CANDIDATE_MISMATCH")
    if variants[1:]!=list(MODEL_CATALOG[1:]):
        raise ProposalValidationError("CANDIDATE_MISMATCH")
    return obj

class OfflineProposalProvider:
    """A fake AI proposer supplying a fixed research plan for safe CI integration."""
    is_live_model=False
    external_calls=0
    api_cost_usd=0
    def propose(self):
        return json.dumps({
            "experiment_id":"offline-model-comparison-v2",
            "hypothesis":"Character n grams improve validation task classification macro F1",
            "expected_falsifier":"No macro F1 improvement over the word baseline on validation",
            "metric":"validation_macro_f1",
            "dataset_ids":list(DATASET_IDS),
            "compute_budget":dict(BUDGET),
            "alternatives":[dict(s) for s in MODEL_CATALOG],
            "stop_conditions":["at_most_three_fits","no_production_promotion"]
        },sort_keys=True)
