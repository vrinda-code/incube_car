import sqlite3
import pytest
import database


@pytest.fixture(autouse=True)
def temp_db(tmp_path):
    # Before every test: point the app at a fresh, empty database file
    database.DB_PATH = str(tmp_path / "test.db")
    conn = sqlite3.connect(database.DB_PATH)
    conn.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    """)
    conn.execute("""
        CREATE TABLE vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            make TEXT NOT NULL,
            model TEXT NOT NULL,
            category TEXT NOT NULL CHECK (category IN ('sedan','hatchback','suv','sports')),
            fuel_type TEXT NOT NULL CHECK (fuel_type IN ('petrol','diesel','electric')),
            year INTEGER NOT NULL,
            color TEXT NOT NULL,
            price INTEGER NOT NULL CHECK (price > 0),
            quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0)
        )
    """)
    conn.commit()
    conn.close()