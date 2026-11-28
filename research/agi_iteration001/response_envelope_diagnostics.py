"""Sanitized inspection of Responses API envelopes (no raw model text emitted).

All fields in emitted metadata are static allowlisted enums or bounded integer
usage counters. This module never stores a response, key, or response ID.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

_ALLOWED_STATUSES={"completed","incomplete","failed","in_progress","cancelled","queued"}
_ALLOWED_REASONS={"max_output_tokens","content_filter"}
_ALLOWED_CONTENT_TYPES={"output_text","refusal"}
MAX_SAFE_USAGE=10_000_000

@dataclass(frozen=True)
class ResponseMetadata:
    status: str
    incomplete_reason: str
    output_text_present: bool
    refusal_present: bool
    input_tokens: int | None
    output_tokens: int | None
    reasoning_tokens: int | None

    def as_dict(self):
        return {
            "response_status":self.status,
            "incomplete_reason":self.incomplete_reason,
            "output_text_present":self.output_text_present,
            "refusal_present":self.refusal_present,
            "input_tokens":self.input_tokens,
            "output_tokens":self.output_tokens,
            "reasoning_tokens":self.reasoning_tokens,
        }

def _safe_count(value: Any) -> int | None:
    if type(value) is not int or not 0<=value<=MAX_SAFE_USAGE:
        return None
    return value

def extract_response_metadata(raw: Any) -> ResponseMetadata:
    if not isinstance(raw,dict):
        raise ValueError("Invalid response envelope")
    status=raw.get("status")
    if status not in _ALLOWED_STATUSES:
        status="unknown"
    details=raw.get("incomplete_details")
    reason=details.get("reason") if isinstance(details,dict) else None
    if reason not in _ALLOWED_REASONS:reason="none_or_other"
    text_present=False
    refusal=False
    output=raw.get("output")
    if isinstance(output,list):
        for item in output[:30]:
            if not isinstance(item,dict) or item.get("type")!="message":continue
            content=item.get("content")
            if not isinstance(content,list):continue
            for part in content[:30]:
                if not isinstance(part,dict):continue
                kind=part.get("type")
                if kind=="output_text" and isinstance(part.get("text"),str):
                    text_present|=bool(part["text"])
                elif kind=="refusal":
                    refusal=True
    usage=raw.get("usage")
    usage=usage if isinstance(usage,dict) else {}
    output_details=usage.get("output_tokens_details")
    output_details=output_details if isinstance(output_details,dict) else {}
    return ResponseMetadata(
        status=status,incomplete_reason=reason,
        output_text_present=text_present,refusal_present=refusal,
        input_tokens=_safe_count(usage.get("input_tokens")),
        output_tokens=_safe_count(usage.get("output_tokens")),
        reasoning_tokens=_safe_count(output_details.get("reasoning_tokens")),
    )

def safe_diagnostic_code(meta: ResponseMetadata) -> str:
    if meta.status=="incomplete" and meta.incomplete_reason=="max_output_tokens":
        return "OUTPUT_TOKEN_BUDGET_EXHAUSTED"
    if meta.status=="incomplete":return "RESPONSE_INCOMPLETE_OR_REFUSED"
    if meta.refusal_present:return "RESPONSE_INCOMPLETE_OR_REFUSED"
    if meta.status!="completed":return "RESPONSE_INCOMPLETE_OR_REFUSED"
    if not meta.output_text_present:return "RESPONSE_TEXT_MISSING"
    return "RESPONSE_ENVELOPE_OK"
