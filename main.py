import os
from telethon import TelegramClient, events
from dotenv import load_dotenv

# ===== LOAD ENV VARIABLES =====
load_dotenv()  # Loads variables from .env file

api_id = int(os.getenv("API_ID"))       # Your Telegram API ID
api_hash = os.getenv("API_HASH")        # Your Telegram API Hash
bot_token = os.getenv("BOT_TOKEN")      # Optional: for bot account

# ===== TELETHON CLIENT =====
session_name = 'userbot'  # Name of the session file
client = TelegramClient(session_name, api_id, api_hash)

# ===== BOT COMMANDS =====

# .alive command
@client.on(events.NewMessage(pattern=r'\.alive', outgoing=True))
async def alive(event):
    await event.reply("I am alive! 😺")

# Auto-reply example: reply to "hi"
@client.on(events.NewMessage(pattern=r'hi', incoming=True))
async def auto_reply(event):
    await event.reply("Hello! How are you?")

# ===== START CLIENT =====
print("Userbot is starting...")

# Starts the client; uses bot_token if provided
client.start(bot_token=bot_token if bot_token else None)

# Keep running until disconnected
client.run_until_disconnected()
