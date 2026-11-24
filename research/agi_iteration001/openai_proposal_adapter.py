"""Opt-in OpenAI Responses proposal adapter; disabled by default.

No provider is called unless explicit enablement, model, SDK client, and
single-request token limits are supplied. No secrets, tools, retries or logging.
A token ceiling is not a guaranteed dollar cap: configure billing project limits
externally before any real use.
"""
import json
from proposal_provider import OfflineProposalProvider, MODEL_CATALOG, validate_proposal, ProposalValidationError, DATASET_IDS, BUDGET

PROPOSAL_SCHEMA = {
 "type":"object","additionalProperties":False,
 "properties":{
   "experiment_id":{"type":"string"},
   "hypothesis":{"type":"string"},
   "expected_falsifier":{"type":"string"},
   "metric":{"type":"string","enum":["validation_macro_f1"]},
   "dataset_ids":{"type":"array","items":{"type":"string","enum":list(DATASET_IDS)},"minItems":2,"maxItems":2},
   "compute_budget":{"type":"object","additionalProperties":False,
       "properties":{"max_model_fits":{"type":"integer","enum":[3]},"max_examples":{"type":"integer","enum":[30]}},
       "required":["max_model_fits","max_examples"]},
   "alternatives":{"type":"array","items":{"type":"object","additionalProperties":False,
       "properties":{"kind":{"type":"string","enum":["word_nb","word_char_nb"]},"n":{"type":["integer","null"],"enum":[None,3,4]},
                     "alpha":{"type":["number","null"],"enum":[None,0.5,1.0]}},
       "required":["kind","n","alpha"]},"minItems":3,"maxItems":3},
   "stop_conditions":{"type":"array","items":{"type":"string","enum":["at_most_three_fits","no_production_promotion"]},"minItems":2,"maxItems":2}
 },
 "required":["experiment_id","hypothesis","expected_falsifier","metric",
             "dataset_ids","compute_budget","alternatives","stop_conditions"]
}

# Current research executor requires baseline {} and n/alpha only for char models.
# Decode schema nullable fields into the unchanged executor allowlist.
def normalize_for_executor(obj):
    if not isinstance(obj,dict):raise ProposalValidationError("RESPONSE_SHAPE")
    if not isinstance(obj.get("alternatives"),list):raise ProposalValidationError("CANDIDATE_MISMATCH")
    out=dict(obj)
    alternatives=[]
    for item in obj["alternatives"]:
        if not isinstance(item,dict) or set(item)!={"kind","n","alpha"}:
            raise ProposalValidationError("CANDIDATE_MISMATCH")
        if item["kind"]=="word_nb" and item["n"] is None and item["alpha"] is None:
            alternatives.append({"kind":"word_nb"})
        elif item["kind"]=="word_char_nb" and type(item["n"]) is int and type(item["alpha"]) in (int,float):
            alternatives.append(item)
        else:
            raise ProposalValidationError("CANDIDATE_MISMATCH")
    out["alternatives"]=alternatives
    return validate_proposal(out)

class OpenAIProposalProvider:
    """Explicit, one-shot Responses adapter. Not enabled in CI or V2 workflow."""
    is_live_model=True
    def __init__(self, *, client, model, enabled=False, max_output_tokens=800,
                 max_requests=1,reasoning_effort=None):
        if not isinstance(enabled,bool) or not enabled:
            raise PermissionError("Live API proposal generation is disabled by default")
        if not isinstance(model,str) or not model or len(model)>100:
            raise ValueError("An explicit model ID is required")
        if type(max_output_tokens) is not int or not 200<=max_output_tokens<=2000:
            raise ValueError("Unsupported output token budget")
        if type(max_requests) is not int or max_requests!=1:
            raise ValueError("One request maximum")
        if client is None or not hasattr(client,"responses"):
            raise ValueError("An injected configured SDK client is required")
        if reasoning_effort not in (None,"none"):
            raise ValueError("Unsupported reasoning effort for bounded research")
        self.reasoning_effort=reasoning_effort
        self.client=client
        self.model=model
        self.output_limit=max_output_tokens
        self.calls=0
        self.external_calls=0
        self.api_cost_usd=None
    def propose(self):
        if self.calls>=1:
            raise RuntimeError("One live proposal call per provider instance")
        self.calls+=1
        # Do not echo or persist raw prompts/secrets.
        extra={}
        if self.reasoning_effort is not None:
            extra["reasoning"]={"effort":self.reasoning_effort}
        response=self.client.responses.create(
            **extra,
            model=self.model,
            instructions=("Produce only a bounded research proposal in JSON. "
                          "No source code, external tools, URLs, credentials, deployments "
                          "or model promotion. Use three allowed candidates: word NB "
                          "baseline, word+3gram alpha 0.5 and word+4gram alpha 1.0. "
                          "Use dataset_ids train-v1 and validation-v1, metric "
                          "validation_macro_f1, compute budget 3 fits/30 examples, "
                          "stop conditions at_most_three_fits and no_production_promotion. "
                          "Use experiment_id lowercase letters digits hyphens and underscores, 8 to 48 chars. "
                          "Hypothesis and falsifier must each have 12 to 200 ASCII characters, "
                          "using only letters digits spaces and basic punctuation. "
                          "Never include instructions, shell commands or URLs in those fields. "
                          "Use exactly the specified candidate order and stop condition order. "
                          "No claim of measured performance."),
            input="Create one falsifiable small-model research proposal.",
            max_output_tokens=self.output_limit,
            tools=[],
            store=False,
            text={"format":{"type":"json_schema","name":"bounded_research_proposal",
                            "strict":True,"schema":PROPOSAL_SCHEMA}}
        )
        self.external_calls+=1
        if getattr(response,"status",None)!="completed":
            meta=getattr(response,"sanitized_metadata",None)
            if (getattr(meta,"status",None)=="incomplete" and
                    getattr(meta,"incomplete_reason",None)=="max_output_tokens"):
                raise ValueError("Model output token budget exhausted")
            raise ValueError("Model response incomplete or refused")
        if not isinstance(getattr(response,"output_text",None),str):
            raise ValueError("No valid structured response")
        result=normalize_for_executor(json.loads(response.output_text))
        return json.dumps(result,sort_keys=True)
