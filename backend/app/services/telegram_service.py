import requests
import os
from pathlib import Path


def send_telegram_alert(objects):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("⚠️ Telegram alert skipped: set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")
        return

    message = f"🚨 ALERT! Dangerous object detected: {objects}"

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": message
    }

    try:
        response = requests.post(url, data=data, timeout=10)
        if response.ok:
            print("📱 Telegram alert sent!")
        else:
            print(f"❌ Telegram API error {response.status_code}: {response.text}")
    except Exception as e:
        print("❌ Telegram failed:", e)