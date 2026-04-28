import sqlite3

def init_db():
    conn=sqlite3.connect('security.db')
    cursor=conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        objects TEXT,
        confidence REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")
    
    conn.commit()
    conn.close()


def save_log(object_name, confidence):
    conn=sqlite3.connect('security.db')
    cursor=conn.cursor()

    cursor.execute(
        "INSERT INTO alerts (objects, confidence) VALUES (?, ?)",
        (object_name, confidence)
    )
    
    conn.commit()
    conn.close()