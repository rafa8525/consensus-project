"""No-cost tests for sanitized API failure reporting, including secret leakage."""
import io
import json
import socket
import unittest
import urllib.error
from contextlib import redirect_stdout
from unittest.mock import patch
from safe_trial_diagnostics import CODES,classify_failure,safe_failure_record
import one_shot_proposal_trial as trial

class SafeTrialDiagnosticsTests(unittest.TestCase):
    def test_http_mapping(self):
        mapping={400:"REQUEST_REJECTED",401:"AUTHENTICATION_REJECTED",
                 403:"PERMISSION_OR_MODEL_REJECTED",404:"PERMISSION_OR_MODEL_REJECTED",
                 422:"REQUEST_REJECTED",429:"RATE_LIMITED",
                 500:"SERVER_REJECTED",503:"SERVER_REJECTED"}
        for status,expected in mapping.items():
            error=urllib.error.HTTPError("https://SECRET",status,
                 "sensitive raw API error",{},None)
            self.assertEqual(classify_failure(error),expected)
    def test_network(self):
        self.assertEqual(classify_failure(TimeoutError("secret")),"NETWORK_TIMEOUT")
        self.assertEqual(classify_failure(socket.timeout("secret")),"NETWORK_TIMEOUT")
        self.assertEqual(classify_failure(urllib.error.URLError("secret")),"NETWORK_FAILURE")
    def test_incomplete(self):
        self.assertEqual(classify_failure(ValueError("Model response incomplete or refused")),
                         "RESPONSE_INCOMPLETE_OR_REFUSED")
    def test_output_exhausted(self):
        self.assertEqual(
            classify_failure(ValueError("Model output token budget exhausted")),
            "OUTPUT_TOKEN_BUDGET_EXHAUSTED")
    def test_missing_text(self):
        self.assertEqual(classify_failure(ValueError("No valid structured response")),
                         "RESPONSE_TEXT_MISSING")
    def test_invalid_json(self):
        try:json.loads("{bad")
        except json.JSONDecodeError as e:
            self.assertEqual(classify_failure(e),"RESPONSE_JSON_INVALID")
    def test_invalid_schema(self):
        self.assertEqual(classify_failure(ValueError("secret schema detail")),
                         "PROPOSAL_VALIDATION_FAILED")
    def test_unknown_object(self):
        self.assertEqual(classify_failure(RuntimeError("secret")),"UNKNOWN_SAFE_FAILURE")
    def test_no_sensitive_details(self):
        for error in (ValueError("sk-secret-EXAMPLE password response"),
                      RuntimeError("https://private.example/secret"),
                      urllib.error.HTTPError("https://private.example/secret",401,
                           "sk-secret-EXAMPLE",{},None)):
            result=json.dumps(safe_failure_record(error,attempted_request=True))
            self.assertNotIn("sk-secret",result)
            self.assertNotIn("private.example",result)
            self.assertNotIn("password",result)
            self.assertTrue(json.loads(result)["request_may_have_been_billed"])
    def test_result_is_allowlisted(self):
        for e in (ValueError("anything"),PermissionError("secret"),OSError("secret")):
            self.assertIn(classify_failure(e),CODES)
    def test_main_prints_category_only(self):
        with (patch.object(trial,"live_once",side_effect=ValueError("sk-SECRET: invalid")),
              patch.object(trial.os,"environ",{}),
              patch("sys.argv",["trial","--live"])):
            out=io.StringIO()
            with redirect_stdout(out):
                with self.assertRaises(SystemExit) as ctx:trial.main()
            self.assertEqual(ctx.exception.code,1)
            self.assertNotIn("sk-SECRET",out.getvalue())
            self.assertIn("PROPOSAL_VALIDATION_FAILED",out.getvalue())
    def test_main_no_retry(self):
        with (patch.object(trial,"live_once",side_effect=TimeoutError("secret")) as call,
              patch.object(trial.os,"environ",{}),
              patch("sys.argv",["trial","--live"])):
            with redirect_stdout(io.StringIO()):
                with self.assertRaises(SystemExit):trial.main()
            self.assertEqual(call.call_count,1)
if __name__=="__main__":unittest.main()
