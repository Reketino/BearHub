import sqlite3
import json
from pathlib import Path

from models.macro import Macro


import sqlite3
import json

def import_macros(db_path: str) -> list[Macro]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    blob = cur.execute(
        "SELECT file FROM data LIMIT 1"
        ).fetchone()[0]

    conn.close()
    
    data = json.loads(blob.decode("utf-8"))
    
    macros = []
    
    for card in data.get("cards", {}).get("cards", []):
        if card.get("attribute") != "MACRO_PLAYBACK":
            continue
        
        macro = card.get("macro", {})
        sequence = macro.get("sequence", {})
        simple = sequence.get("simpleSequence", {})


    return data