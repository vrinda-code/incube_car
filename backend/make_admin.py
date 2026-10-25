import database

email = input("Email of the user to make admin: ")

conn = database.get_connection()
cursor = conn.execute("UPDATE users SET role = 'admin' WHERE email = ?", (email,))
conn.commit()
conn.close()

print("Done." if cursor.rowcount else "No user with that email.")