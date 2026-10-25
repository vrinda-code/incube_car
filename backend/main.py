import hashlib
import os
from fastapi import FastAPI
from pydantic import BaseModel
import database

app = FastAPI()


class RegisterRequest(BaseModel):
    email: str
    password: str


def hash_password(password):
    salt = os.urandom(16)  # random bytes, so the same password hashes differently each time
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return salt.hex() + ":" + hashed.hex()


@app.post("/api/auth/register", status_code=201)
def register(data: RegisterRequest):
    conn = database.get_connection()
    cursor = conn.execute(
        "INSERT INTO users (email, hashed_password) VALUES (?, ?)",
        (data.email, hash_password(data.password)),
    )
    conn.commit()
    user_id = cursor.lastrowid  # the id the database gave the new user
    conn.close()
    return {"id": user_id, "email": data.email}