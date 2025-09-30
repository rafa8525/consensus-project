#!/bin/bash
LOG="memory/logs/heartbeat/full_memory_absorption.log"
echo "[`date`] Starting absorb run" >> $LOG
python3 tools/absorb_memory.py --full >> memory/logs/heartbeat/memory_absorption_heartbeat.log 2>&1
echo "[`date`] Finished absorb run" >> $LOG
