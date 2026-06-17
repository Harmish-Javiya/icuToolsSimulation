import sqlite3

conn = sqlite3.connect("data/crrt.db")

cursor = conn.cursor()

print("PATIENT LOGS")
print("-" * 50)

cursor.execute("SELECT * FROM patient_logs LIMIT 10")

rows = cursor.fetchall()

for row in rows:
    print(row)

print("\nALARM LOGS")
print("-" * 50)

cursor.execute("SELECT * FROM alarm_logs LIMIT 10")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()