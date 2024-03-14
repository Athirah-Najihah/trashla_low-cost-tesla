# telegram_util.py

from telegram import Bot
from datetime import datetime
import configparser

def send_telegram_notification():
    try:
        # Load Telegram configurations from the config file
        config = configparser.ConfigParser()
        config.read('config.txt')

        TOKEN = config.get('TELEGRAM', 'TOKEN')
        CHAT_ID = config.get('TELEGRAM', 'CHAT_ID')

        bot = Bot(token=TOKEN)
        location = "FK Level 1"
        current_time = datetime.now().strftime("%Y-%m-%d, %I:%M:%S %p")
        message = f"‼️ Garbage Disposal Alert ‼️\nLocation: {location}\nDatetime: {current_time}\nPlease empty the bin."
        bot.sendMessage(chat_id=CHAT_ID, text=message)
        print("Message sent successfully!")
    except Exception as e:
        print(f"Error while sending message: {e}")
