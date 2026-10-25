
import sqlite3

from fastapi.testclient import TestClient

import database
from main import app


client = TestClient(app)


def get_token():
    """Register and log in a user, returning a valid access token."""
    username = "vehicle_test_user"
    email = "vehicle_test_user@example.com"
    password = "TestPass123!"

    register_response = client.post(
        "/api/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code in (200, 201), (
        f"Registration failed: {register_response.text}"
    )

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200, (
        f"Login failed: {login_response.text}"
    )

    token = login_response.json().get("access_token")
    assert token, "Login response did not contain an access_token"

    return token


def add_car(quantity=5):
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
                quantity,
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
        headers={"Authorization": "Bearer fake-token"},
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

NEW_CAR = {
    "make": "Tata",
    "model": "Nexon EV",
    "category": "suv",
    "fuel_type": "electric",
    "year": 2024,
    "color": "Blue",
    "price": 1600000,
    "quantity": 4,
}


def test_add_vehicle():
    token = get_token()
    response = client.post(
        "/api/vehicles", json=NEW_CAR, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json()["model"] == "Nexon EV"
    assert "id" in response.json()


def test_add_vehicle_without_token_rejected():
    response = client.post("/api/vehicles", json=NEW_CAR)
    assert response.status_code == 401


def test_add_vehicle_invalid_category_rejected():
    token = get_token()
    bad_car = {**NEW_CAR, "category": "spaceship"}
    response = client.post(
        "/api/vehicles", json=bad_car, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422


def test_add_vehicle_negative_price_rejected():
    token = get_token()
    bad_car = {**NEW_CAR, "price": -100}
    response = client.post(
        "/api/vehicles", json=bad_car, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422

def insert_car(make, model, category, price):
    conn = sqlite3.connect(database.DB_PATH)
    conn.execute(
        "INSERT INTO vehicles (make, model, category, fuel_type, year, color, price, quantity) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (make, model, category, "petrol", 2023, "Red", price, 3),
    )
    conn.commit()
    conn.close()


def seed_search_cars():
    insert_car("Honda", "City", "sedan", 1250000)
    insert_car("Toyota", "Fortuner", "suv", 3800000)
    insert_car("Mahindra", "XUV700", "suv", 2200000)
    insert_car("Maruti Suzuki", "Swift", "hatchback", 750000)


def search(**filters):
    token = get_token()
    return client.get(
        "/api/vehicles/search",
        params=filters,
        headers={"Authorization": f"Bearer {token}"},
    )


def test_search_by_make_ignores_case():
    seed_search_cars()
    response = search(make="honda")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["model"] == "City"


def test_search_by_category():
    seed_search_cars()
    response = search(category="suv")
    assert len(response.json()) == 2


def test_search_by_price_range():
    seed_search_cars()
    response = search(min_price=1000000, max_price=2500000)
    models = {car["model"] for car in response.json()}
    assert models == {"City", "XUV700"}


def test_search_with_combined_filters():
    seed_search_cars()
    response = search(category="suv", max_price=2500000)
    assert len(response.json()) == 1
    assert response.json()[0]["model"] == "XUV700"


def test_search_no_match_returns_empty_list():
    seed_search_cars()
    response = search(make="Ferrari")
    assert response.status_code == 200
    assert response.json() == []


def test_search_without_token_rejected():
    response = client.get("/api/vehicles/search")
    assert response.status_code == 401


def test_search_min_price_above_max_price_rejected():
    response = search(min_price=5000, max_price=100)
    assert response.status_code == 422

def test_update_vehicle():
    add_car()  # the test database starts empty, so this car gets id 1
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    updated = {**NEW_CAR, "price": 1500000, "quantity": 9}

    response = client.put("/api/vehicles/1", json=updated, headers=headers)
    assert response.status_code == 200
    assert response.json()["price"] == 1500000

    # check the change was really saved, not just echoed back
    cars = client.get("/api/vehicles", headers=headers).json()
    assert cars[0]["price"] == 1500000
    assert cars[0]["quantity"] == 9


def test_update_unknown_vehicle_returns_404():
    token = get_token()
    response = client.put(
        "/api/vehicles/999", json=NEW_CAR, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Vehicle not found"


def test_update_vehicle_without_token_rejected():
    add_car()
    response = client.put("/api/vehicles/1", json=NEW_CAR)
    assert response.status_code == 401


def test_update_vehicle_invalid_data_rejected():
    add_car()
    token = get_token()
    bad_car = {**NEW_CAR, "price": -5}
    response = client.put(
        "/api/vehicles/1", json=bad_car, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422

def get_admin_token():
    body = {"email": "admin@test.com", "password": "secret123"}
    client.post("/api/auth/register", json=body)
    # new users are always "user", so promote this one directly in the database
    conn = sqlite3.connect(database.DB_PATH)
    conn.execute("UPDATE users SET role = 'admin' WHERE email = ?", (body["email"],))
    conn.commit()
    conn.close()
    # log in AFTER promoting, because the role is written into the token at login
    return client.post("/api/auth/login", json=body).json()["access_token"]


def test_admin_can_delete_vehicle():
    add_car()
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete("/api/vehicles/1", headers=headers)
    assert response.status_code == 200

    # check it is really gone
    assert client.get("/api/vehicles", headers=headers).json() == []


def test_normal_user_cannot_delete_vehicle():
    add_car()
    token = get_token()
    response = client.delete("/api/vehicles/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_delete_without_token_rejected():
    add_car()
    response = client.delete("/api/vehicles/1")
    assert response.status_code == 401


def test_delete_unknown_vehicle_returns_404():
    token = get_admin_token()
    response = client.delete("/api/vehicles/999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Vehicle not found"

def test_purchase_reduces_quantity():
    add_car(quantity=3)
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/api/vehicles/1/purchase", headers=headers)
    assert response.status_code == 200
    assert response.json()["quantity"] == 2

    # check it was really saved
    cars = client.get("/api/vehicles", headers=headers).json()
    assert cars[0]["quantity"] == 2


def test_purchase_out_of_stock_rejected():
    add_car(quantity=1)
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    first = client.post("/api/vehicles/1/purchase", headers=headers)
    assert first.status_code == 200  # buys the last car

    second = client.post("/api/vehicles/1/purchase", headers=headers)
    assert second.status_code == 409
    assert second.json()["detail"] == "Out of stock"

    # quantity must stay at 0, never go negative
    cars = client.get("/api/vehicles", headers=headers).json()
    assert cars[0]["quantity"] == 0


def test_purchase_without_token_rejected():
    add_car()
    response = client.post("/api/vehicles/1/purchase")
    assert response.status_code == 401


def test_purchase_unknown_vehicle_returns_404():
    token = get_token()
    response = client.post(
        "/api/vehicles/999/purchase", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Vehicle not found"


def test_admin_can_restock():
    add_car(quantity=3)
    token = get_admin_token()
    response = client.post(
        "/api/vehicles/1/restock",
        json={"amount": 5},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["quantity"] == 8


def test_normal_user_cannot_restock():
    add_car()
    token = get_token()
    response = client.post(
        "/api/vehicles/1/restock",
        json={"amount": 5},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_restock_invalid_amount_rejected():
    add_car()
    token = get_admin_token()
    response = client.post(
        "/api/vehicles/1/restock",
        json={"amount": 0},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422


def test_restock_unknown_vehicle_returns_404():
    token = get_admin_token()
    response = client.post(
        "/api/vehicles/999/restock",
        json={"amount": 5},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Vehicle not found"
