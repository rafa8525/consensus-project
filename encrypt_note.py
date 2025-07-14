import datetime
from pathlib import Path

# Simple XOR "encryption" with a static key — minimal obfuscation
def xor_encrypt(text, key="simplekey"):
    return "".join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(text))

def store_encrypted_note(label, plaintext):
    encrypted = xor_encrypt(plaintext)
    date_str = datetime.date.today().isoformat()
    log_dir = Path("memory/logs/security")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"encrypted_notes_{date_str}.md"
    timestamp = datetime.datetime.now().isoformat()
    entry = f"{timestamp} — {label}: {encrypted}\n"

    with log_file.open("a") as f:
        f.write(entry)

if __name__ == "__main__":
    # Example usage
    store_encrypted_note("TwilioToken", "abc123XYZ")
