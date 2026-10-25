import hashlib
import os
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import database
import jwt
from datetime import datetime, timedelta, timezone

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
