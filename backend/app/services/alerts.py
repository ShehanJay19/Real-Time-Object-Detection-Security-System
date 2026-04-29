import sqlite3
import time
from app.services.telegram_service import send_telegram_alert

last_alert_time = 0
ALERT_COOLDOWN = 10  # seconds

def should_trigger_alert(detected_objects):
    global last_alert_time

    current_time = time.time()

    # Prevent spam alerts
    if current_time - last_alert_time < ALERT_COOLDOWN:
        return False

    for obj in detected_objects:
        label = obj.lower()

        if label in ["knife", "gun"]:
            last_alert_time = current_time
            return True

    return False


def trigger_alert(objects):
    print("🚨 ALERT:", objects)

    send_telegram_alert(objects)


def get_alerts():
    conn = sqlite3.connect("security.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM alerts ORDER BY id DESC")
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