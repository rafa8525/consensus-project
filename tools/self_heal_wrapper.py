#!/usr/bin/env python3
import time, functools, traceback
from pathlib import Path
from datetime import datetime
LOG_DIR = Path.home()/ "consensus-project"/"memory"/"logs"/"system"; LOG_DIR.mkdir(parents=True, exist_ok=True)
def log(line, file="self_heal.log"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with (LOG_DIR/file).open("a", encoding="utf-8") as f: f.write(f"[{ts}] {line}\n")
def self_heal(task_name, retries=3, backoff=5, fatal_on_fail=False):
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*a, **k):
            attempt=0
            while True:
                try: return fn(*a, **k)
                except Exception as e:
                    attempt+=1; log(f"ERROR {task_name} attempt {attempt}: {e}\n{traceback.format_exc(limit=6)}")
                    if attempt>=retries:
                        log(f"FAIL {task_name} after {retries} retries"); 
                        if fatal_on_fail: raise
                        return None
                    time.sleep(backoff*attempt)
        return wrapper
    return deco
if __name__=="__main__": print("Import self_heal(...) and decorate any task.")
