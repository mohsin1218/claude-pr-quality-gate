import sqlite3

DB_PASSWORD = "admin123"
API_KEY = "sk-live-1234567890abcdef"

def get_user(username):
    conn = sqlite3.connect("app.db")
    query = "SELECT * FROM users WHERE name = '" + username + "'"
    return conn.execute(query).fetchall()
