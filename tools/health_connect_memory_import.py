#!/usr/bin/env python3
"""Cloud-only Health Connect ZIP -> memory SQLite -> conservative steps candidate.

No ZIP/database files written; no automatic production activation. Uses bounded
HTTP byte ranges, zlib decompression and SQLite deserialize. Requires sufficient
RAM; stops rather than risking unbounded cloud-resource consumption.
"""
from __future__ import annotations
import io
import os
import re
import sqlite3
import struct
import sys
import zipfile
from datetime import datetime,timezone
from pathlib import Path

MAX_ZIP = 800 * 1024 * 1024
MAX_DB = 650 * 1024 * 1024
BLOCK = 4 * 1024 * 1024
URL = "https://www.googleapis.com/drive/v3/files"
class CloudImportError(Exception): pass

class RangeFile(io.RawIOBase):
    def __init__(self, session, url, headers, length):
        self.session,self.url,self.headers,self.length=session,url,headers,length
        self.position=0
        self.block_start=-1
        self.block=b""
        self.bytes_transferred=0
    def readable(self): return True
    def seekable(self): return True
    def tell(self): return self.position
    def seek(self,offset,whence=0):
        pos=offset if whence==0 else self.position+offset if whence==1 else self.length+offset if whence==2 else -1
        if pos<0: raise ValueError("Negative ZIP seek")
        self.position=pos
        return pos
    def read(self,size=-1):
        if self.position>=self.length: return b""
        if size is None or size<0: size=self.length-self.position
        size=min(size,self.length-self.position)
        out=bytearray()
        while size:
            first=(self.position//BLOCK)*BLOCK
            if self.block_start!=first:
                last=min(first+BLOCK,self.length)-1
                headers={**self.headers,"Range":f"bytes={first}-{last}"}
                with self.session.get(self.url,params={"alt":"media"},headers=headers,stream=True,timeout=(15,90)) as r:
                    if r.status_code!=206: raise CloudImportError("Drive refused partial content")
                    if r.headers.get("Content-Range")!=f"bytes {first}-{last}/{self.length}":
                        raise CloudImportError("Drive range mismatch")
                    raw=bytearray()
                    for chunk in r.iter_content(1024*1024):
                        raw.extend(chunk)
                        if len(raw)>last-first+1: raise CloudImportError("Oversized byte-range response")
                    if len(raw)!=last-first+1: raise CloudImportError("Short byte-range response")
                    self.block=bytes(raw)
                    self.block_start=first
                    self.bytes_transferred+=len(raw)
            start=self.position-first
            part=self.block[start:start+size]
            if not part: raise CloudImportError("Empty ZIP range")
            out.extend(part)
            self.position+=len(part)
            size-=len(part)
        return bytes(out)

def import_candidate():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    import requests
    from health_connect_cloud_probe import probe
    info=probe(Path.home()/".secrets/google/token_gmail.json")
    token=Path.home()/".secrets/google/token_gmail.json"
    creds=Credentials.from_authorized_user_file(str(token))
    if not creds.valid: creds.refresh(Request())
    if not creds.valid or not creds.token: raise CloudImportError("OAuth unavailable")
    headers={"Authorization":"Bearer "+creds.token}
    query="'"+info["folder_id"]+"' in parents and name = 'Health Connect.zip' and trashed = false"
    with requests.Session() as session:
        listing=session.get(URL,params={"q":query,"fields":"nextPageToken,files(id,name,size,parents)","pageSize":10},headers=headers,timeout=30)
        listing.raise_for_status()
        files=listing.json().get("files",[])
        if len(files)!=1 or info["folder_id"] not in files[0].get("parents",[]): raise CloudImportError("Drive export changed")
        file=files[0]
        length=int(file["size"])
        if not 0<length<=MAX_ZIP: raise CloudImportError("Unexpected ZIP size")
        rf=RangeFile(session,URL+"/"+file["id"],headers,length)
        with zipfile.ZipFile(rf) as archive:
            members=archive.infolist()
            if len(members)!=1 or members[0].filename!="health_connect_export.db":
                raise CloudImportError("Unexpected ZIP structure")
            member=members[0]
            if not 0<member.file_size<=MAX_DB: raise CloudImportError("Database too large for this approach")
            # In-memory decompression; zipfile validates CRC on completion.
            raw=bytearray()
            with archive.open(member) as source:
                while True:
                    chunk=source.read(1024*1024)
                    if not chunk: break
                    raw.extend(chunk)
                    if len(raw)>MAX_DB: raise CloudImportError("Database exceeded memory safety bound")
        if raw[:16]!=b"SQLite format 3\x00": raise CloudImportError("Not SQLite")
        db=sqlite3.connect(":memory:")
        try:
            db.deserialize(bytes(raw))
            del raw
            db.execute("PRAGMA query_only=ON")
            if db.execute("PRAGMA quick_check").fetchone()[0]!="ok": raise CloudImportError("SQLite integrity failed")
            needed={"steps_record_table","application_info_table","device_info_table"}
            existing={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if not needed.issubset(existing): raise CloudImportError("Missing source tables")
            metadata=db.execute("SELECT app_name,package_name,COUNT(*) FROM steps_record_table s JOIN application_info_table a ON a.row_id=s.app_info_id GROUP BY s.app_info_id ORDER BY COUNT(*) DESC").fetchall()
            schema=[r[1] for r in db.execute("PRAGMA table_info(steps_record_table)")]
            required={"uuid","app_info_id","start_time","end_time","count","local_date"}
            if not required.issubset(schema): raise CloudImportError("Unexpected step schema")
            # Never infer epoch unit from field names. Only print a safe coarse order-of-magnitude class.
            sample=db.execute("SELECT start_time,end_time FROM steps_record_table ORDER BY row_id DESC LIMIT 1").fetchone()
            if not sample or not all(isinstance(v,int) for v in sample): raise CloudImportError("Missing timestamp samples")
            orders=[len(str(abs(v))) for v in sample]
            if len(set(orders))!=1: raise CloudImportError("Mixed timestamp magnitudes")
            result={"records":sum(r[2] for r in metadata),"sources":len(metadata),
                    "timestamp_digits":orders[0],"bytes_transferred":rf.bytes_transferred}
            return result
        finally:
            db.close()

def main():
    try: data=import_candidate()
    except Exception as exc:
        print("ACS03_MEMORY_IMPORT=FAIL "+type(exc).__name__,file=sys.stderr)
        return 2
    print("ACS03_MEMORY_IMPORT=PASS")
    print("RECORDS="+str(data["records"]))
    print("SOURCES="+str(data["sources"]))
    print("TIMESTAMP_DIGITS="+str(data["timestamp_digits"]))
    print("NETWORK_MIB="+str(round(data["bytes_transferred"]/1048576,1)))
    print("PRODUCTION_INGEST=DISABLED")
    return 0

if __name__=="__main__":raise SystemExit(main())
