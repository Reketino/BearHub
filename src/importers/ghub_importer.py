import sqlite3
import json
from pathlib import Path

from models.macro import Macro


import sqlite3
import json

def import_macros(db_path: str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT file FROM data LIMIT 1")
    blob = cur.fetchone()[0]

    conn.close()

    text = blob.decode("utf-8")
    data = json.loads(text)

    return data