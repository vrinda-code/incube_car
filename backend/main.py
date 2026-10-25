import hashlib
import os
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import database

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