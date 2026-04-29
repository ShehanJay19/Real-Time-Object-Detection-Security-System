from fastapi import APIRouter
import sqlite3

router =APIRouter()

@router.get("/logs")
def get_logs():
    conn=sqlite3.connect("security.db")
    cursor =conn.cursor()
    
    cursor.execute("SELECT * FROM alerts ORDER BY id DESC")
    rows = cursor.fetchall()
    
    conn.close()
    
    logs=[]
    for row in rows:
        logs.append({
            "id":row[0],
            "object":row[1],
            "confidence":row[2],
            "timestamp":row[3]
        })
    return {"logs":logs}    