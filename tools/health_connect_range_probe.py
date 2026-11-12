#!/usr/bin/env python3
"""Verify Drive supports bounded HTTP ranges for Health Connect ZIP.

Cloud-only metadata/one-byte probe. Does not download ZIP, persist records,
or alter ACS-03. A full streaming importer must be separately validated.
"""
from pathlib import Path
import sys
from health_connect_cloud_probe import probe

def check():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    import requests
    token=Path.home()/".secrets/google/token_gmail.json"
    info=probe(token)
    creds=Credentials.from_authorized_user_file(str(token))
    if not creds.valid:
        creds.refresh(Request())
    headers={"Authorization":"Bearer "+creds.token}
    folder=info["folder_id"]
    with requests.Session() as s:
        r=s.get("https://www.googleapis.com/drive/v3/files",headers=headers,
            params={"q":"'"+folder+"' in parents and name = 'Health Connect.zip' and trashed = false",
                    "fields":"files(id,size,parents),nextPageToken","pageSize":10},timeout=30)
        r.raise_for_status()
        files=r.json().get("files",[])
        if len(files)!=1 or folder not in files[0].get("parents",[]):
            raise RuntimeError("Cloud export lookup changed")
        item=files[0]
        length=int(item["size"])
        with s.get("https://www.googleapis.com/drive/v3/files/"+item["id"],
            params={"alt":"media"},headers={**headers,"Range":"bytes=0-0"},
            stream=True,timeout=(15,25)) as response:
            if response.status_code!=206:
                raise RuntimeError("Drive byte ranges unavailable")
            wanted="bytes 0-0/"+str(length)
            if response.headers.get("Content-Range")!=wanted:
                raise RuntimeError("Drive range header mismatch")
            data=b"".join(response.iter_content(8))
            if len(data)!=1:
                raise RuntimeError("Drive did not honor one-byte limit")
    return length

def main():
    try:
        size=check()
    except Exception as exc:
        print("ACS03_RANGE_SUPPORT=FAIL "+type(exc).__name__,file=sys.stderr)
        return 2
    print("ACS03_RANGE_SUPPORT=PASS")
    print("TOTAL_ZIP_BYTES="+str(size))
    print("TRANSFERRED_BYTES=1")
    print("ZIP_NOT_DOWNLOADED=YES")
    print("PRODUCTION_INGEST=DISABLED")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
