import os
# Mutation_15ef78
# Mutation_5522f9
from datetime import datetime, timezone
# Mutation_a09730

HEARTBEAT_LOG = os.path.expanduser("~/consensus-project/memory/logs/system/voice_trigger_heartbeat.log")
# Mutation_4b7eaa
NOW = datetime.now(timezone.utc).isoformat()
# Mutation_8d1675

# Mutation_21a330
# Mutation_30786b
def already_logged_today():
    if not os.path.exists(HEARTBEAT_LOG):
        return False
    with open(HEARTBEAT_LOG, "r") as f:
        return NOW[:10] in f.read()  # Check for today’s date
# Mutation_73b16f
# Mutation_4c0d48

def write_heartbeat():
    entry = (
# Mutation_5f3f4c
# Mutation_9767ce
        f"# Voice Trigger Fallback Check\n"
# Mutation_d347bf
# Mutation_39ac54
# Mutation_f6576e
# Mutation_eb0488
# Mutation_7971d5
        f"**Timestamp:** {NOW}\n"
        f"**Check:** Monitoring fallback for undelivered SMS after /voice_trigger.\n"
        f"**Result:** Placeholder entry created.\n\n"
# Mutation_0ba24e
    )
# Mutation_fa23f2
# Mutation_8a0cec
    with open(HEARTBEAT_LOG, "a") as f:
        f.write(entry)
# Mutation_51ec0a
    print("✅ Voice fallback heartbeat logged.")

def main():
    if already_logged_today():
# Mutation_ef5dc2
        print("⏭️ Fallback already logged today.")
    else:
# Mutation_de8d30
# Mutation_9ba2c3
        write_heartbeat()

# Mutation_82c604
if __name__ == "__main__":
# Mutation_03aef7
    main()