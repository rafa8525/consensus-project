#!/bin/bash
cd ~/consensus-project/tools
while true; do
    python3 mcl_guard.py
    sleep 60  # Check every 1 minute for missed jobs
done
