"""Safe failure classifications for the isolated, single-request API experiment.

Never prints arbitrary exception strings, URLs, HTTP bodies, API credentials,
response content, request IDs, or raw model text. All outputs are allowlisted.
"""
from __future__ import annotations
import json
import socket
import urllib.error

CODES=frozenset({
    "AUTHENTICATION_REJECTED","PERMISSION_OR_MODEL_REJECTED",
    "RATE_LIMITED","REQUEST_REJECTED","SERVER_REJECTED",
    "HTTP_REJECTION_OTHER","NETWORK_TIMEOUT","NETWORK_FAILURE",
    "RESPONSE_INCOMPLETE_OR_REFUSED","RESPONSE_TEXT_MISSING",
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
    if isinstance(exc,(TimeoutError,socket.timeout)):
        return "NETWORK_TIMEOUT"
    if isinstance(exc,(urllib.error.URLError,ConnectionError,OSError)):
        return "NETWORK_FAILURE"
    if isinstance(exc,json.JSONDecodeError):
        return "RESPONSE_JSON_INVALID"
    if isinstance(exc,PermissionError):
        return "LOCAL_CONFIGURATION_BLOCKED"
    if isinstance(exc,ValueError):
        # These strings are internal, fixed code paths, not API-controlled text.
        if str(exc)=="Model response incomplete or refused":
            return "RESPONSE_INCOMPLETE_OR_REFUSED"
        if str(exc)=="No valid structured response":
            return "RESPONSE_TEXT_MISSING"
        return "PROPOSAL_VALIDATION_FAILED"
    return "UNKNOWN_SAFE_FAILURE"

def safe_failure_record(exc,*,attempted_request=False):
    code=classify_failure(exc)
    assert code in CODES
    return {"status":"FAILED","failure_category":code,
            "request_may_have_been_billed":bool(attempted_request),
            "automatic_retry_permitted":False,
            "actual_spend_usd":"UNKNOWN_CHECK_PLATFORM",
            "production_changes":False}
