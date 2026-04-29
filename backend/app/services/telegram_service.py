import requests

BOT_TOKEN = "8328434210:AAF1BJSKfYvo02D3WZhaEpltJrLo32MV6Hw"
CHAT_ID = "5004747207"

def send_telegram_alert(objects):
    message = f"🚨 ALERT! Dangerous object detected: {objects}"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        requests.post(url, data=data)
        print("📱 Telegram alert sent!")
    except Exception as e:
        print("❌ Telegram failed:", e)