import sqlite3
from pathlib import Path

DB_PATH = PATH(_file_).resolve().parent / "palettepal.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
