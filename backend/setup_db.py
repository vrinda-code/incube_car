import sqlite3

conn = sqlite3.connect("../database/dealership.db")  # creates the file if it doesn't exist

# 1. Create the tables (the structure)
conn.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user'
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS vehicles (
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

cars = [
    ('Toyota', 'Camry', 'sedan', 'petrol', 2024, 'White', 2800000, 5),
    ('Honda', 'City', 'sedan', 'petrol', 2023, 'Silver', 1250000, 8),
    ('Hyundai', 'i20', 'hatchback', 'diesel', 2022, 'Red', 850000, 6),
    ('Maruti Suzuki', 'Swift', 'hatchback', 'petrol', 2024, 'Blue', 750000, 10),
    ('Hyundai', 'Creta', 'suv', 'diesel', 2023, 'Black', 1600000, 4),
    ('Tata', 'Nexon EV', 'suv', 'electric', 2024, 'Grey', 1500000, 3),
    ('Mahindra', 'XUV700', 'suv', 'diesel', 2025, 'White', 2200000, 2),
    ('Porsche', '911', 'sports', 'petrol', 2023, 'Yellow', 18000000, 1),
    ('Tata', 'Tiago EV', 'hatchback', 'electric', 2024, 'Blue', 950000, 7),
    ('BMW', '3 Series', 'sedan', 'diesel', 2024, 'Black', 5200000, 2),
    ('Ferrari', '296 GTB', 'sports', 'petrol', 2025, 'Red', 55000000, 1)
]

count = conn.execute("SELECT COUNT(*) FROM vehicles").fetchone()[0]
if count == 0:  # only insert if the table is empty, so re-running is safe
    conn.executemany(
        "INSERT INTO vehicles (make, model, category, fuel_type, year, color, price, quantity) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        cars,
    )

conn.commit()
conn.close()