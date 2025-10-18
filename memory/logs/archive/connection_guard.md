[2025-10-17 23:00:02] ---- Gmail Refresh Guard Started ----
[2025-10-17 23:00:02] ❌ Token file missing. Gmail connection cannot be refreshed.
[2025-10-17 23:00:02] ❌ Gmail refresh guard failed. Manual re-authentication may be needed.

[2025-10-17 23:05:35] ---- Gmail Refresh Guard Started ----
[2025-10-17 23:05:35] ⚠️ Could not load existing token file: Expecting value: line 1 column 1 (char 0)
[2025-10-17 23:05:35] Traceback (most recent call last):
  File "/home/rafa1215/consensus-project/tools/gmail_refresh_guard.py", line 51, in get_or_refresh_gmail_token
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
  File "/home/rafa1215/.local/lib/python3.13/site-packages/google/oauth2/credentials.py", line 516, in from_authorized_user_file
    data = json.load(json_file)
  File "/usr/local/lib/python3.13/json/__init__.py", line 293, in load
    return loads(fp.read(),
        cls=cls, object_hook=object_hook,
        parse_float=parse_float, parse_int=parse_int,
        parse_constant=parse_constant, object_pairs_hook=object_pairs_hook, **kw)
  File "/usr/local/lib/python3.13/json/__init__.py", line 346, in loads
    return _default_decoder.decode(s)
           ~~~~~~~~~~~~~~~~~~~~~~~^^^
  File "/usr/local/lib/python3.13/json/decoder.py", line 345, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
               ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.13/json/decoder.py", line 363, in raw_decode
    raise JSONDecodeError("Expecting value", s, err.value) from None
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)

[2025-10-17 23:05:35] ❌ Missing client_secret.json. Cannot authenticate Gmail.
[2025-10-17 23:05:35] ❌ Gmail Refresh Guard failed.

[2025-10-17 23:12:07] ---- Gmail Refresh Guard Started ----
[2025-10-17 23:12:07] ⚠️ Could not load existing token file: Expecting value: line 1 column 1 (char 0)
[2025-10-17 23:12:07] Traceback (most recent call last):
  File "/home/rafa1215/consensus-project/tools/gmail_refresh_guard.py", line 51, in get_or_refresh_gmail_token
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
  File "/home/rafa1215/.local/lib/python3.13/site-packages/google/oauth2/credentials.py", line 516, in from_authorized_user_file
    data = json.load(json_file)
  File "/usr/local/lib/python3.13/json/__init__.py", line 293, in load
    return loads(fp.read(),
        cls=cls, object_hook=object_hook,
        parse_float=parse_float, parse_int=parse_int,
        parse_constant=parse_constant, object_pairs_hook=object_pairs_hook, **kw)
  File "/usr/local/lib/python3.13/json/__init__.py", line 346, in loads
    return _default_decoder.decode(s)
           ~~~~~~~~~~~~~~~~~~~~~~~^^^
  File "/usr/local/lib/python3.13/json/decoder.py", line 345, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
               ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.13/json/decoder.py", line 363, in raw_decode
    raise JSONDecodeError("Expecting value", s, err.value) from None
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)

[2025-10-17 23:12:07] ⚠️ No valid Gmail token found. Starting OAuth flow.
[2025-10-17 23:18:18] ---- Gmail Refresh Guard Started ----
[2025-10-17 23:18:18] ⚠️ Could not load existing token file: Expecting value: line 1 column 1 (char 0)
[2025-10-17 23:18:18] Traceback (most recent call last):
  File "/home/rafa1215/consensus-project/tools/gmail_refresh_guard.py", line 51, in get_or_refresh_gmail_token
    creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
  File "/home/rafa1215/.local/lib/python3.13/site-packages/google/oauth2/credentials.py", line 516, in from_authorized_user_file
    data = json.load(json_file)
  File "/usr/local/lib/python3.13/json/__init__.py", line 293, in load
    return loads(fp.read(),
        cls=cls, object_hook=object_hook,
        parse_float=parse_float, parse_int=parse_int,
        parse_constant=parse_constant, object_pairs_hook=object_pairs_hook, **kw)
  File "/usr/local/lib/python3.13/json/__init__.py", line 346, in loads
    return _default_decoder.decode(s)
           ~~~~~~~~~~~~~~~~~~~~~~~^^^
  File "/usr/local/lib/python3.13/json/decoder.py", line 345, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
               ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.13/json/decoder.py", line 363, in raw_decode
    raise JSONDecodeError("Expecting value", s, err.value) from None
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)

[2025-10-17 23:18:18] ⚠️ No valid Gmail token found. Starting OAuth flow.
