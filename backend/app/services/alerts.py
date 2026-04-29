import sqlite3
import time
from app.services.email_service import send_email_alert
from app.services.telegram_service import send_telegram_alert

last_alert_time = 0
ALERT_COOLDOWN = 10  # seconds
DANGEROUS_LABELS = {"knife", "gun", "pistol", "rifle", "weapon", "handgun"}


def _normalize_label(obj):
    if isinstance(obj, tuple) and obj:
        return str(obj[0]).strip().lower()
    return str(obj).strip().lower()

def should_trigger_alert(detected_objects):
    global last_alert_time

    current_time = time.time()

    # Prevent spam alerts
    if current_time - last_alert_time < ALERT_COOLDOWN:
        return False

    for obj in detected_objects:
        label = _normalize_label(obj)

        if label in DANGEROUS_LABELS:
            last_alert_time = current_time
            return True

    return False


def trigger_alert(objects):

    print("🚨 ALERT:", objects)
    
    # Find dangerous objects from the detected list
    dangerous_objects = []
    max_confidence = 0
    
    for obj in objects:
        if isinstance(obj, tuple):
            label, confidence = obj
        else:
            label = obj
            confidence = 0.5
        
        if label.lower() in DANGEROUS_LABELS:
            dangerous_objects.append(label)
            max_confidence = max(max_confidence, confidence if isinstance(confidence, (int, float)) else 0.5)
    
    # Save dangerous detection to database as an alert
    if dangerous_objects:
        save_alert(dangerous_objects, max_confidence)
    
    send_email_alert(objects)
    send_telegram_alert(objects)


def save_alert(objects, confidence=1.0):
    """Save dangerous object detection as an alert"""
    try:
        conn = sqlite3.connect("security.db")
        cursor = conn.cursor()
        
        objects_str = ", ".join(objects) if isinstance(objects, list) else str(objects)
        cursor.execute(
            "INSERT INTO alerts (objects, confidence) VALUES (?, ?)",
            (objects_str, confidence)
        )
        
        conn.commit()
        conn.close()
        print(f"✅ Alert saved to database: {objects_str}")
    except Exception as e:
        print(f"❌ Failed to save alert: {e}")

def get_alerts(object_name=None, minutes=None):
    conn = sqlite3.connect("security.db")
    cursor = conn.cursor()

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

    alerts = []
    for row in rows:
        alerts.append({
            "id": row[0],
            "objects": row[1],
            "confidence": row[2],
            "timestamp": row[3],
        })

    return alerts