import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_notification(title: str, message: str, level: str = "critical"):
    success = False
    
    if SLACK_WEBHOOK_URL:
        if send_slack_notification(title, message, level):
            success = True
            
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        if send_telegram_notification(title, message):
            success = True
            
    if not success:
        pass # Optional: log that no active channels were found

def send_slack_notification(title: str, message: str, level: str) -> bool:
    color = "#FF0000" if level == "critical" else "#FFCC00"
    payload = {
        "attachments": [
            {
                "fallback": title,
                "color": color,
                "title": title,
                "text": message
            }
        ]
    }
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
        response.raise_for_status()
        print("Notificación Slack enviada.")
        return True
    except Exception as e:
        print(f"Error al enviar notificación a Slack: {e}")
        return False

def send_telegram_notification(title: str, message: str) -> bool:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"""*{title}*

{message}""",
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        print("Notificación Telegram enviada.")
        return True
    except Exception as e:
        print(f"Error al enviar notificación a Telegram: {e}")
        return False
