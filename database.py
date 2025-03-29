import sqlite3
from datetime import datetime

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect("attendance.db")
        create_table(conn)
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    return conn

def create_table(conn):
    sql = """
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL
    );
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Table creation error: {e}")

def mark_attendance(conn, name):
    today = datetime.now().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M:%S")
    
    # Check if already marked today
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM attendance 
        WHERE name = ? AND date = ?
    """, (name, today))
    
    if cursor.fetchone() is None:
        cursor.execute("""
            INSERT INTO attendance (name, date, time)
            VALUES (?, ?, ?)
        """, (name, today, time))
        conn.commit()
        print(f"Attendance marked for {name}")