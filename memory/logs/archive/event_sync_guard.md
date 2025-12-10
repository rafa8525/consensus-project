[2025-12-10 07:04:15] ---- Calendar Sync Guard v3 Started ----
[2025-12-10 07:04:15] ❌ Calendar Guard v3 failed – FileNotFoundError: [Errno 2] No such file or directory: '/home/rafa1215/consensus-project/memory/system/service_account.json'
[2025-12-10 07:04:15] Traceback (most recent call last):
  File "/home/rafa1215/consensus-project/tools/calendar_sync_guard_v3.py", line 28, in main
    creds = service_account.Credentials.from_service_account_file(str(KEY), scopes=SCOPES)
  File "/home/rafa1215/.local/lib/python3.13/site-packages/google/oauth2/service_account.py", line 264, in from_service_account_file
    info, signer = _service_account_info.from_filename(
                   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        filename, require=["client_email", "token_uri"]
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/home/rafa1215/.local/lib/python3.13/site-packages/google/auth/_service_account_info.py", line 78, in from_filename
    with io.open(filename, "r", encoding="utf-8") as json_file:
         ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/home/rafa1215/consensus-project/memory/system/service_account.json'

[2025-12-10 07:04:16] ---- Calendar Sync Guard v3 Started ----
[2025-12-10 07:04:16] ❌ Calendar Guard v3 failed – FileNotFoundError: [Errno 2] No such file or directory: '/home/rafa1215/consensus-project/memory/system/service_account.json'
[2025-12-10 07:04:16] Traceback (most recent call last):
  File "/home/rafa1215/consensus-project/tools/calendar_sync_guard_v3.py", line 28, in main
    creds = service_account.Credentials.from_service_account_file(str(KEY), scopes=SCOPES)
  File "/home/rafa1215/.local/lib/python3.13/site-packages/google/oauth2/service_account.py", line 264, in from_service_account_file
    info, signer = _service_account_info.from_filename(
                   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        filename, require=["client_email", "token_uri"]
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/home/rafa1215/.local/lib/python3.13/site-packages/google/auth/_service_account_info.py", line 78, in from_filename
    with io.open(filename, "r", encoding="utf-8") as json_file:
         ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/home/rafa1215/consensus-project/memory/system/service_account.json'

