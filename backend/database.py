import sqlite3
from pathlib import Path

DB_PATH = str(Path(__file__).resolve().parent.parent / "database" / "dealership.db")

def get_connection():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)
