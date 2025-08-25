from pathlib import Path
def write_note(text="ok"):
    p = Path("memory/agent_note.txt")
    p.write_text(text+"\n", encoding="utf-8")
    return str(p)
