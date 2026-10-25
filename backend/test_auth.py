import sqlite3
import pytest
from fastapi.testclient import TestClient

import database
from main import app

client = TestClient(app)


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
    conn.commit()
    conn.close()


def test_register_creates_user():
    response = client.post(
        "/api/auth/register",
        json={"email": "a@test.com", "password": "secret123"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "a@test.com"
