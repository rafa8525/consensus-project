"""Synthetic no-network tests for bounded Drive byte-range reader."""
import io
from pathlib import Path
import re
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from health_connect_memory_import import RangeFile, CloudImportError

class Response:
    status_code=206
    def __init__(self,start,end,body,total):
        self.headers={"Content-Range":f"bytes {start}-{end}/{total}"}
        self.body=body
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def iter_content(self,n):yield self.body

class FakeSession:
    def __init__(self,data):self.data=data
    def get(self,url,params,headers,stream,timeout):
        start,end=map(int,re.match(r"bytes=(\d+)-(\d+)",headers["Range"]).groups())
        return Response(start,end,self.data[start:end+1],len(self.data))

class TestRanges(unittest.TestCase):
    def test_seek_and_read(self):
        data=bytes(range(256))*40000
        obj=RangeFile(FakeSession(data),"https://example.invalid",{},len(data))
        self.assertEqual(obj.read(10),data[:10])
        obj.seek(5*1024*1024)
        self.assertEqual(obj.read(123),data[5*1024*1024:5*1024*1024+123])
        obj.seek(-15,2)
        self.assertEqual(obj.read(),data[-15:])
        self.assertEqual(obj.read(),b"")
        self.assertLessEqual(obj.bytes_transferred,3*4*1024*1024)
    def test_negative_seek(self):
        r=RangeFile(FakeSession(b"hello"),"test",{},5)
        with self.assertRaises(ValueError):r.seek(-1)

if __name__=="__main__":unittest.main()
