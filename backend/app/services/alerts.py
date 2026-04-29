import time
from app.services.telegram_service import send_telegram_alert

def trigger_alert(objects):
    print("🚨 ALERT:", objects)

    send_telegram_alert(objects)

last_alert_time = 0
ALERT_COUNTDOWN = 10
alert_history = []


def _contains_threat(detected_objects):
    for obj in detected_objects:
        label = obj.lower()

        if label in ["knife", "gun"]:
            return True

    return False


def should_trigger_alert(detected_objects):
    current_time = time.time()

    if current_time - last_alert_time < ALERT_COUNTDOWN:
        return False

    return _contains_threat(detected_objects)


def trigger_alert(detected_objects):
    global last_alert_time

    if not should_trigger_alert(detected_objects):
        return None

    current_time = time.time()
    last_alert_time = current_time

    alert = {
        "timestamp": current_time,
        "message": "Threat detected",
        "detected_objects": detected_objects,
    }
    alert_history.append(alert)

    print("ALERT: Threat detected! Detected objects:", detected_objects)
    return alert


def get_alerts():
    return list(reversed(alert_history))