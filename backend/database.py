import sqlite3

DB_PATH = "database/dealership.db"

def get_connection():
    return sqlite3.connect(DB_PATH)