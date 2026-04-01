import sqlite3

conn = sqlite3.connect('yappy.db')
cursor = conn.cursor()

# View all compressors
print("=== Compressors ===")
cursor.execute("SELECT * FROM compressor")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Name: {row[1]}, Brand: {row[2]}, Price: RM{row[3]}")

# View all users
print("\n=== Users ===")
cursor.execute("SELECT id, username FROM user")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Username: {row[1]}")

# View all orders
print("\n=== Orders ===")
cursor.execute("SELECT * FROM order")
for row in cursor.fetchall():
    print(f"Order ID: {row[0]}, User ID: {row[1]}, Compressor ID: {row[2]}, Status: {row[3]}")

conn.close()