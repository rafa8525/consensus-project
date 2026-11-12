"""Read-only independent-process observer of synthetic staging SQLite state.

Intentionally does not import an agent, event handler, or evaluator. Uses SQLite
mode=ro and checks closed-world expected states without modifying the databases.
"""
import json
import os
import sqlite3
import sys


def rows(folder, database, sql):
    path = os.path.join(folder, database)
    if not os.path.isfile(path):
        return []
    conn = sqlite3.connect("file:" + path + "?mode=ro", uri=True)
    try:
        return conn.execute(sql).fetchall()
    finally:
        conn.close()


def inspect(folder):
    tasks = rows(folder, "tasks.sqlite",
                 "SELECT task_id,state FROM tasks ORDER BY task_id")
    observations = rows(folder, "memory.sqlite",
                        "SELECT evidence_id,task_id FROM observations ORDER BY evidence_id")
    deliveries = rows(folder, "events.sqlite",
                      "SELECT adapter_id,event_id,state FROM deliveries ORDER BY event_id")
    return {"tasks": tasks, "memory": observations, "deliveries": deliveries}


if __name__ == "__main__":
    if len(sys.argv) != 2 or not os.path.isdir(sys.argv[1]):
        raise SystemExit("sandbox directory argument required")
    print(json.dumps(inspect(sys.argv[1]), sort_keys=True))
