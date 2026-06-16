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

    text = blob.decode("utf-8")
    data = json.loads(text)

    return data