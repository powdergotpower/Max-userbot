import asyncio
import os
import importlib
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# -----------------------------
# Your Telegram API credentials
# -----------------------------
api_id = 22071176
api_hash = '7ed5401b625a0a4d3c45caf12c87f166'
string_session = '1BVtsOJoBu3iNN6Rz96Nwbll7dyrrzoVrKYyWhqtZxJUHSiFsN2XvEU3APCn7Bw5w9n_qfG9N47oP_0Sy-bS2ql4NqMnUEKoHa33Wg0kFYTjskpYL8LsBzgp90PUlYbnKA_vH7iI031GpquW3d1Il9kNr_amnO935Oc6PtsGIucUk3sDuWShwlTN2dnI7YbTAy8kQlFAmkcCNbIWAAvUGiWP7e41veGVTZTxCuH8PebQjKXZdG_xGyxm_yf-WqMbWacHDbT9XMWndcKyAbdLBZsNfCL0xaCEBY30hNBWL30L2o8eOwlY1HiNlEXiBRo09ZYx3Cv4lQeDYkbnMs1M6fDx0NMdXi4c='

client = TelegramClient(StringSession(string_session), api_id, api_hash)

# -----------------------------
# Whitelist: Only these IDs can trigger commands
# -----------------------------
ALLOWED_USERS = [8032922682, 5628638472, 7521335983]

# -----------------------------
# Override add_event_handler to enforce whitelist
# -----------------------------
_original_add_event_handler = client.add_event_handler

def whitelist_add_event_handler(callback, event):
    async def wrapped(event_obj):
        # Only allow whitelisted users to trigger any event
        if getattr(event_obj, 'sender_id', None) not in ALLOWED_USERS:
            return
        await callback(event_obj)
    _original_add_event_handler(wrapped, event)

# Apply the override BEFORE loading modules
client.add_event_handler = whitelist_add_event_handler

# -----------------------------
# Dynamic plugin loader
# -----------------------------
modules_path = "./modules"
for file in os.listdir(modules_path):
    if file.endswith(".py") and not file.startswith("__"):
        module_name = file[:-3]
        module = importlib.import_module(f"modules.{module_name}")
        if hasattr(module, "register"):
            module.register(client)
            print(f"[+] Loaded plugin: {module_name}")

# -----------------------------
# Example built-in command
# -----------------------------
@client.on(events.NewMessage(pattern=r'\.alive'))
async def alive_handler(event):
    await event.edit('I am alive!')

# -----------------------------
# Run the userbot
# -----------------------------
async def main():
    await client.start()
    print("Userbot is running...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
