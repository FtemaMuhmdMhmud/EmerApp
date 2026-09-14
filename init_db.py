import sqlite3

def setup_database():
    conn = sqlite3.connect("emergency.db")

    with open("schema.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    conn.close()
    print("Database 'emergency.db' initialized successfully from schema.sql!")

if __name__ == "__main__":
    setup_database()
