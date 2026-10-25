import hashlib
import os
import sqlite3
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
import database
import jwt
from datetime import datetime, timedelta, timezone
from typing import Literal

app = FastAPI()


class RegisterRequest(BaseModel):
    email: str
    password: str = Field(..., min_length=8)  


def hash_password(password):
    salt = os.urandom(16)  # random bytes, so the same password hashes differently each time
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return salt.hex() + ":" + hashed.hex()


@app.post("/api/auth/register", status_code=201)
def register(data: RegisterRequest):
    conn = database.get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO users (email, hashed_password) VALUES (?, ?)",
            (data.email, hash_password(data.password)),
        )
        conn.commit()
    except sqlite3.IntegrityError:  # the email column is UNIQUE, so a repeat fails here
        raise HTTPException(status_code=409, detail="Email already registered")
    finally:
        conn.close()
    return {"id": cursor.lastrowid, "email": data.email}

SECRET_KEY = "change-this-secret"  # in a real deployment this would come from an environment variable


class LoginRequest(BaseModel):
    email: str
    password: str


def verify_password(password, stored):
    salt_hex, hash_hex = stored.split(":")  # the saved value is "salt:hash"
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), 100_000)
    return hashed.hex() == hash_hex


@app.post("/api/auth/login")
def login(data: LoginRequest):
    conn = database.get_connection()
    row = conn.execute(
        "SELECT id, hashed_password, role FROM users WHERE email = ?", (data.email,)
    ).fetchone()
    conn.close()

    if row is None or not verify_password(data.password, row[1]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = jwt.encode(
        {
            "user_id": row[0],
            "role": row[2],
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),  # token expires in 1 hour
        },
        SECRET_KEY,
        algorithm="HS256",
    )
    return {"access_token": token}

def get_current_user(authorization: str = Header(default=None)):
    # The frontend sends the token in a header: "Authorization: Bearer <token>"
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization[len("Bearer "):]
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.InvalidTokenError:  # fake, tampered, or expired token
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@app.get("/api/vehicles")
def list_vehicles(user=Depends(get_current_user)):
    conn = database.get_connection()
    conn.row_factory = sqlite3.Row  # lets us turn each row into a dict
    rows = conn.execute("SELECT * FROM vehicles").fetchall()
    conn.close()
    return [dict(row) for row in rows]

class VehicleRequest(BaseModel):
    make: str
    model: str
    category: Literal["sedan", "hatchback", "suv", "sports"]
    fuel_type: Literal["petrol", "diesel", "electric"]
    year: int
    color: str
    price: int = Field(gt=0)
    quantity: int = Field(ge=0)


@app.post("/api/vehicles", status_code=201)
def add_vehicle(data: VehicleRequest, user=Depends(get_current_user)):
    conn = database.get_connection()
    cursor = conn.execute(
        "INSERT INTO vehicles (make, model, category, fuel_type, year, color, price, quantity) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (data.make, data.model, data.category, data.fuel_type,
         data.year, data.color, data.price, data.quantity),
    )
    conn.commit()
    vehicle_id = cursor.lastrowid
    conn.close()
    return {"id": vehicle_id, **data.model_dump()}

@app.get("/api/vehicles/search")
def search_vehicles(
    make: str = None,
    model: str = None,
    category: str = None,
    min_price: int = None,
    max_price: int = None,
    user=Depends(get_current_user),
):
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=422, detail="min_price cannot be greater than max_price")

    query = "SELECT * FROM vehicles WHERE 1=1"  # "1=1" is always true, so we can add "AND ..." freely
    params = []

    if make:
        query += " AND make LIKE ?"
        params.append(f"%{make}%")
    if model:
        query += " AND model LIKE ?"
        params.append(f"%{model}%")
    if category:
        query += " AND category = ?"
        params.append(category)
    if min_price is not None:
        query += " AND price >= ?"
        params.append(min_price)
    if max_price is not None:
        query += " AND price <= ?"
        params.append(max_price)

    conn = database.get_connection()
    conn.row_factory = sqlite3.Row
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.put("/api/vehicles/{vehicle_id}")
def update_vehicle(vehicle_id: int, data: VehicleRequest, user=Depends(get_current_user)):
    conn = database.get_connection()
    cursor = conn.execute(
        "UPDATE vehicles SET make=?, model=?, category=?, fuel_type=?, "
        "year=?, color=?, price=?, quantity=? WHERE id=?",
        (data.make, data.model, data.category, data.fuel_type,
         data.year, data.color, data.price, data.quantity, vehicle_id),
    )
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:  # no row matched this id
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"id": vehicle_id, **data.model_dump()}

def get_admin_user(user=Depends(get_current_user)):
    # runs the normal token check first, then also requires the admin role
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@app.delete("/api/vehicles/{vehicle_id}")
def delete_vehicle(vehicle_id: int, user=Depends(get_admin_user)):
    conn = database.get_connection()
    cursor = conn.execute("DELETE FROM vehicles WHERE id = ?", (vehicle_id,))
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"message": "Vehicle deleted"}