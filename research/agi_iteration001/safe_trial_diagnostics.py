"""Safe failure classifications for the isolated, single-request API experiment.

Never prints arbitrary exception strings, URLs, HTTP bodies, API credentials,
response content, request IDs, or raw model text. All outputs are allowlisted.
"""
from __future__ import annotations
import json
import socket
import urllib.error
from response_envelope_diagnostics import ResponseMetadata
from proposal_provider import ProposalValidationError

CODES=frozenset({
    "AUTHENTICATION_REJECTED","PERMISSION_OR_MODEL_REJECTED",
    "RATE_LIMITED","REQUEST_REJECTED","SERVER_REJECTED",
    "HTTP_REJECTION_OTHER","NETWORK_TIMEOUT","NETWORK_FAILURE",
    "RESPONSE_INCOMPLETE_OR_REFUSED","OUTPUT_TOKEN_BUDGET_EXHAUSTED","RESPONSE_TEXT_MISSING",
    "RESPONSE_JSON_INVALID","PROPOSAL_VALIDATION_FAILED",
    "LOCAL_CONFIGURATION_BLOCKED","UNKNOWN_SAFE_FAILURE",
})

def classify_failure(exc):
    """Return a category only. Never include the untrusted exception message."""
    if isinstance(exc,urllib.error.HTTPError):
        status=exc.code
        if status==401:return "AUTHENTICATION_REJECTED"
        if status==403 or status==404:return "PERMISSION_OR_MODEL_REJECTED"
        if status==429:return "RATE_LIMITED"
        if 400<=status<500:return "REQUEST_REJECTED"
        if 500<=status<600:return "SERVER_REJECTED"
        return "HTTP_REJECTION_OTHER"
    if isinstance(exc,PermissionError):
        return "LOCAL_CONFIGURATION_BLOCKED"
    if isinstance(exc,(TimeoutError,socket.timeout)):
        return "NETWORK_TIMEOUT"
    if isinstance(exc,(urllib.error.URLError,ConnectionError,OSError)):
        return "NETWORK_FAILURE"
    if isinstance(exc,ProposalValidationError):
        return "PROPOSAL_VALIDATION_FAILED"
    if isinstance(exc,json.JSONDecodeError):
        return "RESPONSE_JSON_INVALID"
    if isinstance(exc,ValueError):
        # These strings are internal, fixed code paths, not API-controlled text.
        if str(exc)=="Model output token budget exhausted":
            return "OUTPUT_TOKEN_BUDGET_EXHAUSTED"
        if str(exc)=="Model response incomplete or refused":
            return "RESPONSE_INCOMPLETE_OR_REFUSED"
        if str(exc)=="No valid structured response":
            return "RESPONSE_TEXT_MISSING"
        return "PROPOSAL_VALIDATION_FAILED"
    return "UNKNOWN_SAFE_FAILURE"

def safe_failure_record(exc,*,attempted_request=False,metadata=None):
    code=classify_failure(exc)
    assert code in CODES
    record={"status":"FAILED","failure_category":code,
            "request_may_have_been_billed":bool(attempted_request),
            "automatic_retry_permitted":False,
            "actual_spend_usd":"UNKNOWN_CHECK_PLATFORM",
            "production_changes":False}
    if isinstance(exc,ProposalValidationError):
        record["validation_reason"]=exc.reason
    # Accept only a locally constructed sanitized envelope, never remote dicts
    # or arbitrary exceptions as user-visible metadata.
    if isinstance(metadata,ResponseMetadata):
        record["response_metadata"]=metadata.as_dict()
    return record
