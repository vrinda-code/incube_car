import sqlite3
import pytest
from fastapi.testclient import TestClient

import database
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def temp_db(tmp_path):
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


def test_register_rejects_duplicate_email():
    payload = {"email": "a@test.com", "password": "secret123"}

    first_response = client.post("/api/auth/register", json=payload)
    duplicate_response = client.post("/api/auth/register", json=payload)

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409


def test_register_rejects_short_password():
    response = client.post(
        "/api/auth/register",
        json={"email": "a@test.com", "password": "short"},
    )

    assert response.status_code == 422


def test_register_does_not_store_password_as_plaintext():
    password = "secret123"
    response = client.post(
        "/api/auth/register",
        json={"email": "a@test.com", "password": password},
    )
    assert response.status_code == 201

    conn = sqlite3.connect(database.DB_PATH)
    row = conn.execute(
        "SELECT hashed_password FROM users WHERE email = ?",
        ("a@test.com",),
    ).fetchone()
    conn.close()

    assert row is not None
    assert row[0] != password


def test_login_returns_token():
    credentials = {"email": "a@test.com", "password": "secret123"}
    register_response = client.post("/api/auth/register", json=credentials)
    assert register_response.status_code == 201

    response = client.post("/api/auth/login", json=credentials)

    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_rejects_wrong_password():
    register_response = client.post(
        "/api/auth/register",
        json={"email": "a@test.com", "password": "secret123"},
    )
    assert register_response.status_code == 201

    response = client.post(
        "/api/auth/login",
        json={"email": "a@test.com", "password": "incorrect"},
    )

    assert response.status_code == 401


def test_login_rejects_unknown_email():
    response = client.post(
        "/api/auth/login",
        json={"email": "unknown@test.com", "password": "secret123"},
    )

    assert response.status_code == 401
