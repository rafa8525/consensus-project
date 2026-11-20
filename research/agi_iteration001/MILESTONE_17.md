# Milestone 17 — Opt-in model-backed proposal adapter (mocked only)

Validated against the OpenAI official Structured Outputs and Responses API docs: https://developers.openai.com/api/docs/guides/structured-outputs and https://developers.openai.com/api/reference/resources/responses/methods/create .

## Delivered
- `openai_proposal_adapter.py`: an opt-in `OpenAIProposalProvider` using an **injected** configured Responses client. It requires `enabled=True`, a model ID, max one request, max 1000 output tokens, `tools=[]`, `store=False`, JSON-schema format, and post-decode strict allowlist validation. The adapter refuses incomplete responses and unsafe values.
- `test_openai_proposal_adapter.py`: completely mocked SDK client. Exercises request construction and token ceilings, unsafe-text rejection, incomplete response rejection, duplicate request refusal, schema validation, and default-disabled behavior.
- Main `three_role_provider_v2.py` deliberately **continues rejecting `is_live_model=True`** and running only `OfflineProposalProvider`. There is no live model call in CI. Adapter exists as a staged implementation, not activated autonomous agents.

## Safety and limitations
The API request's token cap is NOT a real USD hard budget. A live experiment should not run until a project billing cap and credential lifecycle are configured, the precise model is approved, and an execution gate enforces a dollar allowance and per-day job cap. The Python client/SDK is not installed in CI; unit tests inject fake client objects and generate no requests.

The structured-response schema contains nullable `n` and `alpha` so all model variants have a consistent strict schema. After receipt, the adapter normalizes and validates exact allowed variants again before they can enter the existing model engineer.

No paid spend, production writes, model improvements, human-independent reasoning, or claims of achieving AGI.
