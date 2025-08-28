from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# Replace these with your Telegram API credentials
api_id = 22071176
api_hash = '7ed5401b625a0a4d3c45caf12c87f166'

print("This script will help generate your string session for Telethon.")

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print("Please enter the phone number associated with your Telegram account.")
    phone = input("Phone number (international format): ")
    client.start(phone=phone)
    print("\nHere is your string session. Keep it secret and safe:\n")
    print(client.session.save())
