
import sqlite3

from fastapi.testclient import TestClient

import database
from main import app


client = TestClient(app)


def get_token():
    """Register and log in a user, returning a valid access token."""
    username = "vehicle_test_user"
    password = "TestPass123!"

    register_response = client.post(
        "/api/auth/register",
        json={
            "username": username,
            "password": password,
        },
    )

    assert register_response.status_code in (200, 201), (
        f"Registration failed: {register_response.text}"
    )

    login_response = client.post(
        "/api/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )

    assert login_response.status_code == 200, (
        f"Login failed: {login_response.text}"
    )

    token = login_response.json().get("access_token")
    assert token, "Login response did not contain an access_token"

    return token


def add_car():
    """Insert a vehicle directly into the isolated test database."""
    with sqlite3.connect(database.DB_PATH) as conn:
        cursor = conn.execute(
            """
            INSERT INTO vehicles (
                make, model, category, fuel_type,
                year, color, price, quantity
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "Toyota",
                "Camry",
                "sedan",
                "petrol",
                2024,
                "White",
                2800000,
                5,
            ),
        )
        conn.commit()
        return cursor.lastrowid


def test_list_vehicles_without_token_rejected():
    response = client.get("/api/vehicles")

    assert response.status_code == 401


def test_list_vehicles_with_fake_token_rejected():
    response = client.get(
        "/api/vehicles",
        headers={"Authorization": "Bearer fake.invalid.token"},
    )

    assert response.status_code == 401


def test_list_vehicles_with_valid_token():
    add_car()
    token = get_token()

    response = client.get(
        "/api/vehicles",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    vehicles = response.json()

    # Assumes the endpoint returns a JSON list of vehicles.
    assert isinstance(vehicles, list)
    assert len(vehicles) == 1
    assert vehicles[0]["model"] == "Camry"
