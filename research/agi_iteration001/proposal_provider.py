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
    r"(?i)(?:https?://|\\|\\x00|\$\{|\$\(|\b(?:exec|eval|subprocess|"
    r"import|curl|wget|pip|bash|powershell|sudo|rm|chmod|secret|token|"
    r"password|deploy|production|override|ignore instructions)\b|;\s*\w+)"
)

def _safe_text(text):
    if not isinstance(text,str) or not TEXT_RE.fullmatch(text) or BLOCKED.search(text):
        raise ValueError("Unsafe or invalid proposal text")
    return text

def validate_proposal(raw):
    if isinstance(raw,bytes):
        if len(raw)>6000:raise ValueError("Proposal payload too large")
        raw=raw.decode("utf-8")
    if isinstance(raw,str):
        if len(raw.encode("utf8"))>6000:raise ValueError("Proposal payload too large")
        try: obj=json.loads(raw)
        except json.JSONDecodeError as exc:raise ValueError("Invalid proposal JSON") from exc
    elif isinstance(raw,dict):
        obj=raw
    else:raise ValueError("Proposal must be JSON object")
    if not isinstance(obj,dict) or set(obj)!=TOP_KEYS:
        raise ValueError("Proposal must have exactly the declared fields")
    if not isinstance(obj["experiment_id"],str) or not re.fullmatch(r"[a-z0-9_-]{8,48}",obj["experiment_id"]):
        raise ValueError("Invalid experiment identifier")
    for key in ("hypothesis","expected_falsifier"):
        _safe_text(obj[key])
    if obj["metric"]!="validation_macro_f1":
        raise ValueError("Unsupported objective metric")
    if obj["dataset_ids"]!=list(DATASET_IDS):
        raise ValueError("Dataset not approved")
    if not isinstance(obj["compute_budget"],dict) or obj["compute_budget"]!=BUDGET:
        raise ValueError("Compute budget mismatch")
    if obj["stop_conditions"]!=["at_most_three_fits","no_production_promotion"]:
        raise ValueError("Safety stop condition mismatch")
    variants=obj["alternatives"]
    if not isinstance(variants,list) or len(variants)!=3 or variants[0]!=MODEL_CATALOG[0]:
        raise ValueError("Baseline and exactly two variants required")
    if any(not isinstance(v,dict) or v not in MODEL_CATALOG for v in variants):
        raise ValueError("Unapproved model spec")
    if len({json.dumps(v,sort_keys=True) for v in variants})!=3:
        raise ValueError("Duplicate variant")
    if variants[1:]!=list(MODEL_CATALOG[1:]):
        raise ValueError("Variant set differs from engineering allowlist")
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
