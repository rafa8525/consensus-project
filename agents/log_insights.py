# agents/log_insights.py

import os
import re
from collections import Counter

LOGS_DIR = "logs"
AGENTS = ["planner", "executor", "researcher", "scheduler", "memory_manager"]
ERROR_TERMS = ["error", "failed", "exception", "traceback"]
GOAL_KEYWORDS = ["goal", "task", "objective"]

def analyze_logs():
    agent_counter = Counter()
    error_count = 0
    goal_mentions = 0

    for fname in os.listdir(LOGS_DIR):
        if not fname.endswith(".txt"):
            continue
        with open(os.path.join(LOGS_DIR, fname), "r", encoding="utf-8") as f:
            content = f.read().lower()
            for agent in AGENTS:
                agent_counter[agent] += content.count(agent)
            for word in ERROR_TERMS:
                error_count += content.count(word)
            for goal in GOAL_KEYWORDS:
                goal_mentions += content.count(goal)

    summary = [
        "📊 Log Insights Summary",
        "=" * 30,
        "\nTop Agents:",
        *[f"• {agent}: {count}" for agent, count in agent_counter.most_common()],
        f"\n⚠️ Failures/Errors Detected: {error_count}",
        f"🎯 Goal Mentions: {goal_mentions}",
    ]
    return "\n".join(summary)

if __name__ == "__main__":
    print(analyze_logs())
