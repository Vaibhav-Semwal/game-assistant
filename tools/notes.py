from pathlib import Path

NOTES_FILE = Path(__file__).parent.parent / "data" / "notes.txt"

def save_note(note: str) -> str:
    NOTES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(NOTES_FILE, "a", encoding="utf-8") as file:
        file.write(note.strip() + "\n")
    return f"Saved to {NOTES_FILE.name}"

def read_note(): 
    with open(NOTES_FILE, "r", encoding="utf-8") as file:    
        return file.read()