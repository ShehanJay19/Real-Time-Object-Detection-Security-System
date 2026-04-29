from fastapi import APIRouter
import sqlite3
from typing import Optional

router =APIRouter()

@router.get("/logs")
def get_logs(object_name: Optional[str] = None, minutes: Optional[int] = None):
    conn=sqlite3.connect("security.db")
    cursor =conn.cursor()

    object_pattern = None
    if object_name:
        object_pattern = f"%{object_name.lower()}%"

    minutes_modifier = None
    if minutes is not None:
        minutes_modifier = f"-{minutes} minutes"

    cursor.execute(
        """
        SELECT id, objects, confidence, timestamp
        FROM alerts
        WHERE (? IS NULL OR LOWER(objects) LIKE ?)
          AND (? IS NULL OR timestamp >= datetime('now', ?))
        ORDER BY id DESC
        """,
        (object_name, object_pattern, minutes, minutes_modifier),
    )
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