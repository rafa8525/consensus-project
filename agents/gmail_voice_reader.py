#!/usr/bin/env python3
"""
gmail_voice_reader.py
Reads aloud the latest Gmail summaries from daily_summary.md.
Integrates with ChatGPT Voice or Pixel Watch speech interface.
"""

import os
import datetime
import subprocess

SUMMARY_FILE = os.path.expanduser(
    "~/consensus-project/memory/logs/email/daily_summary.md"
)
VOICE_LOG = os.path.expanduser(
    "~/consensus-project/memory/logs/voice/gmail_voice_log.md"
)
LINES_TO_READ = 12  # roughly top 3 emails (4 lines per email)


def get_latest_summary():
    """Extract the most recent summary block."""
    if not os.path.exists(SUMMARY_FILE):
        return "No Gmail summary file found."

    with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Find last "## Gmail Summary" header
    indices = [i for i, line in enumerate(lines) if line.startswith("## Gmail Summary")]
    if not indices:
        return "No Gmail summaries available."
    start = indices[-1]
    latest = lines[start : start + LINES_TO_READ]
    return "".join(latest).strip()


def speak_text(text):
    """Speak or simulate voice output (replace this with your TTS method)."""
    print("\n=== Speaking Gmail Summary ===\n")
    print(text)
    print("\n==============================\n")

    # Placeholder for actual voice interface.
    # If using ChatGPT Voice or your Pixel Watch bridge, replace the print block
    # with a call to your TTS or voice output system.
    # Example for Linux text-to-speech:
    # subprocess.run(["say", text])   # macOS
    # subprocess.run(["espeak", text])  # Linux


def log_voice_action(text):
    """Append spoken text to a log for recordkeeping."""
    os.makedirs(os.path.dirname(VOICE_LOG), exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(VOICE_LOG, "a", encoding="utf-8") as f:
        f.write(f"\n[{ts}] Spoke Gmail summary:\n{text}\n")


def main():
    summary = get_latest_summary()
    speak_text(summary)
    log_voice_action(summary)


if __name__ == "__main__":
    main()
