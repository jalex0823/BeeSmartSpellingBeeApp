import sqlite3

conn = sqlite3.connect('beesmart.db')
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", [t[0] for t in tables])

# Try avatar table
cursor.execute("SELECT slug, folder_path, obj_file, thumbnail_file FROM avatar WHERE obj_file LIKE '%.glb' LIMIT 3")
rows = cursor.fetchall()

for row in rows:
    print(f"\nslug: {row[0]}")
    print(f"folder_path: {row[1]}")
    print(f"obj_file: {row[2]}")
    print(f"thumbnail: {row[3]}")
    print(f"Expected URL: /static/assets/avatars/{row[1]}/{row[2]}")

conn.close()
