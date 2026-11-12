#!/usr/bin/env python3
"""Private PythonAnywhere cloud-only Drive metadata probe for Health Connect.

No downloads, no secrets printed, no writes to the project working tree.
Finds exactly one named folder and exactly one ZIP in it. Exit nonzero for
unavailable permissions, ambiguous file names or stale exports.
"""
from datetime import datetime, timezone
from pathlib import Path
import sys

API="https://www.googleapis.com/drive/v3/files"
FOLDER_NAME="AI-Consensus-Health-Backup"
FILE_NAME="Health Connect.zip"

class ProbeFailure(Exception): pass

def probe(token_path:Path, now=None, session=None):
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    import requests
    now=now or datetime.now(timezone.utc)
    if not token_path.is_file() or token_path.is_symlink():
        raise ProbeFailure("No private OAuth token")
    creds=Credentials.from_authorized_user_file(str(token_path))
    if not creds.valid:
        if not creds.refresh_token:
            raise ProbeFailure("Token has no refresh authorization")
        creds.refresh(Request())
    if not creds.valid or not creds.token:
        raise ProbeFailure("OAuth token unavailable")
    s=session or requests.Session()
    headers={"Authorization":"Bearer "+creds.token}
    def find(query,fields):
        res=s.get(API,headers=headers,params={"q":query,"fields":"nextPageToken,files("+fields+")",
           "pageSize":100},timeout=30)
        res.raise_for_status()
        data=res.json()
        if data.get("nextPageToken"):
            raise ProbeFailure("Ambiguous Drive query")
        return data.get("files",[])
    folders=find("name = '"+FOLDER_NAME+"' and mimeType = 'application/vnd.google-apps.folder' and trashed = false",
                 "id,name,mimeType,parents")
    if len(folders)!=1:
        raise ProbeFailure("Expected one accessible private backup folder")
    folder=folders[0]
    files=find("'"+folder["id"]+"' in parents and name = '"+FILE_NAME+"' and trashed = false",
               "id,name,mimeType,size,modifiedTime,parents")
    if len(files)!=1:
        raise ProbeFailure("Expected one accessible Health Connect ZIP")
    file=files[0]
    if folder["id"] not in file.get("parents",[]) or file.get("name") != FILE_NAME:
        raise ProbeFailure("Drive object relationship mismatch")
    if file.get("mimeType") not in ("application/zip","application/x-zip-compressed","application/octet-stream"):
        raise ProbeFailure("Drive file media type mismatch")
    size=int(file.get("size") or 0)
    if size<=0 or size>800*1024*1024:
        raise ProbeFailure("Export size outside expected limit")
    timestamp=datetime.fromisoformat(file["modifiedTime"].replace("Z","+00:00"))
    age_hours=(now-timestamp).total_seconds()/3600
    if not -0.1<=age_hours<=48:
        raise ProbeFailure("Export is stale or timestamp unexpected")
    return {"status":"ready","folder_id":folder["id"],"age_hours":age_hours,
            "zip_bytes":size}

def main():
    try:
        result=probe(Path.home()/".secrets/google/token_gmail.json")
    except Exception as exc:
        # Do not disclose service responses or OAuth values.
        print("ACS03_CLOUD_DRIVE_PROBE=FAIL "+type(exc).__name__,file=sys.stderr)
        return 2
    print("ACS03_CLOUD_DRIVE_PROBE=PASS")
    print("EXPORT_FOUND=YES")
    print("EXPORT_FRESH_WITHIN_48H=YES")
    print("ZIP_SIZE_MB="+str(round(result["zip_bytes"]/1048576,1)))
    print("AUTHORIZATION_AND_METADATA_ONLY=YES")
    print("INGESTION_ACTIVE=NO")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
