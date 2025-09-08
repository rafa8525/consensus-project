from mcl_v2.sms_policy import SmsPolicy

def test_not_whitelisted_blocks():
    p = SmsPolicy(enabled=True, whitelist=[], quiet_hours="00-00")
    st, meta = p.decide("+19999999999", "hello")
    assert st == "SKIP_NOT_WHITELISTED"
    assert meta["whitelist"] == []

def test_quiet_hours_blocks():
    p = SmsPolicy(enabled=True, whitelist=["+10000000000"], quiet_hours="00-23")
    st, meta = p.decide("+10000000000", "quiet")
    assert st == "SKIP_QUIET_HOURS"
    assert meta["window"] == "00-23"

def test_allow_when_enabled_whitelisted_and_not_quiet():
    p = SmsPolicy(enabled=True, whitelist=["+10000000000"], quiet_hours="00-00")
    st, meta = p.decide("+10000000000", "ok")
    assert st == "ALLOW"
    assert meta == {}
